---
name: agy-setup
description: How this Antigravity CLI setup is customized — claude-mode plugin, guard hook, skill sources, memory location
metadata:
  type: reference
---

agy is the user's primary, all-round AI tool (since 2026-09-29) for coding, system config, research, writing and
general questions. Customization lives in the global plugin `~/.gemini/config/plugins/claude-mode/`:
`rules/AGENTS.md` (operating rules; includes this memory index), `hooks/guard.py` (strict mode: deterministic
PreToolUse guard on every tool; risky actions are denied until the user's latest message says "yes"/"go ahead" or
contains the exact command — one approval per action; catastrophic ones never run; scripts are scanned before running;
log at `~/.cache/agy-guard/decisions.jsonl`; the user chose this over a slower model-based reviewer), and skills (plan, commit, pr,
code-review, security-review, simplify, verify, research, remember, init). `~/.gemini/config/skills.json` also loads
Omarchy's shipped skills from `/usr/share/omarchy/default/agents/skills` (paths there must be absolute; `~` silently
fails).

Marketplace plugins enabled by default (2026-09-29): `chrome-devtools-plugin` (browser automation/debugging; its
MCP server `chrome-devtools` is registered in `~/.gemini/config/mcp_config.json` using `/usr/bin/chromium`, since
Google Chrome isn't installed), `modern-web-guidance-plugin` (Next.js/web best practices), `science` (40 research and
analysis skills for the user's Kaggle/ML projects). GitHub goes through the logged-in `gh` CLI, not a plugin.

This memory folder (`~/.gemini/memory/`) belongs to agy alone — the user wants it kept separate from any other
tool's memory.

**How to apply:** when the user asks to change how agy behaves, edit the plugin files above (not the built-in
skills); everything toggles with `agy plugin disable|enable claude-mode`.
