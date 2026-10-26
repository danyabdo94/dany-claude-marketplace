#!/usr/bin/env python3
"""Build the 🔵 nit round-up comment, with every bullet linked to its line in the MR diff.

Nits are not worth an inline thread each, but they are worthless if the author cannot find
what they refer to. So the round-up is one comment on the MR overview where every bullet
carries a deep link into the diff view, landing on the exact line.

GitLab anchors a diff line with a *line code*:

    sha1(<new file path>)_<old_pos>_<new_pos>

`new_pos` is the line number in the head version (what you already have). `old_pos` is the
old-file counter at that point in the hunk, which is NOT the same number and cannot be
guessed: it has to be walked out of the diff. This script does that walk, then emits
`<mr_url>/diffs#<line_code>`.

When a nit points at a line the diff never touches, there is no line code to build, so the
link falls back to the file at head: `<project>/-/blob/<head_sha>/<path>#L<line>`.

Usage:
    echo '<json>' | python3 nit_roundup.py --mr <iid|url> [--project group/sub/repo] \
        [--host gitlab.com] [--post]

Input JSON (a list, order preserved):
    [{"path": "lib/home/card.dart", "new_line": 31, "text": "isFetching would match..."}]

Prints the comment body to stdout. Nothing is sent unless --post is passed, and --post is
the outward-facing step, so only run it once the user has approved the exact text.
"""
import argparse, hashlib, json, os, re, subprocess, sys, urllib.parse

ENV = dict(os.environ)

HEADER = ("\U0001F535 **Nits, non-blocking**\n"
          "Take or leave, none of these hold the merge up.\n")


def sh(args, **kw):
    return subprocess.run(args, capture_output=True, text=True, env=ENV, **kw)


def remote_url():
    return sh(["git", "remote", "get-url", "origin"]).stdout.strip()


def derive_project(explicit):
    if explicit:
        return urllib.parse.quote(explicit, safe="") if "/" in explicit else explicit
    url = remote_url()
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
    args = ["glab", "api", "--method", method, f"projects/{project}/{path}"]
    if body is not None:
        args += ["-H", "Content-Type: application/json", "--input", "-"]
        r = sh(args, input=json.dumps(body))
    else:
        r = sh(args)
    if r.returncode != 0:
        sys.exit(f"glab api {path} failed: {r.stderr.strip()[:200]}")
    return json.loads(r.stdout) if r.stdout.strip() else {}


def mr_diffs(project, iid):
    out, page = [], 1
    while True:
        batch = api(project, f"merge_requests/{iid}/diffs?per_page=100&page={page}")
        out += batch
        if len(batch) < 100:
            return out
        page += 1


HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@")


def old_pos_map(diff_text):
    """new_line -> old-file counter at that line, walked hunk by hunk.

    Context and removed lines advance the old counter, context and added lines advance the
    new one. An added line's old_pos is the old counter *without* advancing it, which is
    the number GitLab bakes into the line code.
    """
    mapping, old, new = {}, 0, 0
    for line in diff_text.splitlines():
        m = HUNK.match(line)
        if m:
            old, new = int(m.group(1)), int(m.group(2))
            continue
        if not line:
            continue
        tag = line[0]
        if tag == " ":
            mapping[new] = old
            old, new = old + 1, new + 1
        elif tag == "+":
            mapping[new] = old
            new += 1
        elif tag == "-":
            old += 1
        # \ No newline at end of file, and anything else, moves no counter
    return mapping


def build_links(project, iid, nits):
    mr = api(project, f"merge_requests/{iid}")
    mr_url = mr["web_url"]
    head = mr["diff_refs"]["head_sha"]
    project_url = mr_url.split("/-/merge_requests/")[0]

    by_path = {}
    for f in mr_diffs(project, iid):
        by_path[f.get("new_path") or f.get("old_path")] = f

    out = []
    for n in nits:
        path, line = n["path"], n.get("new_line")
        f = by_path.get(path)
        url = None
        if f and line:
            old = old_pos_map(f.get("diff", "")).get(line)
            if old is not None:
                key = f.get("new_path") or path
                code = f"{hashlib.sha1(key.encode()).hexdigest()}_{old}_{line}"
                url = f"{mr_url}/diffs#{code}"
        if url is None:
            anchor = f"#L{line}" if line else ""
            url = f"{project_url}/-/blob/{head}/{path}{anchor}"
            n["fallback"] = True
        loc = f"{path}:{line}" if line else path
        out.append((f"[`{loc}`]({url})", n["text"], n.get("fallback", False)))
    return out, mr_url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mr", required=True, help="MR iid, !iid, or full URL")
    ap.add_argument("--project", help="group/sub/repo path or numeric id (default: from git remote)")
    ap.add_argument("--host", help="GitLab host for glab (default: GITLAB_HOST, else gitlab.com)")
    ap.add_argument("--nits", help="path to nits JSON (default: stdin)")
    ap.add_argument("--post", action="store_true",
                    help="send it as a plain MR comment (/notes). Only after the user approved the text.")
    args = ap.parse_args()

    host = derive_host(args.host)
    if host:
        ENV["GITLAB_HOST"] = host
    project = derive_project(args.project)
    iid = parse_mr(args.mr)
    nits = json.load(open(args.nits) if args.nits else sys.stdin)
    if not nits:
        sys.exit("No nits, no round-up. Post nothing.")

    links, mr_url = build_links(project, iid, nits)
    body = HEADER + "\n" + "\n".join(f"- {loc} {text}" for loc, text, _ in links) + "\n"

    fallbacks = [loc for loc, _, fb in links if fb]
    if fallbacks and not args.post:
        print(f"# note: {len(fallbacks)} nit(s) point outside the diff, linked to the file "
              f"at head instead\n", file=sys.stderr)

    if not args.post:
        sys.stdout.write(body)
        return

    # /notes, never /discussions: a note is a comment, a discussion is a resolvable thread
    res = api(project, f"merge_requests/{iid}/notes", method="POST", body={"body": body})
    print(f"posted: {mr_url}#note_{res.get('id')}")


if __name__ == "__main__":
    main()
