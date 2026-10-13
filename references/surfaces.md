# State checklists per surface

Use as a minimum. Add states the product really has. Draw at real size.

## Desktop shell bar widget / pill (Quickshell, Waybar, eww, GNOME extension)
- Idle (collapsed, in the bar with neighbors drawn so scale is honest)
- Hover / press / focus-ring
- Active data (value changing), warning, critical, no data / loading
- Expanded popup/popover (anchored, with arrow or gap), scrolled content, long text
- Settings / config surface
- Multi-monitor or narrow-bar variant, vertical bar variant if supported
- Dismiss behavior (click-outside, Esc, auto-hide delay)
- Light and dark wallpaper behind translucent surfaces

## Desktop app (Qt/QML, GTK, Electron, Tauri)
- Empty (first run), populated, loading, error/offline, long list/overflow
- Selection (single, multi), drag state, context menu, dialog/confirm, destructive confirm
- Settings (per section), about, shortcuts overlay
- Window sizes: min size, default, maximized; sidebar collapsed/expanded
- Keyboard focus order and visible focus rings
- Title bar/CSD treatment for the platform

## Website / web app
- Desktop 1440, tablet 820, phone 390 for the key page
- Nav (open/closed), hero/first-task view, content-heavy view, empty, error (404, 500, form error)
- Form: pristine, focused, filled, invalid, submitting, success
- Sticky elements, long titles, RTL or long-locale text check
- Skeleton/loading, offline, cookie/consent only if the product really has it
- Dark mode, reduced-motion note

## Mobile app
- Safe areas, status bar, home indicator; 390x844 and a small 360x640
- Tab/nav states, pull-to-refresh, empty, error, offline, permission prompt
- Sheets (half/full), keyboard-up layout, one-hand reach, tap targets >= 44 pt
- Dynamic type (larger text) check

## TUI / terminal app
- Real character grid (monospace cell, e.g. 120x32); draw boxes on the grid
- Normal, focused pane, input mode, error line, help overlay, narrow terminal (80 cols)
- 16-color safe palette plus truecolor variant; no reliance on bold/italic alone
- Key hints bar, scroll indicators, progress/spinner frames

## Tool panel / dashboard / admin
- Default view with *real-looking* data, filtered view, empty filter result, error row
- Dense table with long values, bulk selection, row action menu, detail drawer
- Loading skeleton, partial failure, stale data indicator
- Avoid dashboard-first when the first task is an action; lead with the task

## Settings / preferences
- Section list, a section with mixed control types, a destructive action, restart-required notice
- Search results in settings, reset-to-default affordance, changed-from-default marker

## Notifications / overlays / OSD
- Appear, steady, stack of 3, dismiss; urgency levels; action buttons; long text truncation
- Position per screen edge, timing and easing

## Onboarding / install flow
- Welcome, permission/setup step, progress, success, failure with recovery, skip path

## Data visualization inside any surface
- Single series, multi-series (validated palette), empty, one-point, huge-range, tooltip/hover
- Axis labels with real units, accessible non-color encoding (shape, label, direction)
