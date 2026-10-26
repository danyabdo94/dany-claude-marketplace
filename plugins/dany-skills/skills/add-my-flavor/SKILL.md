---
name: add-my-flavor
description: Full voice pass that rewrites a draft in Dany's voice (warm, lightly emoji'd, punchy) through the Haiku `flavor` agent. Use when Dany types /add-my-flavor, for a new Jira ticket or ticket description rewrite, and for long or high-stakes messages (escalation, cross-team ask). Short Slack messages, MR comments and replies use the voice card in the user's CLAUDE.md instead. Voice only: the `jira-ticket` skill owns ticket structure.
model: haiku
---

# Add My Flavor

Transform any drafted message into Dany's voice. Apply this when Dany types `/add-my-flavor`, for a new Jira ticket or description rewrite, and for long or high-stakes messages. Everyday short messages use the voice card in the user's `CLAUDE.md` in the main loop. When a rule here changes, update the card too so the two stay in step.

If the target platform or recipient is unclear, assume **Slack** and keep the recipient's `@handle` if one is present.

## Run it in the `flavor` agent, always

Dispatch the rewrite as `Agent(subagent_type: "dany-skills:flavor")` and pass the draft in the prompt. Do not run the rewrite in the main loop, and never dispatch it as `general-purpose`.

The `model: haiku` line in this file's frontmatter only binds when the skill *is* the agent. A `general-purpose` agent handed a flavor task inherits the caller's model instead, which is how a bounded rewrite ends up costing about forty times what it should. The `flavor` agent definition pins the model where it cannot be forgotten and removes the write tools, so the rewrite cannot post itself.

One agent per batch, not per draft: several drafts go into one prompt under bare labels and come back in the same order.

## Hard rule: no em dashes

Never use the em dash character in anything written for Dany. Use a colon, comma, period, or parentheses instead, or just split the sentence. (This applies everywhere, not only messages.) Prefer a plain hyphen for ranges too: write `1-3`, not a dash.

## Hard rule: plain international English

Most of the team, Dany included, are not native speakers. Use the word a beginner
English course would teach: `use` not `leverage`, `fix` not `remediate`, `drop` not
`discard`, `check` not `verify`. No idioms. If a word would not appear in everyday
tech writing, pick a simpler one. Word swaps live in `references/ai-tells.md`.

## Reference files

Rules drift when paraphrased, so the calibration lives in verbatim samples. Read the relevant one before rewriting anything substantial.

- `references/ai-tells.md`: the AI writing patterns to strip *before* flavoring (not-X-but-Y, staged openers, stock AI words, forced triads, bold labels) and the plain-English word swaps. Read this for any message.
- `references/voice-markers.md`: the specific tics (reduplication, `mr` honorific, `:eyes:`, closers, punctuation habits). Read this for any message.
- `references/examples-slack.md`: real Slack messages by situation (cross-team ask, QA handoff, standup, nudge, escalation, absence).
- `references/examples-review.md`: real GitLab review comments, and how he replies to reviewers on his own MRs.
- `references/examples-jira.md`: real ticket comments, including the CS/support-facing ones, plus the reference ticket description.
- `references/examples-commits.md`: commit messages and MR titles. Short version: one line, no body.

## Pick the register first

Three registers. Choose by destination *before* applying any flavor. The difference is **length and shape**, not warmth: emoji, `WDYT?` and `we` appear in all of them.

**Peer Slack / team chat** (DMs, team channels, standups, casual asks): the full warm profile below. Greetings, emoji, self-referential humor, `•` status bullets and shorthand all belong here.

**Code review / MR / ticket comments:** one thought per comment, usually phrased as a question. Median real comment is ~60 characters. Keep `:eyes:`, `:pray:`, `WDYT?`, `shall we`, `can we`. Drop the greeting (usually), the topic-marker emoji, and the multi-paragraph build-up. Full detail and examples in `references/examples-review.md`.

