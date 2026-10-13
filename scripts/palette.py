#!/usr/bin/env python3
"""Harmonious palette generator in OKLCH (stdlib only). Produces light + dark token sets whose
neutrals are tinted toward the accent, semantic colors that share the accent's lightness/chroma
logic, and text/surface pairs that pass WCAG (auto-corrected).

  palette.py --hue 28 [--scheme mono|analogous|split|triad] [--mood calm|crisp|warm|dense]
             [--chroma 0.12] [--name ink] [--css out.css] [--json out.json] [--preview out.html]
  palette.py --from-hex "#a3361c"           derive hue/chroma from a brand/reference color

Hue guide (OKLCH degrees): 25 brick/red, 55 ochre/amber, 95 olive-gold, 140 moss green, 180 teal,
215 cyan-ink, 255 blue, 300 violet, 350 rose. (Avoid 255-300 as a lazy default.)
Moods set chroma and neutral tint: calm (low chroma), crisp (high contrast), warm, dense (tight steps).
"""
import argparse, json, math, sys

def srgb_to_lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lin_to_srgb(c): return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055

def oklch_to_rgb(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return r, g, bl

def in_gamut(rgb): return all(-0.0005 <= v <= 1.0005 for v in rgb)

def to_hex(L, C, h):
    # reduce chroma until in sRGB gamut
    c = C
    while c > 0 and not in_gamut(oklch_to_rgb(L, c, h)): c -= 0.002
    r, g, b = (max(0, min(1, v)) for v in oklch_to_rgb(L, max(c, 0), h))
    return "#%02x%02x%02x" % tuple(round(255 * lin_to_srgb(v)) for v in (r, g, b))

def hex_to_oklch(hx):
    hx = hx.lstrip("#"); r, g, b = (srgb_to_lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360

def rel_lum(hx):
    hx = hx.lstrip("#"); r, g, b = (srgb_to_lin(int(hx[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

def ratio(a, b):
    la, lb = sorted((rel_lum(a), rel_lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)

def fix_contrast(L, C, h, bg, need, direction):
    """Move lightness away from bg until ratio >= need."""
    for _ in range(80):
        hx = to_hex(L, C, h)
        if ratio(hx, bg) >= need: return hx
        L += direction * 0.01
        if not 0 <= L <= 1: break
    return to_hex(max(0, min(1, L)), C, h)

MOODS = {  # neutral chroma, accent chroma scale, step between surfaces, text lightness (light/dark)
    "calm":  dict(nc=0.006, ac=0.9, step=0.018, tl=0.24, td=0.90),
    "crisp": dict(nc=0.003, ac=1.1, step=0.025, tl=0.18, td=0.95),
    "warm":  dict(nc=0.010, ac=1.0, step=0.020, tl=0.26, td=0.91),
    "dense": dict(nc=0.005, ac=0.85, step=0.012, tl=0.22, td=0.90),
}

def scheme_hues(h, scheme):
    return {"mono": [h, h, h], "analogous": [h, (h + 30) % 360, (h - 30) % 360],
            "split": [h, (h + 150) % 360, (h + 210) % 360], "triad": [h, (h + 120) % 360, (h + 240) % 360]}[scheme]

def build(h, chroma, mood, scheme):
    m = MOODS[mood]; hues = scheme_hues(h, scheme); ac = chroma * m["ac"]
    out = {}
    for theme in ("light", "dark"):
        light = theme == "light"
        nh = h  # neutrals share the accent hue: this is what makes it feel harmonious
        if light:
            bgL = 0.965; surfL = bgL + 0.018; raisedL = 1.0; lineL = bgL - 0.085
            bg, surf, raised, line = (to_hex(bgL, m["nc"], nh), to_hex(min(surfL, .99), m["nc"], nh),
                                      to_hex(.995, m["nc"] * .6, nh), to_hex(lineL, m["nc"] * 1.3, nh))
        else:
            bgL = 0.17; bg = to_hex(bgL, m["nc"], nh)
            surf = to_hex(bgL + m["step"], m["nc"], nh); raised = to_hex(bgL + 2 * m["step"], m["nc"], nh)
            line = to_hex(bgL + 4.5 * m["step"], m["nc"] * 1.2, nh)
        text = to_hex(m["tl"] if light else m["td"], m["nc"] * 1.2, nh)
        muted = fix_contrast(0.52 if light else 0.70, m["nc"] * 1.6, nh, surf, 4.6, -.01 if light else .01)
        accL = 0.48 if light else 0.74
        accent = fix_contrast(accL, ac, hues[0], surf, 4.6, -.01 if light else .01)
        accent_soft = to_hex(0.93 if light else 0.26, ac * 0.35, hues[0])
        on_accent = "#ffffff" if ratio("#ffffff", accent) >= 4.5 else text if ratio(text, accent) >= 4.5 else "#000000"
        # semantics: fixed hues, same lightness/chroma family as accent so they sit in the palette
        def sem(hue, cscale=0.95):
            return fix_contrast(accL, ac * cscale, hue, surf, 4.6, -.01 if light else .01)
        danger, warn, ok = sem(27, 1.1), sem(75, .9), sem(150, .85)
        ih = 235 if abs(((h - 235 + 180) % 360) - 180) > 40 else 190  # info is blue-ish unless the accent already is
        info = sem(ih, .8)
        out[theme] = dict(bg=bg, surface=surf, raised=raised, line=line, text=text, muted=muted,
                          accent=accent, accent_soft=accent_soft, on_accent=on_accent,
                          danger=danger, warn=warn, ok=ok, info=info)
        # categorical series: same lightness band, hues spread by golden angle, then checked
        series, hh = [], hues[0]
        for i in range(6):
            series.append(to_hex(accL + (0.05 if i % 2 else -0.03) * (1 if light else -1), ac * 0.9, hh))
            hh = (hh + 137.5) % 360
        out[theme]["series"] = series
    return out

def audit(p):
    rows, bad = [], False
    for t, c in p.items():
        for fg, bg, need in (("text", "bg", 7), ("text", "surface", 7), ("muted", "surface", 4.5), ("accent", "surface", 4.5),
                             ("on_accent", "accent", 4.5), ("danger", "surface", 4.5), ("warn", "surface", 4.5), ("ok", "surface", 4.5)):
            r = ratio(c[fg], c[bg]); ok = r >= need - 0.01 or (need == 7 and r >= 4.5)
            bad |= r < 4.5; rows.append((t, fg, bg, r, "ok" if r >= need else ("AA" if r >= 4.5 else "FAIL")))
    return rows, bad

def css(p, name):
    def blk(sel, d, extra=""):
        lines = [f"  --{k.replace('_', '-')}: {v};" for k, v in d.items() if k != "series"]
        lines += [f"  --series-{i + 1}: {v};" for i, v in enumerate(d["series"])]
        return f"{sel}{{\n" + "\n".join(lines) + extra + "\n}\n"
    return (f"/* palette: {name} (generated by palette.py, OKLCH) */\n" + blk(":root", p["light"]) +
            "@media (prefers-color-scheme: dark){\n" + blk(':root:not([data-theme="light"])', p["dark"], "\n  color-scheme: dark;") + "}\n" +
            blk(':root[data-theme="dark"]', p["dark"], "\n  color-scheme: dark;"))

def preview(p, name):
    def col(t):
        d = p[t]; sw = "".join(f'<div style="background:{v};color:{d["text"] if k not in ("accent","danger","warn","ok","info","text") else d["bg"]}"><b>{k}</b><br>{v}</div>'
                               for k, v in d.items() if k != "series")
        se = "".join(f'<i style="background:{v}"></i>' for v in d["series"])
        return f'<section style="background:{d["bg"]};color:{d["text"]}"><h2>{name} / {t}</h2><div class="g">{sw}</div><div class="s">{se}</div></section>'
    return ("<!doctype html><meta charset=utf-8><title>palette</title><style>body{margin:0;font:13px system-ui;display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr))}"
            "section{padding:20px}h2{margin:0 0 12px;font-size:16px}.g{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}.g div{padding:10px;border-radius:6px;font-size:11px;line-height:1.4}"
            ".s{display:flex;gap:6px;margin-top:12px}.s i{flex:1;height:36px;border-radius:6px}</style>" + col("light") + col("dark"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hue", type=float); ap.add_argument("--from-hex")
    ap.add_argument("--chroma", type=float); ap.add_argument("--scheme", default="mono", choices=["mono", "analogous", "split", "triad"])
    ap.add_argument("--mood", default="calm", choices=list(MOODS)); ap.add_argument("--name", default="palette")
    ap.add_argument("--css"); ap.add_argument("--json"); ap.add_argument("--preview")
    a = ap.parse_args()
    if a.from_hex:
        import re
        if not re.fullmatch(r"#?[0-9a-fA-F]{6}", a.from_hex): ap.error(f"--from-hex needs #rrggbb, got {a.from_hex!r}")
        L, C, h = hex_to_oklch(a.from_hex); a.hue = h; a.chroma = a.chroma or C
    if a.hue is None: ap.error("need --hue or --from-hex")
    chroma = min(a.chroma or 0.12, 0.16)  # >0.16 reads as neon on screens
    p = build(a.hue % 360, chroma, a.mood, a.scheme)
    rows, bad = audit(p)
    for nm, hh in (("danger", 27), ("warn", 75), ("ok", 150)):
        if abs(((a.hue - hh + 180) % 360) - 180) < 30:
            print(f"note: accent hue is within 30 deg of {nm}; never let color alone mean {nm} (add icon/label/shape)")
    for t in p:
        print(f"[{t}] " + "  ".join(f"{k}={v}" for k, v in p[t].items() if k != "series"))
        print(f"[{t}] series " + " ".join(p[t]["series"]))
    print("\ncontrast audit:"); [print(f"  {t:5} {fg:9} on {bg:8} {r:5.2f}  {s}") for t, fg, bg, r, s in rows]
    if a.css: open(a.css, "w").write(css(p, a.name)); print("wrote", a.css)
    if a.json: json.dump(p, open(a.json, "w"), indent=1); print("wrote", a.json)
    if a.preview: open(a.preview, "w").write(preview(p, a.name)); print("wrote", a.preview)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
