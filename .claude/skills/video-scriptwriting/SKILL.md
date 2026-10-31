---
name: video-scriptwriting
description: Use when writing, rewriting or punching up a video script, hooks, voiceover, on-screen text, titles or calls to action for short-form or YouTube videos.
---

# Video scriptwriting

## Inputs to read first
- **The `personality-voice` skill and the profile at `[personality].profile`.** Every spoken word follows it. Write facts first, then voice, then humor, then the cringe check.
- `config.toml` + `config.local.toml` → `[creator]` (audience, tone, language, platforms, avoid) and `[script]` (words_per_second, hook_options)
- The style in `styles/styles.json` / `styles/custom/` → structure, timing, pacing
- `docs/hooks-library.md` for hook patterns
- Recent posted scripts in `video-scripts/` and `projects/*/script.md`, so you match the user's voice and don't repeat ideas. Check their Results tables to see what worked.

## Process
1. Create the template: `python3 tools/script_generator.py "<title>" --style <style>` (add `--project <dir>` if a project exists).
2. Write the hooks first. Each one must work in the first 1-3 seconds, with no greetings. Use different patterns (question, bold claim, result-first, mistake, curiosity gap).
3. Size the voiceover per section: words ≈ seconds × words_per_second. Stay within ±10%.
4. Each section needs voiceover, on-screen text (short, under 6 words) and specific B-roll (concrete shots, not "relevant footage").
5. Fill in the shot list, numbered in filming order (group shots by location).
6. Fill in the Post section for each platform (see `docs/platform-specs.md` for caption and tag limits).

## Script formats
- `sections`: voiceover, on-screen text and B-roll per section.
- `av-table` (3 columns: **See | Hear | Notes**): one row per beat. Change the See column whenever the Hear line names something new, and put asset links, sources and SFX in Notes. Used by `tech-explainer` styles (or `--format av-table`).
- The style's `words_per_second` overrides the config value (tech-explainer is ~3.0).

## Tech explainers
Follow `docs/tech-explainer-style.md`. Research comes first: verify facts against official docs and mark anything unverified `[CHECK]`. Include at least one real opinion or "when not to use it". Add a nerdy joke every 15-20 seconds. Never reuse another channel's catchphrases or show names.

## Writing rules
- Write for the ear: short sentences and everyday words, in the configured language and tone. "Taglish" means natural Tagalog-English code-switching.
- One idea per sentence and one point per shot.
- Open loops: tease the best tip early and pay it off later.
- Cut anything that doesn't serve the viewer. Ask "so what?" about every line.
- Write CTAs that are specific ("Comment your budget and I'll suggest a meal"), not generic ("like and subscribe").
- Never use anything in `[creator].avoid`. Never invent facts, stats or prices. Mark anything to verify with `[CHECK]`.

## Before handing over
Run `python3 tools/cringe_check.py <script>` and fix everything it flags.

## Output
Save the filled script, then show the user the hook options and the total word count vs target.
