#!/usr/bin/env python3
"""WCAG contrast and palette checks, stdlib only.

  contrast.py --pairs "#1b1a17:#f4f1ea" "#6d675a:#f4f1ea"      text/bg ratios
  contrast.py --palette "#a3361c" "#3f6b3a" "#d9a441" "#2b5d7a" categorical distinctness
  contrast.py --theme theme.json                              {"bg":..,"text":..,"muted":..,"accent":..}
Exit code 1 if any text pair < 4.5 or any palette pair is too close.
"""
import argparse, itertools, json, math, re, sys

def parse(h):
    h = h.strip().lstrip("#")
    if not re.fullmatch(r"[0-9a-fA-F]{3}|[0-9a-fA-F]{6}", h):
        sys.exit(f"error: not a hex color: {h!r} (use #rgb or #rrggbb)")
    if len(h) == 3: h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

def lum(rgb): r, g, b = map(lin, rgb); return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    la, lb = sorted((lum(parse(a)), lum(parse(b))), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def lab(rgb):
    r, g, b = map(lin, rgb)
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)

def delta_e(a, b):
    return math.dist(lab(parse(a)), lab(parse(b)))

def sim_cvd(rgb, kind):
    # Machado 2009 severity 1.0 matrices on linear RGB
    m = {"protan": [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
         "deutan": [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
         "tritan": [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]}[kind]
    l = [lin(c) for c in rgb]
    out = [max(0, min(1, sum(m[i][j] * l[j] for j in range(3)))) for i in range(3)]
    enc = lambda c: 255 * (12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055)
    return tuple(round(enc(c)) for c in out)

def hexs(rgb): return "#%02x%02x%02x" % rgb

def grade(r, large=False):
    need_aa, need_aaa = (3, 4.5) if large else (4.5, 7)
    return "AAA" if r >= need_aaa else "AA" if r >= need_aa else "FAIL"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pairs", nargs="*", help="fg:bg pairs")
    ap.add_argument("--palette", nargs="*", help="categorical colors")
    ap.add_argument("--theme", help="json with bg,text,muted,accent,(danger,success,surface)")
    ap.add_argument("--min-de", type=float, default=15.0, help="min CIE76 distance between categorical colors")
    a = ap.parse_args()
    bad = False
    pairs = list(a.pairs or [])
    if a.theme:
        t = json.load(open(a.theme)); bg = t["bg"]
        for k in ("text", "muted", "accent", "danger", "success"):
            if k in t: pairs.append(f"{t[k]}:{bg}")
        if "surface" in t:
            for k in ("text", "muted"):
                if k in t: pairs.append(f"{t[k]}:{t['surface']}")
    for p in pairs:
        if p.count(":") != 1: sys.exit(f"error: pair must be fg:bg, got {p!r}")
        fg, bg = p.split(":")
        r = ratio(fg, bg); g = grade(r)
        bad |= g == "FAIL"
        print(f"{fg} on {bg}: {r:5.2f}:1  text {g:4}  large/UI {'ok' if r >= 3 else 'FAIL'}")
    if a.palette:
        cols = a.palette
        print(f"palette ({len(cols)}): min distance {a.min_de} (CIE76), also under simulated colour-blindness")
        for kind in (None, "protan", "deutan", "tritan"):
            sim = cols if kind is None else [hexs(sim_cvd(parse(c), kind)) for c in cols]
            for (i, x), (j, y) in itertools.combinations(enumerate(sim), 2):
                d = delta_e(x, y)
                if d < a.min_de:
                    bad = True
                    print(f"  TOO CLOSE [{kind or 'normal'}] {cols[i]} vs {cols[j]}: dE {d:.1f}  -> change lightness or add a non-color cue")
        if not bad: print("  all pairs distinguishable")
    if not pairs and not a.palette:
        ap.print_help(); return 2
    return 1 if bad else 0

sys.exit(main())
