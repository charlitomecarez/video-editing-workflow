# Video Editing Workflow

My video workflow: topic ideas → script → film → edit in **Kdenlive** → subtitles → reel cutdown → post → review results.
It's built to be used with Claude Code, and almost everything is configurable.

📖 **[Read the Handbook](https://claude.ai/artifact/NySxVJqmBG24KeWFLKfWKn)**: the full guide to setup, the pipeline, commands, styles, personality, graphics, voice, animation and configuration.

🤝 **[Working Together](https://claude.ai/artifact/FWN141iSxvW7d8TZepLgwW)**: who does what on each video, what to send Claude at each stage, how to hand over images and B-roll, and copy-paste messages.

## Setup (macOS)

```bash
tools/setup.sh                                   # installs everything (safe to re-run)
cp config.local.example.toml config.local.toml   # then edit: your name, niches, language, brand colors...
tools/doctor.sh                                  # check everything is installed and valid
```

What gets installed:

| Area | Tools |
|---|---|
| Editing | Kdenlive, FFmpeg, auto-editor |
| Subtitles | Whisper |
| Recording | OBS Studio, teleprompter (browser), Piper (draft AI voice) |
| Graphics | Playwright + Chrome (HTML → PNG), Shiki (code highlighting), Mermaid (diagrams), rembg (background removal) |
| Animation | Motion Canvas |

Python tools live in `.venv/` (Python 3.12 via uv) and Node packages in `node_modules/` and `animations/node_modules/`. Nothing is installed system-wide except the Homebrew packages.
`ffmpeg-full` (installed alongside the normal FFmpeg) is used to burn captions into videos and reels.

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
| `/record projects/<video>` | Length check, draft AI voice, teleprompter, then audio cleanup |
| `/graphics projects/<video>` | All slates, code cards and diagrams from the script's See column |
| `/thumbnail projects/<video>` | 3 thumbnail concepts rendered and reviewed |
| `/animate "idea"` | A Motion Canvas animation scene |
| `/reel projects/<video>` | 60-second vertical summary reel cut from the finished long video |
| `/punchup script.md` | Adds your personality and humor to a script, then removes the cringe |

Claude also loads these **skills** automatically when they're relevant: `kdenlive-editing`, `video-scriptwriting`, `footage-prep`, `captions-subtitles`, `topic-research`, `publishing`, `reference-analysis`, `graphics-thumbnails`, `motion-graphics`, `voiceover` and `personality-voice` and `reel-cutdown`.

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
python3 tools/reel.py transcript projects/<video>/export/final.mp4  # then write reel/reel.json
python3 tools/reel.py build projects/<video>/reel/reel.json      # 60 s vertical summary reel
python3 tools/analyze_cuts.py references/video.mp4 --frames     # study a reference video's editing

python3 tools/cringe_check.py projects/<video>/script.md       # flag corny / AI-sounding lines
python3 tools/teleprompter.py projects/<video>/script.md        # read while recording
tools/voice-draft.sh projects/<video>/script.md                 # draft AI voiceover for timing
tools/clean-voice.sh projects/<video>/audio/voice.wav           # denoise + level a recording

tools/graphic --list                                            # thumbnails, code cards, slates, diagrams...
tools/graphic thumbnail-tech --set "text=Is it *fast?*" --set icon=logo.png --open
tools/cutout.sh photo.jpg                                       # remove a photo's background
cd animations && npm start                                      # Motion Canvas animation editor
```

Every tool takes `--help`. Defaults come from the config, and flags override them for a single run.

## Configuration

| File | Purpose |
|---|---|
| `config.toml` | All defaults: creator profile, quality, loudness, silence detection, subtitles, caption style, vertical mode... |
| `config.local.toml` | Your personal overrides (git-ignored) |
| `styles/custom/*.json` | Your own editing styles (can `extend` built-in ones) |
| `personality/` + `[personality]` | Your on-camera voice: humor toolkit, humor level, profanity, anti-cringe blocklist |
| `[brand]` in config | Colors, fonts, logo and code theme for every graphic and animation |
| `graphics/templates/` | Thumbnail and graphic templates (HTML, easy to add your own) |
| `topics/niches.json`, `topics/formats.json` | Topic generator niches and title formats |

The full reference is in [docs/configuration.md](docs/configuration.md).

## Layout

| Folder | Contents |
|---|---|
| `workflow/` | Step-by-step process ([WORKFLOW.md](workflow/WORKFLOW.md)) |
| `docs/` | [Kdenlive guide](docs/kdenlive-guide.md), [platform specs](docs/platform-specs.md), [hooks library](docs/hooks-library.md), [configuration](docs/configuration.md), [tech explainer style](docs/tech-explainer-style.md), [graphics](docs/graphics.md), [voice & recording](docs/voice-and-recording.md), [animations](docs/animations.md) |
| `styles/` | Editing styles ([STYLES.md](styles/STYLES.md)) |
| `topics/` | Topic generator, niches, title formats, saved ideas |
| `video-scripts/` | Scripts not tied to a project yet |
| `tools/` | Generators, config loader, footage, voice and graphics tools |
| `graphics/templates/` | Graphic templates (thumbnails, covers, code cards, slates, lower thirds, diagrams) |
| `animations/` | Motion Canvas project (animated code, diagrams, titles) |
| `templates/` | Reusable Kdenlive project templates |
| `personality/` | Your voice profile, inspirations and recurring bits |
| `references/` | Reference videos to study (media not committed) and their analysis reports |
| `projects/` | One folder per video (media is not committed, so back it up separately) |
| `.claude/` | Claude Code skills and slash commands |
