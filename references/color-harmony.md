# Color harmony

Harmony is not "nice colors". It is **few hues, shared lightness logic, tinted neutrals**.
Generate, then audit; do not hand-pick eight hexes.

```
python3 scripts/palette.py --hue 28 --mood warm --scheme analogous --name brick \
        --css design/palette.css --preview design/palette.html
python3 scripts/palette.py --from-hex "#2c5b50" --mood calm        # derive from a reference color
```
Output: light and dark token sets (`bg surface raised line text muted accent accent-soft
on-accent danger warn ok info series-1..6`), every pair auto-corrected to WCAG, with an audit.
Paste `palette.css` into `:root`; never hand-edit one value without re-running the audit.

## The system behind it (OKLCH)

OKLCH has perceptual lightness: equal L looks equally light across hues, which a hex or HSL
palette does not. All the rules use it.

1. **One hue family sets the mood.** Neutrals share the accent hue at chroma 0.003-0.010. This single
   move makes surfaces and accent feel like one material. Untinted grey next to a colored accent
   looks pasted on.
2. **60 / 30 / 10.** About 60% background neutrals, 30% surface/secondary neutrals and text, 10% accent.
   If the accent covers more than ~10% of the pixels it is no longer an accent.
3. **Chroma ceiling.** Accent chroma 0.08-0.16 on screens. Above 0.19 reads neon (`slop-lint` flags it).
   Reserve the highest chroma for one tiny signal.
4. **Lightness by role, not by hue.** Light theme: bg L 0.96, surface 0.98, line 0.88, text 0.2-0.26,
   accent 0.45-0.52. Dark theme: bg 0.17, surface +0.02, line +0.08, text 0.9, accent 0.72-0.78.
   Dark is designed, not inverted: lower contrast between surface steps, brighter accent, less chroma.
5. **Semantic colors live in the same family.** danger / warn / ok / info use the accent's lightness and
   a slightly reduced chroma, so they sit in the palette instead of shouting over it. If the accent hue is
   within 30 degrees of a semantic hue (a red accent and danger), add an icon or label; color alone cannot
   carry meaning (`palette.py` prints a note).
6. **Schemes.**
   - `mono`: one hue, lightness and chroma do all the work. Safest, most editorial.
   - `analogous` (+/-30 degrees): calm, natural; second hue for info/links.
   - `split` (150/210 degrees away): lively; use the second hue for data and tags only.
   - `triad`: loud; only for playful products, and keep two of three at low chroma.
7. **Text.** Body text >= 7:1 where possible (>= 4.5 minimum), muted >= 4.5, never lighter. Large text and UI
   outlines >= 3:1.
8. **Surfaces separate by one device.** Fill step, or hairline, or shadow. Not all three.
9. **Data colors** (`series-1..6`): same lightness band, hues spread by the golden angle, then validated with
   `contrast.py --palette` (it simulates protan/deutan/tritan). More than 6 series: switch to small
   multiples, direct labels or a sequential ramp. Pair color with shape, label or position.
10. **Sequential ramps** (heatmaps, usage): one hue, L from 0.95 to 0.35, chroma peaking mid-ramp. Diverging:
    two hues meeting at a neutral, never at white-grey with a different tint.

## Moods

| Mood | Neutral chroma | Feel | Use for |
|---|---|---|---|
| calm | 0.006 | quiet, low glare | notes, reading, health, focus |
| crisp | 0.003 | clean, high contrast | tools, editors, admin |
| warm | 0.010 | friendly, tactile | consumer, media, kitchen/home |
| dense | 0.005 | tight surface steps | data-heavy panels, TUIs |

## Subject-to-hue starting points (not rules)
Archive/finance 55-95 (ochre, olive-gold) · Nature/health 140-165 (moss, sea-green) · Terminal/dev
180-215 (ink-teal, cyan-ink) · Media/creative 25-45 (brick, coral) · Civic/legal 235 desaturated or
ink-black · Music/night 330-350 (rose) · Hardware/industrial 70-85 (safety amber) with graphite.
Avoid 255-300 unless the subject is genuinely that.

## Failure modes
- Accent chosen by taste, text colors by default: palette fights itself. Generate from one hue.
- Dark theme by inverting: surfaces collapse, accent vibrates. Rebuild with the dark column.
- Gradient to hide a weak palette. Remove it; if the flat version is dull, fix lightness steps.
- Five semantic colors at full chroma. Reduce chroma; add icons.
- Status shown only by hue. Add shape/label.
