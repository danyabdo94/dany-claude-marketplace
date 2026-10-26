# Evidence behind the flavor rules

Read `SKILL.md` to write code. Read this only to settle an argument about *why* a
rule is there, or to re-derive the rules against a newer corpus.

## The corpus

All Dart Dany added in **2024-01-01 → 2025-12-31**, taken from the 67 non-merge
commits authored by him in the work app repo in that window:

- **26,047 added lines** across **551** non-generated `.dart` files
  (`.g.dart`, `.freezed.dart`, `.config.dart`, `.mocks.dart` excluded)
- tests 10,419 · presentation 7,077 · shared `lib/` 5,493 · application 1,724 ·
  domain 913 · infrastructure 335 · routes 86

The window ends where the signal does: Dany has **zero commits** between
2026-01-01 and 2026-02-19, when Claude tooling landed (`9d990538`). So
2025-12-31 is his last unassisted commit, and everything after 02-19 in the UB-I
feature, `packages/image_editor`, and the PROJ-16xx notification work is
AI-assisted and excluded.

To rebuild the corpus:

```bash
git log --author="Dany" --since=2024-01-01 --until=2026-01-01 --no-merges \
  -p --unified=0 --format="@@@COMMIT %h %ad %s" --date=short -- '*.dart'
```

## Comment density by layer

| Layer | lines | `//` | `///` |
|---|---|---|---|
| widgets / presentation | 9,825 | 1.10% | 0.37% |
| cubits & blocs | 1,550 | 1.29% | 0.26% |
| domain | 805 | 1.49% | 0.62% |
| services / repositories | 286 | 4.20% | 1.75% |
| **tests** | **9,143** | **3.73%** | **0.00%** |
| all | 23,594 | 1 per 42 lines | — |

Roughly a third of the test comments are Arrange/Act/Assert labels (~110 of
341); strip those and tests still sit above the UI layer at ~2.5%.

## Counts that decided a rule

**Control flow.** `switch (` 24 · `break;` 36 · `case ` 47 · `else if` 35 ·
`} else {` 31 · ternary lines 140 · **switch expressions 2** (`=> switch (this)`
and `return switch (this)`, both total enum→value mappings).

**Cubits.** `emit(` 72 · `state.copyWith` 58 · `case Success` 17 ·
`case Failure` 16 · **`isClosed` 0** · `final` locals 92 · `var` locals 2.

**Widgets.** `context.colorTheme` 245 · `context.theme` 180 ·
`context.colorScheme` 116 · `context.l10n` 107 · `textTheme.X!` 127 vs
`textTheme.X?` 14 · `SizedBox(height:` 56 + `SizedBox(width:` 23 vs `spacing:`
24 · `Function(` 27 · `VoidCallback` 17 · `ValueChanged<` 2 ·
**`Widget _build` 1** · `Key('` 20.

**Tests.** public `class Mock… extends Mock` **55** vs private `_Mock` **1** ·
`MockCubit<`/`MockBloc<` 18+ · `blocTest<` 38 · `late` 88 · `setUpAll(` 12 ·
`registerFallbackValue` 18 · `build: () {` 33 vs `build: () =>` 5 ·
`act: (cubit)` 21 vs `act: (c)` 3 · `verify(` 23 · AAA labels ~110.

**`when(...)` placement.** Of 83 test files Dany touched that still exist,
**44 put `when(...)` inside `setUp`** — the baseline `when(() => x.state)` stub.
Per-test stubs sit in `build:` or the test body. Both halves are real; the old
"`when` never goes in `setUp`" rule was wrong.

**Formatting.** single-quoted strings 1,338 vs double 169 · bare `final` 705 vs
explicit-typed `final` 35 · `=>` bodies 487 · only ~2% of lines exceed 80 cols.

**Declarations.** `abstract interface class` 5 (all services) ·
`abstract class` 15 (repositories + freezed) · `@freezed` 16 · `@injectable` 10
· `@Singleton` 5 · `@LazySingleton` 2 · `extension X on` 14 · `enum` 19 ·
`sealed class` 4.

## Adoption timeline — why some ratios are meaningless

Occurrences of each pattern in added lines, by half-year:

| period | spot | `spacing:` | `find.` | switch | dot-shorthand | MockCubit | AAA |
|---|---|---|---|---|---|---|---|
| 2024-H1 | 0 | 0 | 11 | 0 | 0 | 0 | 0 |
| 2024-H2 | 0 | 1 | 51 | 12 | 0 | 2 | 38 |
| 2025-H1 | 0 | 2 | 106 | 1 | 0 | 7 | 50 |
| 2025-H2 | 40 | 21 | 216 | 11 | **42** | 18 | 65 |

