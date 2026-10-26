#!/usr/bin/env python3
"""Collect the state of every MR the user owns or reviews in the configured repos, as JSON.

Settings come from env vars or flags (flags win):
  STANDUP_GITLAB_PROJECTS  --projects       comma-separated GitLab project paths
  STANDUP_TICKET_PREFIX    --ticket-prefix  Jira project key, e.g. PROJ
  STANDUP_GITLAB_HOST      --host           GitLab host (optional, glab default otherwise)
"""

import argparse
import concurrent.futures
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.parse

PROJECTS_ENV = "STANDUP_GITLAB_PROJECTS"
TICKET_PREFIX_ENV = "STANDUP_TICKET_PREFIX"
HOST_ENV = "STANDUP_GITLAB_HOST"

# set in main() from env vars or flags
GITLAB_HOST = None
TICKET_PATTERN = None
BOT_USERNAME_PATTERN = re.compile(r"^(group|project)_\d+_bot")
COMMIT_PATTERN = re.compile(r"\b[0-9a-f]{7,40}\b")
FIX_WORDS = [
    "✅", "fixed", "done", "dropped", "removed", "renamed", "moved", "switched",
    "swapped", "updated", "added", "changed", "folded", "merged", "addressed",
]
ARGUE_WORDS = [
    "leaving as is", "leave as is", "keeping", "kept as", "on purpose", "by design",
    "intended", "won't", "will not", "not going to", "disagree", "out of scope",
    "separate ticket", "follow-up", "follow up",
]


def call_api(path):
    environment = dict(os.environ)
    if GITLAB_HOST:
        environment["GITLAB_HOST"] = GITLAB_HOST
    result = subprocess.run(
        ["glab", "api", path],
        capture_output=True,
        text=True,
        env=environment,
    )
    if result.returncode != 0:
        raise RuntimeError(f"glab api {path} failed: {result.stderr.strip()}")
    return json.loads(result.stdout)


def call_api_all_pages(path):
    items = []
    page = 1
    separator = "&" if "?" in path else "?"
    while True:
        page_items = call_api(f"{path}{separator}per_page=100&page={page}")
        items.extend(page_items)
        if len(page_items) < 100:
            return items
        page += 1


def is_bot(author):
    username = author.get("username", "").lower()
    name = author.get("name", "").lower()
    if "coderabbit" in username:
        return True
    if "coderabbit" in name:
        return True
    return BOT_USERNAME_PATTERN.match(username) is not None


def find_ticket_keys(merge_request):
    text = merge_request["title"] + " " + merge_request["source_branch"]
    keys = []
    for match in TICKET_PATTERN.findall(text):
        key = match.upper()
        if key not in keys:
            keys.append(key)
    return keys


def list_merge_requests(project_path, me, days):
    encoded_project = urllib.parse.quote(project_path, safe="")
    since = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days)
    since_text = since.strftime("%Y-%m-%dT%H:%M:%SZ")

    found = {}
    for role in ["author", "assignee", "reviewer"]:
        open_path = f"projects/{encoded_project}/merge_requests?state=opened&{role}_username={me}"
        recent_path = (
            f"projects/{encoded_project}/merge_requests?state=all"
            f"&{role}_username={me}&updated_after={since_text}"
        )
        for path in [open_path, recent_path]:
            for merge_request in call_api_all_pages(path):
                found[merge_request["iid"]] = merge_request
    return encoded_project, list(found.values())


def search_ticket_merge_requests(encoded_project, ticket_keys):
    found = {}
    for key in ticket_keys:
        path = f"projects/{encoded_project}/merge_requests?state=opened&search={key}&in=title"
        title_matches = call_api_all_pages(path)
        branch_path = f"projects/{encoded_project}/merge_requests?state=opened&search={key}&in=source_branch"
        try:
            branch_matches = call_api_all_pages(branch_path)
        except RuntimeError:
            branch_matches = []
        for merge_request in title_matches + branch_matches:
            if key in find_ticket_keys(merge_request):
                found[merge_request["iid"]] = merge_request
    return list(found.values())


def is_walkthrough(discussion):
    first_note = discussion["notes"][0]
    if not is_bot(first_note["author"]):
        return False
    return first_note.get("position") is None


def short_text(body):
    one_line = " ".join(body.split())
    if len(one_line) <= 140:
        return one_line
    return one_line[:137] + "..."


