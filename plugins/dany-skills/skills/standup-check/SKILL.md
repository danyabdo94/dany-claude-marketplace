---
name: standup-check
description: Fact-check the user's open work across Jira and GitLab (one or more repos) and draft the daily standup. Use when the user asks to prep the standup, asks "what's my state", "where are my tickets", "what's waiting on me", or wants Jira and MRs checked against each other. Read-only.
---

# Standup check

The **ticket state** is the point of this skill: one line per ticket that says who holds the ball now, backed by the Jira status, the MR and every open comment thread. A Jira status alone is a claim; the MR is the fact that confirms or breaks it.

Read-only. Never moves a ticket, posts a comment, resolves a thread or sends Slack. Every fix is a question for the user.

## Setup

Fill these in once:

- **Jira**: find the cloudId with `getAccessibleAtlassianResources`, and ask the user for the project key. Below, `<project>` stands for that key (tickets look like `PROJ-123`).
- **Reviewer field** (optional): if the project has a "Reviewed by" user field, find its `customfield_XXXXX` id with `getJiraIssueTypeMetaWithFields`. Below, `<reviewer-field>` is that id and `<reviewer-field-number>` is its number alone (for `cf[...]` in JQL). Without such a field, drop it from the JQL and skip the reviewer fact check.
- **GitLab**: the script reads its settings from env vars (or the matching flags):
  - `STANDUP_GITLAB_PROJECTS`: comma-separated project paths, e.g. `my-group/my-app,my-group/my-backend`
  - `STANDUP_TICKET_PREFIX`: the Jira project key, e.g. `PROJ`
  - `STANDUP_GITLAB_HOST` (optional): your GitLab host, e.g. `gitlab.com`. Without it, `glab` uses its own default.
  - The GitLab username comes from `glab api user` unless `--user` is given.

## Steps

1. **Collect the tickets.** Dispatch one `getter:courier` with this JQL, fields `summary, status, assignee, updated, <reviewer-field>`:

   ```
   project = <project> AND statusCategory = "In Progress"
   AND (assignee = currentUser() OR cf[<reviewer-field-number>] = currentUser())
   ```

   Done when the courier returns the table, or the JQL error verbatim.

2. **Collect the MRs.** Dispatch one `getter:courier` that runs this, with every key from step 1, and returns only the exit code and the `errors` array:

   ```bash
   python3 <standup-check skill dir>/scripts/mr_states.py --tickets PROJ-1,PROJ-2 > <scratchpad>/standup-mr.json
   ```

   The script finds every MR in the configured repos where the user is author, assignee or reviewer (open, plus anything updated in the last 14 days), adds the open MRs for the `--tickets` keys (the user can be the Jira reviewer without being the GitLab one, then `my_roles` is empty), and sorts each comment thread into a state (table below). Read the JSON yourself after. Done when the file exists and every repo is in it or named in `errors`.

   Then fetch status and assignee for every ticket key in the JSON that step 1 did not return (`key in (...)`, same fields, one courier). Done when every ticket key from both sides has a Jira status, or is flagged as not found.

3. **Join and judge.** One row per ticket, its MRs under it. Give each row one ticket state from the list below and run every fact check. MRs with no ticket key get their own row. Done when every ticket and every open MR has a state.

4. **Report** in the output format. Done when every mismatch from step 3 shows up as a fix question.

## Comment thread states (from the script)

System notes and the CodeRabbit walkthrough are dropped. `source` is `coderabbit` or `human`. `kind` is `diff`, `general` or `overview`. An overview comment cannot be resolved, so "not replied" there may only be an LGTM: read its `text` before you count it.

| State | On the user's MR | On an MR the user reviews |
|---|---|---|
| `not replied` | someone commented, the user never answered | |
| `they replied again` | the user answered, the other side wrote back | |
| `replied, not resolved` | the user answered last, the thread is still open | |
| `waiting on author` | | the user wrote last, the author has not answered |
| `author replied, check it` | | the author answered the user's thread |
| `other reviewer thread` | | a thread between other people |
| `resolved` | counted in `thread_counts`, not listed | same |

