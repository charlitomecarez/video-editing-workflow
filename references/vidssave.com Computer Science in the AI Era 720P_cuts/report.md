# Cut analysis: vidssave.com Computer Science in the AI Era 720P.mp4

- **Duration:** 7:29.8 (449.8s)
- **Shots:** 189 (188 cuts) → **25 cuts per minute**
- **Shot length:** average **2.38s**, median 1.67s, shortest 0.17s, longest 23.62s
- Settings: threshold 0.12, min shot 0.15s

> Scene detection catches hard cuts and big visual changes. Text or graphics popping onto an unchanged background may not count as a cut, so a graphics-heavy video can feel faster than these numbers. Try `--threshold 0.2` to catch more.

## Speaking rate

- **1860 words** in 447s of speech → **4.16 words/second** (250 wpm)
- Over the full video: 4.14 words/second
- About 9.8 words per shot

## Pace over the video

| Part | Time | Cuts | Avg shot |
|---|---|---|---|
| 0-10% | 0:00.0–0:45.0 | 15 ████████ | 2.88s |
| 10-20% | 0:45.0–1:30.0 | 20 ██████████ | 2.17s |
| 20-30% | 1:30.0–2:14.9 | 14 ███████ | 3.26s |
| 30-40% | 2:14.9–2:59.9 | 32 ████████████████ | 1.40s |
| 40-50% | 2:59.9–3:44.9 | 20 ██████████ | 2.11s |
| 50-60% | 3:44.9–4:29.9 | 9 ████ | 5.24s |
| 60-70% | 4:29.9–5:14.8 | 18 █████████ | 2.42s |
| 70-80% | 5:14.8–5:59.8 | 17 ████████ | 2.78s |
| 80-90% | 5:59.8–6:44.8 | 20 ██████████ | 2.26s |
| 90-100% | 6:44.8–7:29.8 | 23 ████████████ | 1.85s |

## Shot lengths

```
  0-0.5s   37 █████████████████████
  0.5-1s   26 ███████████████
    1-2s   49 ████████████████████████████
    2-4s   52 ██████████████████████████████
    4-8s   17 ██████████
     8s+    8 █████
```

## Longest holds (where the edit slows down)

- 3:42.0–4:05.6 (23.6s)
- 0:09.1–0:26.9 (17.8s)
- 1:27.4–1:42.2 (14.8s)
- 7:05.9–7:19.0 (13.1s)
- 3:25.3–3:37.1 (11.8s)

## Suggested style values

Put these in a custom style (`styles/custom/*.json`) to match this pacing:

```json
{
  "my-style": {
    "extends": "tech-explainer",
    "target_seconds": 450,
    "avg_shot_seconds": 1.7,
    "words_per_second": 4.16
  }
}
```

## How to study it

1. In Kdenlive, add the reference video to the timeline and import `markers.srt` (Project → Subtitles → Import Subtitle File).
2. Step through shot by shot (use the subtitle track to jump between shots).
3. For each shot, ask: **what's on screen, what's being said, and why does the cut land here?**
4. Write a few rows of a See | Hear | Notes table to reverse-engineer the script.
