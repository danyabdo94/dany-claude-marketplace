# Commit messages and MR titles

Not a message-to-a-human register, but it is writing produced on Dany's behalf, so it belongs here.

**The data:** 239 non-merge commits by Dany on the app repo over 10 months. **201 of them (84%) are a subject line with no body at all.** Of the 38 that have a body, 32 carry a `Co-Authored-By: Claude` trailer. So the multi-paragraph commit body with bullet points and rationale is not his style, it is what Claude produces when it commits for him.

Three of those bodies contain em dashes, which breaks the hard rule. When writing a commit body, the no-em-dash rule applies exactly as it does to messages.

## His shape

One line. Ticket prefix, conventional-commit type, then what changed. Both separator styles appear, `-` slightly more often:

```
PROJ-1586 - feat(notifications): implement notification repository and presentation layer
PROJ-1609  fix(profile): guard empty 200 body in updateProfile
PROJ-1579 - feat(photo-editor): implement SlideUpPage for iOS back gesture support
PROJ-1600 - Add missing icon + tests to guard against missing media icon assets
PROJ-1590 - Add semantics wrappers for filter buttons and actionable text input
```

Without a ticket prefix, on follow-up commits within a branch:

```
feat(notifications): reliable refresh-on-visit, back nav, and photo tiles
refactor: convert OptionPicker to StatelessWidget and implement PinnedListView for improved item visibility
```

And for small mechanical work, plain and blunt, no ceremony:

```
Fix tests
delete comments
Make comments readable
Fix MR Comments
Add phase 2
Parameterize URL cases and compare null directly.
```

## Default

Write the subject line only. Add a body when the change genuinely needs a *why* that the diff can't show (a non-obvious constraint, a reverted decision, a security reason). Then keep it to a few lines, no em dashes.

The project rule still applies: on the first commit pushed to a new branch, prefix with the ticket ID from the branch name.