**Jira ticket descriptions** (a new ticket body, or a rewrite of one): a document, not a message. No greeting, no sign-off, no question close. Real Jira headings and numbered lists, one emoji at most. This is the one place where headers are right. **The section order, the fields and what Jira renders belong to the `jira-ticket` skill: read it before rewriting a ticket, and change it there, not here.** A voice sample is in `references/examples-jira.md`.

The no-em-dash rule holds in all three.

## Ticket descriptions: what stays here

Only the voice: plain English, bold the fact a skimmer needs, one emoji at most, no greeting, no sign-off, no question close, no em dashes.

Everything structural lives in `jira-ticket`: which sections a Bug or a Story gets, that `What ships` is a post-MR comment, that acceptance criteria are P0/P1/P2 scenarios in the QA Testing Notes field, which fields to set, and the table of what the Atlassian MCP actually renders. Do not restate any of it here, or the two skills will drift.

Keep every identifier, URL, code span and number from the source. Change wording, not facts.

## The flavor profile

*(Peer Slack / team chat register. For review and ticket comments, see `references/examples-review.md`.)*

**Tone: warm / collaborative.** Talk to the person, not at them.
- Open with a friendly, energetic greeting by name: `Hey @name!`. Doubling it (`Hey Hey @name!`) is on-brand and welcome. For a channel, greet the group: `Hey Hey great team`. **Never drop the greeting to save space** in this register: even a 3-line message keeps it. Compact means trimming the middle, not the opener.
- **Ask for their expertise, don't state your limits.** "infra we need your expertise" beats "infra we can't touch ourselves". Same request, but it credits them instead of describing your own blocked state.
- Cut self-justifying context. Lines like "the review pass is done" defend your work rather than helping them act; drop them unless someone actually asked.
- Frame the message as a shared problem or a request for their help/brain, never a demand or a status dump.
- Be appreciative and low-pressure: "when you've got a sec", "no rush", a `:pray:`.
- Light self-deprecating humor is welcome ("a break day without noisy Danny", talking about Danny in the third person). Keep it playful, never fishing for reassurance.
- Lightly acknowledge their expertise when asking for input ("your backend brain", "you'd know better than me").
- Peer-chat shorthand is fine here: `WDYT?`, `plz`, `BTW`, `IMHO`. Keep it out of anything external-facing. **Never `TL;DR`**, in any register: Dany asked for it to go (2026-09-08). Lead with the point in a plain sentence instead.
- **Propose, then offer the out.** State the call you've already made and explicitly authorise them to reverse it. Never close on a bare open question. The call must come from the draft. A draft that asks "A or B?" without picking stays "A or B? WDYT?" in the rewrite: never add `I say A`, `I'm leaning A`, `A rather than B`. Adding a stance is adding a fact, and the rewrite must not add facts.

**Emoji: 1-3 for asks and updates.** Write Slack shortcodes (`:pray:`), not unicode.
- `:eyes:` is the workhorse: it turns a statement into an invitation and softens an ask. `:pray:` closes most requests. `:smile:` defuses anything that could read as pushy.
- A single topic marker can lead the first line: `:ticket:` `:test_tube:` `:rocket:` `:broom:` `:mega:`.
- Never one-per-line, never as bullet markers.
- The 1-3 cap **does not apply** to sharing something he's pleased about, or to social/celebration posts. Those cluster freely (`:wink: ... :stuck_out_tongue: :smile:`).

**Length: punchy.**
- Lead with the ask, or a one-line `long story short:`. No `TL;DR:` label, ever.
- Cut background to the 1-2 sentences truly needed to answer. Offer to share more or link out instead of inlining detail.
- **Write for the reader.** Strip what their role doesn't need: QA doesn't need file paths, PMs and end-users need plain wording not jargon, an EM wants the decision and the trade-off.
- **Bold the key facts** so they pop on a skim. Bold the term the decision hinges on, not whole sentences.
- Keep asks **specific and actionable** ("do bundles realistically exceed 256KB in prod?") rather than vague ("any thoughts?"). Aim for 3 short paragraphs max.
- **Close a scary update by naming what is not on fire.**

**Slack links and markup.** Slack renders mrkdwn, not markdown. Every MR, commit, ticket or page mentioned gets a link with the id as its text: `<https://git.example.com/.../merge_requests/232|!232>`, `<https://git.example.com/.../commit/<full sha>|8120fc1>`, `<https://jira.example.com/browse/PROJ-1675|PROJ-1675>`. Never a bare id, never `[text](url)`. Bold is `*text*` (single asterisks), inline code stays in backticks. Dany asked for this on 2026-09-08.

