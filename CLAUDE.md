# Video Editing Workflow

This repo holds the workflow, editing styles and tools for making videos with Kdenlive on macOS.

## Map

- Config: `config.toml` (defaults) + `config.local.toml` (user overrides, git-ignored). Read with `python3 tools/vwconfig.py show|get|styles|style`.
- Workflow: `workflow/WORKFLOW.md`
- Styles: `styles/styles.json`, `styles/custom/*.json` (support `extends`), guide in `styles/STYLES.md`
- Topics: `topics/topic_generator.py`, `topics/niches.json`, `topics/formats.json`, saved to `topics/ideas.md`
- Scripts: `tools/script_generator.py` → `video-scripts/` or `projects/<video>/script.md`; `tools/script_view.py <script.md>` renders it as a readable HTML page (`<name>_view.html`, git-ignored, `[script_view]` in config)
- References: `references/` (videos to study, git-ignored; reports committed)
- Projects: `tools/new_project.py` → `projects/<date>-<slug>/`
- Graphics: `tools/graphic` (templates in `graphics/templates/`, brand in `[brand]`), `tools/cutout.sh` (rembg). Assets we can't generate (memes, screen recordings, missing photos) get a placeholder card `graphics/NN-placeholder-<what>.png`; the rough cut swaps in `NN-<what>.<ext>` when it exists (`docs/graphics.md` → Placeholders). Optional animated clips (HyperFrames, `tools/graphic --animate`, `[graphics].animate`, OFF by default: only when the user asks) go next to the PNG as `NN-x.mp4` and replace it in the rough cut
- Voice: `tools/script_text.py`, `tools/voice-draft.sh` (Piper, stock voice), `tools/voice-clone` (Chatterbox clone of the user's voice: `add me <clips>` → `say script.md`, own `.venv-voice`, `[voice_clone]`), `tools/clean-voice.sh`, `tools/teleprompter.py`
- Music: `tools/music.py` (`find`/`get` CC0 or CC BY tracks from Openverse + ccMixter with a license/credit file, `make` original loops you own, `mix` ducks music under a finished video), `[music]` in config, guide `docs/music.md`, `docs/sound-effects.md`. Rough cut puts `audio/music.*` on A2
- Sound effects: `tools/sfx.py` (`build` an original library in `sfx/`, `list`/`play`; `find`/`get` from Myinstants = rights unknown, logged in `sfx/LICENSES.md`). Cue them in a script's Notes column as `sfx:<name> on "word"`; the rough cut places them on A3 and checks the amount. Rules: `docs/sound-effects.md`, `[sfx]` in config
- Stock video + memes: `tools/stock.py` (`find`/`get` from Pexels, Pixabay, Commons = monetization-safe; `find --memes` = GIPHY, rights unknown, logged; `add` for files downloaded by hand, e.g. Tenor; `--caption` burns a photo-style caption onto the clip). Keys in `.env.local`, `[stock]` in config, guide `docs/stock-footage.md`. Clips named `NN-*.mp4` land on row NN; same name as a still replaces it
- Animations: `animations/` (Motion Canvas; scenes in `animations/src/scenes/`, brand synced to `src/brand.ts`)
- Setup: `tools/setup.sh` installs everything; `tools/doctor.sh` checks. Python tools are in `.venv/` (run `.venv/bin/...`), Node in `node_modules/`.
- Planner: `tools/planner.py` reads the Content Planner app (Appwrite, `[planner]` in config, key in `.env.local`): `current` = the video being worked on now + next step, `ideas`, `list`, `show`, `link`, `done`. `/current` uses it.
- Rough cut: `tools/rough_cut.py projects/<video>` matches the raw recording to the script (last full take wins), places `graphics/NN-*` and `footage/broll/NN-*` on V2 by script row, music on A2, and writes `<video>-roughcut.kdenlive` + `roughcut/` (report, srt, preview). `[rough_cut]` in config.
- Reels: `tools/reel.py` (transcript → reel.json → build) cuts a ≤60 s vertical summary from the long-form export into `projects/<video>/reel/`
- Footage tools: `tools/prep.sh`, `cut-silence.sh`, `subtitles.sh`, `burn-captions.sh`, `vertical.sh`, `thumbnails.sh`, `doctor.sh`, `analyze_cuts.py` (all take `--help`)
- Personality: `personality/` (profile, inspirations, recurring bits), `[personality]` in config, `tools/cringe_check.py`
- Docs: `docs/kdenlive-guide.md`, `docs/platform-specs.md`, `docs/hooks-library.md`, `docs/configuration.md`, `docs/tech-explainer-style.md`, `docs/graphics.md`, `docs/voice-and-recording.md`, `docs/animations.md`, `docs/music.md`, `docs/stock-footage.md`
- Skills: `.claude/skills/` (kdenlive-editing, video-scriptwriting, footage-prep, captions-subtitles, topic-research, publishing, reference-analysis, graphics-thumbnails, motion-graphics, voiceover, personality-voice, rough-cut, reel-cutdown)
- Commands: `/current`, `/new`, `/topics`, `/script`, `/edit`, `/publish`, `/analyze`, `/record`, `/graphics`, `/thumbnail`, `/animate`, `/punchup`, `/roughcut`, `/reel`, `/music`

## Rules

- Every spoken word follows the personality profile (`personality-voice` skill). Never copy other creators' catchphrases, bits or show names, only techniques.
- Always respect config. Read `[creator]` before writing anything creative. Never hardcode settings that exist in config.
- Never modify or delete original footage. Tools write new suffixed files and refuse to overwrite unless `FORCE=1`.
- Media in `projects/` is git-ignored. Only `.md`, `.kdenlive`, `.srt` and `.json` files there are committed. Never commit video or audio.
- Back up any `.kdenlive` file before editing it, and make sure it isn't open in Kdenlive.
- When changing a tool's behavior, add a config key for it instead of a hardcoded value, and document it in `docs/configuration.md`.
- After rendering any graphic, look at the PNG before saying it's done.
- When a command needs a video or project and none is given, use `python3 tools/planner.py current`. After finishing a planner step (e.g. `/script` → `script.draft`), tick it with `python3 tools/planner.py done <video> <step>` and say so.
- The user is a beginner editor, so explain Kdenlive steps plainly, one at a time.
