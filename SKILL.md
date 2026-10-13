---
name: spec-mockup-design
description: Use whenever the user asks to design, mock up, reimagine, or produce "design options" for any UI — an app screen, a desktop/Linux shell plugin or bar widget, a website, a mobile screen, a TUI, a tool panel, anything visual. Also use for "tasarım seçenekleri", "mockup", "arayüz taslağı", "tasarla", "bunu daha güzel yap", or when they say "bunu bir skill haline getir" pointing back at a prior design session. Produces original, non-AI-slop mockups grounded in a real reference, as a multi-board canvas with one board per concrete state, a spec, a font board, a theme picker and a verified handoff. Works in Claude Code (Artifact canvas) and in every other agent (one self-contained HTML canvas file). Ships scripts for scaffolding the canvas, extracting tokens from a reference, checking contrast and screenshotting every board.
---

# Spec mockup design

The user rejected a first round of design options as "AI slop" (generic gradients, blue/purple
accents, Inter, dark-with-neon dashboards, every option a recolor of one idea). The workflow below
fixed it, was praised, and is now the default for **every** UI design request on **any** surface.
Works in Claude Code, opencode, Gemini CLI, Codex and anything that can read a file and run a shell.

Files in this skill (paths relative to this folder; `~/.agents/skills/spec-mockup-design/`):

| File | Use it for |
|---|---|
| `references/design-language.md` | The concept sentence, hierarchy, type, space, icons, motion, voice and the consistency audit. Read first. |
| `references/color-harmony.md` | How palettes are built (OKLCH, tinted neutrals, 60/30/10, semantics, data colors, moods). |
| `references/option-archetypes.md` | The axes that make several options structurally different. |
| `references/anti-slop.md` | The blacklist and what to do instead. Read before choosing any palette or font. |
| `references/grounding.md` | How to pull real colors, timings, radii and fonts out of a reference project or screenshot. |
| `references/surfaces.md` | State checklists per surface (bar widget, desktop app, web, mobile, TUI, panel...). |
| `references/fonts.md` | Candidate typefaces by mood, pairings, how to load them offline-safe. |
| `references/spec-template.md` | The written spec skeleton (state machine, motion table, data, non-goals). |
| `references/handoff.md` | Turning the approved mockup into tokens and code without drifting. |
| `scripts/new-canvas.py` | Scaffold the single-file HTML canvas as a **pan/zoom infinite canvas** (runtime inlined). |
| `scripts/canvasify.py` | Add the pan/zoom canvas runtime to ANY hand-written HTML whose boards have `data-board`. |
| `scripts/canvas-runtime.js` | The runtime itself (drag/scroll pan, ctrl+wheel/pinch zoom, focus, board list, per-board download). |
| `scripts/extract-tokens.py` | Count colors, durations, easings, radii, fonts in a source tree. |
| `scripts/palette.py` | Generate a harmonious light+dark palette (OKLCH) from one hue or a reference color; auto-fixes contrast. |
| `scripts/scales.py` | Type, spacing, radius, motion and icon tokens from a ratio and a density. |
| `scripts/slop-lint.py` | Scores a canvas 0-100 for AI-slop tells (defaults, neon, glow, gradients, emoji, lorem, missing states, contrast). |
| `scripts/check-done.py` | Delivery receipt: verifies canvas, boards, lint score, screenshots really exist. Paste its output. |
| `scripts/contrast.py` | WCAG contrast pairs, palette audit, categorical distinctness. |
| `scripts/shoot.sh` | Headless screenshots of every board at desktop and phone width. |
| `scripts/install-everywhere.sh` | Link the skill into every AI tool's skills folder on the machine (idempotent, never overwrites). |
| `tests/selftest.py`, `tests/grade-run.py` | Self-test battery for the scripts; grader for an agent run (skill loaded? scripts run? files real? slop score?). |
| `examples/` | A worked canvas to copy structure from. Replace the content, never reuse it. |

## Quick path (run these, in this order, every time)

