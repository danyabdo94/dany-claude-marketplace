# Real Jira comments, verbatim

Ticket comments are the technical register, but the audience shifts a lot: sometimes the mobile team, often CS/support or product people who filed a bug. Quoted exactly.

Note: some very long comments in his history (`## Root cause CONFIRMED`, big markdown tables, `Supersedes previous comment`) were AI-drafted and are *not* voice samples. The ones below are his.

---

## Chasing a support/CS ticket that arrived incomplete

PROJ-1534, 2026-06-08. `Hello, @X @Y`, numbered asks as `1-`/`2-`/`3-` or bullets, the reason it matters stated plainly, `CC:` line at the end. Firm without being cross.

> Hello, @Mia @Lukas
> There is some missing info.
>
> * Which app version is causing this issue?
> * Can I change this user's's password? Since we don't have a login-as feature.
> * Is it still happening after the latest release?
>
> I added this Confluence page to reduce the back-and-forth communication between us, because this is the third time in a row. We got a ticket with missing data
>
> CC: @Sam @Chris FYI

PROJ-1533, 2026-05-21. Same shape with `1-` numbering and evidence attached.

> Hello @Leo @Lukas
>
> 1- This ticket still lacks screenshots or video recordings.
> 2- I tried to create a social post with the same provided user and on different devices, and here is the video recording
>
> <video>
> 3- As you can see, Facebook has connection issues, as I mentioned before in this comment <link>
>
> CC: @Sam

The pattern: state the gap, show he did the work himself first, link the prior evidence, CC the leads. The complaint is always attached to a fix ("I added this Confluence page").

## Short factual updates

Most of his ticket comments are one or two lines. `BTW` is a real tic here.

> BTW I tested with <admin link> on 3.1.0 and it worked fine.

> BTW I can do it on sandbox

> @Lukas plz ping me when you have them :pray:

> Following up, there are connection issues BTW

> @Nico , no not related, if it still happens plz create another bug ticket

> @Eva if they are single location managers, they will have the same fix

> Actually, it accepts any string, which is wrong!

> tested and working fine :eyes: ! @Omar

> hey hey @Chris WDYT?

> @Sam Shall we remove it from this sprint?

> it's an AI team issue,
> <slack link>

## Investigation findings, hand-written

PROJ-1413, 2026-03-02. Numbered `1-` findings, each one a link to evidence. Note "may-be" and "specially".

> It seems it's an issue with the **silence time** on android,
> From my research, I found a couple of things:
> 1- Is a may-be bug in the library implementation itself, and I added an issue [here](github link)
> 2- Google speech-to-text service, which is the service under the hood, for privacy reasons it stops listening after a small silence period (between phrases).
> 3- The median number of words per message we get from AI assistant users, [is 15 words](metabase link) , which is around 7 seconds as per some external calculation tool like this [one](wordstotime link)
> 4- later (if we need) we can have our own timer and reconnect Google speech to text service if the user didn't exceed the 1 minute,

Every claim carries a link. That is the substance of the register: not hedging, sourcing.

## Blocked / moved / scope-change notices

Short, bolded lead, reason, no ceremony.

> :alert:
> This ticket is blocked on the new status designs showing on each post list item.

> Moved to PROJ-1620 (Backend Story) — the full spec now lives there.
>
> This was an `api-service` change sitting as a sub-bug of a Flutter crash bug, so it blocked PROJ-1617 from closing even though the client fix is independent of it. PROJ-1617 is now linked to PROJ-1620 with _relates to_ instead.
>
> Closing here; no work is lost — track it on PROJ-1620.

(That last one is AI-drafted, em dashes and all. The shape is right, the punctuation is not.)

## Apologising / managing expectations with a stakeholder

PROJ-1330, 2025-12-24. Brief, honest, hands off the part he doesn't own.

> @Ben Hey Ben, Sorry, I was sick yesterday.
> The fix is almost there in code review, but we won't have a release during the holiday period.
> When @Chris is back, he can communicate more about the release dates :pray:

---

# Ticket descriptions, a voice sample

> **Shape warning.** This sample predates the `jira-ticket` skill and still shows `## What ships` and
> `## Acceptance` in the description. Both have moved: `What ships` is now a comment posted after the MR
> exists, and acceptance criteria are P0/P1/P2 scenarios in the QA Testing Notes field. Read this file for
> **wording and rhythm only**. `jira-ticket` is the authority on which sections a ticket gets.

Descriptions are a different register from comments: a document, no greeting, no closer. This one was written for PROJ-1620 on 2026-09-03 with Dany's approval and renders correctly through the Atlassian MCP with `contentFormat: "markdown"`. Use it for wording, not as a section template: the sections and the render rules live in `jira-ticket`.

api-service stores the `permissions` flags the app sends on every sync, then **never reads them** on any send path. An unentitled account keeps receiving those pushes forever. Fix: every send path checks **the stored permission row**, not only the topic row. 👀

## Root cause

All three send paths gate on **the topic row only**:

1. `ReviewPush.isEnabled`: `reviewsTopic?.active != false`
2. `ThreadPush.isEnabled`: `threadsTopic?.active != false`
3. `MessagePush.recipients`: `findTopic(messages, ...)?.active != false`

A missing topic row reads as **enabled**. The permission check does nothing on a null row, and the topic update only clamps when the sync carries topics. An account that never touched a notification setting has no rows at all, so every gate passes.

Verified on dev with an account holding `MESSAGES_READ` but not `REVIEWS_READ`:

```
Permissions: [reviews -> false] · [messages -> true] · [threads -> false]
Notification Topics: ()
```

`POST /reviews` still delivered a review push to that device.

## Decision: absent row means allowed

Absent means the app never synced. **A stored** `false` is what denies. Two sources of truth stay: the permission row says what the user may receive, the topic row says what the user asked for. Both are commented in the code and pinned by tests.

## What this is not

The Settings toggles work, and the send paths honour `topic.active == false`. The gap is only the entitlement mirror. An unentitled user would otherwise have to switch off a Settings row for a feature they cannot even see.

## Acceptance

1. Stored `permissions.<area> = false`: no push from that area's send path, even with zero topic rows.
2. `permissions.<area> = true` with no topic rows: still receives. `topic.active = false` still suppresses.
3. No Notification Center row is written for a suppressed account.
4. The dropped-message counter increments on suppression.
5. Unit tests for `isAllowed` plus one integration test per send path.

## Open questions, not blocking

1. The push sender sets the silent-wake flag on every push, which wakes the iOS app each time and feeds a known crash. Do alert pushes need it?
2. Android config ships a 2 minute TTL, so undelivered pushes just expire.

Split out of PROJ-1617 (was PROJ-1619). This is not a crash fix. It removes a small slice of the PROJ-1617 events, the real problem is pushes sent to people who may not see them.

---

What makes it his and not a spec generator's: the opening paragraph names the wrong thing before the fix, with no `TL;DR` label, "What this is not" stops a reviewer hunting the wrong bug, the decision gets its own heading with the reasoning in one line, and the last paragraph says plainly what the ticket does not solve. A QA-only variant (PROJ-1657) swaps Root cause for `## Before you start` and `## Accounts on dev`, and puts the cases in a table with `#`, `Setup`, `Expected` columns.
