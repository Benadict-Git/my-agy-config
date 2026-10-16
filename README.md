# my-agy-config

My [Antigravity CLI](https://antigravity.google) (`agy`) setup: Claude Code-style behaviour on Gemini, a strict
tool guard, workflow skills, and the plugins I run by default.

## What's inside

| Path | Installs to | What it is |
| --- | --- | --- |
| `config/plugins/claude-mode/` | `~/.gemini/config/plugins/` | The main plugin: rules, strict guard hook, 10 skills |
| `config/skills.json` | `~/.gemini/config/` | Also loads Omarchy's shipped skills from `/usr/share/omarchy/default/agents/skills` |
| `config/mcp_config.json` | `~/.gemini/config/` | `chrome-devtools` MCP server (Chromium) |
| `config/config.json` | `~/.gemini/config/` | Which plugins are enabled (merged, hostname removed) |
| `cli/settings.json` | `~/.gemini/antigravity-cli/` | Theme, model, `always-proceed` (merged; trusted folders removed) |
| `skills/` | `~/.gemini/config/skills/` | Global skills: `markitdown` file reader, `ui-ux-pro-max`, design suite |
| `memory/` | `~/.gemini/memory/` | agy's own memory notes, loaded into every session |

### The `claude-mode` plugin
- **`rules/AGENTS.md`**: operating manual: understand → act → verify, concise updates, git safety, task routing
  (code / questions / research / writing / desktop), persistent memory, strict mode, stay-focused rules.
- **`hooks/guard.py`**: deterministic PreToolUse guard (no model calls, no delay) that makes `always-proceed` safe:
  - allowed instantly: reading, searching, builds/tests, edits inside the project, `~/.config` and `/tmp`
  - blocked until the user's latest message says "yes" (one approval per action): recursive/wildcard deletes,
    `git push`/reset/rewrite, `sudo`/package installs, downloaded or inline code, data uploads, secrets, agent's own
    settings, other apps' data; script files and inline code are scanned before they run
  - never run: deleting `/` or `~`, formatting disks, raw device writes, fork bombs
  - fails closed if the guard itself errors; decisions logged to `~/.cache/agy-guard/decisions.jsonl`
- **Skills**: `plan`, `commit`, `pr`, `code-review`, `security-review`, `simplify`, `verify`, `research`,
  `remember`, `init`.

## Install

```bash
git clone https://github.com/<you>/my-agy-config && cd my-agy-config
./install.sh
```

The script backs up what it replaces (`*.bak-<timestamp>`), merges settings instead of overwriting them, and never
overwrites existing memory files. It rewrites `/home/benny` paths to your `$HOME`. Requires `jq` and `python3`.

## Not included (on purpose)
- **Login/session data**: `oauth_creds.json`, `google_accounts.json`, conversations, logs, trusted-folder lists.
- **Marketplace plugins** (installed from Google, not copied here): `chrome-devtools-plugin`,
  `modern-web-guidance-plugin`, `science`. Ask agy: *"Install chrome-devtools-plugin, modern-web-guidance-plugin and
  science"*.
- **Anthropic's `docx`/`pdf`/`pptx`/`xlsx` skills**: proprietary ("all rights reserved"), so not redistributed.
- **herdr hook** (`~/.gemini/config/hooks.json`): managed by herdr itself.

## Manage
```bash
agy plugin validate ~/.gemini/config/plugins/claude-mode
agy plugin disable claude-mode   # turns the whole bundle off (rules, guard, skills)
agy plugin enable claude-mode
```
