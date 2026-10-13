#!/usr/bin/env python3
"""Build the docs gallery: copy canvases into docs/demos, make thumbnails, score them, inject the list into index.html.

  python3 docs/build_gallery.py docs/gallery.src.json

gallery.src.json: [{"id","title","platform","prompt","model","src": "path/to/canvas.html"}, ...]
Needs Chromium or Chrome for thumbnails. Stdlib only.
"""
import json, os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
CHROME = next((shutil.which(b) for b in ("google-chrome-stable", "google-chrome", "chromium", "chromium-browser") if shutil.which(b)), None)

def main():
    spec = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "gallery.src.json")))
    os.makedirs(os.path.join(HERE, "demos"), exist_ok=True); os.makedirs(os.path.join(HERE, "img"), exist_ok=True)
    out = []
    for e in spec:
        src = os.path.abspath(os.path.expanduser(e["src"])); dst = os.path.join(HERE, "demos", e["id"] + ".html")
        txt = open(src, errors="ignore").read()
        # carry referenced local font files (url(x.woff2) or url(fonts/x.woff2))
        for ref in set(re.findall(r"url\(['\"]?((?:\./)?(?:fonts/)?[\w.\-]+\.woff2)['\"]?\)", txt)):
            for base in (os.path.dirname(src), os.path.join(os.path.dirname(src), "fonts")):
                f = os.path.join(base, os.path.basename(ref))
                if os.path.isfile(f):
                    os.makedirs(os.path.join(HERE, "demos", "fonts"), exist_ok=True); shutil.copy(f, os.path.join(HERE, "demos", "fonts", os.path.basename(ref)))
                    txt = txt.replace(ref, "fonts/" + os.path.basename(ref)) if not ref.startswith("fonts/") else txt
                    break
        open(dst, "w").write(txt)
        subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "canvasify.py"), dst], check=True, capture_output=True)
        t = open(dst).read(); boards = len(re.findall(r'<(?:section|div|article)[^>]*data-board="', t))
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "slop-lint.py"), dst, "--json"], capture_output=True, text=True)
        score = json.loads(r.stdout)["score"] if r.stdout.strip().startswith("{") else 0
        thumb = os.path.join(HERE, "img", e["id"] + ".jpg")
        if CHROME:
            with tempfile.TemporaryDirectory() as td:
                png = os.path.join(td, "t.png")
                base = [CHROME, "--headless=new", "--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", f"--user-data-dir={td}/p", "--virtual-time-budget=8000"]
                dom = subprocess.run(base + ["--window-size=1280,807", "--dump-dom", "file://" + dst + "?cvrects=1"], capture_output=True, text=True, timeout=120).stdout
                m = re.search(r'data-cv-rects="([^"]*)"', dom); view = ""
                if m:
                    rs = json.loads(m.group(1).replace("&quot;", '"')); pick = rs[1:4] if len(rs) > 3 else rs
                    x0 = min(r[1] for r in pick); y0 = min(r[2] for r in pick); x1 = max(r[1] + r[3] for r in pick); y1 = max(r[2] + r[4] for r in pick)
                    w, h = x1 - x0, y1 - y0; k = min((1280 - 120) / w, (720 - 100) / h, 1.0)
                    view = "&view=%.2f,%.2f,%.4f" % ((1280 - w * k) / 2 - x0 * k, (720 - h * k) / 2 - y0 * k, k)
                subprocess.run(base + ["--hide-scrollbars", "--window-size=1280,720", f"--screenshot={png}", "file://" + dst + "?bare=1" + view], capture_output=True, timeout=120)
                if os.path.isfile(png): subprocess.run(["magick", png, "-resize", "900x", "-quality", "80", thumb], check=False)
        out.append(dict(id=e["id"], title=e["title"], platform=e["platform"], prompt=e["prompt"], model=e["model"], boards=boards, score=score, src="demos/" + e["id"] + ".html", thumb="img/" + e["id"] + ".jpg"))
        print(f"{e['id']:12} boards={boards:2} slop={score}")
    idx = os.path.join(HERE, "index.html"); h = open(idx).read()
    h = re.sub(r"/\*GALLERY_START\*/.*?/\*GALLERY_END\*/", lambda m: "/*GALLERY_START*/\nvar GALLERY = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n/*GALLERY_END*/", h, flags=re.S)
    open(idx, "w").write(h); print("gallery:", len(out), "demos")

main()
