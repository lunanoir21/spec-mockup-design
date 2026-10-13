# Anti-slop: what to avoid and what to do instead

"AI slop" is not a style, it is the absence of a decision. Every item below is a default that
nobody chose. Replace each with a decision you can defend in one sentence.

## The blacklist

| Slop | Why it reads as slop | Do instead |
|---|---|---|
| Blue/purple gradient accent | Default of every generated SaaS page | Pick an accent from the subject: ink-teal for a terminal tool, brick/vermilion for media, ochre/gold for finance or archival, moss for calm tools, or no accent at all (monochrome + one state color) |
| Dark ground + neon green/teal + glowing dots | The "hacker dashboard" template; rejected 3x by this user | A real surface: warm paper, bone, graphite, or a dark with one *desaturated* accent and no glow |
| Tiny mono uppercase micro-labels everywhere | Fake "technical" texture | Sentence-case labels in a real UI face; mono only for actual code/numbers that must align |
| Card grid of equal rounded boxes | Layout by default | A hierarchy: one dominant region, supporting list, quiet chrome. Vary density |
| Left-border accent card | The most recognisable AI tell | Fill, weight, position or an icon carry the status |
| `rounded-lg` on everything | No radius system | A scale of 2-3 radii tied to element size (e.g. 4 / 8 / 14) |
| Inter / Roboto / Arial / system-ui as the chosen face | No type decision | A face from `fonts.md`; pair one UI face with one characterful face for hero numbers |
| Emoji as icons or section markers | Cheap and inconsistent across OS | Custom SVG icons, one stroke weight (1.5 px at 16-24 px), same cap/join |
| Gradient washes, blurred blobs, glassmorphism stacked on glass | Decoration standing in for structure | Flat fills; translucency only where the platform really does it (e.g. a compositor blur) |
| Shadow + glow + border on one element | Three effects, zero intent | Pick one separation device: border *or* shadow *or* fill step |
| Lorem ipsum, "John Doe", round numbers (1,000 / 50%) | Content nobody would have | Real names, odd numbers (1,284 / 63%), real units, real timestamps, real error strings |
| Centered hero + three feature cards + CTA | Landing-page template | Start from the product's actual first task |
| Pure `#000` on `#fff` or `#fff` on `#000` | Harsh and unconsidered | Tinted neutrals: text `#1b1a17` on `#f4f1ea`, or `#ece8df` on `#15140f` |
| Same state shown once, polished | Hides the ugly cases | Show empty, error, overflow, long text, loading, disabled |
| Perfect symmetry, equal spacing everywhere | No rhythm | Tight within groups, generous between groups (e.g. 4 / 8 vs 24 / 40) |
| Decorative stats ("99.9% uptime") | Filler | Only data the product really has |
| Placeholder rectangles for images/charts | Not a mockup | A drawn, plausible chart/image with real-looking data |

## Palette recipes (starting points, NOT defaults)

Pick **one family from the subject**, state why, derive everything from it with `scripts/palette.py`.
Agents that copy the first recipe produce the same page every time: that is second-order slop.

**Second-order slop (the clusters AI output falls into; `slop-lint` flags them as `cluster-look`):**
- warm cream background + serif display + terracotta/brick accent
- near-black background + one acid-green or vermilion pop
- hairline-ruled "broadsheet" columns in cream
- purple-to-blue gradient on white
Avoid these unless the subject truly is archival/print/etc. and you can say why.

Subject-driven families (hue = OKLCH degrees; run the generator, do not copy these hexes blindly):
- **Celadon & ink** (health, calm tools): hue 170-185, cool pale green-grey ground, deep ink-green text.
- **Concrete & signal** (hardware, system panels): hue 240 at chroma 0.004 grey ground, one amber (hue 70-80) signal.
- **Plum & brass** (music, night, media): hue 330-345 dark ground, brass accent hue 85.
- **Salt & cobalt-ink** (finance, civic, docs): cool white-blue ground, deep ink-blue accent (hue 255, low chroma), not violet.
- **Lichen & bark** (outdoors, notes): hue 120-135 muted ground, bark brown text, lichen accent.
- **Ochre on graphite** (utilities): hue 70-90 accent over a hue-tinted graphite; the least cliche dark option.
- **Rosewater & slate** (creative tools): hue 10-20 very pale ground at chroma 0.006, slate-blue text, rose accent.
- **Monochrome + one signal**: greys only (hue-tinted), a single state color for exactly one meaning.
Rule: write the hue and the reason ("measurement instrument -> concrete + amber") on the Reference board.
If your chosen family appears in the cluster list above, pick another or justify it explicitly.

Rules for any family:
1. Neutrals are **tinted** toward the accent's hue (chroma 0.005-0.02), never pure grey.
2. Text/background contrast >= 4.5:1 (`scripts/contrast.py`). Muted text still >= 4.5:1 when it carries meaning.
3. One accent, one danger, one success at most. Status never relies on hue alone: add icon or label.
4. Build the dark theme as its own design, not an inversion. Lower surface contrast steps, raise accent lightness.
5. Categorical colors (chart series, tags): at least 3 hue-distinct, lightness-varied steps, checked with `contrast.py --palette`.

## Type decisions

- Two faces max: a UI face and one display/numeric face. Optional mono for code only.
- Size scale from a ratio (1.2 or 1.25), not ad-hoc: e.g. 11 / 13 / 15 / 18 / 24 / 32.
- Tabular figures (`font-variant-numeric: tabular-nums`) for any number that updates.
- Line-height 1.4-1.55 body, 1.1-1.25 display. Letter-spacing slightly negative on large display only.
- Test with the real strings, including Turkish `İ ı Ş ş Ğ ğ Ü ü Ö ö Ç ç`, and a 40-character unbroken word.

## Motion decisions

- Durations by size: micro (hover, press) 90-140 ms, small (popover, toggle) 160-220 ms, large (panel, page) 240-360 ms.
- Easing: ease-out for entrances `cubic-bezier(0.2, 0.8, 0.2, 1)`, ease-in for exits `cubic-bezier(0.4, 0, 1, 1)`, springs only if the platform has them. Prefer *the reference's own curves*.
- Never animate for decoration. Each motion answers "where did that come from / where did it go".
- Respect reduced motion: show the state change without travel.

## Self-test before showing

Cover the logo. Could this be any of a thousand products? If yes, the palette, type or content is
still a default. Then ask: which three decisions here can I defend by pointing at the subject or
the reference? If fewer than three, keep going.
