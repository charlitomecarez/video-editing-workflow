# Cut analysis: videoplayback.mp4

- **Duration:** 5:24.8 (324.8s)
- **Shots:** 115 (114 cuts) → **21 cuts per minute**
- **Shot length:** average **2.82s**, median 2.04s, shortest 0.17s, longest 46.71s
- Settings: threshold 0.12, min shot 0.15s

> Scene detection catches hard cuts and big visual changes. Text or graphics popping onto an unchanged background may not count as a cut, so a graphics-heavy video can feel faster than these numbers. Try `--threshold 0.2` to catch more.

## Speaking rate

- **1140 words** in 321s of speech → **3.55 words/second** (213 wpm)
- Over the full video: 3.51 words/second
- About 9.9 words per shot

## Pace over the video

| Part | Time | Cuts | Avg shot |
|---|---|---|---|
| 0-10% | 0:00.0–0:32.5 | 13 ██████ | 2.48s |
| 10-20% | 0:32.5–1:05.0 | 18 █████████ | 1.74s |
| 20-30% | 1:05.0–1:37.4 | 11 ██████ | 1.50s |
| 30-40% | 1:37.4–2:09.9 | 1 █ | 25.71s |
| 40-50% | 2:09.9–2:42.4 | 11 ██████ | 2.72s |
| 50-60% | 2:42.4–3:14.9 | 7 ████ | 4.58s |
| 60-70% | 3:14.9–3:47.3 | 11 ██████ | 2.93s |
| 70-80% | 3:47.3–4:19.8 | 21 ██████████ | 1.53s |
| 80-90% | 4:19.8–4:52.3 | 13 ██████ | 2.67s |
| 90-100% | 4:52.3–5:24.8 | 8 ████ | 3.64s |

## Shot lengths

```
  0-0.5s   17 ████████████████
  0.5-1s   23 ██████████████████████
    1-2s   16 ███████████████
    2-4s   32 ██████████████████████████████
    4-8s   23 ██████████████████████
     8s+    4 ████
```

## Longest holds (where the edit slows down)

- 1:20.3–2:07.0 (46.7s)
- 2:38.9–2:50.5 (11.6s)
- 4:46.8–4:55.7 (8.8s)
- 2:57.1–3:05.8 (8.8s)
- 4:33.4–4:40.7 (7.3s)

## Suggested style values

Put these in a custom style (`styles/custom/*.json`) to match this pacing:

```json
{
  "my-style": {
    "extends": "tech-explainer",
    "target_seconds": 325,
    "avg_shot_seconds": 2.0,
    "words_per_second": 3.55
  }
}
```

## How to study it

1. In Kdenlive, add the reference video to the timeline and import `markers.srt` (Project → Subtitles → Import Subtitle File).
2. Step through shot by shot (use the subtitle track to jump between shots).
3. For each shot, ask: **what's on screen, what's being said, and why does the cut land here?**
4. Write a few rows of a See | Hear | Notes table to reverse-engineer the script.
