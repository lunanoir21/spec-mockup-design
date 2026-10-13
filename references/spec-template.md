# Spec template

Write when the user asks for detail, when the interaction has more than ~3 states, or before any
non-trivial animation. Plain Markdown, in the project (`docs/specs/<topic>.md`) or the reply. Keep
it numeric; every claim a mockup shows must appear here with the same value.

```markdown
# <Feature> spec

## 1. Goal and non-goals
- Goal: one sentence, the user's task.
- Non-goals: explicit list (what this will NOT do, platforms not covered, features deferred).

## 2. Reference
- Source: <path/URL>, files read, what was borrowed vs new (see grounding.md).

## 3. State machine
| State | Entered by | Leaves by | Visible | Notes |
|---|---|---|---|---|
| idle | app start | hover, data change | pill 38x120 | |
| hover | pointer enter | pointer leave, click | surface +1 step | |
| expanded | click / key X | Esc, click-outside, 8 s idle | popup 360x420 | parent stays visible |
Diagram (ASCII or mermaid) if there are > 4 states or any parallel states.

## 4. Layout and measurements
Per state: size, padding, gap, radius, alignment, min/max, truncation rule, overflow rule.
Units explicit (px at 1x, or dp/pt). Anchoring: which edge, what offset.

## 5. Tokens
Colors (light and dark, with contrast ratios), type scale (face, size, weight, line-height),
radius scale, spacing unit, elevation/borders, icon size and stroke.

## 6. Motion
| Transition | Property | From -> To | Duration | Easing | Delay | Reduced motion |
|---|---|---|---|---|---|---|
| open popup | opacity, y | 0, +8 -> 1, 0 | 180 ms | cubic-bezier(.2,.8,.2,1) | 0 | fade only |

## 7. Data
For each state: fields shown, source, update rate, formatting (units, locale, rounding),
empty/null/stale/error values and what they display.

## 8. Input
Pointer, keyboard (shortcuts, focus order), touch (target sizes), scroll behavior,
accessibility labels/roles.

## 9. Edge cases
Long text, many items, zero items, error, offline, slow load, multi-monitor, small screen,
locale/RTL, high DPI.

## 10. Acceptance checks
Concrete, testable lines: "popup opens in 180 +/- 20 ms", "all text >= 4.5:1", "no clipping at
320 px width", "Esc always dismisses".

## 11. Open questions
Anything the user must decide, each with a recommended answer.
```
