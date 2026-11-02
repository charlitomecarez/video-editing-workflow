# Breakdown: "If You're in Computer Science, Watch This Now" (faceless meme-advice video, 3:12)

Studied for technique only. Don't reuse the channel's lines ("fuck around and find out" as a thesis, "75 Hard for nerds", "fun != unproductive"), its jokes or its graphics. Take the *methods* below and fill them with our own words (personality profile).

## Key numbers

| | This reference | Our config / `meme-commentary` style |
| --- | --- | --- |
| Length | 3:12 total. **2:20 of content**, then a 46 s sponsor, then 6 s outro | `target_seconds` from style |
| Hard cuts (threshold 0.3) | 20 / min, avg 2.96 s, median 2.40 s | — |
| Visual changes (threshold 0.12) | **36 / min, one every 1.66 s** (median 1.28 s) | `avg_shot_seconds` 1.7 |
| Speaking rate | **3.66 words/s** (220 wpm), 683 words | `[script].words_per_second` 2.5, style 2.6 |
| Presenter on camera | Never. Voiceover only | Never |
| Captions | No subtitles. Instead, 1-4 key words as big text cards, cut on the spoken word | Same idea (kinetic captions) |

**Why two cut numbers?** Most changes are text or stickers popping onto the same charcoal background, which the default detector (0.3) doesn't count. The real feel is the 0.12 number: **something new every 1-2 seconds.** Example: 0:55-1:12 reads as one 17 s shot at 0.3, but on screen it's a roast-bot screen recording → "pick whatever" → a game-room sticker with a handwritten "nobody else knows how to play" + arrow → "and just **build.**" → a laptop sticker → a leftovers sticker. Seven visuals, one background.

Pace by part (threshold 0.12):

| Time | Avg visual | Feel |
| --- | --- | --- |
| 0:00-0:19 | 1.6 s | Fast hook |
| 0:19-0:58 | **1.0-1.1 s** | Fastest: list of "why now" reasons, one meme per noun |
| 0:58-1:17 | 4.2 s | Slower: concrete project examples, stickers over one background |
| 1:17-1:55 | 1.1-1.7 s | Fast again: the twist + "relearn things" list |
| 1:55-2:20 | 2.5 s | Calmer payoff |
| 2:20-3:12 | 1.7-2.7 s | Sponsor, cut in the same style as the video |

## Structure (from the transcript)

