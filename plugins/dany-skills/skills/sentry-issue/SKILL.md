---
name: sentry-issue
description: Triage a production crash from Sentry for a Flutter app, from the alert to a fixed MR. Reads the alert from the Slack Sentry alert channel and the issue page in Chrome, groups related alerts, finds the crash site in the code, files a Jira Bug, links it back on Sentry and Slack, then fixes it through the usual gate. Use when someone shares a Sentry issue link, a Sentry short ID or a Sentry alert from Slack, or asks why the app crashes in production.
---

# Sentry issue

## Setup

Fill these in once:

- `#sentry-alerts` / `<sentry-channel-id>`: the Slack channel where the Sentry bot posts alerts, and its channel ID (`slack_search_channels`).
- `<sentry-host>` and `<org>`: your Sentry host (e.g. `sentry.io` or a self-hosted domain) and organization slug.
- `<SHORT-ID-PREFIX>`: the prefix of your Sentry short IDs (the project slug in caps, e.g. `MY-APP`).
- Jira: the cloudId (`getAccessibleAtlassianResources`) and the project key, `<project>` below (tickets look like `PROJ-123`). Find custom field ids with `getJiraIssueTypeMetaWithFields`: `<env-field>` for a required "Testing Environment" field on Bugs, `<qa-field>` for "QA Testing Notes". Skip any your project does not have.

Two data sources, and neither needs a token:

- **Slack alerts** in `#sentry-alerts` (`<sentry-channel-id>`): short ID, issue
  number, exception, culprit, release, OS, device, counts. Always reachable.
- **The Sentry issue page** through claude-in-chrome, when the user's Chrome is
  logged in to `<sentry-host>`: the stack trace with line numbers,
  breadcrumbs, and the Activity feed. The URL needs the org path:
  `https://<sentry-host>/organizations/<org>/issues/<number>/`.
  Without `/organizations/<org>/` Sentry says "organization not found". A plain
  web fetch returns a generic landing page, so it is Chrome or nothing.

Scans of Slack and Sentry go back **1 month** unless the user says otherwise.

## 1. Read the alert

Fetch Slack through `getter:getter` couriers when that skill is installed; otherwise use the
Slack MCP directly (`slack_search_public_and_private`, `slack_read_channel`,
`slack_read_thread`).

1. Find the alert: search the channel for the issue number (`12345`) or the short ID
   (`<SHORT-ID-PREFIX>-6G8`). The search result shows the bot message with an empty text,
   so read the body with `slack_read_channel` around its timestamp.
2. Read its thread and reactions. A 🎫 reaction means a ticket already covers it.
3. Read the rest of the window and list every alert with the same exception text,
   the same culprit, or the same failing path.
4. Open the issue page in Chrome and read the stack trace (in-app frames with
   `file:line`) and the last breadcrumbs. If Chrome is not logged in, say so and go on
   with the alert alone.

Done when you hold, verbatim: short ID, issue number, exception type and message,
culprit, release, OS, device, events, users, first seen, permalink, the stack trace
or a note that it was not reachable, and the list of related alerts with the same
fields.

## 2. Find the crash site

With a stack trace, the top in-app frame is the crash site: read that line.

Without one, the alert names a function, not a line. Grep the culprit function in
`lib/`, read it, and list **every** operation in it that can throw the reported
exception (each `!` for a null check, each `.first` for a `StateError`, each
`GoRouter` lookup for a `GoException`). Say which one you think it is and label it a
hypothesis. A failing path like `/x/details` points straight at the route tree in
`lib/routes/`.

Then split the related alerts into "same cause" and "unrelated", with one line of
reason each.

## 3. Report and stop

Show the user: the issue facts, the crash site as `file:line` with the code, the
cause (confirmed by a stack trace, or a hypothesis), the related-alert split, and a
proposed fix with a time estimate. Wait for them to ask for a ticket or a fix.

## 4. Ticket

Draft a `<project>` **Bug** with the `jira-ticket` skill. Put the Slack permalinks and short IDs
in the description, never in code comments. Show the full draft and create it only
after the user says "go". Bug-specific fields (check yours):

- **Testing Environment** (`<env-field>`) may be required.
- Priority must be one your project accepts. Some schemes have no "Medium" and reject it.
- QA Testing Notes (`<qa-field>`) goes in as ADF.

The user moves the ticket to In Progress.

## 5. Link the ticket

Once the ticket exists, for every alert in the "same cause" list. Show each draft
and post only after a "go".

1. **Sentry**: if Sentry has no Jira integration set up, the link is an Activity
   comment on the issue page in Chrome:
   `tracked in PROJ-123 <jira url>` (add `, fix in review in !456 <mr url>` once the
   MR exists). Click "Submit comment" and wait until the comment shows in Activity
   before leaving the page. Without Chrome, hand the user the exact list to post by
   hand, one line per issue: `<SHORT-ID-PREFIX>-6G8 (12345) → PROJ-123`. This step is
   never skipped silently.
2. **Slack**: reply in the alert thread with the ticket link, in the user's voice,
   Slack mrkdwn, link as `<url|PROJ-123>`.
3. **Slack**: add a 🎫 reaction to the alert.

Done when every "same cause" alert has a Sentry comment confirmed in Activity (or a
line in the hand-off list), a thread reply and a 🎫.

## 6. Fix

1. Branch `bugfix/PROJ-123_<description>` from your main branch, in a git worktree.
   If you use `fvm`, it can fail in a worktree: call the pinned SDK binary directly
   (`~/fvm/versions/<version>/bin/flutter`; pick the version `fvm flutter --version`
   reports in the main checkout).
2. Fix the cause, not only the symptom, and add a test that goes red without the fix.
   A guard that skips bad data must still log it, so the next alert has more detail.
3. When fixing a side effect would change product behaviour (what the user sees,
   when data reloads), ask before making that change.
4. Run your pre-MR gate (checks, tests, a local review), then a QA pass (the
   `qa-test` skill) when the crash can be reached on a simulator.
5. Commit and push only when the user asks. Once the MR is open, update the Sentry
   comment and the Slack reply with the MR link.

## 7. After the fix ships

Set each "same cause" Sentry issue to "Resolved in next release" in Chrome, after a
"go", or hand the user the list to do it by hand.
