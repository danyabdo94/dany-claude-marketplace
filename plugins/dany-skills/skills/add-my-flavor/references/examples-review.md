# Real code review comments, verbatim

From 243 of Dany's GitLab discussion notes on teammates' MRs (`uberall_corex`, Jul 2024 to Aug 2026).

**The number that matters: median comment length is 62 characters.** 233 of the 243 are one or two lines. The long "Scenario:" essays are 4 comments out of 243, and the `**[Medium]**` severity-prefixed ones are 6, all on a single MR, 5 of which contain em dashes: those are `mr-review` skill output, not his hand.

So the register is **not** "formal and cold". It is **short, question-shaped, and collaborative**. Emoji and `WDYT?` belong here. Paragraphs mostly don't.

---

## The default shape: one thought, phrased as a question

He asks rather than instructs, even when he is plainly right. `we` throughout. `:eyes:` does the softening.

> can we extract this?

> can't we structure a bit those long list of Strings? :eyes:

> do we need other enums? :eyes:

> shall we add it to the extinsions?
>
> like: hasUBIFeature => featureAccess?.hasAccess(Feature.UBI)

> semi-colon :eyes:

> repeated code :eyes:
> <screenshot>

> what is this? :eyes:

> why do we have this here? :eyes:

> this has the same key as inboxSection. did we mean to do this?

> using enums? InboxApprval.approvalNeeded ?

> short-hand? `.REJECTED` btw we need to align the statuses to be either uppercase or lowercase for the whole project

> can we add a comment :eyes: plz

> Can we add tests? :eyes: specially for the old cases, those were failing

> the whole branch is outdated, can we pull latest from dev and rebase this branch? :eyes:

> let's do the todo :eyes:

> hello this is not linked to the ticket :eyes:

> why not import 'package:collection/collection.dart';
> ?

> Why the getters specially for openingHours?
> Since we have already passed the full location?

> do you think we can move this logic somewhere else?

> QQ,
> do you think we shall keep them here?
>
> isn't it a Social Directory Property somehow? :eyes:

## Stating a problem without a question

Still one line. `we shouldn't` is as blunt as he gets.

> we shouldn't do this :eyes: "!"

> I don't think we should name it inboxProfile :eyes:

> we shouldn't rely on the name of the secitons nor the approvalBranches, this shall be generic enough to show the children of a route :pray:

> there are a lot of todos we need to tackle them :eyes:

> I think this could be more readable

> I don't think we need to pass any of those attributes, since we already know the domain, which is "service area"

> `type: .error` for the dot shorthand, same on line 66. Rest of the feature already uses it (social_thread_screen.dart:157).

## Admitting he doesn't follow the code

He puts confusion on himself, not on the author. This is a real and frequent move.

> I'm sorry I can't understand this :') can you explain to me how the group of routes are working rn?

> I feel that I can't understand this:
>
> What is the difference between inbox and inboxes??
>
>   const InboxesSection(),
>   const InboxSection(),
>   const InboxApprovalsSection(),

> Sorry, I don't get what this fucntion doing? Is it only for `test`?

> Readability on this one, it took me a few passes.

> because I really can't remember the whole logic of timezone.

## Flagging uncertainty rather than asserting

> I'm not sure if we should do this,
> I think it should always be Date, and for the sake of empty dates it could be nullable and check on `fromJson` function, WDYT?

> I'm a little bit concerned,
> I think this function shouldn't  be aware if it's single location user  or not #Single_ _Responsibility

> I'm not sure if this breaks the timezone or not.
>
> but now, when I create a post on 00:00 on UTC timezone, it becomes 21:00 ...
> can you double check plz if we changed some logic,
>
> because I really can't remember the whole logic of timezone.
> <screenshots>

> how could be a three years old code is causing an issue now :eyes: ??
>
> I think we are not fixing the main issue.. let's dive deeper

> isn't this valid ? :eyes:

## Offering options instead of a verdict

> We can go either ways:
>
> - Having resetSocialPostForSingleLocationManager
>
> - or Passing a `SocialPost` to the `reset` function keeping their data

> or we use path instead of name
> for
> ```
> final firstRouteName = branches[0].defaultRoute!.name!;
> ```

> is there a way to use the same old behaviour without adding ValueListenableBuilder?
>
> Yes? :eyes: WDYT? which one is better?

## Conceding

He drops a thread cleanly and says so.

> Getting a function directly from its own library is better than
>
> Getting a third-party function from another third-party library.
>
> That was my opinion

> the problem:
>
> We rely on a third-party (freezed) to get a direct function from (collection).
>
> Anyway, I'm fine keeping or removing it.

> I agree with both ways BTW.

> okay let's go with the center

> I can't remember any blockers against this approach, fine :pray:
>
> cool

> this is more into your decsision, you do you Sara <3

## Approving

Warm, personal, named. Never a bare "LGTM".

> LGTM, well done @sara.petrovic

> Well done sir Ricc LGTM

> LGTM sir Ricc :white_check_mark:

> revert it will work :magic_wand:

## Pointing at a decision made elsewhere

Review comments carry the meeting, the ticket or the person who decided.

> We agreed on :
>
> - Move the hours logic to a new extension / util
> - Write tests
> - regression test

> @sara.petrovic and me had a meeting talking about putting the constraint numbers inside of the social directories :pray:

> We need it for the case of the user doesn't have any other pages:
>
> as the user related to this bug:
> https://uberall.atlassian.net/browse/MOB-1300

> since this is a we-do-ours @riccardo.scaramagli wdyt?

> Hey Ricc,
> We found that this needs to be changed,
>
> the condition shall be ( 1 Year from the start date, not from Now)

Note the greeting: he does occasionally open a review comment with `Hey Ricc,` or `hey @...`. It is not banned here, it is just uncommon.

