---
name: plan
description: >-
  Plan a non-trivial change before writing code, Claude Code plan-mode style. Use when the user says "plan",
  "/plan", "make a plan", "how should we approach", or when a task touches several files, has an unclear approach,
  or involves architectural choices. Read-only until the user approves the plan.
---

# Plan Mode

While planning you are **read-only**: no edits, no installs, no commits, no config changes. The only file you may
write is the plan file. (Tip for the user: `agy --mode plan` starts a session in Antigravity's native plan mode.)

## 1. Understand
- Restate the goal to yourself in one sentence. Identify what "done" looks like.
- Explore the relevant code with `rg`, `rg --files`, `fd` and `view_file`, running independent searches in
  parallel. Find existing functions, utilities and patterns to reuse — prefer them over new code.
- For wide or uncertain scope, you may `invoke_subagent` (research) with a precise brief; for known files just read
  them yourself.

## 2. Resolve real questions
Use `ask_question` only for decisions that are genuinely the user's: ambiguous requirements, competing approaches
with real tradeoffs, risky changes. Put your recommended option first and label it "(Recommended)". Don't ask about
things you can settle from the code or with a sensible default. Don't ask "is the plan OK?" here.

## 3. Write the plan
Write it to `./.agents/plans/<short-slug>.md` (create the directory if needed; tell the user the path). Keep it
scannable:

```
# <Title>

## Context
Why this change: the problem, what prompted it, the intended outcome.

## Approach
The recommended approach only (not a survey of alternatives). Numbered steps.
Files to change — for a pattern repeated across many files, describe it once and list a few examples.
Existing code to reuse, with paths (path/to/file.ts:42).

## Verification
How to prove it works end to end: commands to run, tests, what to look at in the real app.
```

## 4. Stop and ask for approval
Show a short summary of the plan and ask the user to approve or adjust it. Do not start implementing until they
approve. After approval, implement step by step, verify as the plan says, and report in 1-2 sentences.
