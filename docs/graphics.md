# Graphics: Thumbnails, Code Cards, Slates, Covers and Diagrams

One engine makes every still graphic: `tools/graphic`. It fills an HTML template with your text and images, applies your brand colors and fonts from `[brand]`, and renders a PNG using Chrome (through Playwright).

```bash
tools/graphic --list                       # all templates and their fields
tools/graphic <template> --set key=value   # render one
tools/graphic --batch jobs.json            # render many at once
```

Text fields: `*word*` turns a word the accent color, and `\n` starts a new line. Image fields take a file path and embed it automatically. Add `--open` to preview the result right away.

## Templates

| Template         | Size                  | Use                                                                              |
| ---------------- | --------------------- | -------------------------------------------------------------------------------- |
| `thumbnail-bold` | 1280x720              | Classic YouTube thumbnail: photo background, cut-out subject, huge outlined text |
| `thumbnail-tech` | 1280x720              | Dark tech thumbnail: big glowing logo, punchy text, optional emoji               |
| `cover-vertical` | 1080x1920             | Reels / TikTok / Shorts cover, text kept in the safe zone and the 4:5 grid crop  |
| `code-card`      | transparent           | Syntax-highlighted code in an editor window (Shiki, 200+ languages)              |
| `slate`          | 1920x1080 transparent | The "thing pops on screen" keyword or label (pill, box or plain style)           |
| `lower-third`    | 1920x1080 transparent | Name or source label, bottom-left                                                |
| `diagram`        | 1920x1080 transparent | Mermaid diagram (flowcharts, sequence diagrams...) in brand colors               |

Transparent PNGs go straight onto a track above your footage in Kdenlive.

## Thumbnails, step by step

```bash
# 1. Pull candidate frames from your video
tools/thumbnails.sh projects/my-video/export/final.mp4

# 2. Cut out the subject (you, or a product) from the best frame or a photo
tools/cutout.sh projects/my-video/thumbnails/thumb_07.jpg

# 3. Compose the thumbnail
tools/graphic thumbnail-bold \
  --set "text=Stop *doing*\nthis" \
  --set bg=projects/my-video/thumbnails/thumb_03.jpg \
  --set subject=projects/my-video/thumbnails/thumb_07_cutout.png \
  --set badge=NEW \
  --out projects/my-video/thumbnails/thumbnail-a.png --open
```

**Make 2-3 versions** (different text, colors or subject) and compare them shrunk down to phone size. YouTube's "Test & compare" feature can A/B test them for you.

### What makes a thumbnail work

- **3-5 words at most.** The thumbnail and title should complement each other, not repeat.
- **One clear subject**, big. A face with a strong emotion works, and so does a bold logo.
- **High contrast.** It has to read on both dark and light YouTube themes, and when tiny.
- **Check it small.** Look at it at about 200 px wide. If you can't read it, simplify.
- Keep important things away from the **bottom-right corner**, where YouTube shows the video length.

## Code cards

```bash
tools/graphic code-card --set code=src/example.ts --out projects/x/graphics/03-code.png
tools/graphic code-card --set "code=const x = await fetch(url)" --set lang=ts --set title=api.ts
tools/graphic code-card --set code=snippet.py --set theme=dracula --set size=40 --set frame=full
```

- `frame=full` outputs a 1920x1080 transparent frame with the card centered, so every card lands in the same spot in Kdenlive.
- Keep it to 10 lines at most, so it stays readable on a phone. Use several cards for longer code.
- Themes include github-dark, dracula, one-dark-pro, tokyo-night, nord, catppuccin-mocha and more. The default comes from `[brand].code_theme`.

## Slates and labels

```bash
tools/graphic slate --set "text=*Zero* config" --out projects/x/graphics/05-zero-config.png
tools/graphic slate --set text=Rust --set icon=logos/rust.png --set style=plain
tools/graphic slate --set text=WRONG --set style=box --set pos=bottom
tools/graphic lower-third --set title="Source:" --set sub="bun.sh/docs"
```

## Diagrams (Mermaid)

```bash
tools/graphic diagram --set diagram=diagrams/auth-flow.mmd --set title="How login works"
```

`auth-flow.mmd`:

```
sequenceDiagram
  Browser->>Server: POST /login
  Server->>DB: check password
  DB-->>Server: ok
  Server-->>Browser: session cookie
```

Mermaid supports flowcharts, sequence, class, state, ER, timeline, mindmap and more. See https://mermaid.js.org. For _animated_ diagrams, use Motion Canvas ([animations.md](animations.md)).

## Batch: all the graphics for a video at once

`projects/my-video/graphics/jobs.json`:

```json
[
  { "template": "slate", "set": { "text": "*Bun*" }, "out": "01-bun.png" },
  { "template": "code-card", "set": { "code": "code/install.sh" }, "out": "02-install.png" },
  { "template": "slate", "set": { "text": "4x faster", "style": "box" }, "out": "03-faster.png" },
  {
    "template": "thumbnail-tech",
    "set": { "text": "Is Bun\n*faster?*", "icon": "logos/bun.png" },
    "out": "../thumbnails/thumb-a.png"
  }
]
```

```bash
tools/graphic --batch projects/my-video/graphics/jobs.json
```

Paths in a batch file are relative to the batch file. In Claude Code, `/graphics projects/my-video` writes this file from the See column of your script and renders everything.

## Brand (config)

`[brand]` in `config.toml` / `config.local.toml` controls every template and the animations:
`bg`, `bg2`, `fg`, `accent`, `accent2`, `font_heading`, `font_body`, `font_code`, `font_css` (web fonts), `code_theme`, `logo`.

Example with a Google Font:

```toml
[brand]
font_css = "https://fonts.googleapis.com/css2?family=Montserrat:wght@900&display=swap"
font_heading = "Montserrat, sans-serif"
accent = "#ff3d71"
logo = "brand/logo.png"
```

## Making your own template

1. Copy a folder in `graphics/templates/` and rename it.
2. Edit `template.html`:
   - `{{field}}` inserts text (escaped, with `*highlight*` and `\n` support).
   - `{{{field}}}` inserts raw values (image data, HTML).
   - `{{#field}}...{{/field}}` is shown only if the field is set.
   - Brand CSS variables are available: `var(--bg)`, `var(--accent)`, `var(--font-heading)`...
3. Edit `template.json`: `description`, `size`, `fields` (help text), `defaults`, and optionally `transparent`, `selector` (crop to an element), `code` (Shiki) or `mermaid`.
4. Test it with `tools/graphic <name> --open`.

Or ask Claude: "make a thumbnail template with a split before/after layout".
