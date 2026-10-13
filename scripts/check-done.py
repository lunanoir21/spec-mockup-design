#!/usr/bin/env python3
"""Delivery receipt. Run LAST; paste its output into your final message.
Verifies the deliverables really exist and re-runs the gates, so a report cannot claim steps that
did not happen.

  check-done.py design/<topic>-mockup.html [--spec design/spec.md] [--palette design/palette.css]
Exit 0 only if canvas exists, has >= 3 boards, slop score >= 70, screenshots exist and are non-empty.
"""
import argparse, glob, json, os, re, subprocess, sys
a = argparse.ArgumentParser(); a.add_argument("canvas"); a.add_argument("--spec"); a.add_argument("--palette"); a.add_argument("--shots")
o = a.parse_args(); here = os.path.dirname(os.path.abspath(__file__)); ok = True
def line(flag, msg):
    global ok
    if flag is False: ok = False
    print(("[ok]   " if flag else "[FAIL] " if flag is False else "[note] ") + msg)
if not os.path.isfile(o.canvas) or os.path.getsize(o.canvas) < 1500:
    line(False, f"canvas missing or empty: {o.canvas}"); print("\nRECEIPT: INCOMPLETE. Do not claim the mockup is done."); sys.exit(1)
src = open(o.canvas, errors="ignore").read()
boards = re.findall(r'<(?:section|div|article)[^>]*data-board="([^"]+)"', src)
line(len(boards) >= 3, f"canvas {o.canvas} ({os.path.getsize(o.canvas)//1024} KB), {len(boards)} boards: {', '.join(boards)}")
line("TODO: draw" not in src, "no scaffold TODO placeholders left" if "TODO: draw" not in src else f"{src.count('TODO: draw')} boards still contain the scaffold TODO")
r = subprocess.run([sys.executable, os.path.join(here, "slop-lint.py"), o.canvas, "--json"], capture_output=True, text=True)
try:
    j = json.loads(r.stdout); line(j["score"] >= 70, f"slop-lint score {j['score']}/100; flags: {', '.join(f['code'] for f in j['findings']) or 'none'}")
except Exception: line(False, "slop-lint failed to run: " + r.stderr[:200])
shots = o.shots or os.path.join(os.path.dirname(os.path.abspath(o.canvas)), "shots")
pngs = [p for p in glob.glob(os.path.join(shots, "*.png")) if os.path.getsize(p) > 2000]
line(len(pngs) >= 2 * max(1, len(boards)) // 1 if boards else False, f"{len(pngs)} screenshots in {shots} (expect desktop+phone per board)")
if o.spec: line(os.path.isfile(o.spec) and os.path.getsize(o.spec) > 500, f"spec {o.spec}")
if o.palette: line(os.path.isfile(o.palette) and os.path.getsize(o.palette) > 200, f"palette {o.palette}")
has_rt = "<!-- cv-runtime -->" in src
line(has_rt, "pan/zoom canvas runtime present (<!-- cv-runtime -->)" if has_rt else "canvas runtime missing: run `python3 scripts/canvasify.py " + o.canvas + "`")
if has_rt:
    import shutil, tempfile
    bin_ = shutil.which("google-chrome-stable") or shutil.which("google-chrome") or shutil.which("chromium") or shutil.which("chromium-browser")
    if bin_:
        try:
            with tempfile.TemporaryDirectory() as td:
                r2 = subprocess.run([bin_, "--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", f"--user-data-dir={td}", "--virtual-time-budget=9000", "--window-size=1600,1000", "--dump-dom", "file://" + os.path.abspath(o.canvas) + "?cvtest=1"], capture_output=True, text=True, timeout=90)
            m = re.search(r'data-cv-test="([^"]*)"', r2.stdout); rd = 'data-cv="ready"' in r2.stdout
            tj = json.loads(m.group(1).replace("&quot;", '"')) if m else {}
            line(rd and abs(tj.get("zoomed", 0) - 2) < 0.01 and tj.get("boards") == len(boards), f"canvas runtime boots in a real browser (boards={tj.get('boards')}, zoom x{tj.get('zoomed')}, focus k={tj.get('focusK')})")
        except Exception as e:
            line(None, f"could not run runtime smoke test: {e}")
    else: line(None, "no chromium found; runtime smoke test skipped")
ntok = len(set(re.findall(r"(?<![\w-])--[a-z][\w-]*\s*:", src)))
line(":root" in src and ntok >= 8, f"canvas defines :root design tokens ({ntok} custom properties)")
line(None, "You must still OPEN at least three screenshots and read them; this script cannot see taste.")
print("\nRECEIPT: " + ("COMPLETE" if ok else "INCOMPLETE. Fix the [FAIL] lines; never report steps you did not run."))
sys.exit(0 if ok else 1)
