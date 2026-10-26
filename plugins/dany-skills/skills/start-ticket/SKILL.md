---
name: start-ticket
description: Create a Jira ticket and a matching feature branch in one flow, inheriting metadata from a recent template ticket. The ticket body itself comes from the `jira-ticket` skill. Use when user wants to start a new ticket, create a Jira ticket plus branch, kick off work on a tracked issue, or invokes /start-ticket.
---

# start-ticket

Create a Jira ticket and a matching feature branch in one flow.

This skill owns the **mechanics**: Jira context, template metadata, the branch. The **title, description, QA notes and field choices come from `jira-ticket`**: load it for the body instead of inventing a shape here.

## Workflow

1. **Discover Jira context** (`cloudId`, project key):
   - Read the project's `CLAUDE.md` — look for ticket prefixes and branch conventions like `feature/PROJ-####_*`.
   - List cloudIds via `mcp__claude_ai_Atlassian_Rovo__getAccessibleAtlassianResources`: if exactly one, use it, if multiple, ask.
   - If the project key is still ambiguous, ask the user.

2. **Discover the branch-naming convention**:
   - Check `CLAUDE.md` first — many projects document it explicitly.
   - Otherwise inspect recent branches: `git log --all --format='%D' | head -50`. Look for a dominant `feature/<KEY>-####_<slug>` shape.
   - If still unclear, ask the user for the template.

3. **Find a template ticket** for metadata inheritance:
   - Query: `project = <KEY> AND reporter = currentUser() ORDER BY created DESC` via `searchJiraIssuesUsingJql`. Take the most recent.
   - Read full metadata with `getJiraIssue` (`fields: ["summary","issuetype","priority","labels","assignee","components","description"]`).
   - **Inherit**: assignee, priority, components.
   - **Don't inherit**: `labels` (almost always ticket-specific, e.g. epic-followup labels), `fixVersions` (release information, never set by default), the description content, or its structure. The structure comes from `jira-ticket`.

4. **Confirm the plan** with a single `AskUserQuestion` covering:
   - Ticket type (Story / Bug / Task — default to whatever the user implied)
   - Whether to copy template metadata or go minimal
   - Branch base (current branch / `origin/<current>` / a different ref)

5. **Create the ticket** via `mcp__claude_ai_Atlassian_Rovo__createJiraIssue`:
   - Required: `cloudId`, `projectKey`, `issueTypeName`, `summary`, `description` (markdown), `assignee_account_id`.
   - Priority via `additional_fields: {"priority": {"name": "<name>"}}`.
   - Title, description and QA notes come from `jira-ticket`: run its steps first, flavor pass included, and show Dany the draft before creating.
   - Pass the QA scenarios as `<qa-field>` (QA Testing Notes) in `additional_fields`. Plain text, no markdown.
   - Never set `fixVersions` or `<target-release-field>` (Target release estimate) unless Dany asks for them by name.
   - **Wait for the response and read the actual issue key** — never fabricate it.

6. **Create the branch**:
   - Slug the *ticket summary* into kebab-case (~50 chars max, lowercase, strip articles).
   - `git checkout -b <convention>_<slug>` from the chosen base.
   - Uncommitted changes carry over automatically — that's intentional. Don't stash, don't commit.

7. **Report back**: ticket URL, branch name, and a one-line status of the working tree.

## Anti-patterns

- Don't create the branch before the ticket — orphan branches if Jira fails.
- Don't push, commit, or stash anything — leave the tree as-is.
- Don't inherit `labels` from the template — they're almost always ticket-specific.
- Don't fabricate a ticket key — always read it from the create response.
- Don't slug from the user's free-text prompt: slug from the final ticket summary so branch and ticket stay aligned.
- Don't write the description here. If you are choosing section headings, you skipped `jira-ticket`.
- Don't set `fixVersions`. Release information is out by decision.
