#!/usr/bin/env python3
"""Count design tokens in a source tree: colors, durations, easings, radii, fonts, spacing.

  extract-tokens.py <dir> [--top 25] [--json out.json] [--ext qml,css,tsx]
Most frequent value = the system. Rare values = exceptions. Stdlib only.
"""
import argparse, collections, json, os, re, sys

EXT = {"qml", "css", "scss", "less", "ts", "tsx", "js", "jsx", "vue", "svelte", "html", "kt", "xml",
       "rs", "swift", "dart", "slint", "json", "toml", "conf", "ini", "lua", "py", "cpp", "h"}
SKIP = {"node_modules", ".git", "dist", "build", "target", ".next", "vendor", "out", "__pycache__", ".venv"}

PAT = {
    "color": [r"#[0-9a-fA-F]{8}\b", r"#[0-9a-fA-F]{6}\b", r"#[0-9a-fA-F]{3}\b",
              r"(?:rgba?|hsla?)\([^)]{5,40}\)", r"Qt\.rgba\([^)]{5,40}\)"],
    "duration": [r"(?:duration|Duration|delay|transition-duration)\s*[:=]\s*\d+(?:\.\d+)?\s*(?:ms|s)?",
                 r"\b\d+(?:\.\d+)?m?s\b(?=[^a-zA-Z])", r"\b(?:ease|transition)[^;\n]{0,30}\b\d+m?s\b"],
    "easing": [r"cubic-bezier\([^)]+\)", r"Easing\.[A-Za-z]+", r"\bease(?:-in-out|-in|-out)?\b",
               r"\bspring\([^)]*\)", r"\blinear\b(?=\s*[;,)])"],
    "radius": [r"(?:border-)?radius\s*[:=]\s*\d+(?:\.\d+)?(?:px|rem|em)?", r"\brounded(?:-[a-z0-9]+)?\b",
               r"cornerRadius\s*[:=(]\s*\d+"],
    "font": [r"font-family\s*:\s*[^;}\n]+", r"font\.family\s*:\s*[^;}\n]+", r"FontFamily\([^)]+\)",
             r"fontFamily\s*[:=]\s*[^;,\n]+"],
    "font-size": [r"font-size\s*:\s*[\d.]+(?:px|rem|em|pt)?", r"pixelSize\s*:\s*\d+", r"pointSize\s*:\s*\d+",
                  r"fontSize\s*[:=]\s*[\d.]+"],
    "spacing": [r"\b(?:margin|padding|gap|spacing|leftPadding|topPadding|margins)\s*[:=]\s*\d+(?:\.\d+)?(?:px|rem)?"],
}

def norm(kind, s):
    s = re.sub(r"\s+", " ", s.strip())
    if kind == "color": s = s.lower()
    if kind in ("duration", "easing"): s = s.lower()
    return s

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir"); ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--json"); ap.add_argument("--ext")
    a = ap.parse_args()
    exts = set(a.ext.split(",")) if a.ext else EXT
    counts = {k: collections.Counter() for k in PAT}
    where = {k: {} for k in PAT}
    files = 0
    for root, dirs, fs in os.walk(a.dir):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in fs:
            if f.rsplit(".", 1)[-1].lower() not in exts: continue
            p = os.path.join(root, f)
            try:
                if os.path.getsize(p) > 1_500_000: continue
                txt = open(p, errors="ignore").read()
            except OSError: continue
            files += 1
            for kind, pats in PAT.items():
                seen = set()
                for pat in pats:
                    for m in re.finditer(pat, txt):
                        v = norm(kind, m.group(0))
                        if kind == "color" and any(v != x and x.startswith(v) and len(x) > len(v) for x in seen):
                            continue  # #fff inside #ffffff
                        seen.add(v)
                        counts[kind][v] += 1
                        where[kind].setdefault(v, os.path.relpath(p, a.dir))
    print(f"scanned {files} files in {a.dir}\n")
    out = {}
    for kind, c in counts.items():
        if not c: continue
        print(f"== {kind} ({sum(c.values())} hits, {len(c)} distinct)")
        for v, n in c.most_common(a.top):
            print(f"  {n:4}  {v:48}  {where[kind][v]}")
        print()
        out[kind] = c.most_common(a.top)
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
        print("wrote", a.json)

main()