```
S=~/.agents/skills/spec-mockup-design/scripts           # or the skills dir your agent loaded this from
mkdir -p design
python3 $S/palette.py --hue <H> --mood <calm|crisp|warm|dense> --scheme <mono|analogous|split> --css design/palette.css --preview design/palette.html
python3 $S/scales.py --target <widget|app|web|mobile> --density <compact|normal|airy> --css design/scales.css
python3 $S/new-canvas.py --title "<Name>" --out design/<topic>-mockup.html --boards "idle:WxH,hover:WxH,..." [--themes "light:Light,dark:Dark"]
#   ...fill every board, paste palette.css + scales.css into :root...
#   (hand-written page instead of new-canvas.py?  python3 $S/canvasify.py design/<topic>-mockup.html)
python3 $S/slop-lint.py design/<topic>-mockup.html          # score >= 70
bash    $S/shoot.sh design/<topic>-mockup.html              # then OPEN >= 3 PNGs and read them
python3 $S/check-done.py design/<topic>-mockup.html --spec design/spec.md --palette design/palette.css
```
**Execution honesty.** Your final message must include the real output of `check-done.py`. Never
describe a step as done unless you ran it in this session and saw its output. A report that lists
scripts you did not run, or files that do not exist, is a failed task even if the text is good.
If a step is impossible (no chromium, offline), say so in one line and continue.
**Do not end your turn early.** Narrating "now the spec, then the canvas" and stopping is a failure.
Keep working until `check-done.py` prints `RECEIPT: COMPLETE`. If you truly must stop, say exactly
which steps remain and which files exist.

## Hard rules

1. **Reference before pixels.** Do not design from your own defaults. Find a real thing to ground
   in (section 1). If none exists and none was supplied, say so and ask for one in one line, or
   design ONE restrained direction from a stated palette and type plan. Never fill the gap with
   ten self-invented styles.
2. **Options must differ in structure, not paint.** Layout, information hierarchy, interaction
   model. A recolored copy is not an option. If the user names a count (e.g. "10 options"), give
   exactly that many, each structurally distinct; otherwise 3 is the default.
3. **States, not one pretty composite.** One board per real state (section 5).
4. **Original palette and type on top of borrowed structure.** Never copy a reference's visual
   identity verbatim (section 2, `references/anti-slop.md`).
5. **Generate, do not hand-pick, color and scales.** Run `scripts/palette.py` (one hue, one scheme, one
   mood) and `scripts/scales.py`, paste the output into `:root`. Hand-edited values are re-audited.
6. **Pass the slop gate.** `scripts/slop-lint.py <canvas>` must score >= 70 with no unexplained `high`
   flag before you show anything. A flag you keep needs a one-line justification on the Reference board.
7. **Write the concept sentence** (design-language.md section 1) before the first board. Every later
   decision must be explainable by it.
8. **Look at your own output.** Screenshot every board (`scripts/shoot.sh`), open the PNGs, fix
   what is clipped, overlapping, low-contrast or empty before showing anything. Never claim it
   looks right without having looked.
9. **No implementation before approval.** The mockup is the deliverable of this turn. Do not edit
   the real source until the user picked a direction (unless they said to implement).
10. **Never publish or push** a mockup anywhere without being asked in that turn. Local file or a
   private Artifact only.
11. **Reply in the user's language** (Turkish if they write Turkish). Keep text on the boards in
   the language the product will ship in.
12. **Deliver a canvas, not a page.** Non-Claude agents' output must open as the pan/zoom canvas (`check-done.py` verifies the runtime boots).
13. **Verify before you cite.** A color, duration or easing you attribute to a reference must come
   from its source or a measured screenshot, not memory. Label anything invented as "proposed".

## 0. Pick the output path

- **Claude Code** (you have the `Artifact` tool): call `Artifact` with `action: "quickstart"`,
  `intent: "design"` and build a Design canvas Artifact (`.dc.html` artboards) per that type's own
  instructions. Load the `artifact-design` skill if the quickstart does not. Keep it private.
  Still run section 8 checks on a local copy where possible.
