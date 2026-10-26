# The epic map

Template. Fill in every `<placeholder>` for your own epic and delete the
made-up example rows (marked *example*). Write the date of the snapshot at the
top, and re-check the tracker before trusting a status.

Snapshot taken `<date>`.

- **`<PROJ-100>` `<epic name>`** is v1. It holds only the set that makes the
  feature correct, plus everything already done. It closes when that ships.
- **`<PROJ-200>` `<follow-up epic name>`** holds everything else. Nothing in
  it blocks the v1 release.

## Local checkouts

| Repo | Path | Stack | Style skill |
| --- | --- | --- | --- |
| `<app repo>` | `<~/projects/app>` | `<Flutter>` | `<writing-flutter-code>` |
| `<service repo>` | `<~/projects/service>` | `<Kotlin, Spring WebFlux>` | `<kotlin-spring-conventions>` |
| `<backend repo>` | `<~/projects/backend>` | `<stack>` | `<skill or none>` |

## v1, under `<PROJ-100>`

| Ticket | Repo | Days | Must be live first |
| --- | --- | --- | --- |
| `<PROJ-123>`: `<what it does>` | `<repo>` | `<n>` | `<ticket or nothing>` |
| *example* PROJ-123 part 1: resolve the caller | service | 2.5 | nothing |
| *example* PROJ-123 part 2: the type filter | service | 5 | part 1 |
| *example* PROJ-130: QA on a device | QA | 1 | PROJ-123 part 2 deployed |

Write down why a ticket is split, so nobody merges the parts by accident.
*Example:* PROJ-123 stays two merge requests on purpose. Part 1 changes no
behaviour, so it lands first and gets watched (cache hits, upstream latency,
error rate) before part 2 turns the filter on.

Also riding the same release, already on the branch: `<tickets>`.

## `<PROJ-200>`

| Ticket | Repo | MR | Must be live first |
| --- | --- | --- | --- |
| `<PROJ-124>`: `<what it does>` | `<repo>` | `<MR or none yet>` | `<ticket or nothing>` |
| *example* PROJ-140: send scope with every message | backend | !12 | nothing |
| *example* PROJ-141: read the scope, rate limit subscribe | service | !34 | **PROJ-140 in production** |
| *example* PROJ-142: grouped UI | app | none yet | **PROJ-141 in production** |

Short version of the design decisions that override older pages:

- **`<decision>`:** `<one or two lines>`.
- **Deploy:** `<order, timing, what to watch and for how long>`.
- **Known gap:** `<what is accepted as not covered>`.

## Closed, do not reopen by accident

- **`<PROJ-125>`** closed as `<Duplicate / Won't Do>`. Its items live in
  `<PROJ-ticket>` and ship on that branch.

## Design pages

| Page | Covers |
| --- | --- |
| [`<Main design doc>`](<url>) | Every ticket in both epics. The decisions source. |
| [`<Service design doc>`](<url>) | The service side. |
| [`<App design doc>`](<url>) | The app side. |
| [`<Later decision doc>`](<url>) | `<tickets>` after `<date>`. Wins over the main doc where they differ. |
| [`<Local testing runbook>`](<url>) | Running the service locally. |

List any old or replaced pages that still exist and say not to cite them.

## Grouping rule

Merge two tickets when they touch the same code and neither has to go out before
the other. Split them when they break in different ways, or when one has to be
watched in production before the next turns on.
