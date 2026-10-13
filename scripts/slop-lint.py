#!/usr/bin/env python3
"""Slop linter for HTML/CSS mockups. Flags defaults nobody chose and scores 0-100.

  slop-lint.py design/mockup.html [--json] [--strict]
Exit 1 when score < 70 (or any 'high' finding with --strict). Heuristic: a flag is a question to
answer ("is this a decision?"), not an automatic verdict. Stdlib only.
"""
import argparse, collections, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import palette as P

BAD_FONTS = {"inter", "roboto", "arial", "helvetica", "helvetica neue", "system-ui", "-apple-system", "segoe ui",
             "sans-serif", "open sans", "lato", "poppins", "montserrat", "space grotesk", "dm sans", "ui-sans-serif"}
LOREM = re.compile(r"lorem ipsum|dolor sit amet|john doe|jane doe|acme|foo bar|your text here|placeholder text|sample text", re.I)
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐⬆✅❌]")
HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
STATE_WORDS = {"hover": "hover/press", "empty": "empty", "error": "error", "loading": "loading", "long": "overflow/long text",
               "disabled": "disabled", "focus": "focus"}

def hex_norm(h):
    h = h.lstrip("#")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return "#" + h[:6].lower()

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--json", action="store_true"); ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    if not os.path.isfile(a.file): sys.exit(f"error: file not found: {a.file}")
    src = open(a.file, errors="ignore").read()
    css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", src, re.S)) or src
    body = re.sub(r"<(style|script)[^>]*>.*?</\1>", " ", src, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", body)
    F = []  # (severity, penalty, code, message)
    def add(sev, pen, code, msg): F.append((sev, pen, code, msg))

    # fonts
    fams = [re.split(r",", m)[0].strip().strip("\"'").lower() for m in re.findall(r"font-family\s*:\s*([^;}]+)", css) + re.findall(r"--font[\w-]*\s*:\s*([^;}]+)", css)]
    used = collections.Counter(fams)
    bad = [f for f in used if f in BAD_FONTS]
    if bad: add("high", 12, "font-default", f"primary font is a default: {', '.join(bad)}. Choose a real face (references/fonts.md).")
    if not re.search(r"@font-face|fonts\.googleapis|fonts\.bunny|fontsource", src, re.I) and used:
        add("med", 6, "font-not-loaded", "no @font-face or font link: the chosen face likely falls back silently.")
    if len({f for f in used if f not in BAD_FONTS and f not in ("monospace", "serif", "ui-monospace")}) > 3:
        add("low", 3, "font-count", "more than 3 distinct primary families; keep to UI face + one display (+ mono).")

    # colors
    hexes = [hex_norm(h) for h in HEX.findall(css)]
    cnt = collections.Counter(hexes)
    chromas, hues = [], []
    for h in cnt:
        L, C, hh = P.hex_to_oklch(h)
        if C > 0.02 and 0.2 < L < 0.95: chromas.append(C); hues.append((hh, C, h, cnt[h]))
    if any(c > 0.19 for c in chromas): add("high", 10, "neon", "very saturated color(s) (OKLCH chroma > 0.19): reads neon. Lower chroma or keep for one tiny signal.")
    if hues:
        bluep = [x for x in hues if 245 <= x[0] <= 315]
        if bluep and sum(x[3] for x in bluep) / sum(x[3] for x in hues) > 0.5:
            add("med", 7, "blue-purple", "blue/purple dominates the chromatic colors: the default SaaS accent. Justify it from the subject or change hue.")
        hs = sorted(x[0] for x in hues if x[1] > 0.04)
        if len(hs) >= 4:
            gaps = [(hs[(i + 1) % len(hs)] - hs[i]) % 360 for i in range(len(hs))]
            sector = 360 - max(gaps)
            if sector > 200 and len({round(x / 40) for x in hs}) >= 6:
                add("med", 6, "hue-scatter", "chromatic hues are scattered around the wheel with no scheme; pick mono/analogous/split (scripts/palette.py).")
    greys = [h for h in cnt if P.hex_to_oklch(h)[1] < 0.004 and 0.1 < P.hex_to_oklch(h)[0] < 0.97]
    if len(greys) >= 3: add("med", 5, "dead-greys", f"{len(greys)} untinted greys ({', '.join(greys[:4])}...). Tint neutrals toward the accent hue.")
    if re.search(r"(?<![\w-])(?:color|background(?:-color)?)\s*:\s*(?:#000(?:000)?|#fff(?:fff)?|black|white)\s*[;}]", css, re.I):
        add("low", 3, "pure-bw", "pure #000/#fff used for text or surface; use tinted near-black / near-white.")
    # hardcoded colors outside :root
    root_end = [m.end() for m in re.finditer(r":root[^{]*\{[^}]*\}", css)]
    outside = re.sub(r":root[^{]*\{[^}]*\}", "", css)
    out_hex = HEX.findall(re.sub(r"/\*.*?\*/", "", outside, flags=re.S))
    if len(out_hex) > 12: add("med", 5, "hardcoded-colors", f"{len(out_hex)} literal colors outside :root tokens; style from tokens so themes and the handoff stay consistent.")
    if not re.search(r":root", css): add("high", 8, "no-tokens", "no :root token block.")

    # second-order slop: the clusters AI output falls into
    toks0 = dict((k, hex_norm(v)) for k, v in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b", css))
    bgh = toks0.get("bg") or toks0.get("background") or toks0.get("surface")
    acch = toks0.get("accent") or toks0.get("signal") or toks0.get("primary")
    if bgh and acch:
        bL, bC, bH = P.hex_to_oklch(bgh); aL, aC, aH = P.hex_to_oklch(acch)
        serif = bool(re.search(r"fraunces|instrument serif|playfair|literata|newsreader|dm serif|source serif|cormorant|lora|georgia", css, re.I))
        if bL > 0.93 and 20 <= bH <= 110 and 0.006 <= bC <= 0.04 and 15 <= aH <= 50 and aC > 0.08:
            add("med", 8, "cluster-look", "warm cream ground + terracotta/brick accent" + (" + serif display" if serif else "") + ": the most common AI look. Pick a hue from the subject (references/anti-slop.md) or justify this one.")
        elif bL < 0.2 and aC > 0.15 and (15 <= aH <= 40 or 110 <= aH <= 150):
            add("med", 8, "cluster-look", "near-black ground + one acid-green/vermilion pop: a common AI look. Desaturate or choose another family.")
    # gradients, glow, glass
    grads = re.findall(r"(?:linear|radial|conic)-gradient\([^;]*", css)
    if grads:
        purple = [g for g in grads if re.search(r"purple|violet|indigo|#(?:[6-9a-f][0-9a-f]){0}[5-9a-f][0-9a-f][0-9a-f]{2}", g, re.I)]
        add("med", 6, "gradient", f"{len(grads)} gradient(s). Gradient washes stand in for structure; keep only if it models real light or data.")
    if re.search(r"box-shadow\s*:[^;]*0\s+0\s+\d{2,}px", css) or re.search(r"text-shadow\s*:[^;]*0\s+0\s+\d+px", css) or re.search(r"drop-shadow\([^)]*0\s+0\s+\d+px", css):
        add("high", 10, "glow", "glow shadow (0 0 Npx) detected: the neon/glow tell.")
    if len(re.findall(r"backdrop-filter\s*:", css)) > 2: add("low", 3, "glass", "backdrop-filter on several elements; glass only where the platform really blurs.")
    sh = re.findall(r"box-shadow\s*:", css)
    if len(sh) > 8: add("low", 3, "shadow-everywhere", f"{len(sh)} box-shadow declarations; pick one separation device per level.")

    # accent rail
    if re.search(r"border-left\s*:\s*\d+px\s+solid[^;]*;[^}]*border-radius|border-radius[^}]*border-left\s*:\s*\d+px\s+solid", css):
        add("high", 10, "left-border-card", "left-border accent card (the most recognisable AI tell).")
    # radius
    rad = [m.strip() for m in re.findall(r"border-radius\s*:\s*([\d.]+px)", css)]
    rc = collections.Counter(rad)
    if len(rc) > 5: add("med", 4, "radius-chaos", f"{len(rc)} distinct radii ({', '.join(sorted(rc))}); use a scale of 2-3.")
    if rad and rc.most_common(1)[0][1] / len(rad) > 0.8 and len(rad) >= 6 and float(rc.most_common(1)[0][0][:-2]) >= 10:
        add("low", 3, "rounded-everything", f"{rc.most_common(1)[0][0]} on almost everything; radius should follow element size.")
    # labels
    tiny = len(re.findall(r"text-transform\s*:\s*uppercase[^}]*font-size\s*:\s*(?:9|10|11)px|font-size\s*:\s*(?:9|10|11)px[^}]*text-transform\s*:\s*uppercase", css))
    if tiny >= 3: add("med", 5, "micro-labels", f"{tiny} tiny uppercase micro-label styles: fake-technical texture. Use sentence-case labels.")
    if any(int(x) < 11 for x in re.findall(r"font-size\s*:\s*(\d+)px", css)): add("med", 4, "tiny-text", "font-size under 11px.")
    # content
    if LOREM.search(text): add("high", 10, "placeholder-content", f"placeholder content: '{LOREM.search(text).group(0)}'. Use real strings.")
    bsn = len(re.findall(r"\\n", text))
    if bsn >= 3: add("high", 20, "escaped-newlines", f"{bsn} literal '\\n' sequences in the visible text: a string-escaping bug in the generator. Re-emit the file with real newlines.")
    em = EMOJI.findall(text)
    if em: add("med", 6, "emoji", f"{len(em)} emoji in content ({''.join(em[:5])}). Draw icons with one stroke weight.")
    nums = re.findall(r"(?<![\w.])(100|1000|1,000|50|10|99)(?:\s*%|\b)", text)
    if len(nums) >= 4: add("low", 2, "round-numbers", "many round numbers; real data is odd (1,284 / 63%).")
    # layout
    if len(re.findall(r"repeat\(3,\s*1fr\)|grid-template-columns:\s*repeat\(auto-fit", css)) and len(re.findall(r'class="[^"]*card', body)) >= 6:
        add("low", 3, "card-grid", "grid of 6+ equal cards: layout by default. Create hierarchy (one dominant region).")
    # unfilled scaffold boards
    todo = src.count("TODO: draw"); bare = len(re.findall(r'<div style="padding:16px;color:var\(--muted\)">[^<]{1,40}</div>', src))
    if todo or bare:
        add("high", min(60, 15 + 3 * max(todo, bare)), "empty-boards", f"{max(todo, bare)} board(s) are still the empty scaffold placeholder. Fill every board before showing.")
    # states
    ids = " ".join(re.findall(r'data-board="([^"]+)"', src)).lower()
    if ids:
        missing = [lab for w, lab in STATE_WORDS.items() if w not in ids and w not in css.lower()]
        if len(missing) >= 4: add("high", 8, "states-missing", f"boards show no: {', '.join(missing)}. Mockups must include ugly/edge states.")
        elif missing: add("low", 2, "states-thin", f"consider boards for: {', '.join(missing)}.")
        if len(ids.split()) < 3: add("med", 5, "few-boards", "fewer than 3 boards: one composite is not a mockup.")
    if not re.search(r"prefers-reduced-motion", css) and re.search(r"transition|animation", css): add("low", 2, "reduced-motion", "motion without a prefers-reduced-motion path.")

    # token contrast (if :root has bg/text-like tokens)
    toks = dict((k, hex_norm(v)) for k, v in re.findall(r"--([\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\b", re.search(r":root[^{]*\{([^}]*)\}", css).group(0) if re.search(r":root[^{]*\{", css) else ""))
    bgk = next((k for k in ("bg", "background", "surface", "canvas") if k in toks), None)
    for k in ("text", "fg", "foreground", "muted", "accent"):
        if bgk and k in toks:
            r = P.ratio(toks[k], toks[bgk])
            if r < 4.5: add("high" if k != "accent" else "med", 8, "contrast", f"--{k} {toks[k]} on --{bgk} {toks[bgk]} = {r:.2f}:1 (< 4.5).")

    score = max(0, 100 - sum(p for _, p, _, _ in F))
    order = {"high": 0, "med": 1, "low": 2}
    F.sort(key=lambda x: (order[x[0]], -x[1]))
    if a.json: print(json.dumps({"score": score, "findings": [dict(sev=s, code=c, msg=m) for s, _, c, m in F]}, indent=1))
    else:
        print(f"slop score: {score}/100  ({'ok' if score >= 70 else 'FIX BEFORE SHOWING'})\n")
        for s, p, c, m in F: print(f"  [{s:4}] {c:18} {m}")
        if not F: print("  no flags. Still read the screenshots: a linter cannot judge taste.")
        print("\nEvery flag is a question: is this a decision I can defend from the subject or reference? If yes, note it on the Reference board.")
    return 1 if (score < 70 or (a.strict and any(s == "high" for s, *_ in F))) else 0

sys.exit(main())
