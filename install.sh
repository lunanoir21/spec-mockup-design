#!/usr/bin/env bash
# One-line install: curl -fsSL https://raw.githubusercontent.com/lunanoir21/spec-mockup-design/main/install.sh | bash
set -euo pipefail
DEST="${SKILLS_HOME:-$HOME/.agents/skills}/spec-mockup-design"
mkdir -p "$(dirname "$DEST")"
if [ -d "$DEST/.git" ]; then git -C "$DEST" pull --ff-only; else git clone https://github.com/lunanoir21/spec-mockup-design "$DEST"; fi
bash "$DEST/scripts/install-everywhere.sh"
