# Mutation probes

A test that passes proves the code runs. It does not prove the test would catch
a regression. The gap between those two is where a guarantee quietly stops being
guaranteed, and a **mutation probe** is how you tell them apart: break the
mechanism on purpose, one token if you can, and watch a named test fail.

## Method

1. Find the line that actually enforces the guarantee. Not the test, the
   mechanism: the guard, the transformer, the null-coalesce, the `&&`.
2. Break it minimally. `if (cond)` becomes `if (false)`. `sequential()` becomes
   `concurrent()`. `a ?? b` becomes `a`. One token keeps the blast radius
   readable — a bigger edit can fail for a reason you did not intend.
3. Run only the tests that should care. Record the failing test **by name** and
   quote its failure text.
4. Revert with `git checkout -- <file>` and assert a clean `git status` before
   the next probe. Probes that stack are worthless.
5. A probe that leaves everything green is a finding: the line is unpinned. Say
   so, and name the test that would pin it.

## Why it earns its cost

- It re-establishes a proof a rewrite voided. When a hand-built sync chain was
  replaced with `bloc_concurrency`, the old proof (disabling the chain broke an
  ordering test) no longer applied to anything. Swapping `sequential()` for
  `concurrent()` reproduced the original failure text exactly, which is what
  made the new implementation trustworthy rather than merely green.
- It finds correct-but-unpinned code. An `isClosed` guard, correctly placed,
  survived being replaced with `if (false)` with the whole suite still passing.
  Not a bug — but free for a later refactor to delete.
- It exposes tests that assert on what they also stub. Watch for
  `any(named: 'x')` where `x` is the thing under test. The healthy shape is the
  reverse: capture the argument under test, loosen the noise around it.

## Reporting

A probe table reads better than prose. One row per probe: the guarantee, the
mutation, caught yes/no, and the test that failed. The rows that say **no** are
the ones worth reading.

## Where it does not apply

Mutation probing tests the *test suite*. It says nothing about behaviour the
suite never covers, and it is no substitute for driving the running service or
the app. Use it alongside a live pass, not instead of one.
