# Configuration

Almost everything is configurable without touching code.

## Where settings live
| File | What | Committed? |
|---|---|---|
| `config.toml` | Defaults for every tool | Yes |
| `config.local.toml` | **Your** overrides (only the keys you change) | No (git-ignored) |
| `styles/styles.json` | Built-in editing styles | Yes |
| `styles/custom/*.json` | Your own styles | Yes |
| `topics/niches.json` | Niches and sub-topics for the topic generator | Yes |
| `topics/formats.json` | Title templates for the topic generator | Yes |
| `.claude/skills/*/SKILL.md` | How Claude helps with each part of the workflow | Yes |
| `.claude/commands/*.md` | Slash commands (`/new`, `/topics`, `/script`, `/edit`, `/publish`, `/analyze`) | Yes |

**Precedence:** command-line flag → `config.local.toml` → `config.toml`

```bash
cp config.local.example.toml config.local.toml   # start your overrides
python3 tools/vwconfig.py show                    # see the merged result
python3 tools/vwconfig.py get subtitles.model     # one value
tools/doctor.sh                                   # check that everything is valid
```

## Config sections
| Section | Controls | Used by |
|---|---|---|
| `[creator]` | name, audience, tone, language, platforms, default niches, words to avoid | `/topics`, `/script`, topic generator, script Post/Results sections |
| `[paths]` | where projects, scripts and ideas live | all Python tools |
| `[project]` | subfolders for new projects, date prefix | `tools/new_project.py` |
| `[topics]` | default count and style | `topics/topic_generator.py` |
| `[script]` | default style, layout (`sections` / `av-table` / `auto`), speaking rate, number of hooks, included sections, checklist | `tools/script_generator.py` |
| `[prep]` | fps, quality (crf), speed (preset), loudness, audio bitrate | `tools/prep.sh` |
| `[silence]` | margin, threshold, export type | `tools/cut-silence.sh` |
| `[subtitles]` | Whisper model, language, format, line width and count | `tools/subtitles.sh` |
| `[captions]` | burned-in font, size, colors, outline, position | `tools/burn-captions.sh` |
| `[vertical]` | crop/blur mode, size, blur strength | `tools/vertical.sh` |
| `[thumbnails]` | number of frames, width | `tools/thumbnails.sh` |
| `[analyze]` | scene threshold, minimum shot length, save frames | `tools/analyze_cuts.py` |
| `[render]` | quality for re-encoding tools | vertical, burn-captions |

## Adding a style
Create `styles/custom/<anything>.json`. Use `extends` to copy an existing style and change only what's different:

```json
{
  "food-short": {
    "extends": "short-form",
    "name": "Food short (close-ups, ASMR)",
    "music": "Soft track, let cooking sounds lead",
    "avg_shot_seconds": 1.2
  }
}
```

Optional style fields: `words_per_second` (overrides `[script]`), `script_format` (`sections` or `av-table`), `visuals`, `sound_effects`.

A style without `extends` needs every field: `name, aspect, resolution, fps, target_seconds, avg_shot_seconds, captions, music, transitions, color, structure`. `structure` is a list of `[section, fraction_of_length, note]`, and the fractions should add up to 1.0.

Check it with `python3 tools/vwconfig.py style food-short`.

## Adding niches and title formats
- `topics/niches.json`: `"niche": ["sub-topic", ...]`. Sub-topics should read naturally after "tips for ___" (for example "budget meals", "home workouts").
- `topics/formats.json`: add to `short` or `long`. Use `{t}` for the topic and `{year}` for the current year.

## Per-run overrides
Every shell tool takes flags (`--help` lists them):
```bash
tools/cut-silence.sh clip.mp4 --margin 0.35s --threshold 6%
tools/subtitles.sh clip.mp4 --model medium --language tl
tools/vertical.sh clip.mp4 --mode blur --size 1080x1350
FORCE=1 tools/prep.sh clip.mov       # allow overwriting an existing output
```
