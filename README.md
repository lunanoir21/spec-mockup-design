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

The [live gallery](https://lunanoir21.github.io/spec-mockup-design/#gallery) has eight canvases for different platforms: a mobile habit tracker, a sales dashboard, a macOS menu bar app, a browser extension popup, a game inventory, a web app, a desktop widget and a Linux bar widget. Most were made by free opencode models following this skill. Open one to pan and zoom it yourself.

## Install

One command. It downloads the skill and lets you choose which agents get it (agents found on your machine are pre-selected):

```bash
curl -fsSL https://raw.githubusercontent.com/lunanoir21/spec-mockup-design/main/install.sh | bash
```

```text
spec-mockup-design  install for
Detected agents are pre-selected. Type numbers to toggle, a = all, d = detected, n = none, Enter = go, q = quit.
   1) [x] Claude Code        installed
   2) [x] Codex CLI
   3) [x] opencode
   4) [ ] Gemini CLI
   ...
> 
```

Non-interactive: `bash install.sh --detected --yes`, `--agents claude,codex,opencode --yes`, `--all`, `--list`, `--dry-run`,
`--instructions` (also adds a one-line pointer to `AGENTS.md`/`GEMINI.md`), `--copy` (copy instead of symlink),
`--uninstall` (removes only the links it made). It never overwrites an existing entry. Supported: Claude Code, Codex, opencode,
Gemini CLI, Antigravity, Cursor, Kiro, Qwen Code, zcode, pi, Qoder, Grok CLI, Hermes, jcode. Update later with `git -C ~/.agents/skills/spec-mockup-design pull`.

Manual install: `git clone https://github.com/lunanoir21/spec-mockup-design ~/.agents/skills/spec-mockup-design && bash ~/.agents/skills/spec-mockup-design/install.sh`.
For an agent that has no skills folder, add one line to its instructions file (`AGENTS.md`, `GEMINI.md`, ...):

> For any request to design or mock up a UI, load `~/.agents/skills/spec-mockup-design/SKILL.md` first and follow it.

Requirements: Python 3.8+ (stdlib only), Chromium or Chrome for screenshots (optional but recommended), `bash`.

## Use

Just ask your agent for a design. The skill triggers on its own. Prompts that work well (more in [docs/PROMPTS.md](docs/PROMPTS.md)):

- `Design a CPU temperature widget for my status bar. Show idle, warning and critical states.`
- `Give me 3 options for a settings page that differ in structure, not just color.`
- `Design a new "Disk" page for the app in ~/projects/monitor. Read its source, reuse its real colors and timings, do not modify it.`
- `I only want ONE restrained direction. Neutral, no neon, no gradients.`
- `The first option is closest. Make the hover state clearer and add the error and loading boards.`
- `The design is approved. Export the tokens as a QML Theme singleton and list the components per board.`

 The agent runs a short script sequence (the "quick path" in `SKILL.md`):

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
| `install.sh` | One-command installer with an agent picker (also `scripts/install-everywhere.sh`) |
| `scripts/shoot.sh`, `check-done.py` | Headless screenshots and the delivery receipt |
| `tests/selftest.py`, `tests/grade-run.py` | 99-test battery for the scripts; a grader for an agent run |
| `examples/` | A worked example canvas |

## Does it work?

Nine real agent runs with free opencode models (skill not named in the prompt): the skill was found and used in 8, five scored
full marks, and the failures led directly to fixes (a delivery receipt against made-up reports, a linter rule for empty boards,
an anti-cluster rule after agents copied the first palette recipe). The script battery passes 99/99. See `CHANGELOG.md`.

Honest limits: the linter measures defaults, not taste; look at the screenshots. Quality still depends on the model, and some
models stop early or polish for too long (the skill tells them to run the delivery receipt before finishing).

## Made with AI

This project was built with AI. The skill's code, scripts, tests, documentation and landing page were written by Claude
(Claude Code) in a long session directed by the repository owner, who set the goals, reviewed results and made the decisions.
The demo canvases in the gallery were generated by AI agents following the skill: most by free opencode models, one by Claude;
each card names its model. The sample prompts and the "typical default" comparison page are illustrative. Tests and CI run for real
(`python3 tests/selftest.py`), but review the code before you trust it with anything important.

## Contributing

Issues and PRs welcome, see [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 tests/selftest.py` before sending a change.

## License

[MIT](LICENSE)
