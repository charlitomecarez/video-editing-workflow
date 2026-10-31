---
name: voiceover
description: Use when the user is preparing to record, recording, cleaning up or timing a voiceover, wants a draft AI voice, a teleprompter, or help setting up OBS or a microphone.
---

# Voiceover

Guide: `docs/voice-and-recording.md`. Settings: `[tts]`, `[clean_voice]`, `[teleprompter]`.

## Before recording

1. Check length: `python3 tools/script_text.py <script.md> --stats`. Trim sections marked "too long" by cutting words, not by speeding up.
2. Read it for the ear: flag tongue-twisters, long sentences (over ~20 words) and words the user may stumble on. Offer rewrites.
3. Optional draft voice for timing: `tools/voice-draft.sh <script.md>`. Report the duration vs the style's `target_seconds`.
4. Teleprompter: `python3 tools/teleprompter.py <script.md>`, and remind them of the keys (Space, ↑/↓, +/-).

## After recording

1. `tools/clean-voice.sh <file>`. Use `--denoise 20` if they say the room was noisy, and `deess` if "s" sounds are harsh.
2. `tools/cut-silence.sh <file>_clean.wav --margin 0.1s` for a tight tech-explainer pace (use 0.2-0.3s for relaxed styles).
3. Optional: `tools/subtitles.sh` on the clean file, to check the read against the script (missed or changed lines).
4. Tell them to put it on A1 in Kdenlive and edit the visuals to it.

## AI voices

Piper voices are for drafts and timing. If the user wants to publish with an AI voice, mention that platforms (YouTube, TikTok) may require disclosing synthetic content, and that their own voice usually performs better for building an audience.
