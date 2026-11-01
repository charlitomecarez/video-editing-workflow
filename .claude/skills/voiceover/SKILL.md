---
name: voiceover
description: Use when the user is preparing to record, recording, cleaning up or timing a voiceover, wants a draft AI voice, a teleprompter, or help setting up OBS or a microphone.
---

# Voiceover

Guide: `docs/voice-and-recording.md`. Settings: `[tts]`, `[voice_clone]`, `[clean_voice]`, `[teleprompter]`.

## Before recording

1. Check length: `python3 tools/script_text.py <script.md> --stats`. Trim sections marked "too long" by cutting words, not by speeding up.
2. Read it for the ear: flag tongue-twisters, long sentences (over ~20 words) and words the user may stumble on. Offer rewrites.
3. Optional draft voice for timing. Prefer the user's cloned voice: `tools/voice-clone list`, and if a voice exists, `tools/voice-clone say <script.md>`. Otherwise use `tools/voice-draft.sh <script.md>` (stock Piper voice). Report the duration vs the style's `target_seconds`.
4. Teleprompter: `python3 tools/teleprompter.py <script.md>`, and remind them of the keys (Space, ↑/↓, +/-).

## After recording

1. `tools/clean-voice.sh <file>`. Use `--denoise 20` if they say the room was noisy, and `deess` if "s" sounds are harsh.
2. `tools/cut-silence.sh <file>_clean.wav --margin 0.1s` for a tight tech-explainer pace (use 0.2-0.3s for relaxed styles).
3. Optional: `tools/subtitles.sh` on the clean file, to check the read against the script (missed or changed lines).
4. Tell them to put it on A1 in Kdenlive and edit the visuals to it.

## Cloning the user's voice

When the user sends clips of their own voice: `tools/voice-clone add <name> <clips...>` (default name from `[voice_clone].voice`, usually `me`). If `.venv-voice` is missing, run `tools/setup.sh --voice-clone` first. After `add`, tell them how many seconds of speech it found (aim for 15-60 s) and suggest `tools/voice-clone ref <name>` to hear the reference. Then `say` a short `--text` test before a whole script. Generation takes about 1-2 s per second of audio on Apple Silicon, so run long scripts in the background.

To check a take, transcribe it (`whisper <wav> --model base.en`) and compare with the script. Re-roll bad rows with `--rows N --seed K`. Tuning: `--exaggeration` (energy), `--cfg-weight` (lower = slower), `--speed` (post-processing, keeps pitch). Clone only the user's own voice, or one they clearly have permission to use.

## AI voices

Piper voices are for drafts and timing. If the user wants to publish with an AI voice, mention that platforms (YouTube, TikTok) may require disclosing synthetic content, and that their own voice usually performs better for building an audience.
