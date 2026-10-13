#!/usr/bin/env python3
"""Scaffold a single-file HTML design canvas (the portable "tuval").

  new-canvas.py --title "Screen time pill" --out design/pill-mockup.html \
     --boards "idle:360x120,hover:360x120,expanded:360x420,settings:420x520" \
     [--themes "ink:Ink,bone:Bone"] [--lang tr]

Result: a pan/zoom infinite canvas (canvas-runtime.js inlined): drag to pan, ctrl+wheel/pinch to zoom, focus and
download buttons per board, board list. One fixed-size artboard per board (id = data-board), CSS tokens on :root
with a theme switch, `?only=<id>` (used by shoot.sh), `?flat=1` (classic scroll page), `?theme=<id>`.
Edit the TOKENS block, then fill each <section class="board"> artboard with the real state.
"""
import argparse, html, os, re, sys

TPL = r'''<!doctype html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<!-- CHANGELOG
  r1: scaffold
-->
<style>
/* ===== TOKENS: replace with the real palette/type (see references/anti-slop.md) ===== */
:root{
  --bg:#eff5f3; --surface:#f5fbf9; --line:#d2d9d7; --text:#1c201f; --muted:#636b69; --accent:#016d5e;
  --danger:#953e37; --ok:#326c41;
  --radius-s:4px; --radius-m:8px; --radius-l:14px; --space:4px;
  --dur-micro:120ms; --dur-small:200ms; --dur-large:300ms; --ease-out:cubic-bezier(.2,.8,.2,1);
  --font-ui:"IBM Plex Sans","Public Sans",sans-serif; --font-display:"Bricolage Grotesque","IBM Plex Sans",sans-serif; --font-mono:"JetBrains Mono",monospace;
  /* canvas chrome (not part of the design) */
  --canvas:#dde4e1; --chrome:#566360;
}
__THEME_CSS__
*{box-sizing:border-box}
html{background:var(--canvas)}
body{margin:0;font:14px/1.5 system-ui,sans-serif;color:#14201c}
.shell{padding:24px 16px 80px;max-width:1700px;margin:0 auto}
h1{font:600 20px/1.2 system-ui;margin:0 0 4px}
.sub{color:var(--chrome);margin:0 0 16px;font-size:13px}
nav.index{display:flex;flex-wrap:wrap;gap:6px 12px;margin:0 0 24px;padding:0 0 12px;border-bottom:1px solid #c3ccc8}
nav.index a{color:#14201c;text-decoration:none;font-size:13px;border-bottom:1px solid transparent}
nav.index a:hover{border-bottom-color:currentColor}
.themes{display:flex;gap:8px;margin:0 0 16px;flex-wrap:wrap}
.themes button{font:inherit;font-size:12px;padding:4px 10px;border:1px solid #b0bab6;background:transparent;border-radius:999px;cursor:pointer}
.themes button[aria-pressed=true]{background:#14201c;color:#eef3f1;border-color:#14201c}
.grid{display:flex;flex-wrap:wrap;gap:32px 28px;align-items:flex-start}
.board{display:flex;flex-direction:column;gap:8px;max-width:100%}
.board>header{display:flex;gap:8px;align-items:baseline;font-size:12px;color:var(--chrome)}
.board>header b{color:#14201c;font-weight:600}
.board>header code{font:11px var(--font-mono);opacity:.8}
.artboard{background:var(--bg);color:var(--text);font:14px/1.5 var(--font-ui);border:1px solid #c3ccc8;overflow:hidden;position:relative}
.note{max-width:var(--w,520px);font-size:12px;color:var(--chrome)}
body.only .shell>h1,body.only .sub,body.only nav.index,body.only .themes{display:none}
body.only .shell{padding:12px}
body.only .board:not(.on){display:none}
@media (max-width:600px){.artboard{max-width:100%}}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
</style>
</head>
<body>
<div class="shell">
<h1>__TITLE__</h1>
<p class="sub">Canvas · __COUNT__ boards · real size artboards · edit tokens in :root</p>
<div class="themes" role="group" aria-label="Theme">__THEME_BUTTONS__</div>
<nav class="index">__INDEX__</nav>
<div class="grid">
__BOARDS__
</div>
</div>
<script>
(function(){
  var q=new URLSearchParams(location.search), only=q.get('only'), th=q.get('theme');
  function theme(id){document.documentElement.dataset.theme=id;
    document.querySelectorAll('.themes button').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.theme===id)});
    try{localStorage.setItem('canvas-theme',id)}catch(e){}}
  document.querySelectorAll('.themes button').forEach(function(b){b.onclick=function(){theme(b.dataset.theme)}});
  try{th=th||localStorage.getItem('canvas-theme')}catch(e){}
  theme(th||'__DEFAULT_THEME__');
  if(only){document.body.classList.add('only');var el=document.querySelector('[data-board="'+only+'"]');if(el)el.classList.add('on');}
})();
</script>
</body>
</html>
'''

