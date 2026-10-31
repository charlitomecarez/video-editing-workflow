# Video Editing Workflow

This repo holds the workflow, editing styles and tools for making videos with Kdenlive.

- Workflow steps: `workflow/WORKFLOW.md`
- Styles: `styles/styles.json` (data) and `styles/STYLES.md` (guide)
- Topic ideas: `topics/topic_generator.py`, `topics/ideas.md`
- Scripts: `tools/script_generator.py` writes templates into `video-scripts/`
- Footage tools: `tools/prep.sh`, `tools/cut-silence.sh`, `tools/subtitles.sh`, `tools/vertical.sh`
- Commands: `/topics`, `/script`, `/edit`

Rules:
- Never modify or delete original footage. Write new files with suffixes (`_prep`, `_cut`, `_vertical`).
- Media lives in `projects/` and is git-ignored. Never commit video or audio files.
- Back up any `.kdenlive` file before editing it, and make sure it isn't open in Kdenlive.
- The user is a beginner editor, so explain Kdenlive steps plainly.
