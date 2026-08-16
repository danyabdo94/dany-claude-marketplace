# dany-claude-marketplace

A Claude Code plugin marketplace.

## Structure

```
dany-claude-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # Catalog: lists every plugin + where to find it
├── plugins/
│   └── getter/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       ├── README.md
│       ├── agents/
│       │   └── courier.md              # Read-only fetch agent (Haiku, mutation tools denied)
│       └── skills/
│           ├── getter/
│           │   └── SKILL.md            # Map sources → dispatch couriers → relay
│           └── getter-handoff/
│               └── SKILL.md            # Gather + package into a handoff doc
└── README.md
```

> **Note:** `skills/getter-handoff/SKILL.md` references a sibling `../handoff/SKILL.md`
> skill (`skills/handoff/SKILL.md`) that isn't included yet — add it under
> `plugins/getter/skills/handoff/` for the handoff step to resolve, or point
> `getter-handoff` at wherever that skill actually lives.

## Try it locally

From inside Claude Code:

```
/plugin marketplace add /path/to/dany-claude-marketplace
/plugin install getter@dany-claude-marketplace
```

Then either type `/getter` or just ask something like:

```
what's the status of IN-1915 and who's reviewing it
```

## Publish it

1. Push this folder to `danyabdo94/dany-claude-marketplace` on GitHub.
2. Users add it with:
   ```
   /plugin marketplace add danyabdo94/dany-claude-marketplace
   /plugin install getter@dany-claude-marketplace
   ```
3. Push updates anytime — users refresh with `/plugin marketplace update`.

## Adding more plugins

1. Create a new folder under `plugins/<plugin-name>/`.
2. Add a `.claude-plugin/plugin.json` inside it.
3. Add any of `commands/`, `agents/`, `skills/`, `hooks/`, `.mcp.json` as needed.
4. Add an entry for it in the top-level `.claude-plugin/marketplace.json`
   `plugins` array, pointing `source` at the folder (e.g. `./plugins/<plugin-name>`).

## Notes

- Relative `source` paths in `marketplace.json` only resolve when the
  marketplace is added via a git host (GitHub/GitLab/git URL). If you
  distribute `marketplace.json` via a raw/direct URL instead, use full
  git URLs or npm sources per plugin rather than relative paths.
- Full docs: https://code.claude.com/docs/en/plugin-marketplaces