def has_any_word(text, words):
    lowered = text.lower()
    for word in words:
        if word in lowered:
            return True
    return False


def thread_outcome(discussion, merge_request_author):
    line_changed = False
    author_replies = []
    for note in discussion["notes"][1:]:
        if note.get("system"):
            if "changed this" in note["body"]:
                line_changed = True
            continue
        if note["author"]["username"] == merge_request_author:
            author_replies.append(note["body"])

    for body in author_replies:
        if has_any_word(body, ARGUE_WORDS):
            return "argued"
    if line_changed:
        return "fixed"
    for body in author_replies:
        has_commit = COMMIT_PATTERN.search(body) is not None
        if has_commit or has_any_word(body, FIX_WORDS):
            return "fixed"
    if author_replies:
        return "answered"
    if discussion["notes"][0].get("resolvable") and is_resolved(discussion):
        return "resolved, no reply"
    return "not replied"


def count_rounds(discussion, merge_request_author):
    rounds = 0
    previous_was_author = False
    for note in discussion["notes"]:
        if note.get("system"):
            continue
        is_author = note["author"]["username"] == merge_request_author
        if is_author and not previous_was_author:
            rounds += 1
        previous_was_author = is_author
    return rounds


def thread_state(discussion, me, is_my_merge_request):
    notes = [note for note in discussion["notes"] if not note.get("system")]
    first_note = notes[0]
    last_note = notes[-1]
    started_by_me = first_note["author"]["username"] == me
    last_by_me = last_note["author"]["username"] == me
    has_reply = len(notes) > 1

    if discussion["notes"][0].get("resolvable") and is_resolved(discussion):
        return "resolved"
    if last_by_me:
        if is_my_merge_request:
            return "replied, not resolved"
        return "waiting on author"
    if is_my_merge_request:
        if has_reply:
            return "they replied again"
        return "not replied"
    if started_by_me:
        return "author replied, check it"
    return "other reviewer thread"


def is_resolved(discussion):
    for note in discussion["notes"]:
        if note.get("resolvable") and not note.get("resolved"):
            return False
    return True


def collect_threads(encoded_project, iid, me, is_my_merge_request, merge_request_author):
    discussions = call_api_all_pages(
        f"projects/{encoded_project}/merge_requests/{iid}/discussions"
    )
    threads = []
    for discussion in discussions:
        if discussion["notes"][0].get("system"):
            continue
        if is_walkthrough(discussion):
            continue
        first_note = discussion["notes"][0]
        notes = [note for note in discussion["notes"] if not note.get("system")]
        position = first_note.get("position") or {}
        location = position.get("new_path") or position.get("old_path")
        line = position.get("new_line") or position.get("old_line")

        source = "human"
        commenter = first_note["author"]["name"]
        if is_bot(first_note["author"]):
            source = "coderabbit"
            commenter = "CodeRabbit"

        kind = "diff"
        if discussion.get("individual_note"):
            kind = "overview"
        elif location is None:
            kind = "general"

        threads.append({
            "source": source,
            "kind": kind,
            "commenter": commenter,
            "started_by": first_note["author"]["username"],
            "resolved": is_resolved(discussion) and bool(first_note.get("resolvable")),
            "outcome": thread_outcome(discussion, merge_request_author),
            "author_rounds": count_rounds(discussion, merge_request_author),
            "last_by": notes[-1]["author"]["username"],
            "last_at": notes[-1]["created_at"],
            "note_count": len(notes),
            "state": thread_state(discussion, me, is_my_merge_request),
            "file": location,
            "line": line,
            "text": short_text(first_note["body"]),
        })
    return threads


def summarize_by_commenter(threads):
    summary = {}
    for thread in threads:
        commenter = thread["commenter"]
        if commenter not in summary:
            summary[commenter] = {
                "threads": 0, "open": 0, "resolved": 0,
                "fixed": 0, "argued": 0, "answered": 0,
                "resolved, no reply": 0, "not replied": 0,
            }
        counts = summary[commenter]
        counts["threads"] += 1
        counts[thread["outcome"]] += 1
        if thread["resolved"]:
            counts["resolved"] += 1
        else:
            counts["open"] += 1
    return summary


def count_states(threads):
    counts = {}
    for thread in threads:
        key = thread["source"] + ": " + thread["state"]
        counts[key] = counts.get(key, 0) + 1
    return counts


