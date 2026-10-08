---
name: init
description: >-
  Generate or improve a project AGENTS.md (the project rules file Antigravity loads every session), like Claude
  Code's /init. Use when the user says "/init", "create an AGENTS.md", or "document this repo for the agent".
---

# Init: write the project's AGENTS.md

Goal: a short file that makes a future agent productive in this repo immediately. Only include what can't be
guessed quickly from the code.

1. Explore in parallel: `rg --files | head -200`, README, package/build manifests (`package.json`, `pyproject.toml`,
   `Cargo.toml`, `Makefile`, `go.mod`...), CI config, existing `AGENTS.md`/`GEMINI.md`/`CLAUDE.md`/`.cursorrules`.
2. Find the real commands: build, lint, typecheck, test, **run a single test**, dev server.
3. Understand the big-picture architecture that needs several files to see (data flow, main modules, where entry
   points live).
4. Write `AGENTS.md` at the repo root (if one exists, improve it rather than replace; if a `CLAUDE.md` exists, fold
   its content in):

```markdown
# AGENTS.md

## Commands
- Build: ...
- Test all: ... / single test: ...
- Lint / typecheck: ...

## Architecture
Short explanation of the high-level structure and how the pieces connect.

## Conventions
Only non-obvious rules (e.g. "all DB access goes through src/db/repo.ts", "never edit generated/*").
```

Don't list every file, don't include generic advice ("write tests", "use good names"), don't invent sections you
can't back with evidence. Keep it under ~150 lines. Report the path and a one-line summary.
