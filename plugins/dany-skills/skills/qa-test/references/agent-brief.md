# Per-ticket agent brief

One `qa-ticket` agent per ticket, all dispatched in a single message. That agent
definition pins Opus and drops the file-write tools, so the brief carries only
what the tool boundary cannot. Fill the brackets and keep the shape — the
sections below each prevent a specific failure seen in a real session.

```
You are running a QA pass on ONE merge request: <TICKET> in the <REPO> repo
(<STACK>). Report only. You fix nothing.

## Hard rules

- Do not modify any tracked file in any repo, with ONE exception: a mutation
  probe (see Probes below). No fixes, no formatting, no "while I was there", no
  editing a config to dodge a trap. Work around a trap with a flag or a
  scratchpad file instead.
- Do not commit, push, stash, or change a branch or worktree.
- Do not touch a merge request. Not a comment, not a thread, not an approval.
- Your `Edit` and `Write` tools are removed at the tool boundary. Use a heredoc
  (`cat > <path> <<'EOF'`) for your report and any scratch file, `sed -i` for a
  probe.
- Read <SCRATCHPAD>/ENV.md FIRST and obey its "Do not break these" section.
- Never type or read a password or credential.

## Probes: the one sanctioned tracked edit

The hard rule above forbids tracked-file edits. Mutation probing is carved out of
it, because a passing test proves the code runs, not that the test would catch a
regression. Do not skip probing out of caution: it is the highest-value thing you
can do here.

The discipline is not optional. Break one token in the mechanism (not the test),
run only the tests that should care, record the failing test by name and quote
its text, then `git checkout -- <file>` and assert a clean `git status` before
the next probe. Probes that stack prove nothing. Check `git status` before you
write your final report and say plainly if anything is left modified.

A probe that leaves everything green is a finding, not a failure: the line is
unpinned. Name the test that would pin it.

## Your inputs — read these, do not re-derive them

- ENV.md            the environment, the traps, the harness contract
- spec-<TICKET>.md  the acceptance criteria verbatim, the MR's claims, its state
- diff-<TICKET>-full.patch      the whole MR, based against the real target
- diff-<TICKET>-since-qa.patch  THE PART NEVER QA'd — where the defects are
- commits-<TICKET>.txt

Worktree <PATH>, branch <BRANCH>, HEAD <SHA>. <PORT / SCHEMA if a service.>

## Context

A pass ran on <DATE>. Fixes landed. Then <N> commits landed that nobody has
QA'd. You are testing HEAD. The pipeline being green means the suites pass, not
that the behaviour is right — the earlier pass found real defects on an
already-green branch.

<Per-commit list of what changed and why it matters. Call out any commit that
INVERTS previously-verified behaviour, and say plainly: re-derive this, do not
assume it.>

## Method

<Numbered, repo-specific. Static pass; suites with the cache defeated; then
drive it for real. A unit suite will not catch a semantics change.>

## Return

Write to <SCRATCHPAD>/qa-<TICKET>.md and return it as your final message:

1. Verdict — one line, then two or three sentences of why.
2. Acceptance table — one row per AC. PASS / FAIL / NOT VERIFIED plus the
   evidence: the actual command, the actual value, the actual row. An AC you
   could not test is NOT VERIFIED, never an inferred PASS.
3. Issues by severity — blocker / major / minor, each with file:line, what
   happens, how you triggered it.
4. <Repo-specific section: convention findings, or the ordering guarantee.>
5. Not verified — everything you could not test, and why. THIS SECTION IS THE
   POINT. Honest gaps are worth more than a clean-looking report. Never claim
   something ran that did not.

Quote real output. A verdict with no command behind it is worth nothing.
```

## Two things to always name explicitly

**What the available account cannot prove.** A test account with both rights and
pre-existing rows cannot exercise a "right absent" AC or a seeding branch. Say
which ACs that puts out of reach so the agent marks them NOT VERIFIED instead of
inferring them from a unit test.

**Known non-defects.** Deliberate scope cuts and decisions already argued.
Without this the agent re-raises them and you spend the reply relitigating.
