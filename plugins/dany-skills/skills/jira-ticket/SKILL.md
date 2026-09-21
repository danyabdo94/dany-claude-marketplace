---
name: jira-ticket
description: Write and create Jira tickets: one-line title, short plain-English description, requirements taken from facts only, P0/P1/P2 scenarios into the QA Testing Notes field, and "What ships" posted as a comment once the MR exists. Use when the user wants a new ticket, a ticket description rewritten, QA notes written, or asks to file, raise or open an issue. Other skills reach it for the ticket body and the Jira render rules.
---

# Jira Ticket

This skill owns **what goes in a ticket**. `add-my-flavor` owns how it sounds: run it over the drafted title, description and QA notes before creating anything.

## Setup: your site

Find the cloudId once with `getAccessibleAtlassianResources` and the project key from the user. If the project has a custom field for QA notes (many teams call it **QA Testing Notes**), find its `customfield_XXXXX` id with `getJiraIssueTypeMetaWithFields`. Below, `<qa-field>` stands for that id. Without such a field, the QA notes go in a comment titled `QA notes` instead.

## Steps

1. **Collect the source facts.** Every ticket starts from something: a Slack thread, a QA report, an MR, a parent epic, a Confluence page, a screen recording. Fetch each one through the `getter` skill's couriers, never from the main loop. Done when every claim you plan to write has a named source, or is marked as coming from the user directly in this conversation.

2. **Split facts from assumptions.** Write two lists. A fact is something a source states or the code shows. An assumption is anything you inferred, filled in as "probably", or would have to be right about. Done when every line of the second list is either dropped, confirmed with the user, or moved into `## Open questions`. **Never promote an assumption into a requirement.** This is the step that makes the ticket trustworthy, so do it before writing prose, not while writing it.

3. **Pick the issue type.** `Bug` when behaviour is wrong today. `Story` when a user gains something. `Task` when only the codebase changes (refactor, upgrade, cleanup). If the project has more types (`Spike`, `Design`, `Client Bug`), use one when the work plainly belongs to it. Done when the type is chosen, because it decides the description shape below.

4. **Write the title.** One line, see the rule below. Done when it fits on one line in the Jira list view and names a change, not a topic.

5. **Write the description.** Follow the shape for the chosen type. Short and plain English. Done when nothing in it is an assumption, and no section repeats another.

6. **Write the QA notes** as P0/P1/P2 scenarios for `<qa-field>`. Plain text, no markdown. Done when a QA engineer who has never seen the ticket could replicate every scenario from the notes alone.

7. **Flavor pass.** Run `add-my-flavor` over the title, description and QA notes together. Done when the text comes back in the user's voice with the facts and identifiers unchanged.

8. **Show the user the draft, then create.** Print the title, description, QA notes and the fields you intend to set. Create via `createJiraIssue` with `contentFormat: "markdown"` only after they say go. Read the issue key from the response, never invent it.

9. **After the MR exists,** post `What ships` as a comment. Not before: it describes a merge request that does not exist yet.

## The title

One line. Name the change, not the area.

| Good | Bad |
|---|---|
| `Filter the notification list on the user's plan rights` | `Notification list permissions` |
| `Other directories tab shows for users without the right` | `Directories bug` |

Present tense, no ticket prefix (Jira adds the key), no trailing period. If it needs a comma to hold two ideas, it is probably two tickets.

## The description

Every type opens the same way: **one paragraph, no heading, two to three sentences.** What is wrong or needed, who it affects, and the business consequence. Business before mechanism: a PM should get the point without reading further. One unicode emoji at the end at most, or none.

Then, by type:

**Bug**

```
## What happens

1. <step>
2. <step>

Expected: <one line>
Actual: <one line>

## Root cause
```

`## Root cause` only when it is actually known, one or two sentences, evidence as a fenced block or a small table. Leave it out rather than guess.

**Story / Task**

```
## Context

## Requirements

1. <one requirement, testable, from a source>
```

`## Context` is why this is on the board now: the business driver, the dependency, the complaint. `## Requirements` is numbered, one testable line each, facts only.

A **load-bearing design decision** goes in `## Requirements` as its own numbered line, not under a `## Decision` heading of its own. If the team settled a question and the answer constrains the build ("an absent row means allowed, a stored `false` denies"), it is a requirement. Bold the word the decision hinges on.

**Every type, when they apply, in this order at the end:**

- `## Open questions` — stays in the description, because it hangs off the context and root cause. One line each, name who can answer.
- `## Original report` — the reporter's text, shortened, never deleted. It carries the account names and the build.
- Last line: the design or ERD link, bare.

**Not in the description, ever:** `What ships` (it goes in a comment, step 9), acceptance criteria (they go in QA Testing Notes), release or version information, and a `What this is not` heading.

### Routing "what this is not"

There is no `## What this is not` section. The material is real, but it serves three different readers, so send each piece to the one who needs it instead of parking all three in the description:

| The point | Reader | Goes to |
|---|---|---|
| A correct behaviour that looks like a bug | QA, who would file it | a P2 line in QA Testing Notes |
| Scope defence, so a reviewer stops hunting the wrong bug | the reviewer, mid-MR | the `What ships` comment |
| What the ticket is *not* worth, against a claim someone made | PM or EM | one line in the opening paragraph |

Deleting the heading without routing its contents is a regression: the QA piece is the one that goes missing, and QA does not read the comment thread.

### Release information

