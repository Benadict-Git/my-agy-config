---
name: pr
description: >-
  Open a GitHub pull request for the current branch with gh, Claude Code style. Use when the user asks to create
  a PR / pull request ("/pr", "open a PR", "make a pull request").
---

# Pull Request

1. In parallel, run:
   - `git status` and `git diff` (uncommitted work that may need committing first — ask if unclear)
   - `git rev-parse --abbrev-ref HEAD` and `git status -sb` (does the branch track a remote? ahead/behind?)
   - Find the base branch (`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`), then
     `git log <base>..HEAD --oneline` and `git diff <base>...HEAD --stat`
2. Read ALL commits in the branch, not just the latest, and draft:
   - Title under 70 characters.
   - Body:
     ```
     ## Summary
     - 1-3 bullets on what changed and why

     ## Test plan
     - [ ] checklist of how to verify
     ```
3. If on the default branch, create a new branch first. Push with `git push -u origin <branch>` if needed (the
   user asked for a PR, which authorizes this push; never force-push).
4. Create it with a heredoc body:
   ```bash
   gh pr create --title "..." --body "$(cat <<'EOF'
   ## Summary
   ...
   EOF
   )"
   ```
5. Return the PR URL.
