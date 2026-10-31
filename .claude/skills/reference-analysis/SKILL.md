---
name: reference-analysis
description: Use when the user wants to study, break down or copy the pacing or editing style of a reference video (cut detection, shot lengths, speaking rate, structure), or turn that analysis into a custom style.
---

# Reference video analysis

## Ground rules

- Only analyze files the user already has locally. Don't download videos from platforms for them.
- The goal is learning techniques and pacing, not copying content, branding or catchphrases.

## Process

1. Run cut detection, with frames if the video is under ~5 minutes:
   `python3 tools/analyze_cuts.py <video> --frames`
2. For speaking rate, transcribe it first: `tools/subtitles.sh <video>` then rerun with `--srt <video>.srt`.
3. Read `<name>_cuts/report.md`, `cuts.csv` and look at a sample of `frames/` (beginning, middle, end).
4. Match the transcript lines to shots to reverse-engineer the structure: label each part of the video with a section name (cold open, definition, how it works...) and its timing.
5. If the cut count looks too low for a graphics-heavy video (pop-ins on a static background aren't detected), rerun with `--threshold 0.2` and say so.

## Write up for the user (plain language, beginner-friendly)

- **Pacing:** cuts per minute, average shot length, and where it speeds up or slows down
- **Speaking rate** vs their `[script].words_per_second`
- **Structure:** the sections with timestamps, and how long the hook takes
- **Visual vocabulary:** what kinds of shots appear (logos, code, memes, screen recordings, B-roll) and roughly how often
- **3-5 techniques to try**, each with how to do it in Kdenlive
- **Suggested style:** offer to save a `styles/custom/<name>.json` that `extends` the closest built-in style with the measured `avg_shot_seconds`, `target_seconds` and `words_per_second`

Save the write-up as `references/<name>_cuts/breakdown.md`.

## Comparing several references

Put the key numbers side by side in a table (duration, cuts/min, avg shot, words/s), then recommend values in between for the user's own style.