Out by default: no `## Release` section, no deploy order, no version numbers. Two exceptions, and only these:

- **A hard dependency** ("this cannot go live before ABC-123, or a stale mirror blocks sends") is a `## Requirements` line, plus an `is blocked by` issue link so the board shows it without prose.
- **The deploy order itself** goes in a comment, never the description. It changes as MRs land, and a description that lists MR numbers is stale within a week.

## QA notes: `<qa-field>`

A textarea custom field's create-meta schema claims `string` / `textarea`, **but Jira rejects a plain string** when the field carries the ADF renderer and answers

```
Operation value must be an Atlassian Document
```

So:

- Send it with `contentFormat: "adf"` and an ADF `doc`. `contentFormat: "markdown"` converts the description and comment bodies only, never a custom field.
- Build real ADF structure, not one paragraph with `hardBreak` lines. A flat version is not human readable. Headings, bullet lists and ordered lists all render in this field and pass the size limit fine at 15 scenarios.

Shape, in this order, each as a `heading` (level 3) followed by a list:

```
### Setup                       bulletList: environment, build, pre-checks (one item each)
### Accounts you need           orderedList: one account or role per item, right names in `code`
### P0: must pass               orderedList
### P1: stated requirements off the main path   orderedList
### P2: worth a look            orderedList
```

Each scenario item is one paragraph: the **action in bold**, a colon, then the expected result in plain text.

```
1. **Account without the READ right, open the list**: no rows the account may not see, badge counts only what is shown.
2. **Give the right back, reopen within a minute**: hidden rows return, nothing was deleted.
```

Skip a P-level heading that has no scenarios rather than leaving it empty. The action is replicable, the expectation is observable.

**The rubric**, so P0 does not drift into "whatever I tested first":

- **P0** — the reason the ticket exists. If this fails, the ticket is not done. Also anything that could lose data or crash.
- **P1** — a stated requirement off the main path, or an edge a real user will reach.
- **P2** — worth a look. Cosmetic, a rare state, or a regression check on nearby code.

Every ticket has at least one P0. A ticket with only P1 and P2 scenarios has not been thought through.

**Not a QA scenario:** "write unit tests for `isAllowed`", "add an integration test per send path", "update the docs". Those are dev tasks. A scenario is something a QA engineer can perform against a build and observe the result of. If the line starts with a verb aimed at the implementer, it belongs in `What ships`.

## The `What ships` comment

Posted in step 9, once the MR is open. Jira comments render markdown, so this one gets real lists.

```
## What ships

1. <what the MR delivers>
2. <...>

Not in scope: <what was deliberately left out>

MR: <link>
```

`###` sub-headings when it splits into parts. Numbered lists in a *comment* still use `1.`, not the `1-` style.

Add a short `What this is not:` line here when a reviewer could otherwise hunt the wrong bug, and the deploy order when there is one. Both are reviewer-and-release material, which is exactly this comment's audience.

## Fields

**Set:** `project`, `issuetype`, `summary`, `description`, `assignee_account_id`, `priority` (via `additional_fields`), and the parent or Epic Link when the ticket belongs to an epic.

**Never set by default.** Only when the user asks for them by name in that conversation: `fixVersions` and any release-estimate field. Release information is out by decision.

**Leave alone:** product-owned multiselects (a `Root Cause` picker is not the `## Root cause` heading). `labels` are ticket-specific, so ask rather than inherit.

## What Jira renders

Descriptions and comments go through `createJiraIssue` / `editJiraIssue` / the comment tool with `contentFormat: "markdown"`, which converts to ADF. What renders:

- `##` and `###` render. `#` is too loud, skip it.
- `1.` numbered lists render, nested `   1.` works. The `1-` `2-` style stays plain text in a description.
- `*` bullets render, nested with two spaces. `•` does not become a list.
- Markdown tables with a `| --- |` separator row render. Wiki `||` tables do not.
- Fenced code blocks render. `{code}` wiki macros do not.
- Inline `code` renders. **Bold around inline code is stripped**, so bold the word beside it, not the code span.
- Slack shortcodes (`:eyes:`) stay literal. Use unicode emoji.
- No expand or collapse macro, so shorten the original report instead of folding it.
- Bare URLs become links. Ticket keys like `ABC-123` link on their own.
- **@mentions do not work in markdown.** `[~accountid:...]` comes out escaped. To mention someone, send `contentFormat: "adf"` with a `{"type":"mention","attrs":{"id":"<accountId>","text":"@Name"}}` node after `lookupJiraAccountId`. An existing comment can be replaced in place with `commentId`.

Jira wiki markup (`h2.`, `{{mono}}`, `{panel}`) renders nowhere in this path. Do not use it.

## Anti-patterns

- No assumption written as a requirement. If nobody said it, it is an open question.
- No `What ships` in the description, and none at all before the MR exists.
- No acceptance criteria in the description. They are QA Testing Notes now.
- No release or version anywhere by default.
- No implementation detail in a Story: no file paths, no class names, no "Technical Approach" section. That belongs in the MR.
- No `[placeholder]` brackets left in a created ticket.
- No story points and no `Definition of Done` checklists. Estimation is a separate conversation.
- No section that exists only to be filled. Drop an empty heading instead of writing "N/A".
- No `## What this is not` and no `## Decision` heading. Route the first, fold the second into `## Requirements`.
- No dev task dressed as a QA scenario.
- No em dashes.
