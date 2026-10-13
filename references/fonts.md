# Fonts

Pick by mood, test with real strings. Check what is installed first: `fc-list : family | sort -u | rg -i "<name>"`.
For the HTML canvas, load web fonts from Google Fonts or Fontsource, but **always** give a
fallback stack and confirm in the screenshot that the intended face really rendered (a silent
fallback makes the font board lie). Offline-safe: reference only installed families, or embed
the woff2 as a base64 `@font-face` (keep the canvas under ~3 MB).

## UI faces (body, labels)
| Mood | Candidates |
|---|---|
| Neutral, precise | IBM Plex Sans, Public Sans, Instrument Sans, Figtree |
| Warm humanist | Source Sans 3, Nunito Sans, Mulish, Lexend |
| Editorial / bookish | Newsreader, Source Serif 4, Literata, Fraunces |
| Technical, compact | Geist, Manrope, DM Sans, Schibsted Grotesk |
| Rounded, friendly | Quicksand (light use), Varela Round, M PLUS Rounded 1c |
| Pixel / retro | Silkscreen, Pixelify Sans, VT323, Press Start 2P (display only) |

## Display / hero numbers
| Mood | Candidates |
|---|---|
| Characterful grotesque | Bricolage Grotesque, Familjen Grotesk, Space Grotesk (sparingly) |
| Display serif italic | Instrument Serif, Playfair Display, DM Serif Display, Fraunces italic |
| Condensed impact | Barlow Condensed, Oswald, Big Shoulders Display, Anton |
| LED / segmented | DSEG7, Orbitron (sparingly), Share Tech Mono |
| Handwritten accent | Caveat, Kalam (sparingly, never for data) |

## Mono (code and aligned numbers only)
JetBrains Mono, IBM Plex Mono, Commit Mono, Geist Mono, Recursive Mono. If numbers just need to
align, prefer a UI face with `font-variant-numeric: tabular-nums` over mono.

## Pairings that work
- IBM Plex Sans + Instrument Serif italic numerals (technical, with a human voice)
- Public Sans + Fraunces (civic, editorial)
- Geist + Instrument Serif (modern tool, one expressive moment)
- Literata + IBM Plex Mono (reading/notes tools)
- Barlow + Barlow Condensed (dense control panels)

## Turkish and wide-script check
Every face on the font board must render `ĞÜŞİÖÇ ğüşıöç` and `İstanbul ılık`. If the glyphs fall
back, cross the face out. For CJK/Arabic/Cyrillic products, pick faces with that coverage first.

## Font board recipe
Same sample string in 6-8 faces, each in a row: face name (in a neutral face), the sample at
body size, at display size, a numeral run `0123456789 1,284.50`, and the Turkish check. Use the
product's real strings. Mark the recommended face; the user still picks by looking.
