# Video Editing Workflow

This repo holds the workflow, editing styles and tools for making videos with Kdenlive on macOS.

## Map
- Config: `config.toml` (defaults) + `config.local.toml` (user overrides, git-ignored). Read with `python3 tools/vwconfig.py show|get|styles|style`.
- Workflow: `workflow/WORKFLOW.md`
- Styles: `styles/styles.json`, `styles/custom/*.json` (support `extends`), guide in `styles/STYLES.md`
- Topics: `topics/topic_generator.py`, `topics/niches.json`, `topics/formats.json`, saved to `topics/ideas.md`
- Scripts: `tools/script_generator.py` → `video-scripts/` or `projects/<video>/script.md`
- References: `references/` (videos to study, git-ignored; reports committed)
- Projects: `tools/new_project.py` → `projects/<date>-<slug>/`
- Graphics: `tools/graphic` (templates in `graphics/templates/`, brand in `[brand]`), `tools/cutout.sh` (rembg)
- Voice: `tools/script_text.py`, `tools/voice-draft.sh` (Piper), `tools/clean-voice.sh`, `tools/teleprompter.py`
- Animations: `animations/` (Motion Canvas; scenes in `animations/src/scenes/`, brand synced to `src/brand.ts`)
- Setup: `tools/setup.sh` installs everything; `tools/doctor.sh` checks. Python tools are in `.venv/` (run `.venv/bin/...`), Node in `node_modules/`.
- Rough cut: `tools/rough_cut.py projects/<video>` matches the raw recording to the script (last full take wins), places `graphics/NN-*` and `footage/broll/NN-*` on V2 by script row, music on A2, and writes `<video>-roughcut.kdenlive` + `roughcut/` (report, srt, preview). `[rough_cut]` in config.
- Reels: `tools/reel.py` (transcript → reel.json → build) cuts a ≤60 s vertical summary from the long-form export into `projects/<video>/reel/`
- Footage tools: `tools/prep.sh`, `cut-silence.sh`, `subtitles.sh`, `burn-captions.sh`, `vertical.sh`, `thumbnails.sh`, `doctor.sh`, `analyze_cuts.py` (all take `--help`)
- Personality: `personality/` (profile, inspirations, recurring bits), `[personality]` in config, `tools/cringe_check.py`
- Docs: `docs/kdenlive-guide.md`, `docs/platform-specs.md`, `docs/hooks-library.md`, `docs/configuration.md`, `docs/tech-explainer-style.md`, `docs/graphics.md`, `docs/voice-and-recording.md`, `docs/animations.md`
- Skills: `.claude/skills/` (kdenlive-editing, video-scriptwriting, footage-prep, captions-subtitles, topic-research, publishing, reference-analysis, graphics-thumbnails, motion-graphics, voiceover, personality-voice, rough-cut, reel-cutdown)
- Commands: `/new`, `/topics`, `/script`, `/edit`, `/publish`, `/analyze`, `/record`, `/graphics`, `/thumbnail`, `/animate`, `/punchup`, `/roughcut`, `/reel`

## Rules
- Every spoken word follows the personality profile (`personality-voice` skill). Never copy other creators' catchphrases, bits or show names, only techniques.
- Always respect config. Read `[creator]` before writing anything creative. Never hardcode settings that exist in config.
- Never modify or delete original footage. Tools write new suffixed files and refuse to overwrite unless `FORCE=1`.
- Media in `projects/` is git-ignored. Only `.md`, `.kdenlive`, `.srt` and `.json` files there are committed. Never commit video or audio.
- Back up any `.kdenlive` file before editing it, and make sure it isn't open in Kdenlive.
- When changing a tool's behavior, add a config key for it instead of a hardcoded value, and document it in `docs/configuration.md`.
- After rendering any graphic, look at the PNG before saying it's done.
- The user is a beginner editor, so explain Kdenlive steps plainly, one at a time.
