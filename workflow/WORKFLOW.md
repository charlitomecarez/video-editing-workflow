# Video Workflow

From idea to posted video, using Kdenlive with Claude Code helping along the way.
Shortcut: `/new "your idea"` in Claude Code covers steps 1-3.

## 1. Pick a topic

```bash
python3 topics/topic_generator.py --niche food -n 10 --save
```
Or `/topics food` in Claude Code for ranked, researched ideas. Ideas are saved to `topics/ideas.md`. Tick one off when you use it.

## 2. Create the project

```bash
python3 tools/new_project.py "Your chosen title" --style short-form --script
```
This creates `projects/<date>-<title>/` with `footage/ audio/ graphics/ export/ thumbnails/`, a `notes.md` and a `script.md`. Pick a style from [`styles/STYLES.md`](../styles/STYLES.md).

## 3. Write the script

`/script "Your chosen title"` fills in the hooks, voiceover, B-roll, shot list and post captions.
Patterns are in [`docs/hooks-library.md`](../docs/hooks-library.md). Your voice and humor come from [`personality/bestfriend.md`](../personality/bestfriend.md). Run `/punchup` to add jokes, and `tools/cringe_check.py` catches corny lines.

## 3b. Prepare to record

`/record projects/<video>` checks the script length, offers a draft AI voice (`tools/voice-draft.sh`) and opens the teleprompter (`tools/teleprompter.py`). See [`docs/voice-and-recording.md`](../docs/voice-and-recording.md), including the OBS setup for screen recordings.

## 4. Film

- Follow the shot list, grouped by location.
- Flubbed a line? Pause, then say the **whole line** again. The rough cut keeps the last full take.
- Record 10 seconds of room silence (useful for noise reduction).
- Film extra B-roll. You always need more than you think.
- Vertical styles: frame inside the safe zones ([`docs/platform-specs.md`](../docs/platform-specs.md)).

## 5. Prep footage

Copy your clips into `projects/<video>/footage/`, then:
```bash
tools/prep.sh projects/<video>/footage/*.MOV                    # edit-friendly, levelled audio
tools/cut-silence.sh projects/<video>/footage/talk_prep.mp4     # pauses removed -> .kdenlive
```
Or run `/edit projects/<video>`.

## 5b. Graphics and animations

- `/graphics projects/<video>` renders the slates, code cards and diagrams from the script into `graphics/`.
- `/animate "..."` creates Motion Canvas scenes for anything that should move (animated code, diagrams).
- Clean the voiceover: `tools/clean-voice.sh audio/voice.wav`, then `tools/cut-silence.sh audio/voice_clean.wav --margin 0.1s`.

## 5c. Auto rough cut

Put B-roll in `footage/broll/` and images in `graphics/`, named with the script row they belong to (`05-typing.mp4`, `08-error.png`; `any-name.mp4` for "wherever it fits"). Music goes in `audio/music.mp3`. Then:
```bash
python3 tools/rough_cut.py projects/<video>
```
Or run `/roughcut projects/<video>`. It transcribes the recording, keeps the last full take of each script line, drops false starts and long pauses, and builds `<video>-roughcut.kdenlive`: graphics/B-roll on V2 when each line is spoken, recording on V1, voice on A1, music on A2, a guide per section. Read `roughcut/report.md` and watch `roughcut/preview.mp4` first.

## 6. Edit in Kdenlive

Follow [`docs/kdenlive-guide.md`](../docs/kdenlive-guide.md):
1. Open `<video>-roughcut.kdenlive` (from 5c), or the `_cut.kdenlive` file, or start a new project with the style's profile.
2. Review the auto cuts and fix any that are too tight.
3. Add B-roll, text, music and transitions per the script's editing notes.
4. Work through the edit checklist in `script.md`.

## 7. Subtitles

```bash
tools/subtitles.sh projects/<video>/export/draft.mp4 --language en
```
- **Editable:** in Kdenlive, Project → Subtitles → Import Subtitle File.
- **Burned in (short-form):** `tools/burn-captions.sh projects/<video>/export/final.mp4`

## 8. Export

- Project → Render → **MP4-H264/AAC** → save into `export/`.
- Vertical copy: `tools/vertical.sh export/final.mp4 --mode blur`
- Watch the full render once before posting.

## 8b. Thumbnail

`/thumbnail projects/<video>` creates 3 concepts with `tools/graphic` (plus `tools/cutout.sh` for cut-out subjects). See [`docs/graphics.md`](../docs/graphics.md).

## 8c. Reel (60-second summary)

`/reel projects/<video>` turns the finished long video into a vertical reel of at most 60 seconds, using only clips from the video itself. It transcribes the export, picks the hook, key points and payoff, then builds `reel/reel.mp4` with hook text, captions and a cover.

```bash
python3 tools/reel.py transcript projects/<video>/export/final.mp4   # timestamped lines
python3 tools/reel.py build projects/<video>/reel/reel.json          # cut, 9:16, captions
```

## 9. Post

`/publish projects/<video>/export/final.mp4` checks specs, creates thumbnails (`tools/thumbnails.sh`) and writes titles and hashtags for each platform.

## 10. Review

About 7 days later, fill in the Results table in `script.md`. Claude reads these results when suggesting future topics and scripts, so the workflow learns what works for you.
