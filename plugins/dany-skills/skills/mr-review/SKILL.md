---
name: mr-review
description: Review a GitLab merge request on two axes (Codebase + Ticket) in parallel sub-agents, triage every finding to a colour-coded priority, then post them as inline diff comments anchored to exact lines, always asking for explicit approval first. Use when the user wants an MR reviewed, wants review comments posted on a GitLab MR, or asks to review a branch/PR/merge request.
---

# MR Review

Two-axis review of a GitLab MR, then inline comments on the exact diff lines.

- **Codebase**: does the code conform to this repo's documented coding standards?
- **Ticket**: does the code faithfully implement the originating ticket / PRD / spec?

Both axes run as **parallel sub-agents** so they don't pollute each other's context.
Findings are then triaged to a priority, shown to the user, and (only on an explicit
yes) posted as inline diff comments.

## 🚫 No em dashes, anywhere

Not in the posted comments, not in the console report, not in this file. Use a comma,
colon, parentheses, or a second sentence. Plain hyphen for ranges (`1-3`). An em dash is
the single clearest tell that a comment was machine-written, and these go out under
the reviewer's name.

---

## 🛑 Hard gate: never post without an explicit yes

**Posting to GitLab is outward-facing and visible to the whole team. Ask every single
time, immediately before posting, using `AskUserQuestion`.**

The gate is **not** satisfied by any of these:

- auto-accept / auto-approve / bypass-permissions mode being on
- the user having asked for the review (that authorises the *review*, not the *posting*)
- a "yes" from an earlier review, an earlier MR, or earlier in this same conversation
- a plan approval, or the user saying "go ahead" about some other step
- the user pasting an MR URL

If `AskUserQuestion` is unavailable, ask in plain text and stop. If the answer is anything
other than a clear approval, **do not post**, deliver the report and stop. Never post
"just the blockers" as a compromise unless the user picked that option.

Editing or deleting notes already on the MR counts as posting. Ask again.

---

## Steps

### 1. Resolve the MR

Accept a URL, `!iid`, or infer from the current branch:
`glab mr list --source-branch $(git branch --show-current)`.

**Gotcha:** if the git remote is not literally `gitlab.com` (e.g. `altssh.gitlab.com`),
bare `glab` fails with *"None of the git remotes … point to a known GitLab host"*.
Prefix every `glab` call with `GITLAB_HOST=gitlab.com` and pass `--repo <group/sub/repo>`.

### 2. Gather context with the `getter` skill

Invoke the **`getter`** skill and let its Haiku couriers fetch, in parallel, everything
the review needs. Dispatch one courier per source:

| Courier | Fetches |
|---|---|
| GitLab MR | title, author, source/target branch, `diff_refs` (`base_sha`, `start_sha`, `head_sha`), description, commit list, existing discussions (for bot dedupe and the open-thread check of step 11) |
| Jira ticket | the `MOB-####` (or `SOC-`, `IN-`, …) key from the branch/title: summary, description, acceptance criteria, links |
| Confluence / PRD | any spec page linked from the ticket description, **body in full** |
| Figma (optional) | design node references, only if the ticket links them and the diff is UI-heavy |

Couriers return raw facts only, no analysis. Write the fetched spec to the scratchpad as a
single Markdown file so the Ticket sub-agent can read it in one go.

**If no spec is found:** ask the user where it is. If they say there isn't one, skip the
Ticket sub-agent and say so in the report. Never invent acceptance criteria.

### 3. Pin the fixed point

Use the MR's `diff_refs`: `base_sha` is the merge-base, `head_sha` is the MR head.
The canonical diff command is:

```bash
git diff <base_sha>...<head_sha>          # three-dot, against the merge-base
git log <base_sha>..<head_sha> --oneline
```

Before going further, confirm both SHAs resolve locally (`git rev-parse`, `git fetch`
first if not) and the diff is non-empty. A bad ref or empty diff must fail **here**, not
inside two parallel sub-agents.

Then dump the diff once, to the scratchpad, so neither axis has to re-derive it:

```bash
git diff <base_sha>...<head_sha>              > $SCRATCH/diff.patch
git diff <base_sha>...<head_sha> --name-only  > $SCRATCH/changed-files.txt
git log  <base_sha>..<head_sha> --oneline     > $SCRATCH/commits.txt
```

