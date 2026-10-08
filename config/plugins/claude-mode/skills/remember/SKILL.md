---
name: remember
description: >-
  Save, update, or forget a persistent memory about the user, their feedback, projects, or external references in
  ~/.gemini/memory/. Use when the user says "remember", "/remember", "don't forget", "forget that", or when they
  correct your approach or confirm a non-obvious approach worked and it will matter in future sessions.
---

# Remember

Memory lives in `~/.gemini/memory/`: one Markdown file per memory plus the index `MEMORY.md` (which is loaded into
every session automatically).

## Decide
- Pick the type: `user` (who they are, expertise, preferences), `feedback` (a rule for how to work — from a
  correction OR a confirmed approach), `project` (ongoing work, decisions, deadlines, why), `reference` (where
  things live in external systems).
- Don't save code structure, file paths derivable from the repo, git history, fix recipes, ephemeral task state,
  or secrets. If asked to save something like an activity list, save only what was surprising or non-obvious.
- First check for an existing memory on the topic (`rg -il "<keyword>" ~/.gemini/memory`). Update it instead of
  creating a duplicate.
- Convert relative dates to absolute (`date +%F`).

## Write
`~/.gemini/memory/<type>_<topic>.md`:

```markdown
---
name: short-kebab-slug
description: one-line summary, specific enough to judge relevance later
metadata:
  type: user | feedback | project | reference
---

The rule or fact.

**Why:** the reason (often a past incident or strong preference).
**How to apply:** when/where this kicks in. Related: [[other-memory-name]]
```

Then add or update one line in `~/.gemini/memory/MEMORY.md` (keep it under ~150 characters, no frontmatter):

```
- [Title](file.md) — one-line hook
```

## Forget
Delete the file and remove its line from `MEMORY.md`. Confirm to the user in one sentence.
