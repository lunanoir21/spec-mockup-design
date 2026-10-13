# Contributing

- Run `python3 tests/selftest.py` (needs Chromium or Chrome for the canvas tests). All tests must pass.
- Scripts are Python stdlib only; keep it that way. No build step for the canvas runtime.
- A change to `canvas-runtime.js` needs a test in `tests/selftest.py` (the runtime exposes `?cvtest=1` for headless checks).
- A new slop rule needs a case in the self-test (one page that triggers it, one tasteful page that must not).
- To evaluate the skill with an agent, run a design task with a free model and grade it: `python3 tests/grade-run.py <run_dir>`.
- Keep `SKILL.md` short and imperative; put detail in `references/`.
