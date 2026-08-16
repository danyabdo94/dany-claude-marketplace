# getter

A Claude Code plugin that gathers data from external sources — Jira, Confluence, GitLab, GitHub, Slack, arbitrary URLs — by dispatching one cheap Haiku **courier** subagent per source. The expensive main loop never fetches; it maps the ask to sources, dispatches couriers in parallel, and relays what they bring back.

## Features

- **One courier per source, dispatched in a single message** — a three-source ask fetches in parallel, not in sequence
- **Read-only by construction** — couriers run as the `courier` agent with mutation tools stripped at the tool boundary (`Write`, `Edit`, `NotebookEdit`, `Artifact`, further agent spawning), not merely instructed to behave
- **Raw facts, verbatim** — IDs, titles, statuses, bodies, authors, dates, links; no analysis or recommendations from the courier, so the main loop reasons over unedited source text
- **Gaps stay gaps** — an inaccessible source is reported as "courier could not access X", never filled in from memory
- **Identifiers resolved up front** — a missing ID is inferred where possible (e.g. from the branch name) or asked about *before* dispatching, not after
- **Prefix-agnostic MCP** — couriers resolve their own full tool names via `ToolSearch`, so the same skill works whether Atlassian is installed as `mcp__jira__`, `mcp__atlassian__`, or `mcp__claude_ai_Atlassian_Rovo__`

## Prerequisites

Whatever the sources you actually use require:

| Source | Needs |
|---|---|
| GitLab | `glab` CLI, authenticated (`glab auth status`) |
| GitHub | `gh` CLI; unauthenticated falls back to `curl` for public repos |
| Jira / Confluence | Atlassian MCP server connected |
| Slack | Slack MCP server connected |
| Web pages | nothing |

## Usage

Three entry points.

**1. Slash invocation** — the skill lists as `getter:getter`; type `/getter` and pick it.

```
/getter what's the status of IN-1915 and who's reviewing it
```

**2. Natural language, no slash** — the skill triggers on any ask for information living in an external source. This is the common path:

```
pull the comments on MR !59 and the acceptance criteria from the linked ticket
```

**3. Direct courier delegation** — for one known source, when you don't need the full map-dispatch-relay flow:

```
use the courier agent to fetch the last 30 comments on GitLab MR !59
```

**Examples:**

| Ask | What happens |
|---|---|
| `/getter get the comments on <MR url>, validate them` | 1 courier → `glab api .../notes`; returns notes verbatim, the main loop does the validating |
| `/getter IN-1915 — the ticket, the MR, and any Slack discussion` | 3 couriers in one message, in parallel: Atlassian MCP + `glab` + Slack MCP; relayed grouped by source |
| `/getter what's the state of my current ticket` | Infers the ID from the branch name (`feature/IN-1915-…`); asks first if it can't |
| `/getter summarise <confluence url> and <blog url>` | Confluence courier via MCP, the blog via `WebFetch` |
| `/getter compare our config to what the upstream repo does` | GitHub courier via `gh api`, falling back to `curl` on public repos |

## What it deliberately won't do

Couriers are read-only, so **"post this comment on the MR" is not a getter ask** — it reports that the request needs a write it cannot perform. Same for transitioning a Jira ticket or posting to Slack. Use `mr-review`, or `glab`/`gh` directly, for anything that mutates.

Two output behaviours worth knowing when you read a relay: quoted bodies are verbatim, so odd-looking text is the source's, not a paraphrase; and a courier reporting a gap means it genuinely could not reach the source.

## Cost

The dominant cost of a courier is the payload it pulls into context, not the model — so the lever that matters is the skill's *fetch narrow* rule: request JSON and filter to the asked-for fields (`gh --json`, `jq`, JQL `fields=`), truncate long bodies. Filtering an MR's notes to `id,author.username,body,position.new_path` costs a fraction of piping 40 notes with full diffs.

## Plugin Structure

```
plugins/getter/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   └── courier.md              # Read-only fetch agent (Haiku, mutation tools denied)
└── skills/
    └── getter/
        └── SKILL.md            # Map sources → dispatch couriers → relay
```
