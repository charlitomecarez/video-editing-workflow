# Video Editing Workflow

My video workflow: topic ideas → script → film → edit in **Kdenlive** → subtitles → post.
It's built to be used with Claude Code.

## Requirements (macOS)

```bash
brew install --cask kdenlive
brew install ffmpeg auto-editor openai-whisper
```

## Quick start

```bash
# 1. Get topic ideas
python3 topics/topic_generator.py --niche food -n 5 --save

# 2. Create a script template for one
python3 tools/script_generator.py "3 budget meal tips nobody tells you" --style short-form

# 3. Prep footage and cut silences, then open the .kdenlive file
tools/prep.sh projects/my-video/footage/clip.mov
tools/cut-silence.sh projects/my-video/footage/clip_prep.mp4

# 4. Subtitles
tools/subtitles.sh projects/my-video/export/draft.mp4 small en
```

With Claude Code, open this folder and use `/topics`, `/script` and `/edit`.

## Layout

| Folder | What's in it |
|---|---|
| `workflow/` | Step-by-step process ([WORKFLOW.md](workflow/WORKFLOW.md)) |
| `styles/` | Editing styles ([STYLES.md](styles/STYLES.md), `styles.json`) |
| `topics/` | Topic generator, niches, saved ideas |
| `video-scripts/` | Generated video scripts |
| `tools/` | Script generator and FFmpeg / auto-editor / Whisper helpers |
| `projects/` | Your footage and Kdenlive projects (media is not committed) |
| `.claude/commands/` | Claude Code slash commands |