**Slack mentions use the user ID, never typed text.** A plain `@jo` is just text in Slack and does not tag anyone. Write `<@UXXXXXXXXXX>` (the roster in the `send-slack` skill has every ID). If you don't know the ID, keep the person's first name without `@` and say so to Dany. The `@name` in the examples in this file is a placeholder for that form.

**Structure.** Bullets are `•`, nested `◦`, not `-`. Numbered lists in Jira, comments and descriptions alike, are real `1.` `2.` `3.` lists, because Jira renders them. Older samples in `references/` still show `1-`: keep the voice, not that numbering. A `CC:` line at the end carries the people who need visibility but no action, sometimes `CC: @X @Y FYI`.

**Status updates & standups (a different shape).** When the message is an update, not an ask, skip the question-close.
- Lead with a one-line human context: `Hey Hey, I'm out today`, `As we agreed:`.
- Then `•` bullets, each starting with a past-tense verb of what actually moved.
- Close with a light, human sign-off ("I leave you for a break day without noisy Danny"). No forced question.

## Process

0. **Strip AI tells first** (`references/ai-tells.md`): not-X-but-Y contrasts, staged openers, one-line closers that repeat, stock AI words, forced triads, bold labels. Do this before the voice goes on, so the voice is never stripped back. Dany's own habits (greeting, emoji, `WDYT?`, bold key fact) are not tells.
1. **Find the core ask** and move it to (or near) the top.
2. **Trim context** to the minimum that lets them answer. Replace dumped detail with "happy to walk through it / here's the line: …".
3. **Warm opener:** greet by name, frame collaboratively.
4. **Sprinkle emoji** at real emotional beats.
5. **Close** by proposing something and inviting a veto, only if the draft already contains that proposal. No stance in the draft means a plain `WDYT?` close.
6. **Skim test:** short paragraphs, plain language, no corporate stiffness, no em dashes. Compare against the draft: no new opinion, stance, number or name. Search once more for the five tells that survive most: a not-X-but-Y contrast, a repeating closer, a dash, a triad, a bold label. Then read it as a non-native speaker and swap any word that needs a dictionary.

## Don't

- No walls of text or multi-section essays with headers. The one exception is a Jira ticket description, which is a document and follows the section order in `jira-ticket`.
- No emoji spam and no emoji-as-bullets.
- No em dashes (see the hard rule above).
- Don't open with throat-clearing ("I wanted to reach out regarding…") or sound formal/robotic ("Per my analysis", "Kindly advise").
- Don't strip out the technical specifics that make the ask answerable. Punchy does not mean vague.
- Don't write a review comment as a multi-paragraph essay, and never with a `**[Medium]**` severity prefix. That format is linter output, not his voice.
- No C2 vocabulary. Plain international English only, see the hard rule above.
- Don't sanitise every clause into perfect punctuation. If a rewrite reads flawlessly corporate, it stopped sounding like him (see the sentence-mechanics section of `references/voice-markers.md`).

## Worked example: warm register

**Before (too long, ask buried, stiff, em dashes everywhere):**
> Hi Alex. In PushEventHandler.enqueueMessage we serialize a store's reviewData into a single SQS message. The recent enrichment added the full review data text (mapped as TEXT, no length cap). SQS caps a message at 256KB, and the sendMessage call is wrapped in a try/catch that just logs FAILED, so if a store's bundle exceeds 256KB the whole batch is silently dropped. I was going to add logic to bin-pack reviewData into sub-256KB messages, but I wanted to check a few things first. Please advise.

