# Breakdown: videoplayback.mp4 (faceless tech-news explainer, 5:25)

Studied for technique only. Don't reuse the channel's show name, intro card, catchphrases or jokes.

## Key numbers

| | Reference | Our Heat vs Pacers rough cut |
| --- | --- | --- |
| Length | 5:25 | 4:17 |
| Visual changes | ~21 / min (one every **2.8 s**, median 2.0 s) at threshold 0.12. At 0.3 it reads 10/min because most changes are graphics popping over the same dark background | ~3 / min (14 graphics, camera the rest of the time) |
| Speaking rate | **3.55 words/s** (213 wpm) | ~2.35 words/s (602 words in 4:17) |
| Presenter on camera | **Never** | Most of the video |
| Captions | No full subtitles. Only meme captions and labels | none yet |

Pace by part (threshold 0.12): fast in the cold open (1.5–2.5 s per shot), one long 26 s hold for an explainer diagram at 1:37–2:10, fastest at 3:47–4:20 (1.5 s) when the receipts pile up.

## Structure (from the transcript)

| Time | Section | What happens |
| --- | --- | --- |
| 0:00–0:57 | Cold open | "Just three weeks ago…": a fast montage of headlines and clips building up the hype, then the turn ("then the market took a dump") and a run of bad-news receipts. No greeting. |
| 0:57–1:13 | The question + date stamp | Asks the one question the video answers ("is it finally cooked?"), says what you'll learn, then a short show-name card with the date. |
| 1:13–2:24 | How it works | One diagram built up piece by piece over a single background (the money loop), with a meme sticker reacting to it. This is the 26 s "hold": it doesn't feel slow because elements keep appearing. |
| 2:24–3:53 | What happened | Chronological receipts: headline → tweet → filing → highlighted line, each with a one-line joke. |
| 3:53–4:26 | So, are we cooked? | The opinion: both sides, then a clear take. |
| 4:26–5:17 | Sponsor | Screen recording of the product. |
| 5:17–5:25 | Outro | One line, end card. |

The hook is the first sentence. The "what this video is" line doesn't come until 0:57, after the viewer is already hooked.

## Visual vocabulary (55 sampled frames)

- **Receipts, about 45%:** news headlines as clean white cards, tweets, SEC filings and documents, with the key phrase **highlighted in orange**. Often tilted slightly and stacked on top of each other.
- **Memes and stock clips, about 25%:** reaction images (a goldfish, a monkey with cash), short absurd stock clips (bubble gum, money printer), each held 1–2 s.
- **People as cut-outs, about 15%:** a face cut out and placed next to a headline, with a bold outlined caption ("[LAUGHS IN CAPITALISM]").
- **Data, about 10%:** stock charts, tables, one hand-built diagram.
- **Text cards, about 5%:** "THREE WEEKS AGO…" in bold type on black, used as chapter breaks.
- **Glue:** hand-drawn arrows and circles, a pointing-hand sticker, glitch transitions between sections, everything on a near-black background.

## Techniques to try (in Kdenlive)

1. **Something new every 2–3 seconds.** Put each graphic on V2 and keep it short, 2–3 s. Above V2, add a V3 track for stickers and arrows that land *on* the graphic. Kdenlive: right-click the track header → Insert Track.
2. **Receipts with a highlight.** Screenshot the real source (the ESPN recap, the box score), crop it to one headline or line, and put a semi-transparent orange box over the key words. Kdenlive: Project → Add Color Clip (orange) on the track above, lower its opacity with the Transform effect, and resize it over the line.
3. **Stack and tilt.** Bring headline cards in one after another, each overlapping the last and rotated 2–3°. Kdenlive: Transform effect → Rotation 2–3, plus your Pop In.
4. **Build one diagram step by step** for the hardest idea (for us, the 42 → 19 quarter collapse). Put each element on its own track and start each one a beat later, all ending at the same time.
5. **Glitch between sections.** A 4–6 frame glitch on section changes only, not on every cut. Kdenlive: Effects → search "glitch" (or "Digital Noise"), applied to the first frames of the new section.

## Suggested style

```json
{
  "news-explainer": {
    "extends": "tech-explainer",
    "name": "Fast news explainer (faceless, receipts and memes)",
    "target_seconds": 300,
    "avg_shot_seconds": 2.8,
    "words_per_second": 3.0,
    "graphic_seconds": 0
  }
}
```

`words_per_second` is set at 3.0, between the reference's 3.55 and our 2.35. That's speakable without rushing, and tighter silence cuts get us part of the way there.