---

# Replying to reviewers on his own MRs

## Explaining a choice: one line, no defensiveness

> It was like this, no changes added

> could be freezed later

> for the sake of QA automation

> yes, as agreed with Cliff

> yes it was communicated in one of the standups

> QA needs the first one for testing, it won't matter

> It's not 100% the same as the design, but consistent with Home colors

> it follows the same way in flutter like `.isEmpty` and `isNotEmpty`

> I will add it to the ticket, becuase it was discovered while testing

> the problem was that,
> if the user doesn't have the notification permission, the old way could show another tap as pinned at the bottom, which is not correct, that's why we fixed it

## Author notes on his own MR

Draft comments he leaves on his own diff before the review starts, one per line a reviewer would stop at. Not questions, not defence: the why in one breath, lowercase start, backticks on names, a tiny numbered example when order is the point. Real drafts from corex !1096:

> changed to bloc to use `sequential()` instead of using our own implementation

> what was the problem?
>
> the problem was that when the user was enabling or disabling a lot of topics one by one, we were dropping some of them

> same event for same queue, it holds the sync + updateTopic
> Ex:
>
> 1. Sync starts, reads the account, sees new_review: true.
> 2. User flips reviews off. Toggle PUTs new_review: false and finishes.
> 3. Sync's PUT lands with new_review: true from step 1. The user's toggle is gone.

> this is the fix. `features == null` means user fetch is not done yet: all gates read false so we sync an all-false mirror. mobile-service flips those topics off, so no push and no notification center row. an empty list is valid data and still syncs

> 404 is how mobile-service says the email has no account yet. before, any failure became `AccountModel.empty()` so we could not tell a new account from a network error and would seed topics on failures

> side fix: the refresh was hitting the monolith on every foreground even with the flag off

The `explain-my-mr` skill produces these. Four lines is the ceiling; past that it is description material.

## Pushing back

Explicit, playful, and it ends by handing the decision over.

> I would push back to my original suggestion; let's fight :grin:
>
> For this scenario:
> - When the API renames appStoreUrl or adds a field,
> - we fix one fromMap instead of fixing six occurrences
>
> WDYT? you can ask @riccardo.scaramagli abou his opinion BTW

> IMHO
>
> Working with object keys is fragile and not DRY, let's include Riccardo in our next meeting

> IMHO, breaking the maestro job is a thing that we can afford, but we can't afford the other attacking one.
>
> At the end, lemme know what your final decision is, guys :pray:

> 2 won't work with the idea of permission-based items

> I can see some of code rabbit comments are valid,
> I also thinks shall we actually ask claude to move the previews outside of the widgets? I can see growing files, for no technical reason.

## Not-a-bug replies

When he has actually checked, he says so first, then gives the mechanism.

> Not a bug, I checked: Dart generics are covariant so the untyped literal on line 52 still satisfies `is Map<String, dynamic>` and the `as String?` reads in `inbox_routes.dart` are safe.

---

# The long form, for when a finding genuinely needs it

Reserve this for a real defect with a non-obvious failure path: roughly 1 comment in 50. Claim, then mechanism with `file.dart:line`, then `Scenario:` as bullets, then the fix as `Can we <do X>.` phrased as a statement with a full stop, not a question mark.

> We only re-point `selectedFeedItem` when `_findComment` actually finds the target, but we pass `initialReplyText` down unconditionally at line 203. So when the injection fails we **prefill the reply box while still pointing at the root post**.
>
> Scenario:
> - user taps edit on a Facebook approval
> - `getFeedItem(pendingCommentId)` fails (network blip), `_injectPendingComment` returns the thread untouched
> - `_findComment` returns null, so `selectedFeedItem` stays `widget.socialThread`, which is the root post since we navigated by `rootIdLink`
> - box is still prefilled, no "Replying to" label renders, user hits send
> - the proposed reply gets published as a new top level comment on the post instead of a reply to the customer
>
> Nothing tells the user any of this happened, and it goes out to a live social account.

> We append without checking whether the item is already in there, and that's **a crash rather than a double render**. At depth 1 `RepliesSection` builds with `key: GlobalObjectKey(replies[index].id)` (replies_section.dart:47), so a duplicate puts two identical `GlobalObjectKey`s in the same tree and Flutter asserts. Red screen.
>
> Two realistic ways in: the backend starts including `APPROVAL_NEEDED` items in `getChildren`, or the request gets approved somewhere else between loading the list and opening the thread.
>
> ```dart
> if (node.children.any((c) => c.id == child.id)) return node;
> ```

> Both failure paths end up returning the tree unchanged: this one, and the "parent id isn't anywhere in the tree" fallthrough in `_insertChild`. The screen then renders a perfectly normal thread with no pending item and nothing telling the user why they were sent there.
>
> Can we surface it in the state (a flag on `SocialThreadState`) so the screen can toast. The comment on social_thread_screen.dart needs the same signal to know it shouldn't prefill.
>
> Also: this is the riskiest new logic in the MR and `social_thread_cubit_test.dart` has no case for it. No `pendingCommentId` path, no depth 1 vs depth 2 insert, no parent-not-found, no `getFeedItem` failure. Can we get those in before merge.

What earns the length: a concrete user-visible consequence at the end ("goes out to a live social account", "Red screen"), and naming the exact line that proves it.

## Not this

The severity-prefix format appears on exactly one MR and reads like a linter, not like him. Don't generate it:

> ~~**[Medium] Positional grouping is fragile.** The Location + Approvals grouping relies on the Approvals branch sitting at exactly `i + 1`. If branch ordering in `getAvailableAppSections` ever changes ... will silently **drop** the Approvals item — it is only ever rendered through the adjacency check, never on its own.~~

Same content in his voice would be two lines and a question.
