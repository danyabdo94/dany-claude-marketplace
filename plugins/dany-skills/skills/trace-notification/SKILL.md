---
name: trace-notification
description: Trace where a notification stops when it never arrived: a push, a Notification Center row, or a badge. Use when QA or a user reports a missing notification, when one account gets it and another does not, when a green status code disagrees with what the user sees, or when you need to prove which stage dropped it instead of guessing. Drives real dev environments through probes, witnesses and controls.
---

Something did not arrive. The job is to find the **stage that dropped it**, and to prove it, not to guess it.

The whole method rests on one move: find a **witness**. Everything else is arranging probes so the witness can testify.

A **witness** is a signal that is per-subject, durable, and sits outside the path under test. A counter shared by every account is not a witness. A log line that only appears on success is not a witness.

Rank candidates by **closeness to the missing thing**. Reading the artifact itself always beats reading a proxy for it: if the user says a row never appeared in a list, read that list. Drop to a proxy only when the real read needs an auth you do not have, and say out loud that you dropped, because a proxy answers a slightly different question than the one asked.

The strongest move is **two witnesses at different stages**. One before the break and one after it localises the failure in a single probe, with no guessing in between: the earlier witness moving while the later one stays flat names the stage between them. Look for a pair before you settle for one.

For a live bug in code you can run locally, use `mattpocock-skills:diagnosing-bugs` instead. This skill is for the case where the failure only exists on a real environment and you cannot attach a debugger.

## Steps

1. **Name the subject and the claim.** Which account, id or address, what should have arrived, when, and on which environment. Take the identifiers from the reporter, never from memory. If the claim names a token or credential, decode it and say what it identifies: a service credential names the calling service, not a user, so the subject has to come from somewhere else.
   **Done when** you can write subject, expected thing and environment on one line with real identifiers in it.

2. **Find the witness.** Walk the code path from entry to delivery and list what it writes down. Rank each by: per-subject, durable, written at a known point. Pick the best one and read its current value.
   **Done when** you have named the witness, said which line of code writes it, and read it once. If nothing qualifies, say so out loud before probing, because every later result will be weaker.

3. **Probe.** Fire one controlled request, synchronously, with a fresh unique id, and read the witness before and after from the same source.
   **Done when** you hold a before and after pair. The pair is the finding. A status code is not.

4. **Split the axis, then run a control.** Vary one dimension per probe (subject, location, type, attribute) until you can name what the failure follows. Then send the same probe down the identical path for a different subject.
   **Done when** you can say which dimension the failure tracks, and you can point at a subject that succeeded on that exact path. A passing control turns "the feature is broken" into "this subject is blocked", which is a different ticket.

5. **Discriminate what survives.** If two causes still explain everything, find a signal that only one of them can move, and move it. A counter that increments in one branch but not the other separates them in a single probe.
   **Done when** one cause is left, or you have written down exactly which query or table read would separate the rest. Naming the unresolved fork is a real answer. Guessing between them is not.

## The liars

Each of these looks authoritative and is not. All five cost real time in practice.

- **An async ack.** `202` on a fire-and-forget endpoint means accepted, not done. The work runs after the response and its exceptions never reach you. Re-fire with the synchronous flag before believing anything.
- **A per-pod counter.** Scraping a service's own metrics endpoint gives you whichever replica answered. Counters can go *down* between two reads. Aggregate in the metrics backend instead, and never compare two raw scrapes.
- **A missing log line.** Silent drops are normal: a filter that removes a recipient often writes nothing at all. Absence is evidence only after you have checked that the path logs on that branch.
- **A green status.** It covers transport, not the business decision. The request was accepted and the recipient was still dropped three layers down.
- **Your memory of the "before" value.** Read it from the same source you will read "after" from, in the same session. A remembered baseline has silently moved.

## Pointers

Three worked runs, each stopping at a different stage (send gate, read filter, device fan-out), are in
[`references/examples.md`](references/examples.md). Read one when you want the shape of a full run.

The signal map for your stack (which endpoints answer with the service credential, which metric separates which gate, the Grafana and Loki query recipes, and which datasource is a trap) lives in [`references/signals.md`](references/signals.md). It is a template: fill it in once for your services, then read it whenever the subject is one of them.

For anything that has to be fetched from Jira, Confluence, GitLab or Slack along the way, go through `getter:getter` couriers rather than fetching from the main loop.

Grafana reads (a witness counter, a Loki tally, a before and after pair) go through the `grafana-fact-checker` agent from this plugin, one question per agent, so raw metric and log responses stay out of the main loop. Hand it the exact metric, labels and time window from the signal map, and the probe's unique id when there is one.
