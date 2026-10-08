---
name: simplify
description: >-
  Clean up recently changed code for reuse, simplicity and efficiency, then apply the fixes. Use when the user says
  "/simplify", "clean this up", "simplify", "tidy the diff". Quality only — for bug hunting use code-review.
---

# Simplify

Scope: the current diff (`git diff` + `git diff --staged`), or the files the user names. Don't touch unrelated code.

Look for, in the changed code only:
- **Reuse**: new code duplicating an existing helper/utility in the repo (`rg` for similar names/logic) → call it.
- **Dead weight**: unused variables/imports/params, unreachable branches, needless wrappers, speculative options,
  error handling for impossible cases, backwards-compat shims nobody needs.
- **Over-abstraction**: a class/interface/factory with one user → inline it. Three similar lines beat an abstraction.
- **Clarity**: convoluted conditionals, deep nesting (use early returns), misleading names, comments that restate
  the code (delete) or are missing where the *why* is non-obvious (add one short line).
- **Efficiency**: repeated work in loops, N+1 queries, reading the same file twice, quadratic scans with an easy fix.
- **Altitude**: logic in the wrong layer (e.g. formatting in data access) when moving it is small and local.

Apply the changes with minimal edits, keep behavior identical, then run the tests/build/linter to prove nothing
broke. Report in a few bullets what you changed (`file:line`) and anything you deliberately left alone.
