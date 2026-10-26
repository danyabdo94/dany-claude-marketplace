---
name: my-flutter-code-flavor
description: Cheap Haiku pass that checks Dart for "does this read like Dany's" and strips AI tells from a diff. Use AFTER code is written, or when Dany asks whether a diff reads like his. For actually writing or refactoring Dart, use writing-flutter-code instead.
model: haiku
---

# My Flutter Code Flavor (check pass)

This skill audits code against Dany's style. It does not write features: the
writing happens under the `writing-flutter-code` skill on the session model,
this pass only checks the result.

The rulebook is not duplicated here. Read it first:

1. `/Users/dany/.claude/skills/writing-flutter-code/SKILL.md` in full.
2. `/Users/dany/.claude/skills/writing-plain-code/SKILL.md` in full.
3. `/Users/dany/.claude/skills/writing-flutter-code/reference.md` only to
   settle an argument about the corpus.

Then audit the diff or files you were pointed at:

- Walk §9 "AI tells to strip" and the final self-check list against every
  changed file.
- Walk the eight `writing-plain-code` rules over every changed file: chains,
  nested ternaries, collection-if/for, records, long methods, short or fancy
  names, deep nesting, clever folds.
- Compare each cubit method to §8's right-hand column.
- Check tests against §6: public `MockFoo`, main()-scope fixtures with
  `copyWith` expectations, `createWidgetUnderTest`, `act: (bloc)`, AAA labels.

Report violations as short bullets (`file:line`, what to change, which rule).
If asked to flavor the code rather than just report, apply the fixes directly.

Structure conflicts: project `CLAUDE.md` wins. Texture conflicts: the rulebook
wins.