## Thread outcomes (from the script)

Every thread, open or resolved, also gets an `outcome`, judged from what the **MR author** did with it. `by_commenter` counts them per commenter (`CodeRabbit`, or the reviewer's name), next to `threads`, `open` and `resolved`. `author_rounds` is how many times the author came back into the thread; 2 or more is a back and forth.

| Outcome | Signal |
|---|---|
| `argued` | an author reply pushes back: "leaving as is", "on purpose", "out of scope", "follow-up" and similar. Wins over every other signal |
| `fixed` | GitLab's "changed this line" note in the thread, or an author reply with a commit SHA, ✅, or a fix word (fixed, done, dropped, renamed...) |
| `answered` | the author replied, no fix and no pushback seen |
| `resolved, no reply` | resolved without a word from the author |
| `not replied` | open, the author never replied |

The outcome is a guess from words and line changes. When one decides a fix question, read the thread `text` first.

## Ticket states

Pick the first one that fits, top to bottom:

1. **Blocked**: Jira says Blocked.
2. **Needs me**: on the user's MR, any `not replied` or `they replied again` thread, a failed pipeline, or `merge_status` is `conflict` or `need_rebase`. On an MR the user reviews: `author replied, check it`, or no thread from the user and no approval from the user yet.
3. **Ready to merge**: the user's MR, approved, pipeline green, `merge_status` is `mergeable`.
4. **Waiting on reviewer**: the user's MR, not a draft, only `replied, not resolved` threads open or no threads, not approved yet.
5. **Waiting on author**: an MR the user reviews, only `waiting on author` or `other reviewer thread` threads open.
6. **Coding**: MR is a draft, or there is no MR yet.
7. **In QA / Done**: MR merged.

## Fact checks

Each hit becomes one fix question. Status names below are examples; match them to your board's workflow.

- Jira `Review` but the MR is a draft, or there is no MR.
- Jira `OPEN`, `Development` or `In Progress` but the MR is open, not a draft and has reviewers: move to Review?
- MR merged but Jira is still `OPEN`, `Development`, `In Progress` or `Review`: move to QA? (`QA`, `Ready for Prod` and `Closed` are fine after a merge.)
- Jira `QA`, `Ready for Prod` or `Closed` but an MR for that ticket is still open.
- The user is the Jira reviewer (`Reviewed by`) but not a reviewer on the MR: ask the author to add the user?
- Open MR with no ticket key in the title or branch.
- No update on the ticket or the MR for more than 5 working days.
- Ticket assigned to someone else while the user is the MR author, or the other way round.

## Output format

Terminal only. Four parts:

1. **Ticket table**: ticket (linked), Jira status, MR (`repo !iid`, linked), ticket state, pipeline, approvals (names), open threads total. Rows that need the user go first.
2. **Comments per MR**: for every open MR with threads, one small table, a row per commenter from `by_commenter`:

   ```
   my-app !1120 · PROJ-123 · 35 threads, 12 open
   | Commenter           | Threads | Open | Fixed | Argued | Answered | No reply |
   | Jane Reviewer       |      35 |   12 |    23 |      1 |        2 |        9 |
   ```

   Under it, every open thread that needs the user, one line each: `file:line`, commenter, state, first 80 chars of `text`. Threads with `author_rounds` of 2 or more get `(back and forth)`.
3. **Fix questions**: a table, one row per hit: `# | Ticket | Jira | MR | Mismatch | Question`, e.g. `1 | PROJ-124 | Review | my-app !1118 | MR merged | Move to QA?`
4. **Standup draft** in the status-update register of the user's voice card (in their `CLAUDE.md`) if they have one: one context line, `•` bullets that start with a past-tense verb for what moved since the last working day (merged MRs, threads answered, status changes), then what is next and any blocker. No question at the end. Facts only from steps 1 and 2.
