---
name: writing-flutter-code
description: Style guide for writing Dart/Flutter in this repo, plain code, terse label comments, locals-then-one-emit cubits, public MockFoo test doubles, shared main()-scope fixtures, Arrange/Act/Assert labels in tests. Use BEFORE writing or refactoring any Dart. For checking an existing diff's flavor, use my-flutter-code-flavor instead.
---

# Writing Flutter Code

`CLAUDE.md` says *what* the architecture is. This says *how Dany writes inside
it*. Structure conflicts → `CLAUDE.md` wins. Texture conflicts → this wins.

Load `writing-plain-code` alongside this skill. It wins on simplicity: how
dense a line, how long a method, how deep a tree may be. This wins on Dart
texture: what the plain form looks like in Dart (`break` after each `case`,
block bodies, `Set<int>.from`).

Derived from every line Dany wrote in 2024–2025, before Claude tooling landed in
this repo. Counts, timelines, and raw samples live in `reference.md` — read that
only to settle an argument, not to write code.

**The corpus is a style reference, not a feature ceiling.** Anything the SDK
gained after 2025 is missing from it for that reason alone, and its absence
carries no signal. Always use the current form: dot-shorthands (`.success`,
`.all(8)`), `spacing:` on `Row`/`Column`, `spot` selectors, and
`package:material_ui/material_ui.dart` — never
`package:flutter/material.dart`, which every corpus file imports and `CLAUDE.md`
now forbids. Read the corpus for *shape*, never for which APIs exist.

---

## 1. The governing instinct

Production code is quiet: **one comment per ~40 lines**. A 60-line cubit
usually has none. Tests are the opposite and are the *most* commented layer —
don't carry test commenting into a cubit, and don't strip Arrange/Act/Assert out
of a test.

Comments are short **labels** or informal fragments, never prose:

```dart
// Post media section
// Title
// remove previous listener if any
// getString returns empty string (never null) if key doesn't exist
// We need to change the primary color because it affects the small loading indicator on refresh
```

- Naming a block is legitimate (`// Post media section`, `// Title` above two
  fields). The AI tell is box-drawing (`// ── Constants ──`), not a two-word label.
- Lowercase starts are in voice — don't rewrite them into sentence case.
- A section can be closed (`// End IG Pages BLoC section`). Read that pair as a
  hint the method is too long, not as a thing to add.
- First person plural is fine: `// We need to X because Y`.
- `///` docs are rare outside `lib/widgets/`, and never open a test file.

---

## 2. Class layout

Constructor → instance fields → statics → getters → methods. Field order mirrors
constructor parameter order exactly. Endpoint constants stay **public**
(`static const String directoryPagesApi`). `super.key` comes **first** in widget
constructors, then the required params; trailing `super.key` in an older file is
fine, don't churn it.

---

## 3. Cubits and blocs: build up locals, emit once

The dominant shape. Copy collections into locals, mutate imperatively with plain
`if`/`else`, then a **single** `emit` at the end. Never a chain of `copyWith`
calls. `var` for a counter you increment, `final` for the rest.

```dart
final selected = Set<int>.from(state.selectedLocations);
var count = state.selectedLocationsCount;

if (isChecked) {
  selected.add(locationId);
  count++;
} else {
  selected.remove(locationId);
  count--;
}

emit(state.copyWith(selectedLocations: selected, selectedLocationsCount: count));
```

§8 has the full method next to what Claude would have written instead.

Async methods: emit loading, await, `switch` the `Result`, emit the outcome,
**with `break` after each case**. Dart 3 doesn't need the `break` and the
optional `unnecessary_breaks` lint would flag it; write it anyway, it's the house
habit.

```dart
switch (response) {
  case Success(value: final result):
    emit(state.copyWith(status: .success, title: result.title));
    break;
  case Failure():
    emit(state.copyWith(status: .error, failure: response.failure));
    break;
}
```

- Mutators are plain `void` with named required params. Optional behaviour as a
  trailing defaulted flag: `bool isRegenerating = false`.
