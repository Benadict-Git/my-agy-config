---
name: ironman-screensaver-pipeline
description: How the user's Omarchy Iron Man theme and animated, coloured screensaver are wired (foot shim, ttfx wrapper, generator, custom animations)
metadata:
  type: project
---

The user runs a custom Omarchy theme `iron-man` (~/.config/omarchy/themes/iron-man, applied 2026-09-27) with an animated, realistically lit Iron Man helmet screensaver. The pieces:

- `~/.local/bin/foot` — shim: font size 6 only for the `org.omarchy.screensaver` window (canvas 60x240 on the 1920x1080 @1.6 panel; stock 18 gives 20x83). Env `OMARCHY_SCREENSAVER_FONT_SIZE` overrides.
- `~/.local/bin/ttfx` — user wrapper (runs as comm `ttfx`, so omarchy-screensaver keeps waiting on it): picks a line from `~/.config/omarchy/branding/screensaver-effects.conf` (all 37 ttfx effects, Iron Man-themed, + `@powerup/@faceplate/@nanotech` custom anims; short hold), adds `--existing-color-handling dynamic`, then holds the finished helmet with `@pulse`/`@glint` idle anims. `play()` centres frames with ttfx's own rule: top=(rows-h)//2, left=(cols+1)//2-w//2, and parks the cursor on the bottom row for `--reuse-canvas`.
- `~/.config/omarchy/branding/ironman-art/generate.py` — rebuilds `screensaver.txt` (82x54 quadrant blocks, even top-to-bottom gradients per region, `STYLE = "even"`; "lit" metal shading still available), plain `about.txt` (no escapes: fastfetch `file` logo + `wc -L` sizing), and `anim/*.frames` (diff-encoded, ESC7/ESC8 relative). Shape from `outline.jpg`; palette follows `colour.jpg` but deeper/metallic (user said flat colours were "too bright", then asked for gradients "evenly" like the stock OMARCHY wordmark).

Current state (2026-09-28, latest): filled helmet, `ART = "filled"`, `STYLE = "real"` (studio-lit candy-apple clear-coat red + gold metal, `REAL` params in generate.py; user called flat/even colouring "toy or cartoon"); conf = the 46-entry themed list (all 37 ttfx effects + custom anims). Outline-only and stock-@random variants saved as *.v9-outline / screensaver-effects.conf.v9-stock.

**Why:** many rejected iterations; this is the version built from the user's own two references.
**How to apply:** tweak via generate.py and rerun, never hand-edit art. When testing: pyte's DECRC pops (foot's doesn't) — patch it; `omarchy launch screensaver` bails if *any* cmdline contains the class name, so run test scripts from files; new windows report 24x80 then in-between sizes before fullscreen. See [[verify-against-user-references]].
