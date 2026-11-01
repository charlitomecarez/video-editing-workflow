# Cut analysis: Coding interviews have become insane - bigboxSWE (1080p).mp4

- **Duration:** 6:40.1 (400.1s)
- **Shots:** 198 (197 cuts) → **30 cuts per minute**
- **Shot length:** average **2.02s**, median 1.32s, shortest 0.16s, longest 16.96s
- Settings: threshold 0.12, min shot 0.15s

> Scene detection catches hard cuts and big visual changes. Text or graphics popping onto an unchanged background may not count as a cut, so a graphics-heavy video can feel faster than these numbers. Try `--threshold 0.2` to catch more.

## Speaking rate

- **1634 words** in 396s of speech → **4.12 words/second** (247 wpm)
- Over the full video: 4.08 words/second
- About 8.3 words per shot

## Pace over the video

| Part | Time | Cuts | Avg shot |
|---|---|---|---|
| 0-10% | 0:00.0–0:40.0 | 49 ████████████████████████ | 0.81s |
| 10-20% | 0:40.0–1:20.0 | 28 ██████████████ | 1.42s |
| 20-30% | 1:20.0–2:00.0 | 23 ████████████ | 1.74s |
| 30-40% | 2:00.0–2:40.1 | 11 ██████ | 3.53s |
| 40-50% | 2:40.1–3:20.1 | 9 ████ | 4.58s |
| 50-60% | 3:20.1–4:00.1 | 17 ████████ | 2.34s |
| 60-70% | 4:00.1–4:40.1 | 22 ███████████ | 1.78s |
| 70-80% | 4:40.1–5:20.1 | 18 █████████ | 2.24s |
| 80-90% | 5:20.1–6:00.1 | 12 ██████ | 3.48s |
| 90-100% | 6:00.1–6:40.1 | 8 ████ | 4.59s |

## Shot lengths

```
  0-0.5s   70 ██████████████████████████████
  0.5-1s   16 ███████
    1-2s   33 ██████████████
    2-4s   53 ███████████████████████
    4-8s   22 █████████
     8s+    4 ██
```

## Longest holds (where the edit slows down)

- 6:13.0–6:29.9 (17.0s)
- 3:18.5–3:29.6 (11.2s)
- 2:53.1–3:02.8 (9.7s)
- 2:28.3–2:36.8 (8.6s)
- 3:29.6–3:37.5 (7.8s)

## Suggested style values

Put these in a custom style (`styles/custom/*.json`) to match this pacing:

```json
{
  "my-style": {
    "extends": "tech-explainer",
    "target_seconds": 400,
    "avg_shot_seconds": 1.3,
    "words_per_second": 4.12
  }
}
```

## How to study it

1. In Kdenlive, add the reference video to the timeline and import `markers.srt` (Project → Subtitles → Import Subtitle File).
2. Step through shot by shot (use the subtitle track to jump between shots).
3. For each shot, ask: **what's on screen, what's being said, and why does the cut land here?**
4. Write a few rows of a See | Hear | Notes table to reverse-engineer the script.
