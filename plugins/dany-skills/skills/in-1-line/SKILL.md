---
name: in-1-line
description: Answer in exactly one line. No preamble, no bullets, no follow-up offer.
disable-model-invocation: true
---

# In 1 line

Answer the question in **one line**. One sentence, or a bare value, or a single
command. Nothing else.

If arguments were passed, they are the question. If not, the question is the
message that came with the invocation, or the previous one.

Rules:

- One line of output. No headers, no bullets, no code fences, no blank lines.
- No preamble ("Sure", "Here's", "Looking at the code"), no closing offer.
- Do the work first if the answer needs it: read files, run the search, check
  the code. Silent tool use is fine, only the final answer is capped.
- Never guess to stay short. If you do not know, the line is "I don't know" plus
  what would settle it.
- If the honest answer cannot fit, give the one line that matters most and stop.
  Do not add "let me know if you want more".
- Correctness wins over the cap: a destructive-action warning or a failing
  command's real error text stays intact.

This applies to this turn only. The next message goes back to normal.
