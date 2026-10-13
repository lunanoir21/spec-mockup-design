# Example prompts

Paste any of these into your agent. You never need to name the skill: it loads when you ask for a design.
Replace the nouns with yours. The more real context you give (a repo path, a screenshot, an app name), the better the result.

## Start simple

1. `Design a CPU temperature widget for my status bar. Show idle, warning and critical states.`
2. `Design the main screen of a note-taking terminal app (list, preview, search).`
3. `Mock up a settings page for a music player. Give me 3 options that differ in structure, not just color.`
4. `Design a mobile screen for a water reminder app.`

## Ground it in something real

5. `Design a new "Disk" page for the app in ~/projects/monitor. Read its source and reuse its real colors, radii and animation timings. Do not modify any file in that project.`
6. `Redesign the popup of my Quickshell bar widget. Look at my existing bar config first and keep its spacing and easing.`
7. `Here is a screenshot of the app I like (path). Design our dashboard in the same spirit, but with our own palette.`

## Ask for exactly what you want

8. `Give me 10 different options for a weather widget. Each must use a different layout idea, and show idle, active and empty for every option.`
9. `Add a motion storyboard for the expand animation: frame by frame with durations and easing.`
10. `Compare 8 fonts for the headline and the numbers on this design, using the real strings including Turkish characters.`
11. `Show a light and a dark theme, and a picker with 6 accent colors that re-skin the whole board.`
12. `I only want ONE restrained direction, no options. Neutral, no neon, no gradients.`

## Iterate and finish

13. `Change only the accent color to something warmer. Leave everything else untouched.`
14. `The first option is closest. Make the hover state clearer and add the error and loading boards.`
15. `Write the detailed spec first (states, measurements, timings, non-goals), then draw the boards from it.`
16. `The design is approved. Hand it off: export the tokens as a QML Theme singleton (or CSS variables) and list the components per board.`

## Turkish

17. `Hyprland üst barım için CPU sıcaklığı ve fan hızını gösteren bir widget tasarla. Boşta, uyarı ve kritik durumlarını göster.`
18. `Kitap takip uygulaması için ana ekrana 3 seçenek tasarla. Seçenekler yapıca birbirinden farklı olsun, sadece renkte değil.`
19. `~/projeler/blackbox uygulamasına yeni bir Disk sayfası tasarla. Kaynağını oku, gerçek renk ve süreleri kullan, o klasörde hiçbir dosyayı değiştirme.`

## What you get back

A single HTML canvas (or a Design canvas in Claude Code) with one board per state, a tokens board, a slop score and screenshots,
plus a short note about what was borrowed from the reference and what is new. Open the HTML file, drag to pan,
Ctrl+wheel to zoom, press F to focus a board.