| Time | Section | What happens |
| --- | --- | --- |
| 0:00-0:02 | Title echo | The title read out word by word as text cards ("if you're in" → "Computer Science" over code). Zero greeting. |
| 0:02-0:21 | Anti-hook / promise | "This isn't the part where I tell you to grind…" over a "NO" meme, then the real promise: remember why you liked coding. Ends on a tension line (big tech says don't code manually, *but* the opportunity is close). **The hook is done by 0:21.** |
| 0:21-0:46 | Why now | A list of reasons the next months are quiet: exams, holidays, finals, recruiting slows, LinkedIn influencers disappear. Each item gets its own meme or text card (~1 s each). |
| 0:46-1:17 | The advice | "Build dumb stuff, an hour or two a day." Rules out the clichés (bootcamps, 5 AM club, LeetCode grind), then three absurd concrete project examples. |
| 1:17-1:32 | The twist | "Enjoying it is the actual unlock." A rapid list of grind words (LeetCode, burnout, interviews, LinkedIn) as a montage, then a rhetorical question. |
| 1:32-2:06 | Second list: relearn | Go back to recursion, read real source code, learn a language out of curiosity. Ironic payoff: it ends up on your resume anyway. |
| 2:06-2:20 | Payoff / callback | The grinders are the ones behind, "until March". Repeats the thesis as the closing line ("an hour a day"). |
| 2:20-3:06 | Sponsor (Porkbun) | Bridged from the topic ("if you ship one of these projects, your domain matters"). Product screenshots + the brand's own mascot art, same text-card style. **24 % of the video.** |
| 3:06-3:12 | Outro | One line, "link below" card. |

The thesis appears twice: in the first 20 seconds and as the last content line. Everything in between is lists of short, concrete items.

## Visual vocabulary (65 sampled frames + the hold above)

- **Text cards, about 30 %:** heavy bold serif in white on charcoal (#1e1e1e-ish), one key word in **cyan or green** ("NO BS", "build.", "An Hour A Day", "until March"). Often a small **handwritten-style aside** under it as the joke ("75 Hard" + *for nerds*, "Output" + *is NOT the goal*, "F\*ck Around" + *build dumb sh\*t*). Swear words censored with an asterisk.
- **Meme stills and reaction GIFs, about 35 %:** vintage ad man saying no, wojaks, a crying girl holding her head, a sweating man, Community, a frozen Jack Nicholson ("It's January!"), a party crowd. Mostly literal: whatever noun is spoken shows up as a meme ("finals" → a nervous wojak + "Finals").
- **Screenshots and screen recordings, about 20 %:** settings screen, terminal, LeetCode profile, a tweet, a roast-bot site, brainf\*ck code, an exam paper. Sometimes with a reacting wojak cut out in front.
- **Flat illustrations and stock animation, about 15 %:** lo-fi coder, cartoon 5 AM alarm clock, laptop with hands, isometric room. Cut-out stickers with no background.
- **Glue:** hand-drawn arrows with handwritten notes ("so much free stuff", "nobody else knows how to play"), a red X drawn over things being cancelled ("deadlines"), a pointing-hand emoji. Hard cuts only. No transitions, no fades.

## Techniques to try (in Kdenlive)

1. **Big word + small handwritten joke.** The main word says the point, the handwritten aside is the punchline. In Kdenlive: Project → Add Title Clip. Type the main word in a bold font, then add a second text item in a handwriting font, smaller, in the accent color, slightly tilted (Rotation in the title editor). Save it as a template so every card matches. Or use our `tools/graphic` caption template.
2. **One meme per noun in lists.** When the script lists things ("exams, holidays, finals"), give every item its own 0.7-1.2 s visual. In Kdenlive: put all the clips on V2 in order, then use the Razor tool (X) on the exact frame each word starts. Turn on the audio waveform so you can see the words.
3. **Keep the background, swap the stickers.** For a slower stretch (examples, explanations), keep a plain dark background on V1 and put cut-out PNGs (made with `tools/cutout.sh`) and short text on V2/V3, each for 1.5-3 s. It feels fast without being tiring.
4. **Annotate memes.** A red X over the thing being cancelled, an arrow with a handwritten note pointing at a detail. In Kdenlive: put a transparent PNG of the X or arrow on the track above the meme, and add the Transform effect to place and size it.
5. **Anti-hook, then the promise twice.** Script trick, not editing: open by saying what the video *isn't* ("this isn't another grind video"), state the one-sentence promise by ~0:20, and end the content on the same sentence. Use `/punchup` to write it in our own voice.

Bonus for sponsor reads: bridge in from the topic (one sentence), and cut the sponsor in the same visual style as the video so viewers don't skip.

## Compared with our other references

| Reference | Length | Cuts/min (0.3) | Avg shot | Words/s |
| --- | --- | --- | --- | --- |
| **This one** | 3:12 | 20 (36 at 0.12) | 2.96 s (1.66 s at 0.12) | **3.66** |
| videoplayback (news explainer) | 5:25 | 21 (21 at 0.12) | 2.82 s | 3.55 |
| Computer Science in the AI Era | 7:30 | 25 | 2.38 s | — |
| Coding interviews have become insane | 6:40 | 30 | 2.02 s | — |
| 1000+ hours with Claude Code | 22:30 | 23 | 2.64 s | — |

This one is the **shortest and most text-card driven** of the set, and the closest match to our `meme-commentary` style (avg visual 1.66 s vs our 1.7 s). The big difference is talking speed: 3.66 words/s vs our 2.6.

## Suggested style

Not saved yet. Proposed `styles/custom/cs-advice.json`:

```json
{
  "cs-advice": {
    "extends": "meme-commentary",
    "name": "CS advice (faceless, text cards + one meme per noun)",
    "target_seconds": 150,
    "avg_shot_seconds": 1.7,
    "words_per_second": 3.0,
    "references": "references/If You're in Computer Science, Watch This Now_cuts/breakdown.md"
  }
}
```

`target_seconds` 150 = the 2:20 of content without the sponsor. `words_per_second` 3.0 is between our 2.6 and their 3.66. Their pace is fast, and 3.0 is a realistic step up when recording. Raise it later if it feels slow.
