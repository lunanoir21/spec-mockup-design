#!/usr/bin/env python3
"""Grade an opencode headless run (--format json) of a design task.
  grade-run.py <run_dir> [--json]      run_dir has run.json and the agent's design/ output
Checks: skill loaded, references read, scripts executed, deliverables exist, slop score, honesty
(files claimed in the final text vs files on disk), boards/states, option count.
"""
import argparse, glob, json, os, re, subprocess, sys
SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a = argparse.ArgumentParser(); a.add_argument("dir"); a.add_argument("--json", action="store_true"); o = a.parse_args()
ev = []
try:
    for l in open(os.path.join(o.dir, "run.json"), errors="ignore"):
        try: ev.append(json.loads(l))
        except Exception: pass
except OSError: pass
tools = [e["part"] for e in ev if e.get("type") == "tool_use"]
text = "\n".join(e["part"].get("text", "") for e in ev if e.get("type") == "text")
errs = [e for e in ev if e.get("type") == "error"]
cmds = " ".join(str(t.get("state", {}).get("input", "")) for t in tools)
G = {}
G["tool_calls"] = len(tools)
G["skill_loaded"] = any(t.get("tool") == "skill" and "spec-mockup" in str(t.get("state", {}).get("input", "")) for t in tools) or "spec-mockup-design/SKILL.md" in cmds
G["refs_read"] = len(set(re.findall(r"references/([\w\-]+\.md)", cmds)))
G["scripts_run"] = sorted({s for s in ("palette", "scales", "new-canvas", "slop-lint", "shoot", "check-done", "extract-tokens", "contrast") if re.search(s + r"\.(py|sh)", cmds)})
files = [f for f in glob.glob(os.path.join(o.dir, "**", "*"), recursive=True) if os.path.isfile(f) and not os.path.basename(f).startswith(("run.", "done")) and "/shots/" not in f]
G["files"] = sorted(os.path.relpath(f, o.dir) for f in files)
htmls = [f for f in files if f.endswith(".html") and "palette" not in os.path.basename(f)]
G["canvas"] = None; G["boards"] = 0; G["slop_score"] = None; G["slop_flags"] = []
if htmls:
    big = max(htmls, key=os.path.getsize); G["canvas"] = os.path.relpath(big, o.dir)
    s = open(big, errors="ignore").read(); G["boards"] = len(re.findall(r'data-board="', s)) or len(re.findall(r"<section", s))
    r = subprocess.run([sys.executable, os.path.join(SK, "scripts", "slop-lint.py"), big, "--json"], capture_output=True, text=True)
    try: j = json.loads(r.stdout); G["slop_score"] = j["score"]; G["slop_flags"] = [f["code"] for f in j["findings"]]
    except Exception: pass
G["shots"] = len(glob.glob(os.path.join(o.dir, "**", "shots", "*.png"), recursive=True))
claimed = set(re.findall(r"`?(design/[\w./\-]+\.(?:html|md|css|txt|png|json|svg))`?", text))
G["claimed_files"] = len(claimed)
G["claimed_but_missing"] = sorted(c for c in claimed if not any(f.endswith(os.path.basename(c)) for f in G["files"]) and "/" not in c or (c.startswith("design/") and not os.path.exists(os.path.join(o.dir, c))))
G["hallucinated_report"] = bool(G["claimed_but_missing"]) or (len(tools) == 0 and bool(text.strip()) and bool(claimed))
G["errors"] = [str(e.get("error", {}).get("message", ""))[:120] for e in errs]
G["final_text_chars"] = len(text)
G["asked_question"] = bool(re.search(r"\?\s*$", text.strip().splitlines()[-1] if text.strip() else ""))
pts = 0
pts += 20 if G["skill_loaded"] else 0
pts += min(15, G["refs_read"] * 3)
pts += min(25, 5 * len({"palette", "scales", "slop-lint", "shoot", "check-done"} & set(G["scripts_run"])))
pts += 15 if G["canvas"] else 0
pts += 10 if G["boards"] >= 4 else 0
pts += 10 if (G["slop_score"] or 0) >= 70 else 0
pts += 5 if G["shots"] >= 4 else 0
pts -= 40 if G["hallucinated_report"] else 0
G["grade"] = max(0, min(100, pts))
if o.json: print(json.dumps(G, indent=1, ensure_ascii=False))
else:
    for k, v in G.items(): print(f"{k:22} {v}")