def describe_merge_request(project_path, encoded_project, merge_request, me):
    iid = merge_request["iid"]
    details = call_api(f"projects/{encoded_project}/merge_requests/{iid}")
    approvals = call_api(f"projects/{encoded_project}/merge_requests/{iid}/approvals")

    is_my_merge_request = details["author"]["username"] == me
    roles = []
    if is_my_merge_request:
        roles.append("author")
    reviewer_names = [reviewer["username"] for reviewer in details.get("reviewers", [])]
    if me in reviewer_names:
        roles.append("reviewer")
    assignee_names = [assignee["username"] for assignee in details.get("assignees", [])]
    if me in assignee_names:
        roles.append("assignee")

    approved_by = [entry["user"]["username"] for entry in approvals.get("approved_by", [])]
    pipeline = details.get("head_pipeline") or {}

    threads = []
    if details["state"] == "opened":
        threads = collect_threads(encoded_project, iid, me, is_my_merge_request, details["author"]["username"])

    return {
        "repo": project_path.split("/")[-1],
        "iid": iid,
        "url": details["web_url"],
        "title": details["title"],
        "source_branch": details["source_branch"],
        "target_branch": details["target_branch"],
        "tickets": find_ticket_keys(details),
        "state": details["state"],
        "draft": details.get("draft", False),
        "author": details["author"]["username"],
        "my_roles": roles,
        "reviewers": reviewer_names,
        "approved_by": approved_by,
        "approved_by_me": me in approved_by,
        "pipeline": pipeline.get("status"),
        "merge_status": details.get("detailed_merge_status"),
        "updated_at": details["updated_at"],
        "merged_at": details.get("merged_at"),
        "thread_counts": count_states(threads),
        "by_commenter": summarize_by_commenter(threads),
        "threads": [thread for thread in threads if thread["state"] != "resolved"],
    }


def split_list(text):
    items = []
    for item in text.split(","):
        item = item.strip()
        if item:
            items.append(item)
    return items


def main():
    global GITLAB_HOST
    global TICKET_PATTERN

    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=14)
    parser.add_argument("--user", default=None)
    parser.add_argument("--tickets", default="", help="comma-separated keys whose open MRs to add")
    parser.add_argument("--projects", default=os.environ.get(PROJECTS_ENV, ""),
                        help=f"comma-separated GitLab project paths (or {PROJECTS_ENV})")
    parser.add_argument("--ticket-prefix", default=os.environ.get(TICKET_PREFIX_ENV, ""),
                        help=f"Jira project key, e.g. PROJ (or {TICKET_PREFIX_ENV})")
    parser.add_argument("--host", default=os.environ.get(HOST_ENV, ""),
                        help=f"GitLab host (or {HOST_ENV}); glab default when empty")
    arguments = parser.parse_args()

    projects = split_list(arguments.projects)
    if not projects:
        parser.error(f"no projects: set {PROJECTS_ENV} or pass --projects")
    if not arguments.ticket_prefix:
        parser.error(f"no ticket prefix: set {TICKET_PREFIX_ENV} or pass --ticket-prefix")

    GITLAB_HOST = arguments.host
    TICKET_PATTERN = re.compile(re.escape(arguments.ticket_prefix) + r"-\d+", re.IGNORECASE)

    me = arguments.user
    if me is None:
        me = call_api("user")["username"]

    report = {"me": me, "merge_requests": [], "errors": []}
    jobs = []
    for project_path in projects:
        try:
            encoded_project, merge_requests = list_merge_requests(project_path, me, arguments.days)
        except RuntimeError as error:
            report["errors"].append(f"{project_path}: {error}")
            continue
        ticket_keys = [key.strip() for key in arguments.tickets.split(",") if key.strip()]
        known_iids = [merge_request["iid"] for merge_request in merge_requests]
        for merge_request in search_ticket_merge_requests(encoded_project, ticket_keys):
            if merge_request["iid"] not in known_iids:
                merge_requests.append(merge_request)
                known_iids.append(merge_request["iid"])
        for merge_request in merge_requests:
            jobs.append((project_path, encoded_project, merge_request))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = []
        for project_path, encoded_project, merge_request in jobs:
            future = pool.submit(describe_merge_request, project_path, encoded_project, merge_request, me)
            futures.append(future)
        for future in futures:
            try:
                report["merge_requests"].append(future.result())
            except RuntimeError as error:
                report["errors"].append(str(error))

    json.dump(report, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