- **Always a block body, never an arrow** — the corpus has 14 block-bodied `void`
  cubit methods and zero arrow-bodied ones, and zero `=> emit(`. Even a
  one-liner gets braces:
  ```dart
  void setHasBundledLocations(bool value) {
    emit(state.copyWith(hasBundledLocations: value));
  }
  ```
- The locals-then-`if`/`else` shape holds **even when an expression would fit**.
  Declare the locals, branch, assign in both arms, emit once — don't collapse it
  into `!(state.selectAll ?? false)` plus a ternary in the `emit`:
  ```dart
  bool? next;
  var count = state.selectedLocationsCount;
  if (state.selectAll == true) {
    next = false;
    count = 0;
  } else {
    next = true;
    count = totalCount;
  }
  ```
- A `clearAll()` that emits every initial value explicitly, field by field.
- **No `isClosed` after every await** — the corpus has none. But `emit` after
  `close()` throws, so keep the one guard before a final `emit` that can outlive
  the cubit.
- State: `enum XStatus` above the class, `@Default(...)` on every field, nullable
  `failure`. A hand-written state class with a manual `copyWith` and no freezed
  is equally in voice — don't freezed-ify one you find.

---

## 4. Services and repositories

`abstract interface class` for **services**, interface and `Impl` in the same
file, `@Singleton(as: X)`. Plain `abstract class` for **repositories**, in
`domain/contracts/`, impl in `infrastructure/`, `@LazySingleton(as: X)`.

**Error handling lives in the repository, not the service.** The service issues
the call and lets it throw:

```dart
try {
  return Success(await handlesService.fetchPages(params));
} on DioException catch (e) {
  return Failure(Exception(e.message ?? 'fetchPages Error'));
} catch (e) {
  return Failure(Exception('error while loading handles\n$e'));
}
```

The ladder is always specific `on DioException` first, then a bare `catch`.
Failure messages are informal and lowercase, with `\n$e` appended. Where a typed
failure exists it returns that instead (`AiFailure.connectionError()`).

`Result<T, F>` with `Success`/`Failure` destructuring is core. Log lines are
conversational and sometimes carry an emoji.

---

## 5. Widgets

**`build()` opens with a block of derived `final` locals**, then builds the tree.
Booleans get names rather than being inlined:

```dart
final directoryPageBloc = context.watch<InstagramPagesBloc>();
final blocStatus = directoryPageBloc.state.status;

final isLoading = blocStatus == InstagramPagesStatus.loading;
final isLoadingMore = isLoading && directoryPageBloc.state.page > 0;
```

- A chunk of tree may be assigned to a local and used below
  (`final listViewBuilder = InfiniteScrollWrapper(...)`) — that's the alternative
  to extracting a class, and it's fine. `Widget _buildX()` is not.
- **`if` / `else if` / `else` chains returning widgets**, often inside a
  `Builder`. One ternary in the tree is fine; nested ones are not
  (`writing-plain-code` rule 2). Don't build a widget tree with a switch
  expression.
- `context.colorTheme` / `context.theme` / `context.l10n` used **inline**; hoist
  only when reused several times. `!` on theme text styles
  (`titleMedium!.copyWith(...)`) — keep `?.` for a theme the app doesn't own.
- `StatefulWidget`: mutate the fields, then `setState(() => _selectedCount = n)`.
  The corpus uses a bare `setState(() {})` after mutating fields in place; leave
  those alone, but don't write new ones — and never mutate a collection field in
  place if you hand it to a child, which compares by identity and won't rebuild.
- Callbacks: `VoidCallback`, or `void Function(T)` on new APIs. The corpus's raw
  `Function(T)` declares a `dynamic` return and checks nothing.
- File-level constants above the class for shared spacing
  (`const double elementSpacing = 8.0;`). A bare `8.0` inline is fine too.
- Barrel imports narrowed with `show`. `Key('...')` on anything a test or Maestro
  needs, snake_case or kebab-case, matching neighbours.
