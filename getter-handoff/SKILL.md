---
name: getter-handoff
description: Gather external data via Haiku couriers, then package the conversation into a handoff doc a cheaper agent can continue — keeping Opus/Fable out of the fetch-and-continue grind.
argument-hint: "What will the next session focus on?"
disable-model-invocation: true
---

# Getter-handoff

Two moves chained so the expensive main loop (Opus/Fable) never does the grunt work: cheap Haiku **couriers** fetch every external fact, then a **handoff** doc packages the whole conversation for a fresh — ideally Haiku — agent to carry forward. Opus/Fable spends only the tokens to orchestrate; both the fetching and the continuation run cheap.

## Steps

1. **Gather.** Follow [`../getter/SKILL.md`](../getter/SKILL.md): dispatch one Haiku courier per external source, then relay the raw facts. Done when every source named in the ask is reported or flagged inaccessible.

2. **Hand off.** Follow [`../handoff/SKILL.md`](../handoff/SKILL.md) to write and save the handoff document, then fold the gathered facts from step 1 into it — each with its source link — so the next agent needs no re-fetch. Write it for a Haiku reader: state the task plainly and spell out anything a smaller model shouldn't have to infer. Done when the saved doc covers both the gathered facts and the conversation state, and keeps the "suggested skills" section.

If the user passed an argument, it describes the next session's focus — narrow the gather in step 1 and tailor the handoff in step 2 to it.
