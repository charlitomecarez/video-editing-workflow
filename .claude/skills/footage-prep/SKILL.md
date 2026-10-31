---
name: footage-prep
description: Use when the user has raw footage to prepare, convert, inspect, cut silences from, make vertical, or otherwise process with ffmpeg / auto-editor before or after editing in Kdenlive.
---

# Footage prep

## Always
- Never modify or delete originals. The tools write new files with `_prep`, `_cut`, `_vertical` and `_captioned` suffixes.
- Show the plan and get approval before batch-processing many or large files.
- The tools refuse to overwrite outputs. Use `FORCE=1 tools/x.sh ...` only when the user agrees.
- Settings come from `config.toml` / `config.local.toml`. Pass flags for one-off changes, and suggest editing `config.local.toml` if the user wants a change every time.

## 1. Inspect
```bash
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,avg_frame_rate:format=duration -of compact "<file>"
```
Watch for:
- `r_frame_rate` ≠ `avg_frame_rate` → variable frame rate (phones). Run prep or audio will drift in Kdenlive.
- HEVC/H.265 or 10-bit HDR → prep it for smoother editing.
- Portrait vs landscape vs the style's target aspect.

## 2. Choose tools
| Situation | Tool |
|---|---|
| Phone / VFR / HEVC footage | `tools/prep.sh <files...>` |
| Talking to camera, lots of pauses | `tools/cut-silence.sh <file>` → open `_cut.kdenlive` |
| Cuts too choppy | `--margin 0.3s` or higher |
| Noisy room cuts too little | `--threshold 6%` or higher |
| Need 9:16 from 16:9 | `tools/vertical.sh <file> --mode blur` (keeps whole frame) or `crop` |
| Need subtitles | `tools/subtitles.sh <file>` (see captions skill) |
| Need thumbnail frames | `tools/thumbnails.sh <file>` |

## 3. Handy one-off ffmpeg recipes
- Trim without re-encoding: `ffmpeg -ss 00:00:10 -to 00:00:45 -i in.mp4 -c copy out.mp4`
- Extract audio: `ffmpeg -i in.mp4 -vn -c:a pcm_s16le out.wav`
- Join same-format clips: make `list.txt` with `file 'a.mp4'` lines, then `ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4`
- Speed 2x: `ffmpeg -i in.mp4 -vf setpts=0.5*PTS -af atempo=2 out.mp4`
- Compress for sharing: `ffmpeg -i in.mp4 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k out.mp4`

## 4. Finish
Tell the user exactly which file to open or import in Kdenlive and what to check first.
