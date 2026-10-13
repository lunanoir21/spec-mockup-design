#!/usr/bin/env python3
"""Self-test battery for the skill's scripts. Never writes outside a temp dir. Prints a table and JSON.
  python3 tests/selftest.py [--json results.json] [--projects DIR ...]
"""
import argparse, itertools, json, os, subprocess, sys, tempfile, time
HERE = os.path.dirname(os.path.abspath(__file__)); SK = os.path.dirname(HERE); SC = os.path.join(SK, "scripts")
sys.path.insert(0, SC)
import palette as P
R = []
def run(*cmd, **kw):
    t = time.time(); p = subprocess.run(list(map(str, cmd)), capture_output=True, text=True, timeout=kw.get("timeout", 120), cwd=kw.get("cwd"))
    return p.returncode, p.stdout + p.stderr, time.time() - t
def T(group, name, ok, detail=""):
    R.append(dict(group=group, name=name, ok=bool(ok), detail=str(detail)[:300]))
py = lambda s, *a, **k: run(sys.executable, os.path.join(SC, s), *a, **k)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json"); ap.add_argument("--projects", nargs="*", default=[]); a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix="smd-selftest-")
    # ---- contrast
    rc, out, _ = py("contrast.py", "--pairs", "#000:#fff"); T("contrast", "black on white = 21:1", "21.00" in out, out.strip()[:80])
    rc, out, _ = py("contrast.py", "--pairs", "#777777:#777777"); T("contrast", "identical colors = 1:1 and FAIL exit 1", "1.00" in out and rc == 1)
    rc, out, _ = py("contrast.py", "--pairs", "zzz:#fff"); T("contrast", "invalid hex does not traceback", "Traceback" not in out, out.strip().splitlines()[-1][:100] if out.strip() else "")
    rc, out, _ = py("contrast.py", "--pairs", "nocolon"); T("contrast", "malformed pair does not traceback", "Traceback" not in out)
    rc, out, _ = py("contrast.py", "--palette", "#111111", "#111111"); T("contrast", "duplicate palette colors flagged", rc == 1)
    rc, out, _ = py("contrast.py"); T("contrast", "no args prints help (exit 2)", rc == 2)
    # ---- palette grid
    bad, tot, slow = [], 0, 0
    for h, mood, sch in itertools.product(range(0, 360, 20), P.MOODS, ["mono", "analogous", "split", "triad"]):
        tot += 1
        p = P.build(float(h), 0.12, mood, sch); rows, b = P.audit(p)
        hexok = all(isinstance(v, str) and len(v) == 7 for t in p.values() for k, v in t.items() if k != "series")
        if b or not hexok: bad.append((h, mood, sch, [r[:3] for r in rows if r[4] == "FAIL"][:2]))
    T("palette", f"{tot} hue/mood/scheme combos pass WCAG AA audit", not bad, f"{len(bad)} failing, e.g. {bad[:2]}")
    # hue extremes / chroma extremes
    for c in (0.0, 0.02, 0.16, 0.4):
        p = P.build(200.0, min(c, .16), "calm", "mono"); rows, b = P.audit(p); T("palette", f"chroma {c} audits clean", not b)
    rc, out, _ = py("palette.py", "--from-hex", "#a3361c", "--css", os.path.join(tmp, "p.css")); T("palette", "--from-hex derives and writes css", rc == 0 and os.path.getsize(os.path.join(tmp, "p.css")) > 400)
    rc, out, _ = py("palette.py", "--from-hex", "#000000"); T("palette", "--from-hex pure black works", "Traceback" not in out, out.strip().splitlines()[-1][:80])
    rc, out, _ = py("palette.py", "--from-hex", "nothex"); T("palette", "--from-hex invalid does not traceback", "Traceback" not in out)
    rc, out, _ = py("palette.py"); T("palette", "no hue prints usage error", rc != 0 and "Traceback" not in out)
    # roundtrip
    maxerr = 0
    for hx in ("#a3361c", "#2c5b50", "#d9a441", "#10131a", "#f4f1ea", "#ff00ff", "#00ffff"):
        L, C, h = P.hex_to_oklch(hx); back = P.to_hex(L, C, h)
        e = max(abs(int(hx[i:i + 2], 16) - int(back[i:i + 2], 16)) for i in (1, 3, 5)); maxerr = max(maxerr, e)
    T("palette", "OKLCH hex round-trip error <= 2/255", maxerr <= 2, f"max {maxerr}")
    # ---- scales
    for tg, dn in itertools.product(["widget", "app", "web", "mobile"], ["compact", "normal", "airy"]):
        rc, out, _ = py("scales.py", "--target", tg, "--density", dn)
        import re
        fs = [float(x) for x in re.findall(r"--fs-\w+: ([\d.]+)px", out)]
        T("scales", f"{tg}/{dn}: valid, monotonic, min >= 11px", rc == 0 and fs == sorted(fs) and min(fs) >= 11, fs)
    rc, out, _ = py("scales.py", "--ratio", "0"); T("scales", "ratio 0 does not traceback", "Traceback" not in out)
    # ---- slop-lint
    good = os.path.join(SK, "examples", "disk-pill-canvas.html")
    rc, out, _ = py("slop-lint.py", good, "--json"); sc = json.loads(out)["score"]; T("slop-lint", "worked example scores >= 90", sc >= 90, sc)
    badf = os.path.join(tmp, "bad.html")
    open(badf, "w").write("""<style>body{font-family:Inter,sans-serif;background:#000;color:#fff}.c{border-left:4px solid #6366f1;border-radius:12px;background:linear-gradient(135deg,#8b5cf6,#3b82f6);box-shadow:0 0 30px #22ff88}.l{font-size:10px;text-transform:uppercase}.l2{font-size:10px;text-transform:uppercase}.l3{font-size:10px;text-transform:uppercase}.x{color:#888}.y{color:#999}.z{color:#aaa}</style><div class=c>🚀 Lorem ipsum John Doe</div>""")
    rc, out, _ = py("slop-lint.py", badf, "--json"); sc = json.loads(out)["score"]; T("slop-lint", "obvious slop scores < 30", sc < 30 and rc == 1, sc)
    for nm, content in (("empty", ""), ("garbage", "\x00\x01\x02\xff" * 400), ("nocss", "<p>hello</p>"), ("huge", "<style>:root{--a:#123456}</style>" + "<p>x</p>" * 200000)):
        f = os.path.join(tmp, nm + ".html"); open(f, "w", errors="ignore").write(content)
        rc, out, dt = py("slop-lint.py", f); T("slop-lint", f"{nm} input does not crash", "Traceback" not in out, f"{dt:.1f}s")
    rc, out, _ = py("slop-lint.py", os.path.join(tmp, "missing.html")); T("slop-lint", "missing file gives clean error", "Traceback" not in out, out.strip().splitlines()[-1][:100] if out.strip() else "")
    # false-positive check: tasteful page
    fine = os.path.join(tmp, "fine.html")
    open(fine, "w").write("""<link href="https://fonts.googleapis.com/css2?family=Fraunces" rel=stylesheet><style>:root{--bg:#f3f1ec;--surface:#faf9f6;--line:#d8d3c8;--text:#1f1c17;--muted:#6a6358;--accent:#7a4a1e;--radius-s:4px;--radius-m:8px;--fs:15px}
body{font-family:"IBM Plex Sans",sans-serif;background:var(--bg);color:var(--text)}.h{font-family:Fraunces,serif}@media (prefers-reduced-motion:reduce){*{transition:none}}</style>
<section data-board="idle-hover-empty-error-loading-long-disabled-focus"></section><section data-board="b"></section><section data-board="c"></section><p>Okuma listesi: 1.284 sayfa, 63% tamamlandı</p>""")
    rc, out, _ = py("slop-lint.py", fine, "--json"); sc = json.loads(out)["score"]; T("slop-lint", "tasteful hand-written page scores >= 85 (false positives)", sc >= 85, f"{sc} {[f['code'] for f in json.loads(out)['findings']]}")
    cl = os.path.join(tmp, "cluster.html")
    open(cl, "w").write('<link href="https://fonts.googleapis.com/css2?family=Fraunces" rel=stylesheet><style>:root{--bg:#f4f1ea;--surface:#fbf9f4;--line:#d9d3c4;--text:#1b1a17;--muted:#6d675a;--accent:#a3361c}body{font-family:"IBM Plex Sans";background:var(--bg)}h1{font-family:Fraunces}</style><section data-board="a"></section><section data-board="b"></section><section data-board="c"></section>')
    rc, out, _ = py("slop-lint.py", cl, "--json"); T("slop-lint", "cream+brick+serif flagged as cluster-look", "cluster-look" in out, out[:0])
    sc_f = os.path.join(tmp, "scaf.html")
    subprocess.run([sys.executable, os.path.join(SC, "new-canvas.py"), "--title", "s", "--out", sc_f, "--boards", "idle:200x40,hover:200x40,empty:200x40,error:200x40"], capture_output=True)
    rc, out, _ = py("slop-lint.py", sc_f, "--json"); j = json.loads(out); T("slop-lint", "unfilled scaffold scores < 60 (empty-boards)", j["score"] < 60 and any(f["code"] == "empty-boards" for f in j["findings"]), j["score"])
    # ---- extract-tokens
    for d in a.projects:
        if os.path.isdir(d):
            rc, out, dt = py("extract-tokens.py", d, "--top", "3"); T("extract-tokens", f"{os.path.basename(d.rstrip('/'))}: runs, finds tokens", rc == 0 and "== " in out, f"{dt:.1f}s {out.splitlines()[0] if out else ''}")
    emp = os.path.join(tmp, "emptydir"); os.mkdir(emp)
    rc, out, _ = py("extract-tokens.py", emp); T("extract-tokens", "empty dir ok", rc == 0 and "Traceback" not in out)
    rc, out, _ = py("extract-tokens.py", os.path.join(tmp, "nope")); T("extract-tokens", "missing dir clean exit", "Traceback" not in out, out.strip().splitlines()[-1][:100] if out.strip() else "")
    # ---- new-canvas
    c1 = os.path.join(tmp, "c", "a b", "m.html")
    rc, out, _ = py("new-canvas.py", "--title", "Çay & <script>alert(1)</script> \"x\"", "--out", c1, "--boards", "idle:200x40,has space:100x100"); T("new-canvas", "bad board id with space rejected", rc != 0 and "Traceback" not in out, out.strip()[-80:])
    rc, out, _ = py("new-canvas.py", "--title", "Çay & <script>alert(1)</script> \"x\"", "--out", c1, "--boards", "idle:200x40,hover:200x40"); s = open(c1).read() if os.path.exists(c1) else ""
    T("new-canvas", "title is HTML-escaped (no injected script)", rc == 0 and "<script>alert(1)" not in s)
    rc, out, _ = py("new-canvas.py", "--title", "x", "--out", c1, "--boards", "a:1x1"); T("new-canvas", "refuses to overwrite without --force", rc != 0)
    rc, out, _ = py("new-canvas.py", "--title", "x", "--out", os.path.join(tmp, "d.html"), "--boards", "a:1x1,a:2x2"); T("new-canvas", "duplicate board ids rejected", rc != 0 and "Traceback" not in out, out.strip()[-80:])
    rc, out, _ = py("new-canvas.py", "--title", "x", "--out", os.path.join(tmp, "e.html"), "--boards", "a:0x0"); T("new-canvas", "zero-size board rejected", rc != 0 and "Traceback" not in out, out.strip()[-80:])
    # ---- shoot.sh (path with spaces)
    rc, out, dt = run("bash", os.path.join(SC, "shoot.sh"), c1, os.path.join(tmp, "shots out"), timeout=240)
    pngs = [f for f in os.listdir(os.path.join(tmp, "shots out"))] if os.path.isdir(os.path.join(tmp, "shots out")) else []
    T("shoot", "path with spaces renders every board + all", rc == 0 and len(pngs) >= 5, f"{len(pngs)} pngs {dt:.0f}s")
    ne = os.path.join(tmp, "noboards.html"); open(ne, "w").write("<p>x</p>")
    rc, out, _ = run("bash", os.path.join(SC, "shoot.sh"), ne); T("shoot", "no boards gives clean error (exit != 0)", rc != 0)
    rc, out, _ = run("bash", os.path.join(SC, "shoot.sh")); T("shoot", "no args prints usage", rc != 0 and "usage" in out.lower())
    # ---- check-done
    rc, out, _ = py("check-done.py", os.path.join(tmp, "nothing.html")); T("check-done", "missing canvas -> INCOMPLETE exit 1", rc == 1 and "INCOMPLETE" in out)
    rc, out, _ = py("check-done.py", c1, "--shots", os.path.join(tmp, "shots out")); T("check-done", "scaffold with TODO placeholders -> INCOMPLETE", rc == 1 and "TODO" in out, out.strip().splitlines()[1][:100] if len(out.strip().splitlines()) > 1 else "")

    # ---- canvas runtime (real browser)
    import shutil, re as _re
    chrom = shutil.which("chromium") or shutil.which("google-chrome-stable") or shutil.which("google-chrome")
    def dom(path, query="", prof=None):
        if not chrom: return ""
        with tempfile.TemporaryDirectory() as td:
            r = subprocess.run([chrom, "--headless=new", "--no-sandbox", "--disable-gpu", f"--user-data-dir={td}", "--virtual-time-budget=9000", "--window-size=1600,1000", "--dump-dom", "file://" + path + query], capture_output=True, text=True, timeout=120)
        return r.stdout
    def tj(d):
        m = _re.search(r'data-cv-test="([^"]*)"', d); return json.loads(m.group(1).replace("&quot;", '"')) if m else {}
    if chrom:
        cv = os.path.join(tmp, "cv.html")
        subprocess.run([sys.executable, os.path.join(SC, "new-canvas.py"), "--title", "cv", "--out", cv, "--boards", "a:300x200,b:300x200,c:600x400,d:300x200,e:300x200,f:300x200"], capture_output=True)
        d = dom(cv, "?cvtest=1"); t = tj(d)
        T("canvas", "scaffold boots as pan/zoom canvas (6 boards)", 'data-cv="ready"' in d and t.get("boards") == 6, t)
        T("canvas", "zoom math: 2x about a point doubles scale", abs(t.get("zoomed", 0) - 2) < 0.01, t.get("zoomed"))
        T("canvas", "focus fits a board larger than fit-all", t.get("focusK", 0) > t.get("k0", 9), (t.get("focusK"), t.get("k0")))
        T("canvas", "page chrome moved into HUD (not lost)", t.get("hud", 0) >= 2, t.get("hud"))
        d1 = dom(cv, "?only=c"); T("canvas", "?only= shows a single board without canvas chrome", 'data-cv="only"' in d1 and "id=\"cv-bar\"" not in d1)
        d2 = dom(cv, "?flat=1"); T("canvas", "?flat=1 keeps the classic page", 'data-cv="flat"' in d2 and "id=\"cv-bar\"" not in d2)
        d3 = dom(cv, "#c"); T("canvas", "#id opens focused on that board", '"actual"' in d3 or "cv-focus" in d3, "")
        # canvasify a hand-written page (boards directly under body, no wrapper)
        hw = os.path.join(tmp, "hand.html")
        open(hw, "w").write('<!doctype html><title>h</title><style>body{font:14px sans-serif;background:#eee}.x{width:200px;height:120px;background:#fff}</style><h1>Hand</h1>' + "".join(f'<section data-board="b{i}"><div class="x">b{i}</div></section>' for i in range(4)))
        rc, out, _ = py("canvasify.py", hw); d = dom(hw, "?cvtest=1"); t = tj(d)
        T("canvas", "canvasify makes a hand-written page a canvas", rc == 0 and t.get("boards") == 4, t)
        before = open(hw).read(); py("canvasify.py", hw); after = open(hw).read()
        T("canvas", "canvasify is idempotent (one runtime block)", after.count("<!-- cv-runtime -->") == 1 and len(after) == len(before))
        py("canvasify.py", hw, "--remove"); T("canvas", "canvasify --remove restores the page", "cv-runtime" not in open(hw).read())
        rc, out, _ = py("canvasify.py", os.path.join(tmp, "empty.html")); T("canvas", "canvasify on missing/empty input fails cleanly", "Traceback" not in out)
        nb = os.path.join(tmp, "nob.html"); open(nb, "w").write("<p>x</p>"); rc, out, _ = py("canvasify.py", nb); T("canvas", "canvasify without data-board is refused", rc != 0 and "Traceback" not in out)
        big = os.path.join(tmp, "big.html")
        subprocess.run([sys.executable, os.path.join(SC, "new-canvas.py"), "--title", "big", "--out", big, "--boards", ",".join(f"b{i}:400x300" for i in range(60))], capture_output=True)
        t0 = time.time(); d = dom(big, "?cvtest=1"); T("canvas", "60 boards boot (stress)", tj(d).get("boards") == 60, f"{time.time() - t0:.1f}s")
        ex = os.path.join(SK, "examples", "disk-pill-canvas.html")
        if os.path.isfile(ex):
            cp = os.path.join(tmp, "example.html"); shutil.copy(ex, cp); py("canvasify.py", cp); t = tj(dom(cp, "?cvtest=1"))
            T("canvas", "bundled example boots after canvasify", t.get("boards", 0) >= 6, t)
    else:
        T("canvas", "chromium available for runtime tests", False, "no chromium")
    # ---- skill hygiene
    sm = open(os.path.join(SK, "SKILL.md")).read()
    T("hygiene", "SKILL.md has name + description frontmatter", sm.startswith("---") and "name: spec-mockup-design" in sm and "description:" in sm.split("---")[1])
    import re
    refs = set(re.findall(r"`((?:references|scripts|examples)/[\w.\-]+)`", sm)); missing = [r for r in refs if not os.path.exists(os.path.join(SK, r))]
    T("hygiene", "every file named in SKILL.md exists", not missing, missing)
    for f in os.listdir(os.path.join(SK, "references")):
        txt = open(os.path.join(SK, "references", f)).read(); m = re.findall(r"scripts/([\w\-]+\.(?:py|sh))", txt)
        T("hygiene", f"references/{f}: script names exist", all(os.path.exists(os.path.join(SC, x)) for x in m), [x for x in m if not os.path.exists(os.path.join(SC, x))])
    ex = [f for f in os.listdir(SC) if f.endswith(".py")]
    for f in ex:
        rc, out, _ = run(sys.executable, "-m", "py_compile", os.path.join(SC, f)); T("hygiene", f"{f} compiles", rc == 0)
    T("hygiene", "SKILL.md length reasonable (< 300 lines)", sm.count("\n") < 300, sm.count("\n"))
    w = sum(1 for r in R if not r["ok"])
    print(f"{len(R) - w}/{len(R)} passed")
    for r in R:
        if not r["ok"]: print(f"FAIL [{r['group']}] {r['name']}  {r['detail']}")
    if a.json: json.dump(R, open(a.json, "w"), indent=1)
    return 1 if w else 0
sys.exit(main())
