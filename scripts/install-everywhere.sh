#!/usr/bin/env bash
# Link this skill into every AI tool's skills folder found on the machine. Idempotent; never overwrites or deletes.
#   install-everywhere.sh [--dry-run]
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NAME="$(basename "$SRC")"
dry=0; [ "${1:-}" = "--dry-run" ] && dry=1
dirs=(
  "$HOME/.claude/skills" "$HOME/.codex/skills" "$HOME/.config/opencode/skills" "$HOME/.gemini/skills" "$HOME/.gemini/config/skills"
  "$HOME/.cursor/skills" "$HOME/.kiro/skills" "$HOME/.qwen/skills" "$HOME/.zcode/skills" "$HOME/.pi/skills" "$HOME/.pi/agent/skills"
  "$HOME/.qoder/skills" "$HOME/.grok/skills" "$HOME/.hermes/skills" "$HOME/.jcode/skills"
)
for d in "${dirs[@]}"; do
  [ -d "$d" ] || continue
  t="$d/$NAME"
  if [ -e "$t" ] || [ -L "$t" ]; then
    [ "$(readlink -f "$t")" = "$SRC" ] && echo "ok       $t" || echo "SKIPPED  $t exists and points elsewhere (left untouched)"
  elif [ $dry = 1 ]; then echo "would link $t"
  else ln -s "$SRC" "$t" && echo "linked   $t"; fi
done
echo "Source of truth: $SRC  (edit only here; all links follow)"
