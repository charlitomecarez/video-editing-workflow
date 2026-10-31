---
name: rough-cut
description: Use when the user has recorded their raw video (or voiceover) from a script and wants it assembled into a Kdenlive timeline - best takes, graphics, B-roll and music placed - or asks for a "rough cut", "first cut", "assemble", or "do the rest" after recording.
---

# Rough cut (raw recording + script → Kdenlive project)

Tool: `python3 tools/rough_cut.py projects/<video>`. Settings: `[rough_cut]` in config. It never touches the original footage.

## What the tool does

- Transcribes the recording with Whisper (word timings, cached in `roughcut/transcript.json`).
- Matches speech to the script's Hear column / Voiceover lines. Repeated lines: the **last full take** wins. False starts and chatter between takes are removed. Unscripted speech between lines (ad-libs) is kept with an orange guide unless `adlibs = "drop"`.
- Cuts pauses longer than `max_pause` inside lines and leaves `pad` around each line.
- Builds `<video>-roughcut.kdenlive`: V2 graphics/B-roll, V1 recording, A1 voice, A2 music, guides per section (purple), ad-lib (orange) and things to check (red).
- Writes `roughcut/report.md`, `roughcut/roughcut.srt` (captions on the cut timeline) and `roughcut/preview.mp4` (low-res render with Kdenlive's own engine).

## Inputs it looks for

- **Recording:** the one file in `footage/` (not `broll/`), or `audio/voice.*` for voice-only videos. It prefers `<name>_prep.mp4` for video and `<name>_clean.wav` for audio when they exist. Several recordings → ask which, then pass `--source`.
- **Materials by script row:** `graphics/NN-*.png|jpg|svg` and `footage/broll/NN-*.mp4|mov`. NN = the `#` column in av-table scripts, or the line number of the voiceover in sections scripts (`tools/script_text.py <script> --json` shows rows). Several files on one row share the row's time in name order.
- **`any-*` B-roll:** goes to the bin's "Unplaced B-roll" folder. To place it, look at a frame of each (`ffmpeg -ss 1 -i clip.mp4 -frames:v 1 /tmp/x.png`), pick the script row whose See/Hear fits best, and pass `--place any-name.mp4=07`. Explain your picks.
- **Music:** `audio/music*` (first match), looped, lowered to `music_level_db`, faded out.

## Process

1. Check the project: script has narration, one recording, list the materials and which rows they map to. Mention any file whose number doesn't match a script row.
2. If `graphics/` is missing graphics the See column asks for, offer to run `/graphics` first so they get placed too (they're already named `NN-*.png`).
3. Run the tool. The first run transcribes (about as long as the recording), so say so.
4. Read `roughcut/report.md`. Look at the preview: pull frames at a few guide positions and check the right graphic shows on the right line.
5. Report (below). If many lines are "not found": wrong script, heavy paraphrasing (try `--threshold 0.6`), or a different language (pass `--language tl` for one video, or set `[rough_cut].language`). Use the script's language: a Tagalog/Taglish script needs `--language tl`.

## Faceless videos

Styles with `"rough_cut": {"use_video": false}` (e.g. `news-explainer`) keep only the recording's audio and put a visual on every row. Use the av-table layout with one row per sentence so visuals change every 2-3 s. Rows that the normal match misses but sit between two found rows are filled in by reading order (`infer_between`) and flagged red: tell the user to check them.

A row with several visuals splits its time evenly, unless the See column names the word each one lands on: `` `10-2-19.png` text-card: 19. on "nila nineteen" ``. Cues only apply when all of a row's cues are found and at least `min_graphic_seconds` apart.

To verify sync, transcribe `roughcut/preview.mp4` with Whisper and compare when each line and cue word is heard against `report.md`. Don't trust the tool's own numbers alone.

## Placeholders

`graphics/NN-placeholder-<what>.png` are stand-ins for assets the user still has to add. When `NN-<what>.<any ext>` appears in `graphics/` or `footage/broll/`, the placeholder is skipped automatically on the next build. The report's "Placeholders still in the video" section lists what's left with times. When reporting, list them so the user knows what to add.

## Rebuilding

- If Kdenlive is running, don't overwrite a file it may have open: build a new version with `--name <new>` instead.
- The `.kdenlive` file won't be overwritten without `--force`. Before rebuilding, check whether the user has edited it in Kdenlive; if so, back it up (`cp x.kdenlive x.backup-<date>.kdenlive`) or ask.
- To use an earlier take, the user tells you the row; the report lists every take's raw time. Easiest fix is in Kdenlive (drag the clip's edges in the Clip Monitor); explain it step by step.

## Report to the user

- Length: cut vs raw, lines found / total, ad-libs kept, removed bits (one line each with why).
- Lines not found, and lines with a low match (red guides) - the user should listen to those.
- What's on V2 and what's left in the bin.
- Then the first Kdenlive steps, plainly: open the file (Finder → double-click, or Kdenlive → File → Open), press Space to play, guides are the colored flags on the ruler (Timeline → Guides to jump between them), delete an unwanted ad-lib clip with Delete, then right-click the gap → Remove Space.