Two things to read off this:

1. **AAA labels are stable across every period** (38 → 50 → 65). That is a
   habit, not a phase. It is the single most reliable personal signal in the
   corpus.
2. **`spot`, `spacing:`, and dot-shorthands are step functions**, not
   preferences — they appear the moment the SDK offered them. All 42
   dot-shorthand uses arrived in **one commit**, `c115659c` (2025-12-31), the
   last in the window. This is why `SKILL.md` carries the feature-ceiling rule:
   the corpus cannot vote on an API it never had. `material_ui` /
   `cupertino_ui` are the same story — every corpus file imports
   `package:flutter/material.dart`, which is now forbidden.

## Test naming inventory

262 test names: mean **6.2 words**, median 6, max 12. Not terse.

```
returns failure on network error
successfully creates a new post
MultiLocationSelector auto loads more items if content is small
Should be optional when Facebook and Instagram are selected with brand pages
emits [loadingMore, loaded] with isLastPage=false when loading more does not reach total count
should fallback to UTC timezone when timezone is not found
```

81 `group` names, three flavours, all in voice:

- class under test — `LocationSearchBloc`, `UBICubit`, `ReplyAIServiceImpl`
- method, for nested groups — `getLastPosts`, `upsert`, `deletePost`, `fromHex`
- phrase with a `Tests` suffix — `ErrorScreen Widget Tests`,
  `User Permission Tests`, `HexColor Extension Tests`

Widget-pumping helper names: `createWidgetUnderTest` 3, `createTestWidget` 2,
`buildFacebookPagesWidget`, `buildInstagramPagesWidget`,
`renderToneAdjusterModal`, `_reviewScaffoldRenderer`, `_wrapWithApp`, `wrap`.
`late` mock variables are named **unprefixed** (`postDirectoryCubit`,
`userBloc`, `cubit`, `repository`) about 35 to 10 over `mockFoo`.

## Comment voice — raw sample

```dart
// Post media section          // Blue Shades              // Title
// Call to action section      //Directory pages           // Description
// End IG Pages BLoC section   // plain text               // Login Button
// remove previous listener if any
// Clean first the previously selected ones
// ignore animation errors when scrolling not possible
// getString returns empty string (never null) if key doesn't exist
// We need to change the primary color because it affects the small loading indicator on refresh
//getSelectAll not _selectAll since it's different visually from the actual state
// the get posts API returns objects
// but the post and edit wait for ids
// TODO: until Locator + Pages will not support a Button and a Link at the same time
// we should hide the link field when Google or Facebook are selected with it to
// avoid confusion for the user
```

Properties: two-word block labels are legitimate; lowercase starts are normal;
the space after `//` is sometimes missing; first person plural appears
("We need to…"); a sentence may wrap across two `//` lines unpunctuated.

## Layout variants Dany created and kept

Fine to mirror: `implementations/` instead of `infrastructure/`, `util/` **and**
`utils/`, `contracts/` + `data/`, a top-level `<feature>_feature_builder.dart`,
and small features that are flat widget files plus `entities/` and `widgets/`
(`location_selector/`). Shared widgets live in `lib/widgets/` as flat
`custom_*.dart` files or folder-per-component with a `widgets/` subfolder.

**Not** to mirror: `domain/contracts/facebook_pages_repository_impl.dart` puts a
Dio-touching implementation inside `domain/`, inverting the dependency direction
`CLAUDE.md`'s layering protects.

## Known defects in the corpus

Present in real code, deliberately **not** promoted to rules in `SKILL.md`:

| In the corpus | Why it isn't a rule |
|---|---|
| `static String directoryPagesApi = '…'` | reassignable global; use `static const String` |
| `PagesService handlesService;` on a `@LazySingleton` | mutable field on a singleton; use `final` |
| no `isClosed` anywhere | `emit` after `close()` throws `StateError` |
| `tearDown` frequently absent | unclosed blocs keep subscriptions and bleed across tests |
| `sl<AuthBloc>()` inside a service impl | `CLAUDE.md` forbids service-locator use below the UI boundary |
| in-place mutation of a `Set` field + `setState(() {})` | a child comparing by identity never sees the change |
| `Function(T)` callback fields | declares a `dynamic` return, so any return type passes |
| `// Fetch locations list` above `fetchPages` | comment drifted from the code it labels |
| full state literals in every `expect:` | one new state field breaks every test in the file |
