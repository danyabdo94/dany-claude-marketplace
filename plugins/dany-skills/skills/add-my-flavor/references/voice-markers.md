# Voice markers

The small habits that make a message read as Dany rather than as a well-written message. Derived from ~10 months of his actual Slack, Jira and GitLab writing.

Use these in the **warm register**. Most of them are wrong in code review (see `examples-review.md`).

## Reduplication

He doubles words. It is his single most distinctive habit.

`Hey Hey` · `Hi Hi` · `hey hey` (DMs) · `no no all good` · `do you do you` · `first-ever-ever` · `chat-chat meeting`

`Hey Hey` for channels and most DMs, lowercase `hey hey` for quick DMs. `Hey Hey great team` for a channel where he's asking a group. `Hey Hey team!` for his own squad.

## The `mr` honorific

Lowercase `mr` before a first name, affectionate, applied to people and to tools.

`I helped mr Omer to fix the failing maestro pipeline` · `I asked mr Claude to implement a re-design` · `Happy birthday to you mr @Omar`

To Sam specifically (his manager): `Hey Sir` / `Hey sir` / `Hey Sam,`.

## `:eyes:` is the workhorse emoji

By volume, `:eyes:` beats everything else. It is not "look at this" so much as a soft question mark: it turns a statement into an invitation, or an ask into a low-pressure one.

`can you take a look :eyes:` · `shall we move the ticket to review ? :eyes:` · `Okay? :eyes:` · `Hey Hey any opinions? :eyes:` · `in 45 Mins? :eyes:` · `tested and working fine :eyes: !`

Rest of the real frequency order: `:pray:` (ask/thanks, closes most requests), `:smile:` (defuses anything that could read as pushy), then `:eyes:`-adjacent topic markers.

Custom workspace emoji he actually uses: `:friendly-reminder:` `:hi-slide:` `:outofoffice:` `:no-worries-v1:` `:yay:` `:please:` `:up:` `:alert:` `:broom:` `:mega:` `:test_tube:` `:ticket:` `:rocket:` `:point_down:` `:tada:` `:wave:`

Write Slack emoji as shortcodes, not unicode.

**On the count:** the "1-3 per message" guidance holds for asks and updates. It breaks in two places, and that's correct, not sloppy: sharing something he's pleased about (`:wink: ... :stuck_out_tongue: :smile: CC: @Sam :smile:`) and social posts. Don't cap those.

## Closers

He almost never ends on an open "thoughts?". He ends by proposing something and asking to be vetoed:

`WDYT?` · `Okay? :eyes:` · `So are we happy with the same flow?` · `shall we ...?` / `Shall I ...?` · `any opinions? suggestions?` · `tell me your opinion`

`shall` is a genuine tic, not formality: `shall we move the ticket to review`, `Shall I take a look on this bug?`, `Shall we remove it from this sprint?`

## Sentence mechanics

These are "errors" that carry his voice. Reproduce them in moderation; don't sanitise the writing into flat corporate prose.

- **Trailing commas where a period belongs**, at line ends: `I added a common viewMode widget that is used now in threads and reviews,`
- **Lowercase sentence starts** mid-message: `both of them now in review. but this is not the problem.`
- **`..` as an ellipsis**: `on those questions .. so I don't know how to proceed further`
- **`etc...`**
- **`==>`** for "becomes" / "moves to"
- **Comma before a conjunction he then drops**: `I reviewed your MR, you can ask claude to change the stuff I asked for,. then we can re review it`
- Doubled commas occasionally: `we need to iterate on reviewing and validating them,, we can make a schedule like:`

Don't manufacture typos. But if a rewrite comes back with every clause perfectly punctuated, it stopped sounding like him.

## Vocabulary

`plz` (more often than `pls`) · `BTW` (heavy in Jira) · `IMHO` · `specially` (for "especially") · `long story short:` (never `TL;DR:`, dropped on request 2026-09-08) · `Guys` (addressing the team) · `a kind reminder` · `Can I pump this one` · `when you've got a sec` / `when you have time` · `no rush` · `FYI`

## Structure

- **Bullets are `•`, nested ones `◦`.** Not `-`.
- **Numbered lists in Jira are `1.` `2.` `3.`**, which Jira renders as a list. Older comments used `1-`, which Jira leaves as plain text.
- **`CC:` on its own line at the end** with the people who need visibility but no action, sometimes `CC: @X @Y FYI`. This is a consistent structural element, not decoration.
- **Bold the term the decision hinges on**, not whole sentences.
- Monospace blocks for tables and CLI output; he'll paste a rendered ASCII table rather than a markdown one.

## The two moves that define his asks

1. **Propose, then offer the out.** He states the call he's already made and explicitly authorises the other person to reverse it: `totally fine to go back to the job runner if you reckon the central visibility is worth it`. Never a bare open question.
2. **Close a scary update by naming what is not on fire.** `Nothing breaks on us before then, Dec 2 read-only only stops publishing new pods, not installing what's already out there :slightly_smiling_face:`

## Where the warmth switches off

- **Unplanned illness / bad news about himself**: full sentences, no `Hey Hey`, no emoji, no jokes.
- **Code review**: see `examples-review.md`.
- **Chasing a team outside mobile for the second time**: stays polite and slightly more formal (`Hey everyone, :hi-slide:` ... `Thanks!`) rather than getting sharper.
