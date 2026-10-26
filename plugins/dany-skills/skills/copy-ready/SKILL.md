---
name: copy-ready
description: Put a final draft on Dany's macOS clipboard in the best paste form for its target (Jira, Confluence, Slack, GitLab, email), then show it in a fenced block. Use when Dany asks for something copiable, copy-paste ready, text to paste, on his clipboard, or says he will post a Jira, Slack or GitLab message himself.
---

# Copy ready

Dany pastes, Claude never posts. This skill only changes the **form** of the text, never the words: the wording is already final (voice comes from the voice card in the user's `CLAUDE.md`).

## Steps

1. **Pick the target.** Infer it from context: Jira ticket or comment → `jira`, Confluence page → `jira` (same editor), MR description or comment → `gitlab`, Slack DM or channel → `slack`, anything else → `email`. Ask only when the context names no target. Done when there is one target.
2. **Write the files** to the session scratchpad: `copy.txt` always, `copy.json` (a `slack/texty` delta) for `slack`, `copy.html` for `jira` and `email`. Build both from the same final draft using the form table below. Done when every list, link, code span and emoji in the draft shows up in both files.
3. **Run the helper.**
   - rich: `osascript -l JavaScript <skill-dir>/copy.js <scratchpad>/copy.html <scratchpad>/copy.txt`
   - plain (gitlab): `osascript -l JavaScript <skill-dir>/copy.js --plain <scratchpad>/copy.txt`
   - slack: `slack_pickle.py` then `copy.js --slack` (commands under Mentions)

   Done when it prints `html + plain on clipboard`, `plain on clipboard` or `slack rich text + plain on clipboard`. A non-zero exit means nothing was copied: say so.
4. **Reply** with one line, `On your clipboard as <form> for <target>, paste with Cmd+V`, then the plain-text version in a fenced block. Name each mention and ask Dany to check it became a chip (see Mentions).

## Form per target

| Target | Clipboard | HTML | Plain fallback |
|---|---|---|---|
| `jira` (Jira Cloud, Confluence) | HTML + plain | `<ol>/<ul><li>`, `<code>`, `<a href>`, `<b>` | plain lines, URLs written out |
| `slack` (web in Chrome) | `slack/texty` delta + plain (`--slack` mode, see Mentions) | none | Slack style: `*bold*`, plain URLs, `:shortcodes:` |
| `gitlab` (MR, comments) | plain only | none | GitLab markdown as written |
| `email` / other | HTML + plain | as for `jira` | plain lines, URLs written out |

HTML rules:

- Escape `&`, `<`, `>` in the text before wrapping it in tags.
- Every `1.` `2.` run becomes one real `<ol>`, every `•` / `-` run one `<ul>`. Nested `◦` items go in a `<ul>` inside the parent `<li>`.
- Links are `<a href="url">label</a>` with the id as the label (`PROJ-123`, `!232`).
- Emoji are real characters (🙏 👀 😄), never `:shortcodes:`. Map: `:pray:` 🙏, `:eyes:` 👀, `:smile:` 😄, `:ticket:` 🎫, `:test_tube:` 🧪, `:rocket:` 🚀, `:broom:` 🧹, `:mega:` 📣.
- A plain fragment is enough. No `<html>`, `<head>` or `<meta charset>` needed.

## Mentions

A plain `@Name` tags nobody after a paste. Each target needs its own mention form, built from the person's id on that platform:

| Target | Id to look up | HTML on the clipboard | Plain fallback |
|---|---|---|---|
| `jira` | Atlassian account id (`712020:...`) from `lookupJiraAccountId`, or the `author.accountId` of a comment already fetched | `<span data-mention-id="<accountId>" data-access-level="">@<display name></span>` | `@<display name>` |
| `slack` | member id (`U...`) from the `send-slack` roster, or `slack_search_users` | none, a `slackmention` op in `slack/texty` (below) | `@<display name>` |
| `gitlab` | GitLab username | none (plain only) | `@<username>`, GitLab renders it |

- Jira: the Atlassian editor turns a pasted `span[data-mention-id]` into a real mention node, the same way a mention copied from another Jira comment survives a paste.
- Slack (web in Chrome) ignores HTML for mentions. It reads its own `slack/texty` type: a Quill delta, stored inside Chrome's `org.chromium.web-custom-data` blob. A mention is one op:
  `{"attributes":{"slackmention":{"id":"UXXXXXXXXXX","label":"@Jane Doe","mention":true,"unverified":false}},"insert":"@Jane Doe"}`
  Plain text is `{"insert":"text"}`, the delta ends with `"\n"`. Bold `{"attributes":{"bold":true},...}` and link `{"attributes":{"link":"url"},...}` work (verified by paste).
  Build: write `copy.json` (`{"ops":[...]}`) and `copy.txt`, then
  `python3 -I <skill-dir>/slack_pickle.py <scratchpad>/copy.json <scratchpad>/copy.txt <scratchpad>/copy.bin`
  `osascript -l JavaScript <skill-dir>/copy.js --slack <scratchpad>/copy.bin <scratchpad>/copy.txt`
- To learn a new Slack format, Dany copies a Slack message that has it, then dump `org.chromium.web-custom-data` from the clipboard (`dataForType`, write to a file, decode UTF-16) and read the `slack/texty` delta.
- Never put Slack `<@U...>` or `<url|label>` on the clipboard: that is API-only syntax and a paste shows it as literal text.
- Ids come through a courier (`getter` skill) when they are not already in the conversation. Never guess an id.

After the paste, tell Dany to check each mention turned into a chip. If one did not, he retypes it.

## What was checked

Verified on 2026-10-16 (macOS, Chrome):

- `copy.js` writes `public.html` and `public.utf8-plain-text` in one go; `--plain` writes only the plain type. Read back with `pbpaste` and `NSPasteboard.stringForType(NSPasteboardTypeHTML)`.
- Text with quotes, `$`, backticks and emoji survives, since the script reads the files itself.
- A Cmd+V in a Chrome page delivers both `text/html` and `text/plain` to the page, emoji intact, with or without `<meta charset>`.
- Slack web (Chrome): a built `slack/texty` blob pastes with a real mention chip, bold, a labelled link (`!1143`) and emoji. `slack_pickle.py` also rebuilds a captured Slack blob byte for byte.
- Jira Cloud comment (Chrome): a pasted `span[data-mention-id]` becomes a real mention chip, `<ol>` a numbered list, `<a>` a labelled link, emoji intact.

Assumed, not tested in the real apps (a test paste there was out of scope):

- Confluence turns the pasted `<ol>`, `<ul>`, `<code>`, `<a>` into real nodes (same editor as Jira, likely fine).
- `<code>` in a Jira paste.
- Slack's composer keeps bold, links and lists from pasted HTML, and turns pasted `:shortcodes:` into emoji.
- Slack desktop app reads the same blob (it runs on Chromium).

If one of these turns out wrong in use, fix the table and move the line up to verified.
