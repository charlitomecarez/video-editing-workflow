---
name: captions-subtitles
description: Use when generating, fixing, translating, styling or burning in subtitles or captions (Whisper, .srt files, Kdenlive subtitle track, burned-in captions for short-form).
---

# Captions and subtitles

## Generate
`tools/subtitles.sh <video>` uses `[subtitles]` from config (model, language, line width).
- Model: `small` is a good default. `medium` or `turbo` are better for Tagalog/Taglish or noisy audio. `tiny` is good for quick drafts.
- Set `--language` when you know it. Auto-detect sometimes picks the wrong language on short clips.
- Short-form: `--width 20 --lines 1` gives punchy one-line captions.
- The first run downloads the model. Warn the user it may take a few minutes.

## Fix
After generating, read the .srt and:
- Fix misheard names, brand names and slang, using the script in `video-scripts/` or `projects/*/script.md` as the reference.
- Keep each caption under ~2 lines and on screen for at least ~1 second.
- Don't change timestamps unless asked. Show the user a summary of corrections.

## Use in Kdenlive (editable)
Project → Subtitles → Import Subtitle File → choose the .srt. Style it in the subtitle track's settings.

## Burn in (short-form)
`tools/burn-captions.sh <video> [file.srt]` uses `[captions]` from config (font, size, colors, outline, margin_v).
- ASS colors are `&HAABBGGRR`: yellow = `&H0000FFFF`, white = `&H00FFFFFF`.
- Raise `margin_v` so captions clear the TikTok/Reels UI at the bottom (around 150-250 on 1920-tall video). See `docs/platform-specs.md`.
- Always burn into the final export, never into source footage.

## Translate
To make another language: copy the .srt, translate only the text lines (keep the numbers and timestamps), and save it as `<name>.<lang>.srt`.
