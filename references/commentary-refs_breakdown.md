# Breakdown: meme-commentary references (added 2026-11-01)

Three videos studied for **technique only**. Don't reuse their channel names, mascots, intros, catchphrases or jokes.

| Short name     | File                                                                           |
| -------------- | ------------------------------------------------------------------------------ |
| bigboxSWE      | `Coding interviews have become insane - bigboxSWE (1080p).mp4`                 |
| CS-AI-Era      | `vidssave.com Computer Science in the AI Era 720P.mp4`                         |
| Coding Sloth   | `I Have Spent 1000+ Hours With Claude Code. This Is What I Learned - The Coding Sloth (1080p).mp4` |

Per-video stats: `<file>_cuts/report.md`. Cut threshold 0.12 for all (same as the `videoplayback` breakdown), so the numbers compare.

## Key numbers

| | bigboxSWE | CS-AI-Era | Coding Sloth | Old ref (`videoplayback`) | **Our Heat cut (faceless-v2)** |
| --- | --- | --- | --- | --- | --- |
| Length | 6:40 | 7:30 | 22:30 | 5:25 | 4:07 |
| Cuts / min | 30 | 25 | 23 | 21 | ~17 (71 graphics) |
| Avg shot | 2.0 s | 2.4 s | 2.6 s | 2.8 s | ~3.5 s |
| Median shot | **1.3 s** | 1.7 s | 1.4 s | 2.0 s | — |
| Words / s | 4.1 | 4.2 | 3.9 | 3.6 | **2.35** (Tagalog/Taglish) |
| Words per shot | 8 | 10 | 10 | 10 | ~14 |
| Face on camera | never | never | mascot only | never | never |

**Pace shape:** all three open at their fastest (bigboxSWE: 0.8 s shots for the first 40 s), slow down in the explaining middle (holds of 4–5 s on a screenshot or diagram), then speed up again at a payoff or montage.

## Hooks (first 15 s)

| Video | How it opens | Pattern |
| --- | --- | --- |
| bigboxSWE | "Oh boy, just a few years ago…" then a run of "you get rejected for X" | Nostalgia → the turn → a rapid list of pain points |
| CS-AI-Era | A ridiculous claim said straight-faced for 35 s, then "Okay, I'm just kidding" | Deadpan bait-and-switch |
| Coding Sloth | A complaint in the first sentence ("usage limits suck") | Relatable rant first, topic second |

All three: **no greeting**, and the "what this video is" line comes only after the hook (15–40 s in).

## Visual vocabulary

| Device | Who uses it | How often |
| --- | --- | --- |
| **Kinetic captions:** 1–4 words at a time, big bold rounded white text with a thick dark outline, centered on a flat charcoal background (`#1e1e1e`) | CS-AI-Era (most of the video), bigboxSWE (punchlines) | CS-AI-Era: about every other shot |
| **Inline picture in the caption:** a logo, emoji or small image sits *inside* the sentence ("If you [VS Code logo] your…", "even 🤦 if") | CS-AI-Era | Several per minute |
| **Caption over a clip:** the punchline word written over a meme/movie clip | bigboxSWE ("average 2021 cs grad") | Every joke |
| **Reaction clips:** 0.5–1.5 s movie / anime / meme clip right after a line lands | bigboxSWE, CS-AI-Era, Coding Sloth | Every 10–20 s |
| **Screenshots as receipts:** the real post / doc, with one line highlighted | bigboxSWE, Coding Sloth | During explaining |
| **Hand-drawn diagrams & stamps** (a red "no" circle drawn over a word) | bigboxSWE, CS-AI-Era | Once or twice |
| **Tier list / ranking board** as a running structure | Coding Sloth | Recurring |

## Techniques to try (and how in Kdenlive)

1. **Kinetic caption beats.** Between graphics, cut to a charcoal frame with the 1–3 key words of the line. Our graphics engine renders these as transparent PNGs; in Kdenlive put them on V3 over a charcoal color clip, each 0.4–1.0 s, cut exactly on the spoken word (zoom the timeline, scrub the waveform).
2. **Picture-in-caption.** For player names, put the player's face or team logo inside the caption ("Si [Giannis] naka-Heat jersey"). One PNG per beat.
3. **Pictures floating on charcoal.** Screenshots, photos and stats sit centered on the same charcoal as the captions, sometimes slightly tilted, so captions and pictures feel like one continuous canvas (CS-AI-Era). Kdenlive: Transform effect, scale ~80%, rotation −2° to +2°, over a charcoal color clip.
4. **Reaction-clip punctuation.** After each joke, a 0.5–1 s reaction clip, then straight back. Keep these few and short. Real movie/TV clips are a copyright risk (see notes).
5. **Fast open, breathing middle.** First 20 s: change the picture every 0.8–1.2 s. Stat explanations: hold 3–4 s but keep adding elements (number counts up, a highlight appears).

## Notes for our channel

- **Speaking rate:** your Tagalog/Taglish read is 2.35 words/s, far from these English tech channels (~4). Tagalog uses more syllables per idea, so don't chase 4 words/s. Get the energy from **cut speed**, not talking speed: aim for 4–6 words per shot.
- **Copyright:** the references use lots of movie, anime and TV clips. That's a real claim/monetization risk, and NBA footage even more so. Prefer our own generated cards, kinetic captions, your photos and licensed/free reaction clips. Keep any third-party clip under ~1 s and only as commentary.

_Lokii (`Makeine…`) was studied first and then dropped on 2026-11-01: not the style we want (anime clips framed as cards on paper/cardboard textures)._
