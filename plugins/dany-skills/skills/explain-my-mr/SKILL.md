---
name: explain-my-mr
description: Leave author notes on Dany's own GitLab MR, one short draft comment per line a reviewer would stop at, explaining why the code is the way it is. Use when Dany asks to explain his MR, add comments on his MR, annotate the diff for reviewers, or "add a comment here" with pasted lines. Drafts only, never published, never on someone else's MR.
---

# Explain My MR

Author notes are the comments the MR author leaves on their own diff before a review starts. They answer the question a reviewer would type, before it is typed. Each one is a **draft note**: GitLab keeps drafts private to the author until they press "Submit review", so Dany reads them in place and publishes them himself.

Two neighbours own parts of this:

- `getter` fetches the MR, its diff refs and the existing drafts. Never call `glab` for a read from the main loop. One exception: confirming a write you just made. Re-reading your own drafts in step 6 is yours to do, a courier is for discovery.
- `add-my-flavor` owns the voice. Its `references/examples-review.md` has the section "Author notes on his own MR" with real samples. Every note passes through it before it is created.

## Steps

1. **Find the MR.** If a URL or number was given, use it. Otherwise dispatch a courier for the open MR whose source branch is the current branch. The courier returns: project path, MR iid, author, `state`, `diff_refs` (`base_sha`, `start_sha`, `head_sha`), and the current draft notes (`GET /projects/:id/merge_requests/:iid/draft_notes`: id, note, `position.new_path`, `position.new_line`). Done when all three shas and the draft list are in hand. Stop and say so if the MR author is not Dany, and stop if the state is `merged` or `closed`: notes on a finished MR are work nobody will read.

2. **Pick the anchors.** Read the diff at head. An anchor is a line where a reviewer would stop: the line that is the actual fix, a decision someone would undo (an order of operations, a fail-open or fail-closed choice, a check that looks redundant), an extracted step, a deleted helper and what replaced it, a value class that replaced a string. When Dany pastes lines, those are the anchors, find their current line numbers with `grep -n` in the worktree. Skip a line that already carries a draft or a published comment saying the same thing; a second angle on the same line is fine.

   **Zero anchors is a real answer.** A version bump, a pure rename, a lockfile refresh: nothing in there needs defending. Say so and stop. A note written to fill the table is filler published in Dany's name.

   **Five to eight notes is the ceiling.** Past that the diff is not asking for notes, it is asking for a better MR description. Move the surplus there and tell Dany you did.

   Done when every anchor has a file path and a line number at `head_sha`, or you have said there are none.

3. **Write each note** in the author-note register. One thought. Say **why**, the diff already says what. A tiny numbered example when ordering or a race is the point. Backticks on identifiers. A drop of context a backend reviewer lacks (which screen, which service call). No greeting, no question close, no severity prefix. Done when no note is over about four lines and none restates its own code.

4. **Flavor pass.** Send the whole set to the `flavor` agent in one call, register "author notes on own MR", and take back the numbered list. Done when every note came back and identifiers are unchanged.

5. **Show Dany the table** before anything is created: `#`, `file : line`, note. Wait for a go. When he says "send" or "go", create them. If he already said "send" for this batch, skip the wait.

6. **Create the drafts.** One `POST /projects/:id/merge_requests/:iid/draft_notes` per note, from the repo directory so `:fullpath` resolves. The body must be JSON and glab needs the header or it answers HTTP 415:

   ```bash
   glab api -X POST -H 'Content-Type: application/json' \
     "projects/:fullpath/merge_requests/<iid>/draft_notes" --input - <<'EOF'
   {"note": "<text>",
    "position": {"position_type": "text",
                 "base_sha": "<base>", "start_sha": "<start>", "head_sha": "<head>",
                 "new_path": "<path>", "old_path": "<pre-rename path, else same>", "new_line": <line>}}
   EOF
   ```

   To reword an existing draft use `PUT .../draft_notes/<id>` with the same shape; a draft can also be moved to another file or line this way. Delete a draft only when Dany says so. Done when a fresh `GET .../draft_notes` lists every note with the intended path and line.

7. **Report** the count and one line per note (`file : line`, first words). Remind him they are drafts until he submits the review. Never call `.../draft_notes/bulk_publish` or `.../publish`.

## What an author note is not

- Not a review comment: it asks nothing and flags nothing. If a line looks wrong while doing this, say it to Dany in the chat, do not write it as a note in his name.
- Not a description: if the note needs a heading or a second paragraph, it belongs in the MR description.
- Not a code comment: nothing written here goes into the source.

## Anchor line rules

`new_line` is the line number in the file at `head_sha`, not in the diff view. A deleted file has no `new_line`; anchor the note to the line that replaced it in the new file instead. After a new push the shas change, existing drafts stay where GitLab put them, and new drafts must use the fresh `diff_refs`.

`old_path` matches `new_path` on an ordinary edit, but on a **renamed** file it is the path before the rename. Copying `new_path` into both fields there gets the note rejected or hung on the wrong line, and the diff is the only place that pairing is visible, so read it off the rename hunk rather than guessing.
