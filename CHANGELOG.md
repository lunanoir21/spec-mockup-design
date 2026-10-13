# Changelog

## 0.3.0 (2026-10-13)
- New landing page with a gallery of eight canvases across platforms (mobile, web, macOS, browser extension, game, widget), viewer, prompts, install section.
- One-command `install.sh` with an agent picker; example prompts in `docs/PROMPTS.md`.
- Canvas runtime: `position:fixed` inside boards stays in the board, `?bare=1`, `?view=x,y,k`.
- `slop-lint`: `escaped-newlines` rule (literal `\n` in page text), empty-board rule.
- `docs/build_gallery.py` builds thumbnails and the gallery list.

## 0.2.0 (2026-10-13)
- Pan/zoom infinite canvas runtime for non-Claude agents (`canvas-runtime.js`, `canvasify.py`), `new-canvas.py` output is a canvas.
- `palette.py` (OKLCH), `scales.py`, `slop-lint.py`, `check-done.py`, `install-everywhere.sh`.
- References: design-language, color-harmony, option-archetypes; anti-slop second-order cluster rules.
- Self-test battery (85 tests) and agent-run grader.
- Fixes from nine real agent runs: delivery receipt (made-up reports), empty-board rule, early-stop rule, anti-cluster palette recipes.

## 0.1.0
- Initial skill: reference grounding, boards per state, anti-slop rules, canvas scaffold, contrast and token tools.
