---
name: code-review
description: >-
  Review the current diff, a branch, a PR number, or given files for real correctness bugs, Claude Code style.
  Use when the user asks to "review", "/code-review", "check my changes", "find bugs in this diff". Add --fix to
  apply the findings.
---

# Code Review

## Scope
- No target: review uncommitted work (`git diff` + `git diff --staged`), or if clean, the branch vs its base
  (`git diff <base>...HEAD`).
- PR number: `gh pr diff <n>` and `gh pr view <n>`.
- Paths: those files.

## Method
1. Read the diff, then read the **surrounding code** of every changed hunk with `view_file` (callers, callees,
   types, tests). A diff alone hides most bugs.
2. Hunt for defects that would actually break something: wrong logic/conditions, off-by-one, null/undefined
   paths, unhandled errors at real boundaries, race conditions, resource leaks, broken callers of a changed
   signature, security holes (injection, XSS, path traversal, secrets), data loss, wrong API usage.
3. **Verify each candidate** before reporting: trace the concrete inputs/state that trigger it. If you can, run the
   tests or a quick script to prove it. Drop anything you can't substantiate. Style nits are not findings.
4. Optionally note clear simplification/reuse wins, labelled separately and kept few.

## Report
Ranked most severe first, each as:

```
N. path/to/file.ext:LINE — one-sentence defect
   Failure: concrete inputs/state → wrong output/crash
   Fix: the minimal change
```

If nothing survives verification, say so plainly. Don't pad the list.

## --fix
Apply the fixes for verified findings with minimal edits, run the tests/build, and report which were fixed and
which were skipped (and why).
