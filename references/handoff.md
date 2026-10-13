# Handoff: from approved board to code

Only start after the user picked a direction (or told you to implement).

## 1. Freeze
- Copy the canvas to `design/<topic>-mockup.v<N>-approved.html`; never edit the approved copy.
- Export the Tokens board as data: `design/tokens.json` with `color.{light,dark}`, `type`, `radius`,
  `space`, `motion` (duration/easing), `icon` (size, stroke).
- Confirm the spec (`spec-template.md`) matches the boards number for number.

## 2. Map
Table: board -> component -> file. One component per reusable thing, not per board. List its
states and which tokens each state uses. Example:

| Board | Component | File | States |
|---|---|---|---|
| idle/hover/pressed | Pill | `components/Pill.qml` | idle, hover, pressed, warn |
| expanded | StatsPopup | `components/StatsPopup.qml` | closed, opening, open, closing |

## 3. Implement against tokens, not against pixels
- Create or extend the project's theme mechanism (QML singleton, CSS variables, Tailwind theme,
  Kotlin `Color` object). No hardcoded hex/ms in components.
- Match the project's conventions: file layout, naming, comment density, formatter.
- Animate with the spec's duration/easing table. Add the reduced-motion path.
- Real data wiring last; keep a fixture mode that renders every board's state so visual diffs are
  possible (`--demo-state=expanded` or equivalent).

## 4. Compare
For each board: screenshot the implementation (headless or on a hidden workspace; never leave a
test window on the user's screen, never steal focus) and put it next to the board screenshot.
Differences of 1-2 px in antialiasing are fine; wrong spacing, radius, weight or color are bugs.
Re-run `scripts/contrast.py` on the real colors.

## 5. Report
Short list: what matches, what deviates and why (platform limit, font fallback), what was not
checked. Update the spec if reality forced a change. Run the project's tests/build.

## 6. Stop here
Do not publish, push or tag. Offer the next step (edge-case boards, dark theme polish, README
screenshots) in one line.