- **Any other agent**: write ONE self-contained `.html` file that is a **pan/zoom infinite canvas**, the
  same experience as Claude's Design canvas: boards laid out on a dark endless surface, each with a title,
  an expand button and a download button; drag to pan, ctrl+wheel or pinch to zoom, double-click to fit all,
  `F` to focus a board, a "Tahtalar" list to jump around. Do not hand-roll a long scrolling page.
  `python3 scripts/new-canvas.py --title "<name>" --out design/<topic>-mockup.html --boards
  "idle:360x120,hover:360x120,expanded:360x420,settings:420x520"` creates it with the runtime inlined; fill each
  board. If you already wrote a page by hand, mark every board `data-board="<id>"` and run
  `python3 scripts/canvasify.py design/<topic>-mockup.html` (safe to re-run). Inline CSS/JS only, no build step.
  Give the user the file path, and say how to move: drag, ctrl+wheel, F, Esc, 0 (fit), the "Tahtalar" list.
  Open it with `xdg-open` only if the user is at the machine and said so.

Both paths use the same boards and rules below.

## 1. Ground it in a real reference

Order of preference:
1. What the user pointed at (repo, screenshot, app name, URL).
1b. The user's own machine: for a desktop/Linux widget look in `~/.config/quickshell*`, `~/.config/waybar`,
   `~/.config/hypr`, `~/.config/*/theme*`; for apps, sibling projects in `~/Desktop` and `~/`. Real theme
   tokens and a real bar that already exist beat any public reference.
2. The closest component **in the same codebase** (settings panel, popup, stats view).
3. A well-known real product in the same space, studied from its source or screenshots.
4. Nothing: state the palette and type plan explicitly (hard rule 1).

When a source tree exists, **read it, do not skim file names**. Run
`python3 scripts/extract-tokens.py <dir>` for the proven values, then open the 2-3 files that do
the closest job. Capture: color system (exact values, light and dark), radius scale, spacing scale,
transition durations and easing curves, hover/press behavior, any existing pattern for the
interaction being designed. Details and greps in `references/grounding.md`.

Write the findings down in 6-10 lines at the top of your reply or on a "Reference" board: *what
was borrowed (structure, timings) and what is deliberately new (palette, type)*.

## 2a. Build the design language
1. Concept sentence + one bold move (`references/design-language.md`).
2. `python3 scripts/palette.py --hue <H> --mood <calm|crisp|warm|dense> --scheme <mono|analogous|split|triad> --css design/palette.css --preview design/palette.html`
   (or `--from-hex` a reference color). Pick the hue from the subject (`references/color-harmony.md`).
3. `python3 scripts/scales.py --target <widget|app|web|mobile> --density <compact|normal|airy> --css design/scales.css`.
4. Choose fonts (`references/fonts.md`), draw the icon set at one stroke weight.
5. Paste palette and scales into the canvas `:root`. Components use tokens only.
For several options, differ by structure (`references/option-archetypes.md`); one palette family per concept.

## 2. Borrow structure, never identity

Reuse translucency, radius scale, spacing, hairlines, ecosystem conventions. Then design an
original palette and type pairing. Read `references/anti-slop.md` now. Short version:

- No blue/purple "AI/SaaS" accent unless the subject calls for it. Warm golds, brick reds, moss
  greens, ink-teal, bone-white-on-near-black, or strict monochrome read as deliberate.
- No dark-ground + neon-green/teal + glowing dots + tiny mono micro-labels + card grid. The user
  has rejected that exact dashboard three times.
- Never Inter, Roboto, Arial, system-ui as the *chosen* face. Pick a real one (`references/fonts.md`).
- One consistent stroke weight for custom icons. No emoji as icons or section markers.
- No gradient washes, no left-border accent cards, no `rounded-lg` on everything, no
  shadow-and-glow stacking, no lorem ipsum.
- Use **real content**: realistic names, numbers, units, timestamps, long and short strings, the
  actual product's vocabulary.

## 3. Ask only about real architecture forks

Persist vs appear-on-trigger, one control cycling states vs two independent ones, does the parent
hide while a child is open, modal vs inline, drawer vs page: these are UX decisions. Ask (use your
structured question tool if you have one; otherwise a short numbered list) with 2-4 concrete
options and a recommendation. Do not ask about pure visual taste: the boards are for that. Ask
once, up front, batched; then build.

