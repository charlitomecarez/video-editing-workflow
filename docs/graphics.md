# Graphics: Thumbnails, Code Cards, Slates, Covers and Diagrams

One engine makes every still graphic: `tools/graphic`. It fills an HTML template with your text and images, applies your brand colors and fonts from `[brand]`, and renders a PNG using Chrome (through Playwright).

```bash
tools/graphic --list                       # all templates and their fields
tools/graphic <template> --set key=value   # render one
tools/graphic --batch jobs.json            # render many at once
```

Text fields: `*word*` turns a word the accent color, and `\n` starts a new line. Image fields take a file path and embed it automatically. Add `--open` to preview the result right away.

## Templates

| Template         | Size                  | Use                                                                                                                                                              |
| ---------------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `thumbnail-bold` | 1280x720              | Classic YouTube thumbnail: photo background, cut-out subject, huge outlined text                                                                                 |
| `thumbnail-tech` | 1280x720              | Dark tech thumbnail: big glowing logo, punchy text, optional emoji                                                                                               |
| `cover-vertical` | 1080x1920             | Reels / TikTok / Shorts cover, text kept in the safe zone and the 4:5 grid crop                                                                                  |
| `code-card`      | transparent           | Syntax-highlighted code in an editor window (Shiki, 200+ languages)                                                                                              |
| `slate`          | 1920x1080 transparent | The "thing pops on screen" keyword or label (pill, box or plain style)                                                                                           |
| `lower-third`    | 1920x1080 transparent | Name or source label, bottom-left                                                                                                                                |
| `diagram`        | 1920x1080 transparent | Mermaid diagram (flowcharts, sequence diagrams...) in brand colors                                                                                               |
| `scoreboard`     | 1920x1080             | Final score or matchup in team colors, optional photo background                                                                                                 |
| `stat-card`      | 1920x1080             | Big numbers (grid) or a two-column list, optional photo on the left                                                                                              |
| `bar-chart`      | 1920x1080             | Two series side by side (e.g. points per quarter), one bar can be highlighted                                                                                    |
| `progress-bar`   | 1920x1080             | Progress toward a number (a record or goal) with the gap called out                                                                                              |
| `text-card`      | 1920x1080             | Big punchline or number, chapter title, or a dashed PLACEHOLDER for a meme to add                                                                                |
| `photo-caption`  | 1920x1080             | A photo full-frame or as a tilted card, with a bold meme-style caption                                                                                           |
| `fact-card`      | 1920x1080             | A "receipt": headline, highlighted words and the source, on a tilted paper card                                                                                  |
| `caption`        | 1920x1080             | Kinetic caption: 1-4 big rounded words on charcoal, cut on the spoken word. `[img]` puts a face or logo inside the sentence; `bg` writes it over a meme or photo |
| `paper-card`     | 1920x1080             | Any picture or existing graphic as a tilted card on crumpled paper, grid paper or cardboard. `under` = the previous card, so cards stack                         |

`caption` is the meme-commentary look (style `meme-commentary`, see `references/commentary-refs_breakdown.md`). `paper-card` can reuse every graphic you already made: `--set img=19-giannis-stats.png --set texture=charcoal`.

Transparent PNGs go straight onto a track above your footage in Kdenlive. The data templates (`scoreboard`, `stat-card`, `bar-chart`, `progress-bar`) are full-frame cards: they cover the footage while they're on screen.

List fields use `;` between items and `|` inside an item, e.g. `--set "rows=31|PTS;18|REB;10|AST"` (stat-card) or `--set "a_values=42;19;27;37"` (bar-chart).

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

## Placeholders (assets you'll add later)

Some visuals can't be generated: memes, reaction GIFs, your own screen recordings, photos you don't have yet, real game clips. Instead of leaving a hole in the edit, put a **placeholder** there: a yellow dashed card that says exactly what goes in that spot. The rough cut is complete and watchable from day one, and you swap in the real assets whenever you have them.

**Make one** (it's a `text-card` with `variant=placeholder`, named `NN-placeholder-<what>.png`):

```bash
tools/graphic text-card --set variant=placeholder \
  --set "text=MEME: someone asleep on the couch while the game is on" \
  --out projects/my-video/graphics/05-placeholder-meme-asleep.png
```

In a batch file:

```json
{
  "template": "text-card",
  "set": { "variant": "placeholder", "text": "SCREEN REC: you scrolling a streaming menu (5 s)" },
  "out": "21-placeholder-netflix-scroll.png"
}
```

Start the text with what kind of asset it is (`MEME:`, `CLIP:`, `PHOTO:`, `SCREEN REC:`) and describe it well enough that you could find or record it from that line alone.

**Replace one:** save the real file as the same name **without** `placeholder-`, with any image or video extension:

| Placeholder                             | Your file                                | Where            |
| --------------------------------------- | ---------------------------------------- | ---------------- |
| `05-placeholder-meme-asleep.png`        | `05-meme-asleep.jpg` (or `.png`, `.gif`) | `graphics/`      |
| `21-placeholder-netflix-scroll.png`     | `21-netflix-scroll.mov` (or `.mp4`)      | `footage/broll/` |
| `62-2-placeholder-netflix-callback.png` | `62-2-netflix-callback.mp4`              | `footage/broll/` |

Then rebuild with `/roughcut`. The rough cut skips any placeholder whose real file exists, so there's nothing to delete. `roughcut/report.md` lists the placeholders still in the video, with their times. The word `placeholder-` can be changed with `[rough_cut].placeholder_tag`.

The script keeps the to-do list: an **Assets you still need to add** section with one line per placeholder and the file name to save.

## Animated graphics (optional, off by default)

Graphics are still images unless you ask for movement. Turned on, each graphic also gets a short animated clip next to its PNG (`01-1-cap-42.png` → `01-1-cap-42.mp4`), made with [HyperFrames](https://github.com/heygen-com/hyperframes) (open source, Apache 2.0, runs on your Mac):

| Template     | What moves                                                                      |
| ------------ | ------------------------------------------------------------------------------- |
| `caption`    | Pops in with a quick bounce, the highlighted word gets a small punch            |
| `text-card`  | `big`: numbers count up from 0. `chapter`: slides in with a small glitch shake  |
| `scoreboard` | Teams slide in, scores count up, the loser's score dims, the photo slowly zooms |

Other templates and placeholders stay still. The movement takes about 1.5 s, then the clip holds its last frame.

```bash
tools/setup.sh --animated-graphics                                   # once (~150 MB)
tools/graphic --batch projects/my-video/graphics/jobs.json --animate  # this run only
```

Or set `[graphics].animate = true` to make it the default (`--no-animate` turns it off for one run). Each clip takes about 15–20 s to render, so a video with 120 graphics takes around 35 minutes.

The rough cut uses the `.mp4` instead of the `.png` with the same name, at the same time and with the same script cue. **To go back to stills, delete the `.mp4` files** and rebuild the rough cut.

To animate another template, add an `animate.js` next to its `template.html` (see `tools/graphics/animate.mjs` for the helpers: `tl`, `pop`, `counters`). Settings: `animate_seconds`, `animate_hold_seconds`, `animate_fps`, `animate_quality` in `[graphics]`.

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
