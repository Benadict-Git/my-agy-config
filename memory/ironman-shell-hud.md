---
name: ironman-shell-hud
description: Iron Man restyle of the Omarchy shell (bar, battery, network, agents, lock, popups) — where each change lives and how to revert
metadata:
  type: project
---

2026-09-28: user asked for the whole desktop to feel Iron Man. Done without touching /usr/share/omarchy:

- Theme surface overrides in `~/.config/omarchy/themes/iron-man/shell.<section>.toml` (bar, controls, popups, tooltip, notifications, launcher, menu, lock, polkit) — merged into the generated shell.toml; apply with `omarchy theme refresh` (keeps wallpaper).
- Cloned plugins (via `omarchy plugin clone`) in `~/.config/omarchy/plugins/`: `benny.menu` (arc-reactor menu button — bar-widget ONLY since 2026-09-28; see below), `benny.workspaces` (gold numbers, focused ws in a lit ring), `benny.power` (battery icon reverted to the stock glyph on 2026-09-28 at user request; clone kept only for panel readability tweaks), `benny.network` (icon in bar gold, red when disconnected), `benny.lock` (reactor + J.A.R.V.I.S. label + crimson tint; stock copy at LockView.qml.stock). Each has its own `ArcReactor.qml` Canvas component — avoid canvas shadowBlur (clips to a visible square at bar size).
- `benny.agents` (user's own plugin) edited: arc-blue icon, blue→gold meters; pre-edit copy at `~/.config/omarchy/plugins-backup-benny.agents`.
- Bar made opaque (`omarchy bar transparent false`); shell.json backup `shell.json.bak.ironman`.

Readability fix (user: text in panels "blended with the background", wants clear but not pure white): all shell surfaces opaque (alpha 1.0, bg #07080b), bar text champagne #ffe4b0, panel text #fbecd2; in the benny.* clones faded labels raised to opacity 0.85, Qt.darker factors 1.4-1.5 -> 1.15, PanelSectionHeader forced to gold #e8c07a. Stock panels (audio, bluetooth, monitor, clock) still use stock dimming.

**How to apply:** preview the lock safely with `omarchy-shell lock preview` / `hidePreview` — never actually lock to test. Revert a widget with `omarchy plugin disable benny.<x>` + `omarchy plugin enable omarchy.<x>`. Related: [[ironman-screensaver-pipeline]].

Boot unlock screen (Plymouth, LUKS prompt): Iron Man arc-reactor theme in `~/.config/omarchy/branding/plymouth-ironman/` (theme/, source/ generators, install.sh). User runs `sudo bash .../install.sh` (`--undo` restores omarchy). On this machine rebuild MUST be `limine-mkinitcpio` (Omarchy's own sequence), not `plymouth-set-default-theme -R` (plain mkinitcpio -P; no presets here). Password logic copied verbatim from omarchy.script.

Apps-menu fix (2026-09-28, user: "why no apps are showing"): a third-party (cloned) *menu*-kind plugin gets `shell.appLibrary == null` from the scoped PluginShellApi, so Menu → Apps showed "Nothing here yet". Fix: benny.menu manifest cut to kinds ["bar-widget"] with no `omarchy.clonedFrom` (else resolveEnabledId still redirects omarchy.menu → benny.menu), and omarchy.menu removed from shell.json `disabledPlugins`. Backups: `benny.menu/manifest.json.bak.appsfix`, `shell.json.bak.appsfix`. Don't re-clone omarchy.menu for looks — menu styling lives in `shell.menu.toml`/`shell.launcher.toml`. Plugin console.warn doesn't reach logs and keepLoaded menu edits need `omarchy restart shell`.