Both axes read those three files. Two agents each re-running `git diff` and re-listing the
tree is the single largest waste in this skill: it buys nothing and costs a third of every
axis run.

### 4. Spawn both axis sub-agents in parallel

One message, two `Agent` calls, `subagent_type: "dany-skills:mr-review-axis"` for both. Never
`general-purpose`: the axis agent is pinned to a cheaper model and has its write tools
removed at the tool boundary, and a review axis that can edit files is a review axis that
starts fixing things. Do not pass a `model` override, the definition owns that.

Both prompts must carry every input the axis needs, because the axis agent is told not to
go hunting for context it was not handed. A missing input comes back as a complaint
instead of a review.

**Codebase sub-agent**, give it:
- the scratchpad paths from step 3 (`diff.patch`, `changed-files.txt`, `commits.txt`) and
  the `base_sha`/`head_sha`, so it can resolve a line without re-deriving the diff
- the standards sources you found: `CLAUDE.md`, `CONTRIBUTING.md`,
  `CODING_STANDARDS.md`, `.specify/memory/constitution.md`, plus 1-2 comparable existing
  features as the de-facto convention reference
- the path `references/smell-baseline.md` (in this skill dir) and an instruction to read it
- **the brief:** "Report, per file/hunk, (a) every place the diff violates a documented
  standard: cite the standard (file + rule); (b) any baseline smell: name it and quote
  the hunk; and (c) every code comment the diff adds that is verbose, narrates the obvious,
  or restates the code: quote it and propose the one-line why-only version (or deletion).
  Distinguish hard violations from judgement calls. Documented-standard breaches
  can be hard, baseline smells are always judgement calls, and a documented repo standard
  overrides the baseline. Skip anything tooling enforces. Use `file:line` references. Under
  400 words."

**Ticket sub-agent**, give it:
- the same three scratchpad paths and the two SHAs
- the scratchpad path of the spec file from step 2
- **the brief:** "Report (a) requirements the spec asked for that are missing or partial;
  (b) behaviour in the diff that wasn't asked for (scope creep); (c) requirements that look
  implemented but where the implementation is wrong. Quote the spec line (requirement
  number or acceptance scenario) for each finding and give a `file:line` reference. Under
  400 words."

**When the MR was authored by a non-engineer or by an AI** (PM using Claude, a bot, a
"Generated with Claude Code" footer), say so explicitly in both prompts and tell them to
apply extra scrutiny. AI-authored changes tend to fork existing widgets/services instead
of reusing them, substitute an easier API for the specified one, ship tests that were
never re-run after the implementation changed, and over-comment (paragraph comments,
what-comments, changelog narration), so the comment-verbosity check in the Codebase brief
matters double here. Instruct both agents to verify the
implementation by reading the code, **not** by trusting the MR description.

### 5. Verify every finding's line number

Sub-agents routinely report **diff-hunk offsets**, not real file lines. Posting those
anchors comments to the wrong code, or to nothing.

For each finding, resolve the true line in the MR head version:

```bash
git grep -n '<pattern>' <head_sha> -- <path>
```

Shell note: `$REF:lib/...` triggers zsh's `:l` modifier. Use `git grep` or
`git show <ref> -- <path>`, never `git show $REF:path`.

Drop any finding whose anchor you cannot confirm, and spot-check the two or three most
severe claims against the real files yourself before reporting them.

### 6. Number and triage every finding

Give every surviving finding a **stable number**, `1..N`, numbered straight through both
axes (Codebase first, then Ticket) so no number is used twice. That number is the handle
the user selects by ("post only 1 and 3"). It lives **in the console report only** and
never appears in a posted comment body.

Then assign exactly one priority:

| Icon | Priority | Meaning |
|---|---|---|
| 🔴 | **Blocker** | Must not merge. Broken behaviour, spec requirement violated, tests that cannot pass, data/security risk. |
| 🟠 | **Major** | Should fix before merge. Hard breach of a documented standard, wrong edge-case handling, missing required test. |
| 🟡 | **Minor** | Worth fixing. Code smells, duplication, judgement calls, naming. |
| 🔵 | **Nit** | Optional. Style, wording, preference. Non-binding. |

Every finding keeps its axis label. Judgement-call smells cap at 🟡 unless they cause a
real defect.