## 4. Spec first when the user asks for detail

Write it before drawing, from `references/spec-template.md`: state machine, measurements,
motion timeline (duration and easing per stage), data per state, explicit non-goals. Mockups
illustrate the spec and must agree with it numerically. A mockup that contradicts its spec is a bug.

## 5. Boards

A canvas is a grid of fixed-size, labeled artboards at the **real size** of the thing (a 38 px bar
pill is drawn 38 px tall, not scaled up into a marketing hero). Layout: index/legend, then
Reference, then states, then motion, then system boards.

Always:
- **One board per real state**: idle, hover, pressed/focus, active/expanded, loading, empty,
  error, offline/disabled, overflow (long text, many items), first-run. Pull the surface-specific
  list from `references/surfaces.md`.
- **Motion storyboard** for any non-trivial transition: frames left to right, with `t=` offsets,
  duration and easing on each arrow, matching the spec table.
- **Font comparison board** whenever typography is in question or a face looks "plain": the same
  real sample string (including numerals, a long word, and non-ASCII such as `ğüşıöç` for Turkish
  UIs) in 6-8 candidate fonts, each labeled by name.
- **Theme picker + a re-skinned board** whenever theming applies: every accent as live swatches,
  and at least one full state board in an alternate theme. Accent-derived elements (charts,
  progress, selection) must visibly derive from the accent, not stay hardcoded.
- **Tokens board**: the final palette (with contrast ratios), type scale, radius, spacing, motion
  constants. This is what handoff reads.
- **Reference board** (when grounded): the borrowed structure vs the new identity, side by side.

Validate color before shipping: `python3 scripts/contrast.py --pairs "fg:bg ..."` for text,
`--palette` for categorical colors (chart series, heatmaps, tags). Check light and dark.

When the user asked for several options, put each option in its own **section** with the same
state set (at minimum idle, active, one edge case), so options compare like for like.

## 6. Iterate fast and narrowly

The user reacts to one thing (a color, a font, a spacing value). Change only that thing across the
affected boards. Re-read the current file first, it may have changed since your last write. Do not
regenerate unrelated boards. Keep a `CHANGELOG` comment at the top of the canvas with one line per
round.

## 7. Keep the loop going

End every round by asking which direction or element to carry forward (and offering the next
useful step: spec, edge-case boards, handoff). This is a conversation, not a one-shot delivery.
Keep the end-of-turn message short: where the file/link is, what is on the boards, what you
borrowed vs invented, the one question.

## 8. Verify before showing (always)

0. `python3 scripts/slop-lint.py design/<topic>-mockup.html` (score >= 70) and fix flags first.
1. `scripts/shoot.sh design/<topic>-mockup.html` renders every board (`?only=<id>`) at desktop
   and 390 px phone width into `design/shots/`. Open at least the idle, the busiest and the
   error board as images and read them.
2. Check: nothing clipped or overflowing its artboard, text contrast >= 4.5:1 (3:1 large text and
   UI), tap targets >= 40 px where touch applies, fonts actually loaded (not silently falling
   back), no leftover placeholder text.
3. For animation claims, make the CSS/JS prototype actually run on hover/click for the main
   transition, and time it. Static frames alone do not prove the motion works.
4. State what you could not check (e.g. "fonts rendered from local fallbacks", "not opened in a
   real browser").

## 9. Handoff (after approval)

Follow `references/handoff.md`: freeze tokens, map each board to a component, list states per
component, then implement against the board with screenshots side by side. Re-run the contrast and
screenshot scripts on the implementation. Update the spec if the build forced a change.

## Gotchas

- Test windows for a real implementation: run them on a hidden/secondary workspace or headless;
  never leave a verification window open on the user's screen and never switch their workspace.
- `~/.agents/skills/` is the single source of truth. The Claude, opencode, Gemini and Codex skill
  folders are symlinks to it; edit here only.
- If the user says an option "looks like AI slop" again, stop iterating on the same family. Go
  back to section 1 and ask for a concrete reference.
