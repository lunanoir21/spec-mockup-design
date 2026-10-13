# Spec Mockup Design

**An agent skill that makes AI coding agents design real UIs instead of AI slop.**
Works with Claude Code, Codex, opencode, Gemini/Antigravity, Cursor, Kiro, Qwen and any agent that reads `SKILL.md`.

[Türkçe](README.tr.md) · [Live demo](https://lunanoir21.github.io/spec-mockup-design/) · MIT licensed

![Pan and zoom canvas demo](assets/canvas-demo.gif)

Ask an agent to "design a settings screen" and you usually get the same page: purple gradient, Inter, rounded cards, a
left-border accent, lorem ipsum, one pretty state. This skill replaces that with a workflow that produced designs people
actually kept:

1. **Ground in a real reference.** Read the project's own source (or a named product), extract real colors, radii, spacing and animation timings. Never invent when something real exists.
2. **Build a design language, not a mood.** One concept sentence, a generated OKLCH palette with tinted neutrals, a modular type scale, one icon stroke weight.
3. **Show every state.** One board per real state: idle, hover, empty, error, loading, overflow, disabled, focus, plus a motion storyboard, font comparison, theme picker and tokens board.
4. **Gate against slop.** A linter scores the result, a delivery receipt proves the files exist, screenshots get read.
5. **Deliver a canvas.** Agents without a design tool output a single HTML **pan/zoom infinite canvas** (drag to pan, ctrl+wheel to zoom, focus and download any board), the same experience as Claude's Design canvas.

| Overview | Focus a board |
|---|---|
| ![overview](assets/shot-overview.jpg) | ![focus](assets/shot-focus.jpg) |
| ![weather widget](assets/shot-weather.jpg) | ![cpu fan widget](assets/shot-cpu.jpg) |

All four were produced by free opencode models following this skill. Open the [live demo](https://lunanoir21.github.io/spec-mockup-design/) to pan and zoom them yourself.

## Install

```bash
git clone https://github.com/lunanoir21/spec-mockup-design ~/.agents/skills/spec-mockup-design
bash ~/.agents/skills/spec-mockup-design/scripts/install-everywhere.sh
```

`install-everywhere.sh` symlinks the skill into every agent's skills folder it finds (`~/.claude/skills`, `~/.codex/skills`,
`~/.config/opencode/skills`, `~/.gemini/skills`, `~/.cursor/skills`, `~/.kiro/skills`, `~/.qwen/skills` and more). It is
idempotent and never overwrites or deletes (`--dry-run` shows what it would do). For an agent that has no skills folder, add one line to its
instructions file (`AGENTS.md`, `GEMINI.md`, ...):

> For any request to design or mock up a UI, load `~/.agents/skills/spec-mockup-design/SKILL.md` first and follow it.

Requirements: Python 3.8+ (stdlib only), Chromium or Chrome for screenshots (optional but recommended), `bash`.

## Use

Just ask your agent for a design: "design a CPU temperature widget for my status bar", "give me 3 options for a settings page".
The skill triggers on its own. The agent runs a short script sequence (the "quick path" in `SKILL.md`):

```bash
S=~/.agents/skills/spec-mockup-design/scripts
python3 $S/palette.py --hue 178 --mood calm --css design/palette.css      # harmonious light+dark palette, WCAG-fixed
python3 $S/scales.py --target widget --css design/scales.css              # type, spacing, radius, motion tokens
python3 $S/new-canvas.py --title "CPU widget" --out design/mockup.html --boards "idle:360x120,hover:360x120,expanded:360x420"
python3 $S/slop-lint.py design/mockup.html                                # score >= 70
bash    $S/shoot.sh design/mockup.html                                    # screenshot every board, desktop and phone
python3 $S/check-done.py design/mockup.html                               # delivery receipt: proves the work exists
```

Moving around the canvas: **drag** the background to pan, **Ctrl+wheel** or pinch to zoom, **double-click** to fit all,
**F** to focus a board (arrows for next/previous, **Esc** back), **0** fit, **1** 100%, the **Boards** list to jump, the
download button on a board to save it as a standalone HTML file. `?only=<id>` shows one board, `?flat=1` the classic
scrolling page, `#<id>` opens focused on a board.

## What is inside

| Path | Purpose |
|---|---|
| `SKILL.md` | The skill: rules, workflow, quick path |
| `references/` | design-language, color-harmony, anti-slop, option-archetypes, grounding, surfaces, fonts, spec-template, handoff |
| `scripts/palette.py` | OKLCH palette generator: tinted neutrals, semantic colors, categorical series, auto WCAG fix |
| `scripts/scales.py` | Type, spacing, radius, motion and icon tokens |
| `scripts/slop-lint.py` | 0-100 slop score: default fonts, neon, glow, gradients, emoji, lorem, cream+terracotta cluster, empty boards, missing states, contrast |
| `scripts/new-canvas.py`, `canvasify.py`, `canvas-runtime.js` | The pan/zoom canvas, and a way to add it to any hand-written HTML |
| `scripts/extract-tokens.py` | Count real colors, durations, easings, radii, fonts in a reference codebase |
| `scripts/contrast.py` | WCAG contrast pairs and color-blind-safe categorical palette check |
| `scripts/shoot.sh`, `check-done.py` | Headless screenshots and the delivery receipt |
| `tests/selftest.py`, `tests/grade-run.py` | 85-test battery for the scripts; a grader for an agent run |
| `examples/` | A worked example canvas |

## Does it work?

Nine real agent runs with free opencode models (skill not named in the prompt): the skill was found and used in 8, five scored
full marks, and the failures led directly to fixes (a delivery receipt against made-up reports, a linter rule for empty boards,
an anti-cluster rule after agents copied the first palette recipe). The script battery passes 85/85. See `CHANGELOG.md`.

Honest limits: the linter measures defaults, not taste; look at the screenshots. Quality still depends on the model, and some
models stop early or polish for too long (the skill tells them to run the delivery receipt before finishing).

## Contributing

Issues and PRs welcome, see [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 tests/selftest.py` before sending a change.

## License

[MIT](LICENSE)
