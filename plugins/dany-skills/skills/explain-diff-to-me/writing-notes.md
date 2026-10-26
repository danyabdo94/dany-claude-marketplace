# Writing one line note

The reader is Dany: a mobile developer, not a native English speaker, reading
code he did not write. He wants to understand, not be impressed.

## Shape

- At most two sentences.
- Sentence one: what the line does. Start with a verb: "Adds", "Removes",
  "Replaces", "Calls", "Returns", "Checks". A removed line starts with "Was:".
- Sentence two: why. Start with "so that" or "because". Skip it only when the
  why is the same as the previous line's.
- A note that covers several lines (a bracket, a closing paren, the tail of a
  multi-line call) says so: "Lines 41-45:".

## Words

- The plain-English rule from the user's `CLAUDE.md` applies: `sync` not
  `reconcile`, "stale" not "superseded", "drop" not "discard".
- Any term outside everyday English or basic Flutter/Swift/Kotlin gets its
  meaning in brackets the first time it appears in that file:
  "emits (sends the new state to the screen)". Keep a running list; it becomes
  the page glossary.
- Sentences of about 15 words. One idea per sentence.

## Never

- Judge the code or suggest a change.
- Use a metaphor or an idiom.
- Say "simply", "just", "obviously", "of course".
- Repeat the code in words ("sets `x` to 5") without saying why.

## Samples

Added Dart cubit line:

```
+ final selected = Set<int>.from(state.selectedLocations);
```
> Copies the selected location ids into a new set. So that the next lines can
> change the copy and the old state stays unchanged (the screen only rebuilds
> when the state object is a new one).

Removed Swift guard:

```
- guard session.isReachable else { return }
```
> Was: stopped here when the iPhone was not reachable. Removed because the
> manager now shows the "iPhone not available" alert instead of failing
> silently.

Kotlin `when` branch:

```
+     is PushResult.Failed -> retryQueue.add(request)
```
> When the push failed, puts the request in the retry queue. So that a short
> network drop does not lose the notification.

Bracket-only line:

```
+ );
```
> Lines 40-46: closes the `emit(...)` call started on line 40. Nothing runs
> here.

Import line:

```
+ import 'package:watch_connectivity/watch_connectivity.dart';
```
> Brings in the plugin that talks to the Apple Watch. Needed for
> `WatchConnectivity()` on line 19.

Test expectation:

```
+   baselineState.copyWith(status: .loadingMore),
```
> Expects the first state the cubit sends to be the baseline with status
> `loadingMore`. Derived with `copyWith` (copy with one field changed) so a new
> state field later does not break this test.
