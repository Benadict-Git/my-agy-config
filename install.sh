#!/usr/bin/env bash
# Install this agy setup into ~/.gemini. Safe to re-run: existing files are backed up as *.bak-<date>,
# settings are merged (your trusted folders, login and other keys are kept), memory is never overwritten.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
G="${HOME}/.gemini"
STAMP="$(date +%Y%m%d-%H%M%S)"
command -v jq >/dev/null || { echo "jq is required" >&2; exit 1; }

backup() { [ -e "$1" ] && cp -a "$1" "$1.bak-$STAMP" && echo "  backed up $1"; true; }
rehome() { sed -i "s#/home/benny#${HOME}#g" "$@"; }

mkdir -p "$G/config/plugins" "$G/antigravity-cli" "$G/memory"

echo "plugin: claude-mode"
if [ -d "$G/config/plugins/claude-mode" ]; then
  mkdir -p "$G/backups"
  mv "$G/config/plugins/claude-mode" "$G/backups/claude-mode-$STAMP"
  echo "  old copy moved to $G/backups/claude-mode-$STAMP"
fi
cp -r "$SRC/config/plugins/claude-mode" "$G/config/plugins/"
rehome "$G/config/plugins/claude-mode/rules/AGENTS.md"
chmod +x "$G/config/plugins/claude-mode/hooks/guard.py"

echo "skills.json + mcp_config.json"
for f in skills.json mcp_config.json; do
  backup "$G/config/$f"
  cp "$SRC/config/$f" "$G/config/$f"
  rehome "$G/config/$f"
done

echo "config.json (merge plugin switches + user settings)"
if [ -f "$G/config/config.json" ]; then
  backup "$G/config/config.json"
  jq -s '.[0] * .[1]' "$G/config/config.json" "$SRC/config/config.json" > "$G/config/config.json.new"
  mv "$G/config/config.json.new" "$G/config/config.json"
else
  cp "$SRC/config/config.json" "$G/config/config.json"
fi

echo "CLI settings (merge)"
S="$G/antigravity-cli/settings.json"
if [ -f "$S" ]; then
  backup "$S"
  jq -s '.[0] * .[1]' "$S" "$SRC/cli/settings.json" > "$S.new" && mv "$S.new" "$S"
else
  cp "$SRC/cli/settings.json" "$S"
fi

echo "memory (only files that don't exist yet)"
for f in "$SRC"/memory/*.md; do
  b="$(basename "$f")"
  if [ "$b" = MEMORY.md ] && [ -f "$G/memory/MEMORY.md" ]; then
    # append index lines that are missing
    while IFS= read -r line; do
      grep -qxF -- "$line" "$G/memory/MEMORY.md" || echo "$line" >> "$G/memory/MEMORY.md"
    done < "$f"
  elif [ ! -e "$G/memory/$b" ]; then
    cp "$f" "$G/memory/$b"
  fi
done

echo "global skills (markitdown, ui-ux-pro-max and design skills)"
mkdir -p "$G/config/skills" "$HOME/.agents/skills"
if [ -d "$SRC/skills" ]; then
  for s in "$SRC"/skills/*; do
    [ -d "$s" ] || continue
    sname="$(basename "$s")"
    if [ ! -d "$G/config/skills/$sname" ]; then
      cp -r "$s" "$G/config/skills/$sname"
      echo "  installed skill $sname"
    fi
    ln -sfn "$G/config/skills/$sname" "$HOME/.agents/skills/$sname"
  done
fi

cat <<'EOF'

Done. Remaining manual steps:
  1. Install the marketplace plugins by asking agy:
       "Install chrome-devtools-plugin, modern-web-guidance-plugin and science from the Build with Google plugins"
  2. Chrome MCP uses /usr/bin/chromium - edit ~/.gemini/config/mcp_config.json if your browser path differs.
  3. Check:  agy plugin validate ~/.gemini/config/plugins/claude-mode
EOF