- Private handler methods take `BuildContext context` and re-guard with
  `if (context.mounted)` after each await.
- Extra widgets in the same file are usually **public and doc-commented**; a
  private `_Foo extends StatelessWidget` is fine too.

The one place Dany writes at length is a widget `///` doc — a bulleted
capability/state list, e.g. `/// This widget provides:` then `- Text input …`.

---

## 6. Tests

40% of the corpus and the strongest fingerprint. Get these right.

**Test doubles are PUBLIC `MockFoo`**, declared between imports and `main()`.
`MockBloc<E, S>` / `MockCubit<S>` from `bloc_test` for anything a widget reads:

```dart
class MockLocationRepository extends Mock implements LocationRepository {}
class MockUserBloc extends MockBloc<UserEvent, UserState> implements UserBloc {}
```

**`late` variables are typed as the interface and named without a `mock` prefix.**
`setUpAll` at the top of `main()` for `registerFallbackValue` and timezone init.
Close cubits in `tearDown` — often absent in the corpus, but an unclosed bloc
bleeds into the next test.

**Shared fixtures are `const`/`final` declarations at `main()` scope**, above the
`group`. A `_userWith()` / `_config()` builder **function** is not in voice; a
plain literal is:

```dart
const location = Location(id: 1, city: 'Berlin', country: 'Germany');

final baselineState = LocationSearchState(
  const [],
  count: 0,
  status: .loaded,
  locationsRequestParams: const LocationsRequestParams(),
);
```

**Derive expected states from that baseline with `copyWith`** rather than writing
a full state literal per expectation. The corpus repeats the whole literal every
time, which means one new state field breaks every test in the file — the
baseline-plus-`copyWith` form is both closer to how Dany already handles fixtures
and far less brittle:

```dart
expect: () => [
  baselineState.copyWith(status: .loadingMore),
  baselineState.copyWith(status: .loaded, isLastPage: true),
],
```

**A widget-pumping helper inside `main()` is expected**, not avoided — default to
`createWidgetUnderTest`, wrapping in `MainAppTest(child: ...)`:

```dart
Widget createWidgetUnderTest({
  required Function(LocationSelectionResult) onSubmit,
  bool hasSelectAll = false,
}) { ... }
```

**`when(...)` splits by role.** The baseline stub every test needs — usually
`when(() => someCubit.state).thenReturn(...)` — goes in `setUp`. The stub that
varies per test goes in `build: () { ... }` (block form) or inline at the top of
the `testWidgets` body, repeated in full; that repetition is deliberate. It sits
in `act:` when it depends on values computed there.

**`blocTest` act param is named after the subject**: `act: (bloc)` / `act: (cubit)`,
never `c`. The bloc is constructed inside `build:`.

**Arrange / Act / Assert labels are a core habit** — steady across every period of
the corpus. Case and wording vary (`// Arrange`, `// arrange`, `//given`, `// when`).
Use them in widget tests, and narrate interaction steps alongside
(`// Tap the forgot password button`, `// Verify modal is shown`):

```dart
// Arrange
final publicationDate = DateTime.utc(2055, 10, 5, 12, 0, 0);
await _loadPostPreviewDate(tester: tester, post: ...);

// Act
await tester.pumpAndSettle();

// Assert
spotText('October 5, 2055 12:00 PM').existsOnce();
```

**Test names are descriptive, ~6 words.** Not terse. Canonical bloc-test form is
`emits [stateA, stateB] when <condition>`. Let the `group` carry the subject
rather than repeating it in every name. `group` names are the class under test,
a method name for nested groups, or a phrase with a `Tests` suffix.

Assertions use whatever `CLAUDE.md` mandates — `spot` selectors,
`pumpWidgetAndSettle` / `pumpRouterWidget`, `findsNWidgets`, no
`isA<>().having()`. The corpus's `find.*` is history, not debt: leave it unless
you're already rewriting that test. What carries over is the *structure* above,
not the finders.

