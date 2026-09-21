---
name: writing-plain-code
description: Readability rulebook for code in any language (Dart, Swift, Kotlin, anything else). Use alongside the language style skill whenever writing or refactoring code, and when Dany says code is hard to read, too clever, too dense, or asks to make it simple. Wins on simplicity; the language skill wins on texture.
---

# Writing Plain Code

Plain code is code Dany can read once, top to bottom, out loud, without
stopping. Every rule below serves that reading test.

Simplicity comes from the **shape** of the code, never from a comment that
explains a dense line. Do not add comments: the explanation lives in
`explain-diff-to-me`.

Load this together with the language skill (`writing-flutter-code` for Dart).
On how dense, long or nested code may be, this skill wins. On what the plain
form looks like in that language (`break` after a Dart `case`, block bodies,
`Set<int>.from`), the language skill wins.

## The eight rules

Each rule: the bad shape, the plain shape, then how it looks in Swift and
Kotlin when the construct differs. Longer before/after pairs in `examples.md`.

**1. One step per line.** A chain of two or more calls becomes named locals.

```dart
// bad
final names = users.where((u) => u.isActive).map((u) => u.name).toList();

// plain
final activeUsers = users.where((user) => user.isActive);
final names = activeUsers.map((user) => user.name).toList();
```

Kotlin: `x?.let { a(it) }?.also { b(it) }` becomes `if (x != null) { a(x); b(x) }`.
No `let`, `also`, `apply`, `run`, `with`: set the fields in plain statements.
Swift: same, and no `.map { }.compactMap { }` chain longer than two calls.

**2. Branch with `if` / `else`, not with an expression.** No nested ternaries,
no collection-`if` / `for`, no `switch` / `when` expression for branching, no
`..` cascades.

```dart
// bad
children: [if (isLoading) Spinner() else for (final p in posts) PostTile(p)],

// plain
final List<Widget> children;
if (isLoading) {
  children = [Spinner()];
} else {
  children = posts.map((post) => PostTile(post)).toList();
}
```

A Kotlin `when` or Swift `switch` over a whole enum, one plain line per case,
is fine. A `when` with conditions or `in` ranges is a branch: use `if`. One
ternary is fine, two nested are not.

**3. Name the value, not the shape.** No records or tuples crossing a function
boundary. A small class with named fields. Destructure one level deep at most.

```dart
// bad
(int, String) load() => (count, title);

// plain
class LoadResult {
  const LoadResult({required this.count, required this.title});
  final int count;
  final String title;
}
```

Swift: no `(Int, String)` return, a `struct`. Kotlin: no `Pair` / `Triple`
return, a `data class`.

**4. Fits on one screen.** A method stays under about 30 lines. A `build`,
SwiftUI `body` or composable deeper than four nesting levels or longer than
about 60 lines gives a chunk to its own widget or view, named after what it
shows.

```dart
// bad: a 120-line build, Column > Padding > Row > Expanded > Column > ...

// plain
Column(children: [PostHeader(post), PostMedia(post), PostActions(post)])
```

Dart: a `StatelessWidget`, never `Widget _buildX()`.

**5. Whole everyday words for names.** No abbreviations, no fancy English, no
single letters outside a two-line lambda. Booleans read as a question.

```dart
// bad
final locCnt = cardinality(sel);
final superseded = ...;

// plain
final locationCount = selected.length;
final isStale = ...;
```

The plain-English word list in `~/.claude/CLAUDE.md` applies to identifiers
too: `sync` not `reconcile`, `stale` not `superseded`, `drop` not `discard`.

**6. Guard first, then a flat body.** Exits at the top, the happy path not
nested. Two levels of nesting at most.

```dart
// bad
if (user != null) {
  if (user.isActive) {
    // 20 lines
  }
}

// plain
if (user == null) return;
if (!user.isActive) return;
// 20 lines
```

Swift: `guard let user, user.isActive else { return }`.
Kotlin: `val user = user ?: return`.

**7. Hard logic gets a named step.** A condition with more than two parts, or
a formula, becomes a named local before it is used.

```dart
// bad
if (title.isNotEmpty && !isSending && (media.isEmpty || media.every((m) => m.isUploaded))) {

// plain
final isMediaReady = media.isEmpty || media.every((item) => item.isUploaded);
final canSubmit = title.isNotEmpty && !isSending && isMediaReady;
if (canSubmit) {
```

**8. No cleverness to save a line.** A `for` loop over `fold` / `reduce` when
building a collection. No operator tricks (`??=` chains, `!` everywhere, bit
tricks). No generics or extension methods the API does not force.

```dart
// bad
final byId = items.fold(<int, Item>{}, (m, i) => m..[i.id] = i);

// plain
final byId = <int, Item>{};
for (final item in items) {
  byId[item.id] = item;
}
```

Kotlin: `associateBy { it.id }` is fine (one named call). A `fold` with a
lambda body is not.

## Before handing code over

Read the diff once, top to bottom, out loud. Every line you had to stop on
breaks one of the eight rules. Fix the shape. Do not add a comment.
