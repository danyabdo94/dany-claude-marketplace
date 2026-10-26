---
name: explain-diff-to-me
description: Explain a diff to Dany himself, every changed line with a plain-English note on what it does and why, in a private Artifact page with the hard parts first. Use when Dany asks to explain the diff, branch or MR to him, walk him through the changes, or says he does not understand a change. Read-only, posts nothing. For notes that reviewers read on GitLab, use explain-my-mr instead.
---

# Explain Diff To Me

A **line note** is one short plain-English note beside one changed line: what
the line does, and why it is here. The page is for Dany and nobody else reads
it, so a note may say the obvious. Every changed line gets one. Nothing is
posted anywhere.

Neighbours:

- `getter` fetches MR data. Never call `glab` from the main loop.
- `artifact-design` owns how the page looks. Load it before writing the page.
- `writing-plain-code` lists the dense constructs. A line that uses one is a
  **hard part**.

## Steps

1. **Resolve the input to one diff.** Three branches:
   - Nothing given: `git diff develop...HEAD`, or `main...HEAD` when the repo
     has no `develop`.
   - MR URL or number: dispatch a courier for title, description,
     `source_branch`, `target_branch`, iid. Then
     `git fetch origin <source> <target>` and diff
     `origin/<target>...origin/<source>` locally.
   - Commit range or one sha: `git diff a..b`, or `git show <sha>`.

   Dump once to the scratchpad, the same way `mr-review` does:

   ```bash
   git diff <base>...<head>              > $SCRATCH/diff.patch
   git diff <base>...<head> --name-only  > $SCRATCH/changed-files.txt
   git diff <base>...<head> --numstat    > $SCRATCH/numstat.txt
   ```

   Done when `diff.patch` exists and you can state: source, target, file
   count, changed-line count.

2. **Drop generated files, then size-gate.** Skip `*.g.dart`, `*.freezed.dart`,
   `*.mocks.dart`, `*.config.dart`, `*.gr.dart`, `*.lock`, `*.xcodeproj/*`,
   `*.xcscheme`, anything under `build/`, and any file whose header says it is
   generated. Keep the skipped list for the page footer. If more than 400
   changed lines remain, show Dany the per-file counts and ask which files to
   explain first; one page per answer. Done when every kept file has a one-line
   purpose written down and the skipped list is complete.

3. **Read each hunk in its file at head.** Open the whole method, widget or
   view around every hunk, not just the hunk, so the note can say why. Done
   when every kept hunk has been read in context and every removed helper has
   its replacement located.

4. **Write the notes** following `writing-notes.md`. One note per changed line,
   added or removed. A line that is only a bracket, comma or blank shares the
   note of the statement it belongs to, and that note says which lines it
   covers. Mark a note **hard** when the line uses a dense construct, an API
   Dany has not used in this repo before, or a decision that could have gone
   another way. Done when `notes == changed lines` (count both, state both
   numbers) and every jargon term has its meaning in brackets the first time
   it appears in that file.

5. **Load `artifact-design`, then build the page** as `page-layout.md` says.
   Write the HTML to the scratchpad and publish it with the Artifact tool.
   Done when the page is published and holds: header, Start here, Hard parts
   first, Files at a glance, every file section with every note, Glossary,
   Not explained.

6. **Report in chat**: one line with the counts (files, lines, hard parts) and
   the link. No MR comment, no draft note, nothing written into the repo.

## What a line note is not

- Not a review: it never judges the line or suggests a change. If a line looks
  wrong, say so in the chat after the report, not in the page.
- Not an author note for reviewers: that is `explain-my-mr`.
- Not a code comment: nothing written here goes into the source.
