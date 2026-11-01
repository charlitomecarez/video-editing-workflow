# Cut analysis: I Have Spent 1000+ Hours With Claude Code. This Is What I Learned - The Coding Sloth (1080p).mp4

- **Duration:** 22:30.4 (1350.4s)
- **Shots:** 511 (510 cuts) → **23 cuts per minute**
- **Shot length:** average **2.64s**, median 1.38s, shortest 0.15s, longest 39.67s
- Settings: threshold 0.12, min shot 0.15s

> Scene detection catches hard cuts and big visual changes. Text or graphics popping onto an unchanged background may not count as a cut, so a graphics-heavy video can feel faster than these numbers. Try `--threshold 0.2` to catch more.

## Speaking rate

- **5188 words** in 1332s of speech → **3.89 words/second** (234 wpm)
- Over the full video: 3.84 words/second
- About 10.2 words per shot

## Pace over the video

| Part | Time | Cuts | Avg shot |
|---|---|---|---|
| 0-10% | 0:00.0–2:15.0 | 77 ██████████████████████████████████████ | 1.73s |
| 10-20% | 2:15.0–4:30.1 | 61 ██████████████████████████████ | 2.22s |
| 20-30% | 4:30.1–6:45.1 | 99 ██████████████████████████████████████████████████ | 1.36s |
| 30-40% | 6:45.1–9:00.1 | 45 ██████████████████████ | 3.02s |
| 40-50% | 9:00.1–11:15.2 | 40 ████████████████████ | 3.34s |
| 50-60% | 11:15.2–13:30.2 | 39 ████████████████████ | 3.55s |
| 60-70% | 13:30.2–15:45.2 | 54 ███████████████████████████ | 2.46s |
| 70-80% | 15:45.2–18:00.3 | 44 ██████████████████████ | 3.04s |
| 80-90% | 18:00.3–20:15.3 | 25 ████████████ | 5.47s |
| 90-100% | 20:15.3–22:30.4 | 26 █████████████ | 4.94s |

## Shot lengths

```
  0-0.5s  121 ██████████████████████████████
  0.5-1s   78 ███████████████████
    1-2s  115 █████████████████████████████
    2-4s  105 ██████████████████████████
    4-8s   55 ██████████████
     8s+   37 █████████
```

## Longest holds (where the edit slows down)

- 18:08.8–18:48.5 (39.7s)
- 21:26.5–21:47.5 (21.0s)
- 6:54.2–7:15.0 (20.8s)
- 21:07.9–21:26.5 (18.6s)
- 10:11.0–10:29.4 (18.4s)

## Suggested style values

Put these in a custom style (`styles/custom/*.json`) to match this pacing:

```json
{
  "my-style": {
    "extends": "tech-explainer",
    "target_seconds": 1350,
    "avg_shot_seconds": 1.4,
    "words_per_second": 3.89
  }
}
```

## How to study it

1. In Kdenlive, add the reference video to the timeline and import `markers.srt` (Project → Subtitles → Import Subtitle File).
2. Step through shot by shot (use the subtitle track to jump between shots).
3. For each shot, ask: **what's on screen, what's being said, and why does the cut land here?**
4. Write a few rows of a See | Hear | Notes table to reverse-engineer the script.
