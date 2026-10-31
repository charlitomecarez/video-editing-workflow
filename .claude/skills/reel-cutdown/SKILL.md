---
name: reel-cutdown
description: Use when the user wants a reel, short, TikTok or vertical clip made from an existing long-form video, especially a ~60 second summary cut from the video's own footage.
---

# Reel cutdown (long-form → 60 s summary)

The reel is **only clips from the long video**: no new recording, no new voiceover, no extra content. It summarizes the whole video in at most `[reel].max_seconds` (default 60), aiming for `[reel].target_seconds`.

Tool: `tools/reel.py` (`transcript` and `build`). Settings: `[reel]` in config.

## Process
1. **Find the source:** the final long-form export, usually `projects/<video>/export/final.mp4` (ask if there are several).
2. **Transcript:** `python3 tools/reel.py transcript <final.mp4>`. It runs Whisper if no `.srt` exists, which can take a while for long videos, so say so. Also read `script.md` to understand the video's structure and main promise.
3. **Pick segments.** The reel must work as a standalone 60-second summary:
   - **Hook (first 3-5 s):** the most striking line in the whole video. It doesn't need to be the first line.
   - **Body:** the 2-4 key points, each as complete sentences, in a logical order (usually chronological).
   - **Payoff:** the conclusion, opinion or best punchline. End on a strong line, not mid-thought.
   - Cut on transcript line boundaries, never mid-word or mid-sentence. Merge adjacent lines into one segment where possible (fewer cuts sound smoother).
   - Skip intros, sponsor reads, "subscribe" asks, and lines that only make sense with earlier context ("as I said before", "this one").
   - Keep the best jokes when they fit. They follow the personality profile, so they're already on-voice.
   - Total ≤ `max_seconds`. Add up the durations and show the math.
4. **Write `projects/<video>/reel/reel.json`** with `source` (relative to the json), `segments` (`start`, `end`, `note`) and `hook_text` (3-6 words on screen during the hook, `*word*` for accent, following the personality profile and passing the cringe check). Add `mode` only if this video needs a different one from the config (crop for a face talking to camera, blur for screens, code and graphics).
5. **Build:** `python3 tools/reel.py build projects/<video>/reel/reel.json`
6. **Check:** confirm the duration ≤ max. Pull 3 frames (start, middle, end) with ffmpeg and look at them: is the hook text readable, is the subject visible in the frame? If crop mode cuts off the important part, switch to blur and rebuild.
7. **Cover:** `tools/graphic cover-vertical --set bg=<a good frame> --set "text=<hook>" --out projects/<video>/reel/cover.png`
8. **Post text:** a short caption (hook first, then "full video on my channel"), plus 3-5 hashtags for each short-form platform in `[creator].platforms`. Add it to the Post section of `script.md` under a "Reel" heading.

## Report to the user
A table of segments (time range, length, what's said), the total length, the output files (`reel.mp4`, `reel_captioned.mp4` if captions were burned, `reel.srt`, `cover.png`), and one line on why this hook was chosen. If captions couldn't be burned in, tell them to import `reel.srt` in Kdenlive or install `ffmpeg-full`.

## Making it better in Kdenlive (optional)
For more control, the user can open `reel.mp4` in a vertical Kdenlive project (1080x1920), import `reel.srt` on the subtitle track, and add punch-in zooms or a stronger hook graphic.