**After (flavored):**
> Hey @alex! :pray: Quick backend gut-check on PROJ-1583 when you've got a sec. Want to make sure I build the right thing here (or nothing at all).
>
> **The risk:** we now pack full review text into a single SQS message in `PushEventHandler`, and the send just logs `FAILED` on error. So if a store's bundle ever crosses **256KB**, the whole batch of notifications gets silently dropped :grimacing:
>
> **The call:** do these bundles realistically get that big in prod, or should I just add a guard + log instead of building the message-splitting? Don't want to over-engineer if it can't actually happen :slightly_smiling_face:

## Worked example: review register

Same person, different hat. Not colder, just shorter. One thought, phrased as a question, `we` throughout.

**Vague draft:**
> Maybe we should reload notifications when a push comes in? Not sure about rapid ones.

**Flavored:**
> can we reload the list when a push comes in? :eyes:
>
> and cancel the previous request each time a new one lands, otherwise two pushes a second apart fire overlapping reloads and we might render the older one.

Two lines. If the finding genuinely needs a failure path spelled out, use the long form in `references/examples-review.md`, but that is roughly 1 comment in 50.

## Worked example: ticket description

**Before (facts right, shape wrong: a `TL;DR:` label, prose paragraphs, `1-` numbering that Jira leaves as text, `:eyes:` that renders literally, em dashes):**
> TL;DR: nothing filters the list, on any path. The rights we need arrive on every request already — api-service calls GET /me to resolve the caller and keeps only the email. Keep the features, read the plan access too, and filter the three read queries on the allowed notification types. :eyes:
>
> Scope, two MRs:
> 1- upstream first: hand-written identity DTO instead of the generated User model, GET /me and GET /plan called concurrently, cached (identity 60 s by hashed token, plan 10 min by user), connect and response timeouts
> 2- the filter: the caller lookup returns email plus allowedTypes; NotificationType enum with requiredRight; type IN (:types) on the page query and both counts
>
> Acceptance:
> • no REVIEWS_READ: no review and no thread_update rows
> • neither right: empty list, totalCount 0, badge 0, no SQL error

**After (flavored, and split the way `jira-ticket` splits it):**

*Description:*
> The notification list returns **every row** stored for the account. Nothing checks the user's rights or plan **on any path**, so a user on a plan without review access still sees review notifications. 🧹
>
> ## Context
>
> The rights we need already arrive on every request: api-service calls `GET /me` to resolve the caller and keeps only the email.
>
> ## Requirements
>
> 1. The list and both unread counts are filtered on the server, not the client.
> 2. A user with no allowed notification type gets an empty list and a zero badge, not an error.
>
> ## Open questions
>
> 1. Does the plan check need to survive offline, or is a stale cached list acceptable? Alex would know.

*QA Testing Notes (flat lines, sent as ADF, see `jira-ticket`):*
> Setup: staging, account with no REVIEWS_READ right.
>
> P0 - open the notification list: no review and no thread_update rows, totalCount and unreadCount match the list.
> P0 - revoke both rights and reopen: empty list, totalCount 0, badge 0, no error toast.
> P1 - grant the right in the admin panel and reopen: rows appear, badge matches the row count.

*Comment, once the MR is open:*
> ## What ships
>
> 1. Hand-written identity model instead of the generated `User` model, so an unknown enum value cannot break the call.
> 2. `GET /me` and `GET /plan` called together and cached: identity 60 s by hashed token, plan 10 min by user.
> 3. `type IN (:types)` on the page query and on both counts. An empty allowlist returns an empty page before any SQL runs.
>
> Not in scope: the client-side badge animation.
>
> MR: !232

Same facts, same identifiers, three destinations. Note the QA notes stay flat lines with no headings: `jira-ticket` covers why and how that field is sent. A voice sample of a full ticket is in `references/examples-jira.md`.

## Refining the flavor

If Dany corrects a rewrite ("too many emojis", "shorter", "drop the greeting for this channel"), update the rules above so the next run reflects it. Add the corrected version to the matching `references/examples-*.md` file as a real sample. This skill should converge on how Dany actually writes.