---

## 7. Everything else

**Formatting.** Single quotes. `dart format` defaults: 80 cols, trailing commas
on multi-line arg lists. Bare `final` over explicit types on locals, though both
appear in the service layer — don't convert either direction. Arrow bodies are
common for getters, callbacks, and widget expressions, but **never for a cubit
method** (§3).

**Bloc imports.** Genuinely mixed — `package:flutter_bloc/flutter_bloc.dart` 5,
bare `package:bloc/bloc.dart` 3. `flutter_bloc` is the safer default since the
cubit usually ends up beside a `BlocProvider` anyway; match the feature you're in
and don't churn either.

**Switch expressions** appear twice in 26k lines, both total enum→value mappings.
That's the only place one earns its keep; `if` / `else if` is the native form for
branching logic, and rewriting a working chain into a switch is churn.

**Imports.** Relative for same-feature siblings, `package:<app>/...` across
features; both in one file is normal.

**Layout.** Features follow `domain/application/infrastructure/presentation`
loosely — `reference.md` lists the accepted variants.

**Commits.** `MOB-####` prefix on a branch's first commit, then a plain
imperative summary. Bodies usually absent.

```
PROJ-1213 Implement location selection feature with cubit and request parameters
PROJ-1347 Fix loading more on last page
```

---

## 8. Worked example — the same cubit method, both ways

This is the whole skill in one diff. **What Claude tends to write:**

```dart
/// Toggles a single location's membership in the current selection.
///
/// Two sets are maintained rather than one: [LocationSelectionState.selectedLocations]
/// holds explicit picks, while [LocationSelectionState.excludedLocations] holds
/// removals layered on top of a "select all" baseline. A location may therefore
/// appear in neither set, which is why the checked branch must consult both.
///
/// See PROJ-1213 for the approval-flow interaction that motivated the split.
void toggleSelection({required int locationId, required bool isChecked}) {
  // Guard against emitting after the cubit has been disposed.
  if (isClosed) return;

  // Copy, not mutate: emitting the same Set instance would defeat the
  // equality check and the UI would not rebuild.
  final updatedSelected = {...state.selectedLocations};
  final updatedExcluded = {...state.excludedLocations};

  // A check either cancels a prior exclusion or adds a selection — never both,
  // since the two sets are mutually exclusive by construction.
  final wasExcluded = updatedExcluded.contains(locationId);
  switch ((isChecked, wasExcluded)) {
    case (true, true):
      updatedExcluded.remove(locationId);
    case (true, false):
      updatedSelected.add(locationId);
    case (false, _):
      // Symmetric case: drop an explicit pick, otherwise record an exclusion.
      updatedSelected.contains(locationId)
          ? updatedSelected.remove(locationId)
          : updatedExcluded.add(locationId);
  }

  // Keep the denormalised count in step with the two sets.
  emit(state.copyWith(selectedLocations: updatedSelected));
  emit(state.copyWith(excludedLocations: updatedExcluded));
  emit(state.copyWith(
    selectedLocationsCount: state.selectedLocationsCount + (isChecked ? 1 : -1),
  ));
}
```

**What Dany writes** — the real code, unedited:

```dart
void toggleSelection({required int locationId, required bool isChecked}) {
  final selected = Set<int>.from(state.selectedLocations);
  final excluded = Set<int>.from(state.excludedLocations);
  var count = state.selectedLocationsCount;

  if (isChecked) {
    if (excluded.contains(locationId)) {
      excluded.remove(locationId);
    } else {
      selected.add(locationId);
    }
    count++;
  } else {
    if (selected.contains(locationId)) {
      selected.remove(locationId);
    } else {
      excluded.add(locationId);
    }
    count--;
  }

  emit(
    state.copyWith(
      selectedLocations: selected,
      excludedLocations: excluded,
      selectedLocationsCount: count,
    ),
  );
}
```

