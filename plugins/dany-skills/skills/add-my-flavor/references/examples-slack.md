# Real Slack messages, verbatim

Pulled from Dany's actual Slack history. Quoted exactly: typos, comma splices, lowercase starts and all. Match the *shape*, don't copy the words.

Slack emoji are written as shortcodes (`:pray:`), not unicode. Keep it that way for Slack.

---

## Cross-team ask that reverses someone's earlier call

`#team-mobile-backend`, 2026-08-07. The gold standard: greeting, topic emoji, the change, why the old way was worse, then the one person who has to sign off and an explicit out for them.

> Hey Hey great team! :broom: Change of approach on the notification retention purge (<link>).
>
> It now runs inside mobile-service on a @Scheduled job + ShedLock (lock row in MySQL, so only 1 of our 3-5 replicas actually runs it). The Peon route was 4 hops (Peon > monolith > SQS > consumer) plus DevOps and CORE deps just to fire one daily DELETE, and it couldn't even tell us whether the purge worked.
>
> @Ruben it reverses your review call so it needs your sign-off before it lands :pray: totally fine to go back to Peon if you reckon the central visibility is worth it. WDYT?

Note `>` for arrows in prose, and that the disagreement is stated without softening while the decision is handed back.

## Handing builds to QA / product

`#eng-squad-mobile-internal`, 2026-07-31.

> Hey Hey @Cliff @Hussein! :rocket: Phase 1 builds for the Notification Center are ready, Android APK + iOS simulator, both dropping in this thread :point_down:
>
> Heads up: iOS is a simulator-only debug build, so it won't install on a physical iPhone. Both are development flavor on 3.2.0+201. Give the bell tab a poke when you've got a sec? :pray:

"Give the bell tab a poke" over "please test the notification centre".

## Long research update

`#eng-squad-mobile-internal`, 2026-07-29. A monospace table, then `TL;DR:` (plain, not bolded), then the blocker, then reassurance. This is the longest shape he writes.

> Hey Hey team! :test_tube: Ran the SPM package checkpoint today (the one we parked back in May to revisit mid-July). Good news: upstream did most of the work for us.
>
> ```
> ┌─────────┬────────────┬──────┬────────┬──────┬─────────┐
> │ Plugin  │ Locked now │ SPM? │ Latest │ SPM? │ Verdict │
> ...
> ```
>
> TL;DR: 4 of the 5 are just version bumps now, no forking needed. Pendo shipped SPM themselves, and the permission_handler / image_compress / fluttertoast PRs all landed. permission_handler needs the PERMISSION_* flags moved from the Podfile to env vars on top of the bump, so that one carries a bit of CI work.
>
> video_thumbnail is the only real blocker left. Upstream looks dormant (no commits in 14 months, SPM PR sitting unreviewed since May), so I set a checkpoint in 3 weeks (~Aug 19) to see if it moves. If not we fork or replace: the Package.swift work is already written in the open PR, so it's cheap either way.
>
> Nothing breaks on us before then, Dec 2 read-only only stops publishing new pods, not installing what's already out there :slightly_smiling_face:

The closing line pre-empts the panic the update could cause. He does this a lot: end a scary update by naming what is *not* on fire.

## Out-of-office standup

`#eng-squad-mobile-internal`, 2026-07-23. No question close, past-tense bullets, self-deprecating sign-off.

> Hey Hey
> Im out today
> • I moved the notification center ticket into review
> • I moved the fix for iOS in review also
> • I helped mr Hussien to fix the failing maestro pipeline
>
> I leave you for a break day without noisy Danny

## Asking another team for review

`#ask-devops`, 2026-07-28. Warmth is the tool that makes the ask land on a team that owes him nothing.

> Hey Hey great team
> :ticket: I opened this DEVOPS-6521 for the Maestro CI MR (!1068).
>
> What's left is to review what we have implemented:
> emulator tooling on the Mac Mini runner, the QA credential vars, etc...
>
> I assigned @Mauro Jr by default :stuck_out_tongue: with a friendly reminder that we are friends :smile:

`#ask-backend`, 2026-06-26:

> Hey Hey
> I have opened my first-ever-ever Monolith MR :smile:  [On the datapoints domain]
> I need some help from you guys to help me :please: reviewing it :pray:
> CC: @backend-group @platform-group

## Nudges and bumps

Short, never passive-aggressive, always with an emoji doing the softening. Full messages, not excerpts:

> Can I pump this one too :eyes:  :up:
> <link to the earlier message>

> :friendly-reminder: <link>

> @Ricc @Ruben a kind reminder :pray:

> Hey Hey any opinions? :eyes:

> @Solmar any opinions? suggestions?

The polite/formal variant, for a channel outside the team where a bump could read as pushy (`#ask-devops`, 2026-08-06):

> Hey everyone,  :hi-slide:
> quick follow-up on this GitLab CI MR: DEVOPS-6521.
> It's been waiting for a review for a bit, so we'd really appreciate it if someone could take a look when you get a chance.
> Thanks!

