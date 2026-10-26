# AI tells to strip before flavoring

Condensed from the humanizer skill (Wikipedia's "Signs of AI writing"). Strip these
first, then put the voice on. Order matters: the voice adds emoji, bold facts and
`WDYT?` closers on purpose, and this list must never strip them back.

## Voice overrides this list

Dany's habits are not tells. Keep them even when a rule below would flag them:
`Hey Hey` greetings, 1-3 emoji, `:eyes:` / `:pray:`, `WDYT?` / `Okay? :eyes:` /
`shall we` closers, bold on the fact a skimmer needs, `•` bullets, `1.` lists in Jira
comments, `CC:` lines, the sentence mechanics in `voice-markers.md`.

## Plain international English

Most readers are not native speakers. Use the word a beginner English course would
teach. `use` not `leverage`, `fix` not `remediate`, `stale` not `superseded`, `drop` not
`discard`, `sync` not `reconcile`, `check` not `verify`, `start` not `kick off`. No
idioms (`circle back`, `low-hanging fruit`, `on the same page`). If a word would not
appear in everyday tech writing, pick a simpler one.

## Strip on one sighting

**Not X but Y.** "It's not just a fix, it's a redesign" / "X rather than Y" / "..., no
guessing". The negative half argues with nobody. State the point.
> before: it's not about speed, it's about trust
> after: users need to trust the list

**One-line closer that repeats the point.** "That is the real win." "Read that again."
A row of fragments ("No retries. No cache. No hope."). Cut it, or merge into a sentence
with a new fact.

**Sayings that sound deep.** "the real question is", "at its core", "what really
matters", "X is the Y of Z". Replace with the specific claim.

**Staged run-up.** "Let's dive in", "Here's the thing", "Honestly?", "Quick note:",
"Heads up". Also `TL;DR:`. Delete the run-up and start with the point.

**Arguing with no one.** "To be clear", "I'm not saying", "Don't get me wrong", "A
tempting approach would be", "You might think ... but". Cut the defense; keep any real
claim inside it.

**Chatbot residue.** "Hope this helps", "Let me know if", "Great question", "Here is
a ...". Remove.

**Stock AI words.** actually, additionally, align with, crucial, deep dive, delve,
enhance, foster, highlight (verb), key (adjective), landscape, leverage, meticulous,
pivotal, robust (figurative), seamless, showcase, streamline, testament, underscore
(verb), utilize, valuable, vibrant. Swap for the plain word.

## Strip when two or more show up together

**Forced triads.** "fast, reliable, and scalable." Three items by habit, not by
meaning. Keep the ones that add a distinct idea.

**Dashes everywhere.** Em dash is already banned. Also watch ` -- ` and spaced ` - `
used as a dash: use a comma, colon, period or parentheses.

**Stacked qualifiers.** "could potentially possibly". One hedge if the doubt is real,
otherwise none.

**Bold as decoration / bold labels with a colon on every bullet.** "**Performance:**
faster. **Security:** safer." Bold only the term the decision hinges on.

**Hyphenated pairs after the noun.** "the report is high-quality" becomes "high
quality". Keep the hyphen before a noun.

**-ing riders.** "..., ensuring a smooth experience", "..., highlighting the
importance of". Cut the rider, keep the fact.

## Skim test additions

Before returning, search the rewrite once more for the five tells that survive most:
a not-X-but-Y contrast, a repeating closer, a dash, a triad, a bold label. Then read
it as a non-native speaker: any word you would need a dictionary for gets swapped.
