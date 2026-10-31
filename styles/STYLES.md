# Editing Styles

The machine-readable versions live in [`styles.json`](styles.json). The script generator uses them to time each section. Edit that file to tune a style or add your own.

| Style key | Use for | Format | Length | Shot length |
|---|---|---|---|---|
| `short-form` | Reels, TikTok, Shorts | 9:16, 1080x1920, 30 fps | ~45 s | ~1.5 s |
| `talking-head` | YouTube explainers, opinions | 16:9, 1080p, 30 fps | ~8 min | ~4 s |
| `vlog` | Day-in-the-life, travel | 16:9, 1080p, 24 fps | ~10 min | ~3 s |
| `tutorial` | How-tos, screen recordings | 16:9, 1080p, 30 fps | ~7 min | ~6 s |
| `cinematic` | Montages, travel films, promos | 16:9, 24 fps | ~90 s | ~2.5 s |

## short-form
- **Hook in 1-3 seconds.** No intros and no "hey guys."
- Big word-by-word captions. Use Kdenlive's subtitle styling, or a title clip per phrase.
- Punch-in zooms (Transform effect at 110-120%) every few cuts keep the video moving.
- Cut music to the beat. Use whooshes sparingly.
- End in a way that loops back to the start.

## talking-head
- Jump cuts remove every pause. Run `tools/cut-silence.sh` first.
- Alternate between normal and zoomed framing to hide jump cuts.
- Show a B-roll or graphic at least every 20-30 seconds.
- Keep music very low and drop it out when making a key point.

## vlog
- Open cold with the best moment.
- Use J-cuts and L-cuts: audio starts before the video, or carries over after it.
- Use a warm color grade with consistent white balance across clips.
- Use music to separate chapters.

## tutorial
- Show the final result first.
- Number every step on screen.
- Zoom into the part of the screen being clicked (Transform/Crop effect).
- Turn on subtitles by default.

## cinematic
- Music leads the edit. Mark the beats first (Kdenlive: `M` adds a marker).
- Go from wide to close to detail, then repeat.
- Use speed ramps on movement (Time Remap).
- Apply one LUT or grade to every clip for a consistent look.

## Kdenlive effects cheat sheet
| Want | Effect |
|---|---|
| Zoom / punch-in | Transform |
| Color look | LUT (Apply LUT), Lift/Gamma/Gain |
| Blur background | Box Blur / Gaussian Blur |
| Speed ramp | Right-click clip → Time Remap |
| Clean voice | Audio: Noise suppressor for voice, Compressor, Loudness |
| Text | Title clip or Subtitles track |
