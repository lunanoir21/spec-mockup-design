# Design language

A design language is a small set of **repeated decisions**. A mockup looks designed when the same
few decisions recur on every board, and looks generated when every element makes its own.

## 1. Choose the concept first (one sentence)
"A quiet instrument panel: paper surfaces, one brick accent, serif numerals." / "A fast terminal-native
tool: graphite, ochre signal, tight 4 px grid." Write it at the top of the Reference board. Every later
decision must be explainable by it. If the concept could describe any product, it is not a concept.

## 2. Hierarchy: one thing wins per view
- One dominant element per board (the number, the primary action, the current item). Everything else
  is supporting or quiet. Squint test: blur the screenshot; you should still see the dominant region.
- Build hierarchy from **size > weight > position > color**, in that order. Use color last.
- Group by proximity: space within a group is about half the space between groups (e.g. 6 vs 16-24).
- Align to a small number of edges. Every left edge that is off by 1-2 px is a bug.
- Density is a decision: widgets and panels compact (unit 3-4 px), reading apps airy (unit 4-6 px).
  `scales.py --density compact|normal|airy`.

## 3. Type
- Roles: display (hero numbers, titles), UI (labels, body), data (tabular numerals), code (mono).
- A modular scale (`scales.py`); 5-7 steps; never an ad-hoc size.
- Weight does hierarchy: 400 body, 500-600 labels, 700 only for the dominant element.
- Numbers that update: `tabular-nums`, fixed width container so layout does not jitter.
- Line length 45-75 characters; short UI lines can be tighter.
- Large display: letter-spacing -0.01 to -0.02em; small caps/labels: +0.04em.
- Sentence case for labels. Real units next to numbers, smaller and muted.

## 4. Space and shape
- 4 px base unit, ladder 4/8/12/16/24/32/48. Pick the ladder values, do not interpolate.
- Radius from element size: small controls ~30% of font size, containers ~60-100%, pills only for
  genuinely pill-shaped things. Two or three radii in the whole product.
- Borders: 1 px hairline in `--line`. Elevation: at most two levels (surface, raised). Shadows are soft,
  low-opacity, one direction (down), no colored glow.
- Touch/pointer targets: 40 px desktop minimum for primary actions, 44 pt touch.

## 5. Iconography
- One set, one stroke weight (1.5 px at 16-24 px), round caps and joins, same optical size and
  padding in a 16 or 24 grid. Draw as inline SVG with `currentColor`.
- Icons carry meaning only with a label, tooltip or an obvious convention. Do not decorate.
- No emoji. No mixed filled and outline icons in one view.

## 6. Imagery and illustration
- Draw plausible content: a believable chart with real axes, a photo-like placeholder with a caption
  describing it, avatars as initials on tinted fills. No gray boxes with an X.
- Charts: direct labels over legends, light grid, emphasized end-point, tabular numbers, accessible
  colors from `series-*`.

## 7. Motion language
- One easing family, three durations (`scales.py`): micro 120 / small 200 / large 300 ms.
- Motion explains: where it came from, where it went, what it is attached to. Same direction for the
  same action everywhere (a popup that grows from its anchor always grows from its anchor).
- Entrances ease-out, exits ease-in and shorter than entrances. Reduced motion: opacity only.

## 8. Voice
- Name things as the user does. Buttons are verbs ("Save", "Pause tracking"). Errors say what
  happened and what to do. No exclamation marks, no filler ("Oops!").
- Show real strings and locale: Turkish dates `13 Eki 2026`, decimal comma if the product ships that way.

## 9. Consistency audit (run before showing)
Pick any three boards. Do they share: the same radius scale, the same type roles, the same spacing
ladder, the same icon weight, the same state colors, the same motion curve? If not, a decision is
missing from the Tokens board; add it there and apply it.

## 10. Distinctiveness: one bold, rest quiet
Choose a single memorable move (a numeral face, an unusual layout axis, a strict monochrome with one
signal, a physical metaphor such as a ledger or a gauge) and keep everything around it plain. Boldness
spread across ten elements is noise; boldness in one place is identity.
