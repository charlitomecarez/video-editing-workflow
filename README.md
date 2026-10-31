# Video Editing Workflow

My video workflow: topic ideas → script → film → edit in **Kdenlive** → subtitles → post → review results.
It's built to be used with Claude Code, and almost everything is configurable.

## Setup (macOS)

```bash
brew install --cask kdenlive
brew install ffmpeg auto-editor openai-whisper
brew install ffmpeg-full                         # optional: only for tools/burn-captions.sh
cp config.local.example.toml config.local.toml   # then edit with your name, niches, language...
tools/doctor.sh                                  # check everything is installed and valid
```

## Using it with Claude Code

Open Claude Code in this folder:

| Command | What it does |
|---|---|
| `/new "idea"` | Idea → title → project folder → full script → shot list |
| `/topics food` | Researched, ranked topic ideas saved to `topics/ideas.md` |
| `/script "title"` | Full script with hooks, voiceover, B-roll and post captions |
| `/edit projects/<video>` | Inspects and preps footage, then walks you through Kdenlive |
| `/publish export/final.mp4` | Captions, thumbnails, titles and hashtags for each platform |
| `/analyze references/video.mp4` | Breaks down a reference video's cuts, pacing and structure |

Claude also loads these **skills** automatically when they're relevant: `kdenlive-editing`, `video-scriptwriting`, `footage-prep`, `captions-subtitles`, `topic-research`, `publishing` and `reference-analysis`.

## Using the tools directly

```bash
python3 topics/topic_generator.py --niche food -n 10 --save     # topic ideas
python3 tools/new_project.py "Budget meals" --script            # project folder + script
python3 tools/script_generator.py "Title" --style tutorial      # script template only

tools/prep.sh projects/<video>/footage/*.MOV                    # edit-friendly footage
tools/cut-silence.sh projects/<video>/footage/clip_prep.mp4     # pauses removed -> .kdenlive
tools/subtitles.sh projects/<video>/export/final.mp4            # .srt with Whisper
tools/burn-captions.sh projects/<video>/export/final.mp4        # captions burned in
tools/vertical.sh projects/<video>/export/final.mp4 --mode blur # 9:16 version
tools/thumbnails.sh projects/<video>/export/final.mp4           # thumbnail candidates
python3 tools/analyze_cuts.py references/video.mp4 --frames     # study a reference video's editing
```

Every tool takes `--help`. Defaults come from the config, and flags override them for a single run.

## Configuration

| File | Purpose |
|---|---|
| `config.toml` | All defaults: creator profile, quality, loudness, silence detection, subtitles, caption style, vertical mode... |
| `config.local.toml` | Your personal overrides (git-ignored) |
| `styles/custom/*.json` | Your own editing styles (can `extend` built-in ones) |
| `topics/niches.json`, `topics/formats.json` | Topic generator niches and title formats |

The full reference is in [docs/configuration.md](docs/configuration.md).

## Layout

| Folder | Contents |
|---|---|
| `workflow/` | Step-by-step process ([WORKFLOW.md](workflow/WORKFLOW.md)) |
| `docs/` | [Kdenlive guide](docs/kdenlive-guide.md), [platform specs](docs/platform-specs.md), [hooks library](docs/hooks-library.md), [configuration](docs/configuration.md), [tech explainer style](docs/tech-explainer-style.md) |
| `styles/` | Editing styles ([STYLES.md](styles/STYLES.md)) |
| `topics/` | Topic generator, niches, title formats, saved ideas |
| `video-scripts/` | Scripts not tied to a project yet |
| `tools/` | Generators, config loader and footage tools |
| `references/` | Reference videos to study (media not committed) and their analysis reports |
| `projects/` | One folder per video (media is not committed, so back it up separately) |
| `.claude/` | Claude Code skills and slash commands |
