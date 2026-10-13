#!/usr/bin/env python3
"""Make any HTML mockup a pan/zoom infinite canvas (the portable version of Claude's Design canvas).

  canvasify.py design/mockup.html [--out other.html] [--remove]

Every board must carry data-board="<id>" (new-canvas.py output already does). The runtime is injected
inline (idempotent: re-running updates it in place). Features: drag/scroll to pan, ctrl+wheel or pinch to
zoom, fit-all, focus a board (expand button, F), board list, per-board HTML download, `?only=<id>` for
screenshots, `?flat=1` for the classic scroll page. Stdlib only.
"""
import argparse, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
OPEN, CLOSE = "<!-- cv-runtime -->", "<!-- /cv-runtime -->"

def inject(src, js):
    block = f"{OPEN}\n<script>\n{js}\n</script>\n{CLOSE}"
    if OPEN in src:
        return re.sub(re.escape(OPEN) + r".*?" + re.escape(CLOSE), lambda m: block, src, flags=re.S)
    i = src.lower().rfind("</body>")
    return src[:i] + block + "\n" + src[i:] if i >= 0 else src + "\n" + block + "\n"

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--out"); ap.add_argument("--remove", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.file): sys.exit(f"error: file not found: {a.file}")
    src = open(a.file, errors="ignore").read()
    if not re.search(r'data-board\s*=', src): sys.exit("error: no data-board attributes found; mark every board with data-board=\"<id>\" first")
    if a.remove:
        out = re.sub(re.escape(OPEN) + r".*?" + re.escape(CLOSE) + r"\n?", "", src, flags=re.S)
    else:
        js = open(os.path.join(HERE, "canvas-runtime.js")).read()
        out = inject(src, js)
    dest = a.out or a.file
    open(dest, "w").write(out)
    n = len(re.findall(r'<(?:section|div|article)[^>]*data-board="', out))
    print(f"{'removed runtime from' if a.remove else 'canvas runtime injected into'} {dest} ({n} boards)")

main()
