# dany-claude-marketplace

Dany's personal Claude Code plugin marketplace. Two plugins:

| Plugin | What it holds | Install |
|---|---|---|
| `getter` | Fetch anything outside the repo (Jira, Confluence, GitLab, GitHub, Slack, URLs) through cheap read-only Haiku couriers. | `/plugin install getter@dany-claude-marketplace` |
| `dany-skills` | General-purpose skills that work in any repo. | `/plugin install dany-skills@dany-claude-marketplace` |

Add the marketplace first:

```
/plugin marketplace add danyabdo94/dany-claude-marketplace
```

Refresh later with `/plugin marketplace update dany-claude-marketplace`.

## getter

- **getter** — Map the sources named in a request, dispatch one `getter:courier` per source, relay the raw facts. Model-invoked.
- **getter-handoff** — Gather via couriers, then package the conversation into a handoff doc a cheaper agent can continue. Uses `mattpocock-skills:handoff`. User-invoked.
- Agent **courier** — Haiku, read-only at the tool boundary.

## dany-skills

Skills that name a Jira site, a Slack roster, a repo or a metrics stack ship with `<placeholder>` values and a short setup note. Fill them in once for your team.

### Writing code

- **writing-plain-code** — Readability rulebook for any language: one step per line, `if`/`else` over clever expressions, one-screen methods, guard then flat body.
- **writing-flutter-code** — Dany's Dart/Flutter style guide: plain code, short label comments, locals-then-one-emit cubits, public `MockFoo` doubles, shared `main()`-scope fixtures, Arrange/Act/Assert labels. Load before writing any Dart.
- **my-flutter-code-flavor** — Cheap Haiku pass over a finished Dart diff: does it read like Dany's, and strip the AI tells. Checks only, never writes.

### Planning and learning

- **grilling** — Interview the user relentlessly about a plan until every branch of the decision tree is resolved. Model-invoked.
- **grill-me** / **grill-with-docs** — The user-invoked twins of `grilling`. The docs variant writes ADRs and a glossary as it goes.
- **in-1-line** — Force the next answer down to one line.
- **teach** — Teach a skill or concept over multiple sessions, using the current directory as a stateful workspace.
- **writing-great-skills** — Reference for writing and editing skills well.

### Writing on your behalf

- **add-my-flavor** — Rewrite any outward-facing draft in Dany's voice. Runs in the `dany-skills:flavor` agent so the pass stays on Haiku.
- **copy-ready** — Put a final draft on the macOS clipboard in the best paste form for Jira, Confluence, Slack, GitLab or email (real Slack mention chips included).
- **send-slack** — Send a Slack message to your team roster, DM or channel, always confirming before it goes out. You fill in the roster.

### Tickets and reviews

- **jira-ticket** — What goes in a Jira ticket: one-line title, facts not assumptions, P0/P1/P2 QA scenarios as ADF in your QA notes field, `What ships` as a comment once the MR exists. Plus what Jira renders from markdown. Bring your own cloudId and project key.
- **start-ticket** — Create a Jira ticket and its matching feature branch in one flow, copying metadata from a recent template ticket. The body comes from `jira-ticket`.
- **mr-review** — Review a GitLab MR on two axes (codebase and ticket) in parallel `dany-skills:mr-review-axis` agents, sort findings by priority, post them as inline diff comments after explicit approval.
- **explain-my-mr** — Leave short "why" notes on your own MR as GitLab drafts, one per line a reviewer would stop at. Shown to you first, never published by the model.
- **explain-diff-to-me** — Explain a diff to yourself: every changed line with a plain-English note, in a private Artifact page with the hard parts first. Read-only.
- **standup-check** — Fact-check your open tickets against your MRs, sort every open review thread by who answers next, and draft the standup. Read-only.

### QA and production

- **qa-test** — QA pass over one or more MRs, one `dany-skills:qa-ticket` agent per ticket. Distrusts handoffs, rebuilds the harness, fetches ACs verbatim, and pins guarantees with mutation probes. Bundles a read-only environment verifier; you supply a per-repo reference file.
- **sentry-issue** — Triage a production crash from a Sentry alert to a fixed MR.
- **trace-notification** — Find the stage where a push, a notification row or a badge got dropped, with probes, witnesses and controls instead of guesses. You fill in `references/signals.md` for your stack.
- **notification-ticket** — Template for a long multi-ticket epic: gather the ticket body, the design doc, the release order and the guard a ticket moves before touching code.

Agents (all read-only, model pinned in the definition):

- **flavor** — Haiku. Rewrites one draft and returns the text.
- **review-finder** — Sonnet. One dimension of a code review, candidate findings only.
- **review-verifier** — Haiku. Tries to disprove one review finding against the real code.
- **mr-review-axis** — Sonnet. One axis of an MR review (codebase or ticket), dispatched by `mr-review`.
- **qa-ticket** — Opus. Runs the QA pass for one MR and reports. Edit and Write removed, never fixes, commits or touches an MR.
- **grafana-fact-checker** — Haiku. Answers one question with numbers from Grafana (metrics, logs, traces). Never writes to Grafana.

`getter-handoff` uses `mattpocock-skills:handoff` from the official marketplace.

## Layout

```
.claude-plugin/marketplace.json     catalog
plugins/<name>/.claude-plugin/plugin.json
plugins/<name>/skills/<skill>/SKILL.md
plugins/<name>/agents/<agent>.md
```

Agents inside a plugin are namespaced: dispatch them as `<plugin>:<agent>` (for example `getter:courier`), never by the bare name.

## Adding a plugin

1. Create `plugins/<name>/` with a `.claude-plugin/plugin.json`.
2. Add `skills/`, `agents/`, `commands/`, `hooks/` or `.mcp.json` as needed.
3. Add an entry to `.claude-plugin/marketplace.json` with `source` pointing at the folder.

Relative `source` paths resolve only when the marketplace is added via a git host. Docs: https://code.claude.com/docs/en/plugin-marketplaces