Same behaviour, 30 lines against 40, and no comment earns its place. Nine
differences, in rough order of how much they hurt a review:

| In the AI version | In Dany's |
|---|---|
| A six-line `///` essay with a ticket reference | Nothing |
| A comment above every step | Nothing |
| `[Symbol]` cross-refs in prose | Nothing |
| `if (isClosed) return;` on a synchronous method | Absent — no await to outlive |
| A switch over a `(bool, bool)` tuple | `if` / `else if` / `else` |
| A ternary used for its side effects | A plain `if` / `else` |
| Three `emit`s | One `emit` at the end |
| The count recomputed inline in the emit | `var count` incremented in the branch |
| `{...state.x}` spread | `Set<int>.from(state.x)` |

If a diff you're about to hand over reads like the left column, it isn't done.

---

## 9. AI tells to strip

| Tell | What Dany writes instead |
|---|---|
| A comment above nearly every line of production code | ~1 per 40 lines; most cubit methods get none |
| Multi-sentence "why" essays on failure modes and tradeoffs | One short fragment, or nothing |
| `// X, not Y: because …` constructions | Just write the code |
| Em dashes and `*emphasis*` inside comments | Plain fragments, lowercase is fine |
| Box-drawing dividers (`// ── Constants ──`) | A bare `// Post media section` if anything |
| `[SymbolName]` cross-refs in `//` comments | Only inside a real `///` API doc |
| Ticket IDs, Sentry IDs, MR numbers, issue links in comments | The commit message and the MR |
| `/// Regression coverage for MOB-####:` file headers | Tests open straight at the imports |
| Doc comments explaining ownership and disposal duties | A one-line summary |
| Private `_MockFoo` in tests | Public `MockFoo` |
| A per-test `when(...)` hoisted into `setUp` | In `build:` (a shared baseline stub in `setUp` is right) |
| `act: (c)` | `act: (bloc)` / `act: (cubit)` |
| Extracted `_userWith()` / `_payload()` builder functions | `const`/`final` fixtures at `main()` scope |
| Deleting the Arrange/Act/Assert labels from a widget test | Keep them — a core habit |
| Switch expressions for branching or widget trees | `if` / `else if` |
| `isClosed` guards after every await | Only before an `emit` that can outlive the cubit |
| A named constant plus a justification paragraph per literal | Name it if reused; bare `8.0` is fine |
| `Widget _buildX()` helpers | A `StatelessWidget`, or a `final someWidget = ...` local |
| "Single source of truth for…" doc essays | Extract the function, no sermon |
| try/catch → `Result` mapping inside the service | Service throws; the repository maps |
| Dense constructs: chained calls, cascades, collection-if/for, records, nested ternaries, deep pattern matching | One step per line, plain `if` / `else`, a named local or a small class (`writing-plain-code`) |

---

## Self-check before handing a diff over

1. **Delete comments in production code.** Would Dany have stopped to write
   this? Most go. Keep the two-word block labels.
2. Constructor above fields; field order mirrors constructor order; `super.key`
   first.
3. Cubit method: locals built up, then **one** emit. `break` after each `case`.
   `isClosed` only where an await can outlive the cubit.
4. Service throws; repository wraps in `Result` via the
   DioException-then-bare-catch ladder.
5. `build()` opens with named `final` locals; `if` / `else if`, not switch
   expressions; `context.colorTheme` inline.
6. Tests: public `MockFoo`; `late` vars typed as the interface, unprefixed;
   fixtures as `const`/`final` at `main()` scope with expectations derived by
   `copyWith`; a `createWidgetUnderTest` helper; baseline `when` in `setUp` and
   per-test `when` in `build:`; `act: (bloc)`; AAA labels present; names ~6
   words; cubits closed in `tearDown`.
7. Current APIs throughout: dot-shorthands, `spacing:`, `spot`, `material_ui`.
8. No ticket IDs, Sentry IDs, or `[Symbol]` refs in `//` comments. No test file
   headers.
9. Compare against §8. Does it read like the right column?
