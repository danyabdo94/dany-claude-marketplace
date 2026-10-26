#!/usr/bin/env python3
"""Post GitLab MR review findings as inline diff comments (anchored to exact lines).

Why this script exists: `glab api -f "position[new_line]=4"` flattens the nested
position into a bogus key, so GitLab silently creates a *general* note instead of an
inline one. The only reliable path is a raw JSON body (nested `position` object) sent
with Content-Type: application/json. This script does that, fetches diff_refs for you,
and reports per-comment success so a partial failure never goes unnoticed.

Usage:
    python3 post_inline_comments.py --mr <iid|url> [--project <path-or-id>] \
        [--host gitlab.com] [--draft] [--findings <file.json>]   # findings default: stdin

Findings JSON (a list):
    [
      {"path": "lib/foo.dart", "new_line": 42, "body": "markdown..."},
      {"path": "lib/bar.dart", "old_line": 10, "new_line": 10, "body": "..."}
    ]

Line anchoring rules (GitLab):
  - ADDED (green) line   -> set new_line only.
  - CONTEXT (unchanged)  -> set BOTH old_line and new_line (else: "invalid line code").
  - DELETED (red) line   -> set old_line only.
"""
import argparse, json, os, re, subprocess, sys, urllib.parse

# glab refuses to run when the git remote host isn't one it knows (e.g. altssh.gitlab.com).
# Every glab call goes through sh(), so pin GITLAB_HOST here once.
ENV = dict(os.environ)


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, env=ENV, **kw)


def remote_url():
    return sh(["git", "remote", "get-url", "origin"]).stdout.strip()


def derive_project(explicit):
    if explicit:
        # already a path or numeric id; url-encode slashes for the path form
        return urllib.parse.quote(explicit, safe="") if "/" in explicit else explicit
    url = remote_url()
    # git@gitlab.com:group/sub/repo.git  or  https://gitlab.com/group/sub/repo.git
    # also matches altssh.gitlab.com and other subdomain-prefixed mirrors
    m = re.search(r"(?:gitlab\.com[:/])(.+?)(?:\.git)?$", url)
    if not m:
        sys.exit(f"Cannot derive project from remote: {url!r} (pass --project)")
    return urllib.parse.quote(m.group(1), safe="")


def derive_host(explicit):
    if explicit:
        return explicit
    if ENV.get("GITLAB_HOST"):
        return ENV["GITLAB_HOST"]
    return "gitlab.com" if "gitlab.com" in remote_url() else None


def parse_mr(mr):
    m = re.search(r"/merge_requests/(\d+)", mr) or re.search(r"!?(\d+)$", mr)
    if not m:
        sys.exit(f"Cannot parse MR iid from {mr!r}")
    return m.group(1)


def api(project, path, method="GET", body=None):
    args = ["glab", "api", "--method", method,
            f"projects/{project}/{path}"]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "--input", "-"]
        return sh(args, input=json.dumps(body))
    return sh(args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mr", required=True, help="MR iid, !iid, or full URL")
    ap.add_argument("--project", help="group/sub/repo path or numeric id (default: from git remote)")
    ap.add_argument("--host", help="GitLab host for glab (default: GITLAB_HOST, else gitlab.com)")
    ap.add_argument("--findings", help="path to findings JSON (default: stdin)")
    ap.add_argument("--draft", action="store_true", help="post as draft notes instead of published")
    args = ap.parse_args()

    host = derive_host(args.host)
    if host:
        ENV["GITLAB_HOST"] = host

    project = derive_project(args.project)
    iid = parse_mr(args.mr)
    findings = json.load(open(args.findings) if args.findings else sys.stdin)

    r = api(project, f"merge_requests/{iid}")
    if r.returncode != 0:
        sys.exit(f"Failed to load MR {iid}: {r.stderr.strip()}")
    refs = json.loads(r.stdout)["diff_refs"]

    ok = fail = 0
    for f in findings:
        pos = {
            "position_type": "text",
            "base_sha": refs["base_sha"],
            "start_sha": refs["start_sha"],
            "head_sha": refs["head_sha"],
            "new_path": f["path"],
            "old_path": f.get("old_path", f["path"]),
        }
        if "new_line" in f:
            pos["new_line"] = f["new_line"]
        if "old_line" in f:
            pos["old_line"] = f["old_line"]

        if args.draft:
            payload = {"note": f["body"], "position": pos}
            endpoint = f"merge_requests/{iid}/draft_notes"
        else:
            payload = {"body": f["body"], "position": pos}
            endpoint = f"merge_requests/{iid}/discussions"

        res = api(project, endpoint, method="POST", body=payload)
        anchor = f.get("new_line") or f.get("old_line")
        if res.returncode != 0:
            fail += 1
            print(f"FAIL  {f['path']}:{anchor} -> {res.stderr.strip()[:160]}")
            continue
        # verify position attached (published discussions only)
        try:
            d = json.loads(res.stdout)
            attached = bool(d.get("position") or (d.get("notes") or [{}])[0].get("position"))
        except Exception:
            attached = args.draft  # draft endpoint returns a different shape
        ok += 1
        tag = "draft" if args.draft else ("inline ✓" if attached else "⚠ general (position dropped)")
        print(f"OK    {f['path']}:{anchor} ({tag})")

    print(f"\n{ok} posted, {fail} failed.")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