**Nits never get their own inline comment.** 🔴, 🟠 and 🟡 anchor to their diff line as
usual. Every 🔵 goes into a single round-up list posted once on the MR overview, as a plain
comment that nobody has to resolve. A nit is by definition not worth a thread: four blue
threads sitting unresolved make an MR look contested when the actual verdict was "looks
good, minor taste notes". The nits keep their numbers in the console report so they can
still be selected individually, and they keep their `file:line` reference inside the list
so they stay actionable.

If a 🔵 seems to deserve its own thread, it was not a nit. Re-triage it to 🟡 rather than
smuggling it out of the round-up.

### 7. Report to the user, one section per priority class

Group the console report by **priority**, one section and one table per class, in order:
🔴 Blockers, 🟠 Majors, 🟡 Minors, 🔵 Nits. Skip a class with no findings.

Each section is a scan table followed by the details for that class only:

```
## 🔴 Blockers (N)

| # | Axis | Location | Finding |
|---|---|---|---|
| 1 | Codebase | `test/foo_test.dart:32` | fixture shape the service never produces |
| 14 | Ticket | `lib/foo_service.dart:47` | specified endpoint replaced by a fuzzy lookup |

**1.** `test/foo_test.dart:32`
<What is wrong, in a sentence.>
**Why it matters:** <the concrete consequence: what breaks, for whom, when. Cite the
requirement number or the standard's rule.>
**Fix:** <the specific change, one line.>
> <the comment body that will be posted, exactly as it will appear>
```

**The 🔵 section is shaped differently.** It is one table, then the single round-up body
exactly as it will be posted, not a per-finding detail block. The user is approving one
comment, so show them that one comment:

```
## 🔵 Nits (3)

| # | Axis | Location | Finding |
|---|---|---|---|
| 9 | Codebase | `lib/home/actions.dart:4` | export looks unused |
| 10 | Codebase | `lib/home/card.dart:31` | `isLoading` reads better as `isFetching` |
| 11 | Codebase | `test/card_test.dart:60` | test name says "renders", it asserts a tap |

Posted as one comment on the MR overview, each bullet linked to its diff line:
> 🔵 **Nits, non-blocking**
> Take or leave, none of these hold the merge up.
>
> - [`lib/home/actions.dart:4`](.../diffs#a1b2c3_0_4) this export looks unused,
>   `home_screen.dart` imports the actions file directly
> - [`lib/home/card.dart:31`](.../diffs#d4e5f6_27_31) `isFetching` would match the cubit,
>   `isLoading` reads like it covers the whole screen
> - [`test/card_test.dart:60`](.../diffs#7a8b9c_58_60) name says "renders" but the body
>   asserts a tap, rename it?
```

Truncate the URLs to `.../diffs#<code>` in the console report. The reviewer is approving the
wording, not proofreading forty hex characters, and the script built them.

**The console report is the detailed one. The posted comment is the terse one.** They are
written differently on purpose: here the user is deciding what to post, so give them
enough to judge without opening the file. The table alone is never the report. Every
finding still gets its "why it matters", its fix, and the exact body that would be posted,
so the user approves the real text rather than a paraphrase.

**Keeping the two axes intact.** Priority is the grouping the user acts on, so it wins the
layout, but the axis distinction must not dissolve into it. Every row and every detail
block carries its axis tag, and the closing summary reports **totals per axis and the
worst issue within each axis**, never a single winner across axes. A change can pass one
axis and fail the other, and a priority-sorted list hides that if the tags go missing.

Numbering runs continuously across the whole report (Codebase first, then Ticket) so a
number identifies exactly one finding regardless of which table it sits in.

### 8. Ask (the gate from the top of this file)

`AskUserQuestion`, e.g. "Post these N comments as inline comments on MR !1076?" with
options: post all / post 🔴+🟠 only / post as draft notes / don't post.

