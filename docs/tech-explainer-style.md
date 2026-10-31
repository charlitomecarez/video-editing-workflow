# Fast Tech Explainer Style

Inspired by fast, faceless, graphics-driven tech channels like Fireship. Style keys: `tech-explainer` (16:9, ~2.5 min) and `tech-explainer-short` (9:16, ~50 s).

> Learn from the style, but don't copy a channel's branding, catchphrases, intro or show names. Build your own voice, look and recurring jokes.

## The big lesson: writing matters more than editing
People who edit for channels like this say the editing is simple: *a thing flies onto the screen, the narrator talks about it, then moves to the next thing.* What makes a channel stand out is:

1. **Knowing the topic deeply.** You can't compress what you don't understand.
2. **Good writing.** Dense, funny, and with no wasted words.
3. **Having something to say.** An opinion or perspective, even in a basic explainer.
4. **Consistency.** Do it over and over.

So most of your time goes into research and the script. The edit follows the script.

## Step 1: Research
- Read the official docs, the "getting started" guide and the changelog. Build something tiny with it.
- Collect: who made it, when, what problem it solves, the core concepts, one real code example, the trade-offs, alternatives, and one surprising fact.
- Form an opinion. When would you use it, and when wouldn't you?

## Step 2: Write the 3-column script
`python3 tools/script_generator.py "Topic" --style tech-explainer` creates it (or `/script "Topic" tech-explainer`).

| See (on screen) | Hear (voiceover) | Notes |
|---|---|---|
| Logo pops in, center | "This is Bun, a JavaScript runtime that's fast. Like, unreasonably fast." | logo: bun.sh press kit, pop SFX |
| Benchmark bar chart | "It starts up four times faster than Node..." | [CHECK] source the benchmark |
| Code: `bun install` in terminal | "...and installs packages before you finish blinking." | screen record, speed up 2x |

Rules for the table:
- **One row = one visual = roughly one sentence.** At about 1.8 s per shot and 3 words per second, that's about 5-8 words per row.
- The **See** column changes when the **Hear** column names something new. Visuals match the exact word being spoken.
- Fill **Notes** while writing (asset links, sources, SFX), or you'll waste time hunting for things during the edit.
- Mark every fact you need to verify with `[CHECK]`.

**Structure** (built into the style): Cold open → What it is → How it works → Gotchas & ecosystem → Wrap-up.

**Writing style:**
- Short sentences, active voice and specific numbers
- A joke or witty aside every 15-20 seconds, ideally a nerdy one
- No "in this video we will...". Say it instead of announcing it.
- Read it out loud. If you stumble, rewrite it.

## Step 3: Record the voiceover
- Record the whole script in one go with a decent USB mic, in a small room with soft furnishings (closets work great).
- Speak a bit faster and with more energy than feels natural. The target is about 3 words per second.
- Leave a short pause and redo any line you flub, then run `tools/cut-silence.sh voice.wav --margin 0.1s` to tighten it automatically.
- Clean it in Kdenlive with Noise suppressor for voice → Compressor → Loudness.
- An AI voice is an option, but your own voice builds a stronger connection with viewers and is more distinctive.

## Step 4: Gather assets (from the Notes column)
| Asset | Where |
|---|---|
| Logos | Official press kits / brand pages |
| Code snippets | Screenshot from your editor with a dark theme and big font, or type it in a Kdenlive title clip with a monospace font |
| Diagrams | Excalidraw, Figma or draw.io, exported as PNG with a transparent background |
| Screenshots / screen recordings | Docs, GitHub, your own terminal |
| Memes / reaction images | Use sparingly, and be aware of copyright. Your own drawings are safest. |
| Stock clips | Pexels, Pixabay (free licenses) |
| SFX | Freesound, Pixabay (check licenses) |

Keep them in `projects/<video>/graphics/` with names matching the script rows (`03-benchmark.png`).

## Step 5: Edit in Kdenlive
1. **Profile:** HD 1080p 30 fps (or Vertical 1080x1920 for the short).
2. **Background:** a dark color clip on V1 for the whole video (Project Bin → Add Color Clip, `#0d1117`).
3. **Voiceover on A1.** It's your timeline's spine. Add markers (`M`) at each row of the script as you listen.
4. **Visuals on V2/V3**, one per marker, starting exactly on the word.
5. **Pop-in animation** (the signature move):
   - Add a **Transform** effect to the image.
   - Keyframe at frame 0: size 0% (or 80% with opacity 0).
   - Keyframe at frame 4: size 110%.
   - Keyframe at frame 6: size 100%.
   - Then **save it as a custom effect** (effect menu → Save Effect). Name it "Pop In" and reuse it on every element.
6. **Slide-in:** Transform keyframes moving position from off-screen to final position over 4-6 frames.
7. **Code:** show it big (fills about 60% of the screen). Reveal it line by line, or highlight the line being talked about with a semi-transparent color box above it.
8. **SFX:** a soft pop or whoosh on A3 for entrances. Not on every element, or it gets tiring.
9. **Music:** a low, steady track on A2 at about -28 dB under the voice.
10. **No dead frames.** If nothing has changed for more than about 3 seconds, add something.

**Save time:** make a **template project** (`templates/tech-explainer.kdenlive`) with the background, tracks, your Pop In effect and title styles ready. Copy it for every new video.

## Step 6: Study references
Analyze videos you admire:
```bash
python3 tools/analyze_cuts.py references/some-video.mp4 --frames
whisper references/some-video.mp4 --model small --output_format srt --output_dir references
python3 tools/analyze_cuts.py references/some-video.mp4 --srt references/some-video.srt
```
You'll get cuts per minute, average shot length, speaking rate and pace over time, plus `markers.srt` to step through every cut in Kdenlive. Compare a few videos, then tune your style in `styles/custom/`. Run `/analyze` in Claude Code to get a written breakdown.

## Quality checklist
- [ ] The first sentence says what it is and why I should care
- [ ] Every claim is verified (no `[CHECK]` left)
- [ ] At least one real opinion or "when not to use it"
- [ ] A visual change at least every 3 seconds
- [ ] Visuals land on the exact spoken word
- [ ] Code is readable on a phone screen
- [ ] Jokes land (have someone else watch it)
