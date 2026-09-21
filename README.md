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
- **getter-handoff** — Gather via couriers, then package the conversation into a handoff doc a cheaper agent can continue. Uses `dany-skills:handoff`. User-invoked.
- Agent **courier** — Haiku, read-only at the tool boundary.

## dany-skills

Skills:

- **writing-plain-code** — Readability rulebook for any language: one step per line, `if`/`else` over clever expressions, one-screen methods, guard then flat body.
- **grilling** — Interview the user relentlessly about a plan until every branch of the decision tree is resolved. Model-invoked.
- **grill-me** / **grill-with-docs** — The user-invoked twins of `grilling`. The docs variant writes ADRs and a glossary as it goes.
- **handoff** — Compact the current conversation into a handoff document so another agent can continue.
- **in-1-line** — Force the next answer down to one line.
- **teach** — Teach a skill or concept over multiple sessions, using the current directory as a stateful workspace.
- **writing-great-skills** — Reference for writing and editing skills well.
- **add-my-flavor** — Rewrite any outward-facing draft in Dany's voice. Runs in the `dany-skills:flavor` agent so the pass stays on Haiku.
- **jira-ticket** — What goes in a Jira ticket: one-line title, facts not assumptions, P0/P1/P2 QA scenarios as ADF in your QA notes field, `What ships` as a comment once the MR exists. Plus what Jira renders from markdown. Bring your own cloudId and project key.
- **qa-test** — QA pass over one or more MRs, one `dany-skills:qa-ticket` agent per ticket. Distrusts handoffs, rebuilds the harness, fetches ACs verbatim, and pins guarantees with mutation probes. Bundles a read-only environment verifier; you supply a per-repo reference file.

Agents (all read-only, model pinned in the definition):

- **flavor** — Haiku. Rewrites one draft and returns the text.
- **review-finder** — Sonnet. One dimension of a code review, candidate findings only.
- **review-verifier** — Haiku. Tries to disprove one review finding against the real code.
- **qa-ticket** — Opus. Runs the QA pass for one MR and reports. Edit and Write removed, never fixes, commits or touches an MR.

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
