# The guard model

Template. Read it out of the code, write the date at the top, and fill in every
`<placeholder>`. The rows marked *example* show the shape with a made-up
notification feature; delete them once yours are in.

Read out of the code on `<date>`.

## What guards what

One row per path a user can reach the feature through, one column per guard.
Each cell says where the guard is enforced today, or which ticket adds it.

| Path | `<guard 1>` | `<guard 2>` | `<guard 3>` | `<guard 4>` |
| --- | --- | --- | --- | --- |
| `<path>` | `<today / PROJ-123 / never / not used>` | | | |
| *example* The notifications list | PROJ-123 | PROJ-123 | never | PROJ-141 |
| *example* The push itself | per message, from the payload (PROJ-140) | PROJ-124 | today | PROJ-141 |
| *example* Push timing | | | | PROJ-141: grouped users get one push per hour, quiet hours at night |

Write down the rules that follow from the table, one line each. These are the
ones that bite. *Examples* from the made-up notification feature:

- **Topics never filter the list.** A row is written at send time if the topic is
  on. The list is then read straight off the account id. So turning a topic off
  hides nothing that is already stored.
- **Scope comes from the backend, not the app.** On every sync the service reads
  the user's links from the backend and diffs them. A lost link keeps its pushes
  until the next app open. That is accepted.
- **An absent permission row means allowed.** By design. A `false` row denies, a
  missing row does not.

## The authorities

If the read path and the send path trust different sources, name them here.
They may disagree on purpose, so name which one you are in before changing
anything.

- **The read path** asks `<source>` for `<what>`, `<per request / cached>`.
- **The send path** reads `<source>`, which `<who>` writes `<when>`.

## The chain that surprises people

Any guard whose effect is indirect, so a grep on the obvious name finds
nothing. *Example:*

```
app syncs permissions
  -> RightsChecker.setPermission
    -> muteTopicWithoutRight  (turns the matching topic off)
      -> the send path sees topic.active == false and skips
```

**The hole** in that example: the send paths read the topic as
`?.active != false`, so a missing row reads as enabled. A user with a `false`
permission and no topic row still gets pushes. It is a missing row, not an
ignored flag.

## Where each guard lives

One table per repo.

### `<app repo>`

| Concern | File |
| --- | --- |
| `<concern>` | `<path>` |
| *example* Plan and rights, one place | `lib/features/core/util/gates.dart` |
| *example* The mirror the app syncs | `lib/features/sync/settings_sync.dart`, `_sync` |
| *example* Push tap routing | `lib/features/message/push_router.dart` |

Notes that are not visible from the table, for example: "the app does no
filtering of the list, every list guard has to be server side".

### `<service repo>`

| Concern | File |
| --- | --- |
| `<concern>` | `<path>` |
| *example* The list, both counts, read and delete | `controller/InboxController.kt` |
| *example* The permission mirror | `service/RightsChecker.kt` |
| *example* Topics and the push subscription | `service/TopicRegistry.kt` |

### `<backend repo>`

Where the backend sends events, which flags gate it, and which code is dead
because of a config value.

## Open questions

Carry them into any ticket that touches the same ground. Strike one through
and write the answer when it is decided.

1. `<question>`
2. *example* What should "topic off" mean for the list: stop new rows only, or
   hide the old ones too?
