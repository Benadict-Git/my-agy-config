---
name: commit
description: >-
  Create a git commit safely, Claude Code style. Use only when the user explicitly asks to commit ("commit this",
  "/commit", "make a commit"). Never commit on your own initiative.
---

# Commit

1. In parallel, run:
   - `git status` (never `-uall`)
   - `git diff` and `git diff --staged`
   - `git log -8 --oneline` to match the repository's message style
2. Review what will be committed:
   - Leave out files that likely contain secrets (`.env`, `*credentials*`, keys, tokens). If the user asked to
     commit one, warn them first.
   - Leave out large binaries and build output unless clearly intended.
3. Draft the message: 1-2 sentences focused on **why**, using the right verb ("add" = new feature, "update" =
   enhancement, "fix" = bug fix, "refactor", "docs", "test"). Follow the repo's existing style.
4. Stage files **by name** (not `git add -A` / `git add .`), then commit with a heredoc:
   ```bash
   git add path/one path/two
   git commit -m "$(cat <<'EOF'
   Short summary of why

   Optional detail line.
   EOF
   )"
   git status
   ```
5. If a pre-commit hook fails: the commit did NOT happen. Fix the underlying issue, re-stage, and create a NEW
   commit. Never `--amend` (that would rewrite the previous commit) and never `--no-verify`.

Rules: never change git config, never use interactive flags (`-i`), never push unless the user asks, never create
an empty commit when there are no changes. Report the commit hash and message in one line.
