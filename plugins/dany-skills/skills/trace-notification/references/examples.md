# Worked examples

Three runs of the same five steps. Each stops at a different stage, which is the point: the method does
not assume where the break is, it locates it.

The runs are based on real investigations, with names, ids and hosts swapped for made-up ones. The
service, metric and log names match the placeholders in `signals.md`.

Commands are shortened. `$H` is `https://dev.example.com/api/notify`, `$B` the service
credential header, `$T` a user access token.

---

## 1. Nothing arrived at all: push and list row both missing

**Subject and claim.** `qa.user+2@example.com`, location `4242`, dev. A review was posted and
neither a push nor a list row followed. The Basic credential in the reporter's curl decodes to the
username of a calling service, so it names nothing about the recipient. The subject had to come from
the reporter instead.

**Witnesses.** No user token, so the list read was out. Dropped to the badge, and said so.

```bash
curl -H "$B" -G "$H/locations" -d locationId=4242 -d account=qa.user+2@example.com
# {"badge":172}
```

**Probe.** Synchronous, fresh id:

```bash
curl -X POST "$H/reviews" -H "$B" -H 'Content-Type: application/json' \
  -d '{"locationId":4242,"reviewData":[{"id":"PROBE-1","type":"REVIEW","directory":"GOOGLE","rating":"5"}],"awaitSend":true}'
# 200. Badge after: 172. Flat.
```

The first attempt used the reporter's own `"awaitSend": false` and returned `202` in
milliseconds. That `202` meant nothing: the work runs after the response.

**Split the axis, then control.** Probed a second location of the same account, then all four
directories and ratings 1 to 5. Badge flat every time, so the failure follows the **account**, not the
location and not the review attributes, which rules the directory and star sub-filters out. Then the
control, from Loki over the same probe window:

```
{namespace="notify-service-dev"} |= "Push send by token"
```

Tallying `account=`: `qa.user+11@` got 45 and `qa.other+7@` got 15 on the same location,
`+2` got zero. The pipeline is healthy. One account is blocked. Different ticket.

**Discriminate.** Two causes left: permission row false, or topic switched off. The counter
`push_dropped_total{status="permission"}` increments only inside `isAllowedToSend`, so only the
permission gate can move it. It ran 2 to 46 over the morning. And `topic_review_total{active="false"}`
ticked 5 to 6 between 10:40 and 10:42 UTC, three minutes after the account's last working push.

Permission went false first, `muteTopicWithoutRight` switched the topic off behind it, and
`setMainTopic` then refuses to switch it back on, so the user cannot recover from the app. The same
kind of indirect chain is described in the `notification-ticket` skill's `references/guards.md`.

---

## 2. The row exists but the list is empty

Here the two witnesses disagree, which is the whole finding.

**Witnesses.** Both available: a user token for the list, the service credential for the badge.

**Probe.** One review, synchronous, then read both:

```bash
curl -H "accessToken: $T" "$H/api/inbox?max=10"
curl -H "$B" -G "$H/locations" -d locationId=... -d account=...
```

**Read the pair.** Badge moved, list still empty. By the table in `signals.md` that is the
**read filter**, not the send gate: the row was written and `InboxFilter.visibleTypes` hides
it from this caller.

**Discriminate.** `NEW_REVIEW` needs right `INBOX_READ` and a plan selling `INBOX`.
`GET /api/me` with the same token says which the caller holds. `inbox_filtered_total{type="review"}`
confirms the gate fired on that request rather than the row simply not existing.

Restore the right and re-read: the rows come back, because the filter hides and never deletes. That is
also a good QA case, and it is the cheap proof that nothing was lost.

---

## 3. The row is there, the push never came

**Read the pair.** Badge moved and the list shows the row. So persistence and the read filter are both
fine and the break is after `recordForAccounts`, in the device fan-out.

**Witness.** Loki, scoped to the subject:

```
{namespace="notify-service-dev"} |= "<email>"
```

Three outcomes worth telling apart:

- **`Push send by token: {code=200, ...}` is present.** The service sent it. The break is past the
  push provider: a stale token, notifications off at the OS, or a simulator, which cannot take real
  APNs pushes.
- **No send line at all.** No device passed `findNotifiableDevicesForAccount`. Count the account's rows
  with `notify: true`, not the total. One real QA account carried 423 device rows with only 18
  notifiable and 4 of those iOS, so "the account has a device" is not the same claim.
- **`Device error: ... error=NOT_FOUND`** followed by `Device update: inactive`. The push provider
  rejected the token and the service retired it. Expected after a reinstall, and the app registers a
  new one on next sync.

---

## Shape this generalises to

Nothing above is notification-specific except the names. A webhook that never fired, a queued email, a
job that never ran: same five steps. Find a per-subject durable record the pipeline writes, read it
before and after one synchronous probe, vary one dimension at a time, run a second subject down the
same path, then pick a signal only one surviving cause can move.