Count the nit round-up as **one** comment, however many nits it holds, and say so ("6
inline, 1 nit round-up covering 3"). "Post 🔴+🟠 only" drops the round-up entirely.

Say in the question that the user can also reply with specific numbers ("post only 1, 3
and 7"), since `AskUserQuestion` always offers a free-text "Other". Honour the answer
exactly. A number list means post exactly those, nothing adjacent, nothing "while we're
here".

### 9. Post

Two things get posted here, by two different routes: the anchored 🔴 🟠 🟡 findings, and
the one 🔵 round-up.

Build a findings JSON list, one object per inline comment, **🔵 excluded**. **Strip the
numbers**, they are a console-only handle:

```json
[{"path": "lib/foo.dart", "new_line": 42, "body": "🔴 **Blocker, [Ticket AC]**\n..."}]
```

```bash
echo '<json>' | GITLAB_HOST=gitlab.com python3 scripts/post_inline_comments.py --mr <iid|url>
```

The script derives the project from `git remote get-url origin`. Pass
`--project group/sub/repo` to override, `--draft` for draft notes. It fetches `diff_refs`
itself, sends a nested `position` object as raw JSON, verifies each note actually attached,
and prints `inline ✓` vs `⚠ general` per comment.

The 🔵 round-up is built and posted by its own script, which resolves each bullet's diff
link and then sends the comment through `/notes`:

```bash
echo '[{"path":"lib/home/card.dart","new_line":31,"text":"isFetching would match the cubit"}]' \
  | GITLAB_HOST=gitlab.com python3 scripts/nit_roundup.py --mr <iid|url>          # prints
  | GITLAB_HOST=gitlab.com python3 scripts/nit_roundup.py --mr <iid|url> --post   # sends
```

Without `--post` it prints the body and sends nothing, which is how you get the exact text
in front of the user at step 8. Only add `--post` once they have said yes to that text.

For each nit it computes the GitLab line code `sha1(<path>)_<old_pos>_<new_pos>` by walking
the MR diff, and links to `<mr_url>/diffs#<line_code>`. A nit pointing at a line the diff
never touched has no line code, so it falls back to `<project>/-/blob/<head_sha>/<path>#L<n>`
and the script says on stderr how many did that. Both land the reader on the right line.

If you post the comment by hand instead, **use `/notes`, not `/discussions`:**

```bash
GITLAB_HOST=gitlab.com glab api --method POST \
  "projects/<P>/merge_requests/<iid>/notes" -F body=@nits.md
```

`/discussions` without a position creates a **thread**, which GitLab renders with a Resolve
button and counts in the unresolved-threads badge that blocks the merge widget. `/notes`
creates a comment, which is what a nit list should be: readable, ignorable, and never
sitting in anyone's way. Getting this endpoint wrong is the whole point of the rule, so
check it before sending.

Write the body to a file and pass it with `-F body=@file` rather than inlining it. A
multi-line list with backticks in `-f body="..."` gets mangled by the shell.

Post it once. If a second round of review later adds nits, edit the existing note
(`PUT .../notes/<note_id>`) rather than posting a second list.

### 10. Confirm

Report per-line results with links. Anything that came back `⚠ general` lost its anchor:
say so, and either re-anchor to a nearby added line or delete it.

The 🔵 round-up and the unanchored summary are supposed to be general notes. Report them as
"posted on the overview", never as a dropped anchor, and confirm the round-up shows no
Resolve button. If it does, it went to `/discussions` by mistake: delete it and repost
through `/notes`.

### 11. Open threads: verify, then ask before resolving

If the MR has open discussion threads (the reviewer's own from an earlier round, or anyone
else's), check each one against the latest diff and the author's replies: addressed,
partially addressed, or unanswered. Report the per-thread status alongside the findings.

Then, for the threads the diff actually addressed, **always ask** (`AskUserQuestion`)
whether to resolve them. Resolving a thread is outward-facing, so the hard gate at the top
applies: never resolve silently, never bundle it into the comment-posting approval, and
never resolve a thread whose fix you did not verify in the code. If a reply is worth
posting along with the resolve (a short "thanks, verified" or a pushback), draft it, show
the exact text, and get a yes on that text before sending.

---

## Writing the comment

This is the part that gets read by a human, so it matters more than the machinery above.

**Run every body through the `add-my-flavor` skill.** Load it, don't approximate it. These
comments publish under the reviewer's name and have to read like a colleague typed them in the
review box, not like a linter with a thesaurus.

### Shape

```
<icon> **<Priority>, <Axis>**
<the finding, in one or two plain sentences>
```

`<Axis>` is written in square brackets and spells out what the axis means, so a reader who
has never seen this skill knows what the finding is grounded in:

- Ticket axis → `[Ticket AC]`
- Codebase axis → `[Codebase issue]`

So the label reads `🔴 **Blocker, [Ticket AC]**` or `🟠 **Major, [Codebase issue]**`. The
console report of step 7 keeps the bare axis names in its tables, only the posted body uses
the bracketed form.

The label sits on its own line, then the prose. No separator character between them, and
never an em dash. The icon and label are structure, not decoration: keep them, they make
the review skimmable. Everything after the label is normal human writing.

That shape is for the anchored comments, 🔴 🟠 🟡. 🔵 has its own, below.

### Rules

1. **Lead with the problem, not the rule.** "this rebuilds the whole list on every
   keystroke" beats "this violates constitution IV". Cite the rule at the end, in
   parentheses, if at all.
2. **Never describe what the code does.** The author wrote it. Go straight to what's wrong
   with it.
3. **One or two sentences.** A blocker may add a short code block and a closing question.
   Nothing else earns more.
4. **Ask when you're not sure, state when you are.** "is this intentional?" is a real
   question and often the right comment. Don't fake uncertainty about a genuine bug.
5. **Frame fixes as shared work.** "can we / should we / let's", never "you must" or
   "consider refactoring".
6. **Keep the technical specifics.** The endpoint, the constant, the file it duplicates,
   the line it conflicts with. Terse is not vague, and a comment the author can't act on
   is wasted.
7. **No consequence essays.** The "why it matters" paragraph belongs in the console report,
   not the MR. Post it only when the consequence is genuinely non-obvious, and then in one
   clause.
8. **Show, don't narrate.** A three-line code block beats a sentence describing the change.
9. **No emoji beyond the priority icon.**
10. **Spec requirements are "AC", written non-linkable.** See below.

### Sounds like a bot vs sounds like a person

| Bot | Person |
|---|---|
| "This violates constitution IV which requires `buildWhen`." | "no `buildWhen` here, can we scope it to what the builder reads?" |
| "Consider extracting this duplicated logic into a shared component." | "this is a copy of `ProfileListItem`, can we reuse it?" |
| "The implementation deviates from the specified endpoint, which may result in incorrect data being returned." | "this searches Places by name instead of fetching the linked listing, so it can return the business next door." |
| "It may be worth considering whether this is the intended behaviour." | "is this intentional?" |
| "This change modifies global state affecting all consumers of the drawer." | "this changes pinning for every drawer section, not just ours." |

The tell in every left-hand cell: it explains rather than points, and it hedges instead of
asking. Read the body out loud. If you wouldn't say it to the author standing at their
desk, rewrite it.

### Spec requirements: call them AC, keep them plain

The numbered requirements in the spec (`FR-015`, `SC-004`, `US-2`, however that doc labels
them) are the ticket's acceptance criteria. In a posted comment call them **AC**, and write
them with a **space, never a hyphen**: `AC 015`, not `FR-015`.

GitLab auto-links any bare `[A-Z]+-\d+` token to the configured Jira project, so `FR-015`
renders as a link to a Jira issue that does not exist. `AC 015` cannot match that pattern,
so it stays plain text with no escaping needed.

Keep the spec's own number so the reference stays traceable (`FR-009a` becomes AC 009a).
This applies to every requirement, acceptance-criterion and success-criterion ID in a
posted body. Real ticket keys (`PROJ-123`) stay bare, those links resolve. The console
report may keep the spec's original labels, nothing linkifies there.

### The nit round-up

One comment, on the MR overview, one bullet per nit. It exists to be skimmed in ten seconds
and then ignored, so it has to look like a list of small things and not like a review.

Every bullet **links to its line in the diff**. A nit list without links is a list of
homework: the author has to find each spot themselves, and the cost of looking outweighs
the value of any single nit, so the whole comment gets skipped. With links it is three
clicks and done.

```
🔵 **Nits, non-blocking**
Take or leave, none of these hold the merge up.

- [`lib/home/actions.dart:4`](https://gitlab.com/g/p/-/merge_requests/12/diffs#a1b2c3_0_4)
  this export looks unused, `home_screen.dart` imports the actions file directly
- [`lib/home/card.dart:31`](https://gitlab.com/g/p/-/merge_requests/12/diffs#d4e5f6_27_31)
  `isFetching` would match the cubit, `isLoading` reads like it covers the whole screen
- [`test/card_test.dart:60`](https://gitlab.com/g/p/-/merge_requests/12/diffs#7a8b9c_58_60)
  name says "renders" but the body asserts a tap, rename it?
```

**Do not hand-write those URLs.** The fragment is a GitLab *line code*,
`sha1(<file path>)_<old_pos>_<new_pos>`, and `old_pos` is the old-file counter at that
point in the hunk, not the line number you have. It has to be walked out of the diff, so
`scripts/nit_roundup.py` builds the whole body for you (step 9). A guessed line code does
not error, it just silently scrolls nowhere.

Rules on top of the ones above:

1. **One line each.** A nit that needs two sentences is not a nit, re-triage it to 🟡.
2. **Lead with the linked `file:line`**, backticked inside the link, so the author can jump
   straight there. No axis label per bullet, the header covers the whole list.
3. **Say up front that none of it blocks.** That one opening line is what stops a list of
   preferences reading like a list of demands.
4. **No numbering.** The console numbers are ours, the author gets bullets.
5. **Keep it short.** Past roughly eight bullets it stops being read. Cut the weakest, or
   fold repeats of the same point into one bullet naming the files.
6. If there is exactly one nit, it is still the round-up comment, not an inline note. The
   rule does not have a special case for N=1.

### Examples

```
🔴 **Blocker, [Ticket AC]**
this searches Places by name + coordinates and takes the first hit, it doesn't fetch the
listing linked to the location. For a mall or a franchise we'd generate a QR pointing at a
different business. AC 015 asks for `GET /locations/{id}/google/page`, did that one not
work?

🟠 **Major, [Codebase issue]**
no `buildWhen` on this `BlocBuilder`, so every search keystroke rebuilds the whole list.
Can we scope it to `locations` and `status`?

🟡 **Minor, [Codebase issue]**
this card is a copy of `ProfileListItem`, can we reuse it with an injected trailing widget?
```

Three icons here, not four: a 🔵 never appears on its own like this, it appears as a bullet
in the round-up above.

Link the file only when the finding points somewhere other than the anchored line.

---

## Line anchoring

GitLab decides inline-vs-general from the `position` object:

- **Added (green) line** → set `new_line` only.
- **Context (unchanged) line** → set **both** `old_line` and `new_line`, or you get
  `400 … "line_code must be a valid line code"`. Prefer anchoring to a nearby **added** line.
- **Deleted (red) line** → set `old_line` only.

Why the script and not raw `glab -f`: `glab api -f "position[new_line]=4"` flattens the
nested position to a bogus flat key, so GitLab **silently creates a general note**.

**Findings with no line** (missing test file, absent feature flag, whole-MR concerns) go in
one MR-level summary note, not forced onto an unrelated line.

**Nits never anchor at all**, whether or not they have a line. They go in the 🔵 round-up.

That makes at most two MR-level posts, and they stay separate: the unanchored summary is
substantive and usually 🔴 or 🟠, the nit round-up is not. Merging them buries a blocker in
a list of naming preferences. Both use `/notes`, so neither shows a Resolve button.

---

## Modifiers (honour when asked)

- **One comment per finding** (default) vs **one discussion per file**: for the latter,
  concatenate that file's findings into one body anchored to a single line. Either way the
  🔵 round-up stays one MR-level comment, it is not per-file.
- **Nits inline anyway**: only if asked outright ("comment on the nits too"). Say that the
  default is the round-up, then honour it and anchor them like any other finding.
- **Draft review**: `--draft` posts to `draft_notes`, the user publishes later.
- **Priority filter**: "only blockers" → drop the rest before building the JSON, and drop
  the 🔵 round-up with them.
- **Selection by number**: "post 1, 3 and 7" → build the JSON from exactly those numbers
  from the step 7 report. If the selection includes some nits but not others, the round-up
  carries only the selected ones. If it includes none, there is no round-up. Read the
  numbers back before posting so a mis-parse is caught before it reaches the MR.
- **Dedupe against bots**: before posting, compare against existing discussions and skip
  lines already flagged by CodeRabbit or others:
  `GITLAB_HOST=gitlab.com glab api "projects/<P>/merge_requests/<iid>/discussions?per_page=100"`,
  matching on `position.new_path` + `position.new_line`.
- **Codebase only / ticket only**: skip the other sub-agent, say so in the report.

## Cleanup

Wrong or duplicate note:

```bash
GITLAB_HOST=gitlab.com glab api --method DELETE \
  "projects/<P>/merge_requests/<iid>/discussions/<disc_id>/notes/<note_id>"
```

Bulk-editing note bodies is slow (roughly 10s per `glab` call). Run them through a
`ThreadPoolExecutor` with 4 workers and raise the Bash timeout, or a 20-note pass will
time out halfway.
