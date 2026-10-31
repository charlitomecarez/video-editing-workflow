# Video Editing Workflow

This repo holds the workflow, editing styles and tools for making videos with Kdenlive on macOS.

## Map
- Config: `config.toml` (defaults) + `config.local.toml` (user overrides, git-ignored). Read with `python3 tools/vwconfig.py show|get|styles|style`.
- Workflow: `workflow/WORKFLOW.md`
- Styles: `styles/styles.json`, `styles/custom/*.json` (support `extends`), guide in `styles/STYLES.md`
- Topics: `topics/topic_generator.py`, `topics/niches.json`, `topics/formats.json`, saved to `topics/ideas.md`
- Scripts: `tools/script_generator.py` → `video-scripts/` or `projects/<video>/script.md`
- Projects: `tools/new_project.py` → `projects/<date>-<slug>/`
- Footage tools: `tools/prep.sh`, `cut-silence.sh`, `subtitles.sh`, `burn-captions.sh`, `vertical.sh`, `thumbnails.sh`, `doctor.sh` (all take `--help`)
- Docs: `docs/kdenlive-guide.md`, `docs/platform-specs.md`, `docs/hooks-library.md`, `docs/configuration.md`
- Skills: `.claude/skills/` (kdenlive-editing, video-scriptwriting, footage-prep, captions-subtitles, topic-research, publishing)
- Commands: `/new`, `/topics`, `/script`, `/edit`, `/publish`

## Rules
- Always respect config. Read `[creator]` before writing anything creative. Never hardcode settings that exist in config.
- Never modify or delete original footage. Tools write new suffixed files and refuse to overwrite unless `FORCE=1`.
- Media in `projects/` is git-ignored. Only `.md`, `.kdenlive` and `.srt` files there are committed. Never commit video or audio.
- Back up any `.kdenlive` file before editing it, and make sure it isn't open in Kdenlive.
- When changing a tool's behavior, add a config key for it instead of a hardcoded value, and document it in `docs/configuration.md`.
- The user is a beginner editor, so explain Kdenlive steps plainly, one at a time.
