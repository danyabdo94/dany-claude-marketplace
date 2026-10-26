---
name: notification-ticket
description: Gather the context for a ticket in a long, multi-ticket feature epic before touching code: the ticket body, the design doc, where it sits in the release order, and which guard it moves. Use when starting, planning, estimating, reviewing or QA-ing any ticket under the epic(s) listed in references/epic-map.md, and whenever the work touches the code paths that epic owns. A template: fill in the two reference files for your own epic.
---

# Notification Ticket

A template for any long feature epic that spans several tickets, repos and
design pages. The example here is a notification center, but the method fits
any feature where many tickets move the same few guards.

Almost every bug in such an epic comes from the same move: acting on a guard
nobody checked, in a repo that is not the one holding the answer. **Write the
brief before you write code.**

## Setup: your epic

Fill in two files before first use:

- `references/epic-map.md`: the epic(s), the repos and local checkouts, every
  ticket with its repo and what must be live first, and the design pages.
- `references/guards.md`: the guards that decide whether the feature reaches a
  user, which path reads which authority, and where each guard lives in code.

Both ship as templates with `<placeholder>` rows and one made-up example row.
Delete the example rows once yours are in.

## The brief

The brief is five lines. Gathering is done when you can write all five with no
guesses in them:

1. Ticket, repo, epic, wave.
2. What must already be live in production before this can ship.
3. Which guard it moves, on which path.
4. What the design doc already decided, so you do not decide it again.
5. What proves it works.

## Steps

1. **Fetch the ticket and its design doc section.** Through `getter:getter`
   couriers, never straight from the main loop. Take the ticket description
   verbatim: these tickets carry file names, line numbers and acceptance
   criteria that are already correct, and paraphrasing loses them.
   `references/epic-map.md` says which epic and wave the ticket sits in and
   which page covers it.
   **Done when** you hold the full description and the design doc section
   naming this ticket, or you have said out loud that the doc does not cover it.

2. **Find what must be live first.** Several tickets are inert or harmful until
   another one is deployed. `references/epic-map.md` lists every such pair.
   **Done when** you can name the thing that must be live, or say "nothing".

3. **Name the guard.** A few things decide whether the feature reaches a
   person. In the notification example: the product plan, the user's rights,
   the topic switch, and location scope, plus timing rules (grouping, quiet
   hours) for some users. They do not cover the same ground, and the read path
   and the send path may read different authorities. `references/guards.md`
   holds the matrix, the authorities, and where each guard lives in each repo.
   **Done when** you can say which guard this ticket moves, whether it is on the
   read path or the send path, and which authority that path trusts.

4. **State the brief, then start.** Five lines, to the user, before the first
   edit. A line you cannot write without guessing sends you back to step 1.
   **Done when** the five lines are written and none of them contains a guess.

## While you work

Load the style skill for each repo you touch, as listed in
`references/epic-map.md`. For example:

- **Flutter app**: load `writing-flutter-code` first. The project `CLAUDE.md`
  wins on architecture, that skill wins on texture.
- **Kotlin service**: load `kotlin-spring-conventions`.
- Anything a human will read as coming from the user: `add-my-flavor`.

## Retire this

Clear the two reference files when the epic closes. They are a snapshot of one
epic, not a lasting rule, and a stale snapshot is worse than none.