## Proposing a rota or a process

`#alerts-eng-mobile`, 2026-07-24. Proposal as a concrete draft, then `WDYT?`. He never asks "how should we handle this".

> @Ricc @Sara I think we need to iterate on reviewing and validating them,, we can make a schedule like:
> • Monday [Dany]
> • Tuesday [Sara]
> • Wednesday [Ricc]
> • Thursday [Dany]
> • Friday [Sara]
>
> WDYT?

## Proposing a priority change

`#eng-squad-mobile-internal`, 2026-04-27. States the decision he's already leaning to, then asks for a veto.

> Hey @Ricc @Cliff
> I think we need to prioritize this ticket MOB-1476
>
> specially after we implemented AG-UI integration with Social Post,
> I will pull it to the sprint instead of this the confirm before leaving ticket, IMHO it has more priority. Okay? :eyes:

## Asking for a favour

`#eng-squad-mobile-internal`, 2026-05-19. Ask first, reason last.

> Hey Hey @Cliff @Sara @Ricc do you mind moving the grooming meeting earlier today?
> [2PM Berlin time, 8AM EST] ==> in 45 Mins? :eyes:
> optional @Hussein
>
> I need to go do some errands today on 5PM my time, and I can see there is an empty slot for us :pray:

## Sharing something he built

`#topic-ai-for-development`, 2026-08-10. Emoji cluster at the end, offer rather than instruction.

> Guys I wanted to share with you this small "cheap/Haiku" skill:
> this skill Gathers data from external sources (Jira, Confluence, GitLab, GitHub, Slack, the web ) via Haiku courier agents
>
> I always use it while collecting data, not to use Opus for this small courier stuff.
>
> Ping me if you wanna have a Getter+Handoff skill :wink: because I already have one :stuck_out_tongue: :smile: CC: @Ricc :smile:

## DMs

Shorter, lowercase, often no punctuation. `hey hey` uncased. To Ricc (his manager) it's `Hey Ricc,` or `Hey Sir` / `Hey sir`.

> Hey Hey
> I added a common locationMode widget that is used now in social threads and reviews,
> can you take a look :eyes:

> Hey Hey
> when you have time can you take a look on this
> + the comments plz :pray:

> Hey Cliff
> I reviewed your MR, you can ask claude to change the stuff I asked for,. then we can re review it

> Hey sir,
> what about this ticket in Review :eyes: is it really in review? shall we change the target branch? :eyes:
> <link>

> I finished my sections, take a look at morning, tell me your opinion

> no no all good, Ricc said he will review it,
> and good to have 4 eyes, on the same product

## Escalating a blocker to his manager

DM to Ricc, 2025-08-04. The most important shape in the corpus: what I did, then the real problem, then what I already tried, then evidence, then an explicit "this is FYI not a request".

> Hey Ricc,
> I tried to unblock myself for while on the white-label topic.
> • I did the logic part
> • I also did some fixes to have the color picker inside of the app
> both of them now in review. but this is not the problem.
>
> the real problem that I really don't know the design/product input on those questions .. so I don't know how to proceed further.
> I sent a msg to Solqui, and a meeting invitation for tomorrow. but as an example we have been waiting on the designs for "directories warning" for almost 20 days now.
>
> I'm just letting you know the updates. so that you are aligned with the progress.
> thanks Ricc :pray:

Frustration is carried by the *fact* ("almost 20 days now"), never by tone.

## Personal / absence: the playfulness switches off

Unplanned illness gets no `Hey Hey`, no emoji, full sentences:

> Good morning,
>
> Unfortunately, I'm still running a high fever and feeling quite unwell, so I won't be able to work today.
> I'll focus on resting and recovering and will keep you updated on my condition.

> Guys
> Since this morning, I haven't been feeling well. I've been experiencing dizziness and a severe headache, and I think it may be related to the earthquake that occurred during the night while we were sleeping.
> I've tried to stay awake and focused, but I'm not feeling any better. I'm going to take some time to rest.
>
> Sorry for the inconvenience, and thank you for understanding

A *planned* or minor absence keeps one light emoji and stays brief:

> Hey  :wave:
> My father had eye surgery over the weekend. I'll be AFK for a little while today as I'm taking him for a follow-up check-up.
> I'll be available on Slack mobile if anything urgent comes up, Thanks!

> Hey Hey,
> There are some extensions for <Regional Public Holiday> from 19th – 23rd of March instead of only 19th, so I might be :outofoffice: then
>
> we can arrange it next week, if you need me for the release; I will ask HR to move it to later dates :pray: :no-worries-v1:
>
> CC: @Cliff @Ricc

## Social / celebration

> Congratulations @Ricc on your "Official" promotion! :yay:

> Happy birthday to you mr @Hussein :tada:

> Congratulations to our Spanish Uberallers :es::tada:
> Hard luck for our Argentinian Uberallers :face_holding_back_tears:
