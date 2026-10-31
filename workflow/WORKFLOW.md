# Video Workflow

From idea to posted video, using Kdenlive with Claude Code helping along the way.

## 1. Pick a topic

```bash
python3 topics/topic_generator.py --niche food -n 10 --save
```
Or in Claude Code: `/topics food`. Ideas are saved to `topics/ideas.md`. Tick one off when you use it.

## 2. Write the script

```bash
python3 tools/script_generator.py "Your chosen title" --style short-form
```
This creates a timed template in `video-scripts/`. In Claude Code, `/script <title>` writes the full script for you.
Pick the style from [`styles/STYLES.md`](../styles/STYLES.md).

## 3. Film

- Follow the shot list in the script.
- Film each line 2-3 times and keep the best take.
- Record 10 seconds of room silence (useful for noise reduction).
- Film extra B-roll. You always need more than you think.

## 4. Organize footage

Make one folder per video under `projects/` (media files are git-ignored):

```
projects/2026-11-01-budget-meals/
  footage/    raw clips
  audio/      music, voiceover
  export/     renders
  project.kdenlive
```

## 5. Prep footage

```bash
tools/prep.sh projects/<video>/footage/clip.mov        # edit-friendly H.264 + level audio
tools/cut-silence.sh projects/<video>/footage/clip_prep.mp4   # removes pauses -> .kdenlive
```

## 6. Edit in Kdenlive

1. Open the `_cut.kdenlive` file, or start a new project with the profile from your style.
2. Review the auto cuts and fix any that are too tight.
3. Add B-roll, on-screen text, music and transitions per the style's editing notes.
4. Turn on proxies for smooth playback (Project Settings → Proxy).

## 7. Subtitles

```bash
tools/subtitles.sh projects/<video>/export/draft.mp4 small en
```
Import the `.srt` file in Kdenlive from the Subtitles menu, then fix any wrong words.

## 8. Export

- Project → Render → **MP4 – H264/AAC**.
- Need a vertical version? Run `tools/vertical.sh export/final.mp4 blur`.
- Watch the full render once before posting.

## 9. Post and review

- Fill in the "Post" section of the script file (title, description, tags).
- Set the script's status to `posted`.
- After about 7 days, write down views and retention in the script file to learn what works.
