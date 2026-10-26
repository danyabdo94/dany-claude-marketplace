---
name: send-slack
description: Send a Slack message to the user's usual roster (people DMs or team channels) via a Haiku sender, always confirming before it goes out. Use when the user wants to send or post a message to Slack, DM a teammate, or drop something in a team channel.
---

# Send Slack

Sending runs on a **Haiku sender**: a Haiku subagent that makes the actual `slack_send_message` call and returns the link. The main loop drafts and confirms; the Haiku sender delivers. The send NEVER happens before the user confirms.

## Setup: your roster

Fill in the tables below once with the people and channels you message most. Find a user ID with `slack_search_users` (or "Copy member ID" in their Slack profile) and a channel ID with `slack_search_channels` (or the channel details panel). IDs are stable, so after setup no lookup is needed. Also set `<issue-tracker-url>` and `<code-host-url>` for the link rules in Notes.

## Roster

The user's usual recipients. To DM a person, pass their user ID as `channel_id`.

**People (DMs):**

| Handle | Name | user_id (= channel_id) |
|---|---|---|
| @alice | `<Full Name>` | `UXXXXXXXX` |
| @bob | `<Full Name>` | `UXXXXXXXX` |

**Channels:**

| Handle | Name | channel_id |
|---|---|---|
| @team | #team-channel | `CXXXXXXXX` |
| @team-internal | #team-internal-channel | `CXXXXXXXX` |

## Steps

1. **Resolve recipients.** Map each named handle to the roster table above. If the user says "the usual" / "everyone" / names no one, treat it as the full roster and confirm in step 3. For a recipient NOT in the roster, resolve it with `slack_search_users` (people) or `slack_search_channels` (channels); if the search is ambiguous, ask the user which one rather than guessing. Done when every intended recipient has a `channel_id`.

2. **Draft.** Compose the message text. Write it in the user's voice using their voice card (in their `CLAUDE.md`, Slack register) if they have one. Use the full `add-my-flavor` pass only for long or high-stakes messages (escalation, cross-team ask) or when the user asks. Skip both if the user supplied final text to send verbatim. Done when there is one final message string.

3. **Confirm: hard gate.** Show the user the final message text and the exact recipient list by name (e.g. "→ Alice, #team-channel"). Wait for an explicit go-ahead. Never dispatch a sender before this. If the user edits the text or the recipients, redo this step. Done when the user has explicitly approved this exact text and recipient set.

4. **Send via Haiku.** Dispatch one `Agent` call with `model: "haiku"` per target, in a single message. Each sender's prompt names: the tool (`mcp__claude_ai_Slack__slack_send_message`), the `channel_id`, the exact message text, and the return contract: the message permalink only, no commentary. The sender loads the tool schema itself with one `ToolSearch` `select:` call first. Done when every approved target has a sender in flight.

5. **Report.** Relay each returned message link back to the user, one line per recipient. A failed send is reported as failed, never silently dropped.

## Notes

- **Links, always.** Every MR, commit, ticket or page in the message is a Slack link with the id as its text, mrkdwn form `<url|text>`: `<<code-host-url>/<group>/<repo>/-/merge_requests/232|!232>`, commits with the full sha in the URL and the short sha as text, tickets to `<issue-tracker-url>/browse/<KEY>`. Bare ids and markdown `[text](url)` do not render. Bold is `*text*`. The sender posts the raw mrkdwn as given.

- **Mentions are `<@user_id>`, never `@name` text.** Before step 3, replace every `@handle` in the draft with `<@user_id>` from the roster (e.g. `Hey <@UXXXXXXXX>!` for Alice). Typed `@alice` posts as plain text and tags nobody. In the confirm preview, show the mention as `<@UXXXXXXXX>` (Alice) so the user can see it is a real tag.
- Threads: to reply in a thread, pass `thread_ts` (the parent message ts) to the sender; add `reply_broadcast: true` to also post to the channel.
- Private channels cannot be posted to via Slack Connect. That is fine as long as the user is a member.
- If the user hasn't reviewed the text yet and wants a preview in Slack itself rather than here, use `slack_send_message_draft` instead of sending.
