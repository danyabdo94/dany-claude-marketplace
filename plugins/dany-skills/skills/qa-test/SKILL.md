---
name: qa-test
description: Run a QA pass over one or more merge requests, one read-only agent per ticket. Use when the user wants to QA, test, retest or verify tickets or MRs, start or resume a QA session, check whether a branch still meets its acceptance criteria, re-run a pass after new commits landed, or hands over a handoff document to pick up. Also reach for it when asked to prove a guarantee is really pinned by a test rather than merely passing.
---

# QA Test

A QA pass is worth exactly as much as the evidence under it. The failure this
skill exists to prevent is a clean-looking report whose rows were inferred from
a green pipeline. **A green pipeline means the suites pass. It does not mean the
behaviour is right** — every session so far has found real defects on branches
whose pipelines were already green.

Two branches:

- **First pass**, no handoff. Start at step 2.
- **Retest**, driven by a handoff from a previous session, which adds step 1.

## 1. Read the handoff, then distrust it

A handoff is a **map, not a verdict**: it tells you where the bodies are buried,
not what is true today. It was written at a moment that has passed, and commits,
pipelines and environments have moved under it.

Verify before you dispatch anything. Cheap, and it has caught something every
time:

- Every SHA. `git -C <repo> log -1 --format='%h %s'` per branch. A HEAD one
  commit past the handoff means one commit nobody has read.
- Every branch and worktree, and whether the tree is clean and level with origin.
- Every environment claim. Run `scripts/verify-env.sh`.
- Every pipeline status. The handoff's "green" is a snapshot; re-fetch it.
- Every "still on disk" claim. Scratchpads are swept. **Assume last session's
  scripts are gone** and check.
- Every trap it warns you about. One handoff said a logging fix had regressed
  when the fix had been deliberately moved to another MR, which sends you hunting
  a bug that does not exist. Confirm the cause before you accept the framing.

**Done when** every row of the handoff's state table is either confirmed or
corrected in writing, and the corrections are in your first reply to the user. They
read those corrections as the real status; burying them costs them the session.

## 2. Rebuild the harness rather than inherit it

A **harness** is the fixtures, stubs and seed data a pass runs against. Last
session's harness was deleted while its handoff survived, and the orphaned stub
process was still listening with its source gone — reconfigurable only through a
full-replace endpoint with no way to read it back.

So: rebuild from your repo's stub scripts, on a fresh port, and leave any orphan running
untouched as a fallback. Never probe a live stub with a write call to learn its
schema; that is how a config gets destroyed.

Write the contract down in `ENV.md` in the scratchpad as you go — ports, tokens,
schemas, what not to kill. The agents read it instead of rediscovering it, and
it becomes the next handoff's environment section.

**Done when** the harness answers a real request and `ENV.md` describes it well
enough that someone else could drive it.

**If it will not come up**, do not stall the pass and do not quietly dispatch
anyway. Say in `ENV.md` and in your first reply to the user which paths are now
untestable, dispatch with that gap named in every brief, and let the agents mark
those ACs NOT VERIFIED. A pass that reports half the truth loudly beats one that
waits for a harness nobody can fix today.

## 3. Fetch the spec through couriers

Acceptance criteria are the only thing a verdict can be measured against, and
they live in Jira, not in the code or the MR. Load the `getter` skill and
dispatch one courier per source — never fetch from the main loop.

Ask each courier for ACs **verbatim and untruncated**. A renumbered or
paraphrased AC quietly changes what you are testing against.

Write one `spec-<TICKET>.md` per ticket holding: the ACs, the claims the MR
description makes (as claims, not facts), and the MR's fetched state.

**Done when** every ticket has a spec file and no AC exists only in a courier's
reply.

## 4. Hand the agents their inputs

Every agent that re-runs `git diff` or re-greps the repo pays full price for
context you already had. Dump it once:

- `diff-<TICKET>-full.patch` — the whole MR, against the **real** target branch.
  An MR often targets a feature branch, not the main one; diffing against the
  wrong base buries the change in unrelated files.
- `diff-<TICKET>-since-qa.patch` — commits since the last pass. **This is the
  unreviewed code**, and where the defects are.
- `commits-<TICKET>.txt`.

**Done when** each ticket has both diffs, and the full diff's file count is
plausible for the change.

## 5. Dispatch one agent per ticket, in parallel

One agent per ticket, all in a single message, `subagent_type: "dany-skills:qa-ticket"`.
Never `general-purpose`. The definition pins Opus and removes `Edit`, `Write`
and `NotebookEdit` at the tool boundary, so the write boundary is enforced
rather than merely asked for. Do not pass a `model` override.

`Bash` stays, because a pass has to run suites, drive services and probe. So the
rules Bash cannot enforce still go in the brief: **no tracked-file change
outside a mutation probe, no commit, no push, no touching an MR.** Reports and
scratch files go through a heredoc.

Each agent gets: `ENV.md`, its spec, both its diffs, its commit list, its report
path, and the path of its repo reference.

**Above three or four tickets, ask the user which come first.** A pass is 150 turns
of Opus per ticket, and six of them at once is a bigger commitment than the word
"parallel" makes it sound. Better to land three trustworthy verdicts today than
six thin ones.

Use `references/agent-brief.md` as the template.

Two rules to put in every brief:

- **PASS / FAIL / NOT VERIFIED**, never an inferred PASS. Quote the command, the
  counter value, the actual row.
- **The "not verified" section is the point.** The honest gaps are worth more
  than a clean report. An agent that hides a skipped path has produced nothing.

**Done when** every ticket has an agent in flight.

## 6. Prove the guarantees with mutation probes

A passing test proves the code runs, not that the test would catch a
regression. A **mutation probe** settles it: break the mechanism deliberately,
one token, and watch a named test fail.

This is the single highest-value technique in every session so far. It found a
correct-but-unpinned guard, and it re-established an ordering guarantee whose
earlier proof had been voided by a rewrite.

The ticket agents run their own probes, and a probe **is** a tracked-file edit,
so it is the one edit carved out of "never modify a tracked file". Say that in
every brief, or an agent obeying the hard rule will skip the best thing it could
have done. The carve-out is only as safe as the restore, so the brief must carry
that too: one token, run the named test, `git checkout -- <file>`, assert a clean
`git status` before the next probe, and check the tree is clean before writing
the final report.

Full method and the restore discipline: `references/mutation-probe.md`.

## 7. Reconcile, then report

Agents work in isolation, so two can describe the same thing differently and
both be partly right. Where their accounts touch, check yourself before
relaying — a commit history that looks like a regression to one agent and a
deliberate revert to another is one fact, and the user needs the resolved version.

Lead with the verdict per ticket, then what they must act on. Findings that cross
tickets matter most: a release-order dependency, a fix that lives on one branch
and not the other, a shared fixture whose safety net was weakened.

**Done when** every ticket has a verdict, every cross-ticket finding is stated
once, and every gap is named.

## Repo reference

Every repo has traps that cost real time and are not guessable: the toolchain
version the build needs, a task runner that caches a pass and reports green
without running anything, ports and schemas, containers shared with other
work, how to drive it for real. Keep one `<repo>.md` per repo, next to your
handoffs or in the repo's `.claude/` folder, and hand its path to every agent.

A good reference answers: how to build in a fresh worktree, how to defeat the
test cache (`--rerun-tasks`, `--no-build-cache`, deleting a marker), what must
never be torn down, and what "driving it for real" means for this codebase.
If none exists yet, write it during step 2 from what you learn.
