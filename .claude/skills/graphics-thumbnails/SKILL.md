---
name: graphics-thumbnails
description: Use when making or improving thumbnails, Reels/TikTok covers, code cards, slates, lower thirds, diagrams or any still graphic for a video, or when creating or editing graphic templates and brand settings.
---

# Graphics and thumbnails

Engine: `tools/graphic` (HTML templates → PNG via Chrome). Full reference: `docs/graphics.md`.
Run `tools/graphic --list` to see the current templates and fields.

## Always

- Read `[brand]` from config first. Use brand colors and fonts, and don't hardcode new ones in templates. Use `var(--accent)` etc.
- Put outputs in the project: `projects/<video>/thumbnails/` for thumbnails and covers, and `projects/<video>/graphics/NN-name.png` for in-video graphics (NN = the script row from the `#` column, so `/roughcut` places each one when its line is spoken).
- Look at every rendered PNG (Read the image) before telling the user it's done. Check that the text fits, nothing is cut off, it's readable small, and the composition is balanced.
- Never use another creator's logo, face or branding as if it were the user's own. Product logos used to discuss a technology are fine.

## Thumbnails

1. Read the script to understand the video's promise. The title and thumbnail should complement each other, not repeat.
2. Get options: frames (`tools/thumbnails.sh <video>`) or user photos. Cut out the subject with `tools/cutout.sh <img>` (the `birefnet-portrait` model is best for people).
3. Propose 3 concepts (text + layout + subject), each 3-5 words. Render them all with different text or colors so they can be compared.
4. Check them small: render with `--scale 1`, then judge at about 200 px wide. Simplify if it isn't readable.
5. The bottom-right corner gets covered by the video length. Keep it clear.

Template choice: a face or object photo → `thumbnail-bold`. A technology or tool → `thumbnail-tech`. Vertical → `cover-vertical`.

## In-video graphics (from a script)

For `tech-explainer` scripts, go through the **See** column. For each row that needs a graphic, write a batch job:

- keyword or label → `slate`
- code → `code-card` (save the code to `projects/<video>/graphics/code/NN.ext` first, max ~10 lines, `frame=full` so cards line up)
- flow or architecture → `diagram` (Mermaid)
- source or credit → `lower-third`

For other scripts (sports, recaps, reviews), read the Shots / B-roll lines the same way:

- final score or matchup → `scoreboard`
- a player's or product's numbers, a list (injuries, standings, schedule, recap) → `stat-card` (`layout=grid` or `list`, optional `photo` from the user's files)
- comparison over time (per quarter, per month) → `bar-chart`
- distance to a record or goal → `progress-bar`
- on-screen text with no other graphic → `slate`; a small credit or stat line → `lower-third`

In sections scripts NN is the voiceover row from `tools/script_text.py <script> --json`. Several graphics on one row: `NN-1-*.png`, `NN-2-*.png`, in the order they're spoken. Use only numbers from the script's source.

**Placeholders:** when a row needs something you can't generate (a meme, a reaction GIF, the user's own screen recording, a photo nobody has provided, a real clip), don't skip the row and don't fake it. Add a placeholder job: `text-card` with `variant=placeholder`, text starting with `MEME:` / `CLIP:` / `PHOTO:` / `SCREEN REC:` plus a one-line description, out `NN-placeholder-<what>.png`. Never fetch memes or other people's images from the internet. Add each placeholder to the script's **Assets you still need to add** section with the file name to save (`NN-<what>.<ext>`). Full guide: `docs/graphics.md#placeholders-assets-youll-add-later`.

Save the jobs to `projects/<video>/graphics/jobs.json`, run `tools/graphic --batch ...`, then list which file goes with which script row.

**Animated graphics are opt-in.** Render still PNGs only. Add `--animate` (or set `[graphics].animate`) only when the user asks for animated graphics in this request. Don't offer to turn it on unprompted. If it isn't installed, tell them to run `tools/setup.sh --animated-graphics`. Look at a frame from the start and the end of a few clips (`ffmpeg -ss 0.1 -i clip.mp4 -frames:v 1 x.png`). Guide: `docs/graphics.md#animated-graphics-optional-off-by-default`.

## New templates

Copy the closest template folder in `graphics/templates/`, edit `template.html` and `template.json` (description, size, fields, defaults, transparent, selector, code, mermaid), and render it with defaults to test. Document new fields in `template.json`.