BOARD = '''<section class="board" id="{id}" data-board="{id}" style="--w:{w}px">
  <header><b>{title}</b><code>{w}×{h}</code></header>
  <div class="artboard" style="width:{w}px;height:{h}px">
    <!-- TODO: draw the real "{id}" state here at real size. Use var(--...) tokens only. -->
    <div style="padding:16px;color:var(--muted)">{title}</div>
  </div>
  <div class="note"><!-- one line: what changes in this state, which spec row it matches --></div>
</section>'''

def slug(s): return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--boards", required=True, help="id:WxH,... (e.g. idle:360x120)")
    ap.add_argument("--themes", default="", help="id:Label,... first is default; each needs a CSS block (stubs generated)")
    ap.add_argument("--lang", default="en"); ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if os.path.exists(a.out) and not a.force:
        sys.exit(f"{a.out} exists; pass --force to overwrite (it would erase your work)")
    boards = []
    for spec in a.boards.split(","):
        m = re.fullmatch(r"\s*([\w-]+)\s*:\s*(\d+)\s*x\s*(\d+)\s*", spec)
        if not m: sys.exit(f"bad board spec: {spec!r} (want id:WxH)")
        if int(m[2]) < 8 or int(m[3]) < 8: sys.exit(f"board {m[1]!r}: size must be at least 8x8")
        if any(b[0] == m[1] for b in boards): sys.exit(f"duplicate board id: {m[1]!r}")
        boards.append((m[1], int(m[2]), int(m[3])))
    themes = [t.split(":") + [""] for t in a.themes.split(",") if t.strip()]
    themes = [(t[0].strip(), (t[1] or t[0]).strip()) for t in themes] or [("default", "Default")]
    theme_css = "\n".join(
        f':root[data-theme="{i}"]{{ /* {lab}: override --bg --surface --line --text --muted --accent */ }}'
        for i, lab in themes[1:])
    theme_buttons = "".join(f'<button data-theme="{i}" aria-pressed="false">{html.escape(l)}</button>' for i, l in themes)
    out = (TPL.replace("__TITLE__", html.escape(a.title)).replace("__LANG__", a.lang)
           .replace("__COUNT__", str(len(boards))).replace("__THEME_CSS__", theme_css)
           .replace("__THEME_BUTTONS__", theme_buttons).replace("__DEFAULT_THEME__", themes[0][0])
           .replace("__INDEX__", "".join(f'<a href="#{i}">{i}</a>' for i, _, _ in boards))
           .replace("__BOARDS__", "\n".join(BOARD.format(id=i, w=w, h=h, title=i.replace("-", " ").title()) for i, w, h in boards)))
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    js = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "canvas-runtime.js")).read()
    out = out.replace("</body>", "<!-- cv-runtime -->\n<script>\n" + js + "\n</script>\n<!-- /cv-runtime -->\n</body>")
    open(a.out, "w").write(out)
    print(f"wrote {a.out} ({len(boards)} boards). Next: edit :root tokens, fill boards, then scripts/shoot.sh {a.out}")

main()
