---
name: verify
description: >-
  Launch and drive the actual app/program to prove a change works (not just tests). Use when the user says "run
  it", "does it work", "/verify", "screenshot it", or after finishing a feature, UI, config or desktop change.
---

# Verify for real

1. **Find how to run it.** Check the project's AGENTS.md/README, `package.json` scripts, `Makefile`, `justfile`,
   `pyproject.toml`, `Cargo.toml`. Prefer the project's own dev command.
2. **Pick the method by type:**
   - **CLI / script**: run it with realistic args, including one edge case (empty input, bad path). Check exit code.
   - **Server / API**: start it as a background task (`manage_task`), wait until the port answers
     (`curl -sf localhost:PORT/health` in a short retry loop), hit the changed endpoint, read the response and the
     server log, then stop the task.
   - **Web UI**: start the dev server, then use the browser subagent to open the page, exercise the golden path
     and one edge case, check the console for errors, and take a screenshot.
   - **Desktop / Omarchy / Hyprland / QML**: reload the relevant piece (`omarchy restart shell`,
     `hyprctl reload`, `omarchy theme refresh` — see the `omarchy` skill), then `grim /tmp/verify.png` (or
     `grim -g "$(slurp)"`) and `view_file` the image. Never lock the real screen to test a lock screen — use the
     preview commands.
   - **Terminal art / TUI**: measure the real grid (`stty size`, or the window's size) and render to an image
     rather than trusting a text dump.
3. **Compare** against what was asked (and any reference images the user gave). Look for regressions in
   neighbouring features.
4. **Report** in 1-3 sentences: what you ran, what you saw, pass/fail. If something can't be verified here, say
   exactly what and why. Clean up background processes and temp files you created.
