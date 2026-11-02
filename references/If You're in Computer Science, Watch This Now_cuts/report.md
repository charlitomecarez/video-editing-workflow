# Cut analysis: If You're in Computer Science, Watch This Now.mp4

- **Duration:** 3:12.4 (192.4s)
- **Shots:** 65 (64 cuts) → **20 cuts per minute**
- **Shot length:** average **2.96s**, median 2.40s, shortest 0.37s, longest 16.80s
- Settings: threshold 0.3, min shot 0.15s

> Scene detection catches hard cuts and big visual changes. Text or graphics popping onto an unchanged background may not count as a cut, so a graphics-heavy video can feel faster than these numbers. Try `--threshold 0.2` to catch more.

## Speaking rate

- **683 words** in 186s of speech → **3.66 words/second** (220 wpm)
- Over the full video: 3.55 words/second
- About 10.5 words per shot

## Pace over the video

| Part | Time | Cuts | Avg shot |
|---|---|---|---|
| 0-10% | 0:00.0–0:19.2 | 8 ████ | 2.26s |
| 10-20% | 0:19.2–0:38.5 | 10 █████ | 1.86s |
| 20-30% | 0:38.5–0:57.7 | 10 █████ | 1.84s |
| 30-40% | 0:57.7–1:17.0 | 3 ██ | 6.99s |
| 40-50% | 1:17.0–1:36.2 | 4 ██ | 4.05s |
| 50-60% | 1:36.2–1:55.4 | 8 ████ | 2.19s |
| 60-70% | 1:55.4–2:14.7 | 5 ██ | 4.43s |
| 70-80% | 2:14.7–2:33.9 | 7 ████ | 2.58s |
| 80-90% | 2:33.9–2:53.1 | 5 ██ | 3.83s |
| 90-100% | 2:53.1–3:12.4 | 4 ██ | 4.60s |

## Shot lengths

```
  0-0.5s    1 █
  0.5-1s   12 ████████████████
    1-2s   13 █████████████████
    2-4s   23 ██████████████████████████████
    4-8s   13 █████████████████
     8s+    3 ████
```

## Longest holds (where the edit slows down)

- 0:55.5–1:12.3 (16.8s)
- 3:01.9–3:12.4 (10.5s)
- 1:23.2–1:33.5 (10.3s)
- 1:52.0–1:59.0 (6.9s)
- 2:41.7–2:48.4 (6.7s)

## Suggested style values

Put these in a custom style (`styles/custom/*.json`) to match this pacing:

```json
{
  "my-style": {
    "extends": "tech-explainer",
    "target_seconds": 192,
    "avg_shot_seconds": 2.4,
    "words_per_second": 3.66
  }
}
```

## How to study it

1. In Kdenlive, add the reference video to the timeline and import `markers.srt` (Project → Subtitles → Import Subtitle File).
2. Step through shot by shot (use the subtitle track to jump between shots).
3. For each shot, ask: **what's on screen, what's being said, and why does the cut land here?**
4. Write a few rows of a See | Hear | Notes table to reverse-engineer the script.
