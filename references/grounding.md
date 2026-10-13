# Grounding in a real reference

Goal: carry forward **proven** numbers and patterns so the mockup feels like real, considered
software for that ecosystem, then put an original identity on top.

## Step 1. Locate the reference

- User named it (repo path, app, URL, screenshot): use exactly that.
- Same codebase: find the closest-job component. `rg -il "popup|panel|settings|stats|widget" --glob '!node_modules'`.
- Same ecosystem: for Quickshell/Hyprland, other shells in `~/.config/quickshell*` and their repos;
  for apps, sibling projects in the user's home or workspace folders;
  for web the product's public CSS.
- A well-known product: study its real screenshots/CSS; do not recall values from memory.
- Nothing available: stop and ask for one (hard rule 1).

## Step 2. Pull the tokens

```
python3 scripts/extract-tokens.py <dir> [--top 25] [--json out.json]
```
Prints frequency tables for: colors (hex/rgb/hsl/QML `Qt.rgba`/`Qt.color`), durations (`duration:`,
`transition`, `animation`, `ms`, `.2s`), easings (`cubic-bezier`, `Easing.*`, `ease-*`), radii
(`radius`, `border-radius`, `rounded`), font families and sizes, spacing (`margin`, `padding`,
`spacing`, `gap`). The **most frequent** value is the system; rare values are exceptions.

Then read the 2-3 files that do the closest job. Note by hand what scripts cannot see:
- interaction states (hover/press/focus/disabled) and which property each changes;
- the structure pattern for the interaction you design (compact vs expanded, popup anchoring,
  dismiss behavior);
- existing theming mechanism (theme file, singleton, CSS variables, JSON);
- how text is truncated, how lists scroll, what the empty state says.

Useful greps:
```
rg -n "Behavior on|NumberAnimation|easing\.type|duration" --glob '*.qml'
rg -n "transition|animation|@keyframes|cubic-bezier" --glob '*.{css,scss,tsx,jsx,vue,svelte}'
rg -n "Qt.rgba|color:\s*\"#|palette\.|Theme\.|Colors\." --glob '*.qml'
rg -n "--[a-z-]+:\s*#" --glob '*.css'
```

## Step 3. From a screenshot

If you only have an image: open it with the image viewer tool, then measure, do not eyeball.
Sample colors with `magick image.png -format '%[pixel:p{x,y}]' info:` (ImageMagick) or Python PIL
`Image.open(f).getpixel((x,y))`. Measure heights/paddings in pixels at 1x, state the screenshot
scale. Mark every measured value "measured" and every guess "estimated".

## Step 4. Write the Reference summary

6-10 lines, put it on the Reference board and in your reply:

```
Reference: <name/path>   (read: <files>)
Borrowed:  radius scale 6/10/16, popup anchored under bar, 180 ms ease-out-cubic open,
           hover = surface +1 step, spacing unit 4
New:       palette (paper & ink, accent #a3361c), type (<UI face> + <display face>), icon set
Proposed (not in reference): empty state copy, error board, motion for reduced-motion
```

## Step 5. Boundaries

- Reuse **structure and numbers**; do not copy logos, brand colors, bespoke illustrations, or
  copyrighted assets.
- If the reference has a light and dark variant, design both from the start.
- If the reference contradicts what the user asked, say so in one line and follow the user.
