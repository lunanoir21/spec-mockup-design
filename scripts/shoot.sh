#!/usr/bin/env bash
# Headless screenshots of every board of a canvas made by new-canvas.py.
#   shoot.sh design/topic-mockup.html [outdir]    -> outdir/<board>.desktop.png, .phone.png, _all.desktop.png
# Uses chromium/chrome headless: no window ever appears on the user's desktop.
set -euo pipefail
f=${1:?usage: shoot.sh canvas.html [outdir]}
out=${2:-$(dirname "$f")/shots}
mkdir -p "$out"
bin=$(command -v google-chrome-stable || command -v google-chrome || command -v chromium || command -v chromium-browser || true)
[ -n "$bin" ] || { echo "no chromium/chrome found; open the file manually and check by eye" >&2; exit 2; }
abs=$(realpath "$f")
prof=$(mktemp -d)
trap 'rm -rf "$prof"' EXIT
run() { # url w h png
  timeout 60 "$bin" --headless=new --disable-gpu --no-sandbox --disable-dev-shm-usage --hide-scrollbars \
    --user-data-dir="$prof" --force-device-scale-factor=1 --virtual-time-budget=4000 \
    --window-size="$2,$3" --screenshot="$4" "$1" >/dev/null 2>&1 || echo "failed: $4" >&2
}
ids=$(grep -oE '<(section|div|article)[^>]*data-board="[^"]+"' "$f" | grep -oE 'data-board="[^"]+"' | sed 's/data-board="//;s/"//' | awk '!s[$0]++')
[ -n "$ids" ] || { echo "no data-board attributes found" >&2; exit 2; }
run "file://$abs" 1600 1000 "$out/_all.desktop.png"
for id in $ids; do
  run "file://$abs?only=$id" 1600 900 "$out/$id.desktop.png"
  run "file://$abs?only=$id" 390 844 "$out/$id.phone.png"
done
ls -1 "$out"
echo "open these PNGs and read them; then check clipping, contrast, fonts, empty boards."
