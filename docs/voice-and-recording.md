# Voice and Recording

## The flow

1. **Draft voiceover** (optional): `tools/voice-clone say script.md` reads the script **in your own voice** (cloned from a few of your clips), or `tools/voice-draft.sh script.md` uses a stock AI voice. Use it to time the edit and hear the script's length and flow.
2. **Record** your real voice while reading from the **teleprompter**. Use **OBS** if you're also recording your screen.
3. **Clean** the recording: `tools/clean-voice.sh voice.wav`
4. **Tighten** it: `tools/cut-silence.sh voice_clean.wav --margin 0.1s`
5. Put it on A1 in Kdenlive and edit the visuals to it.

## Script tools

```bash
python3 tools/script_text.py projects/x/script.md            # just the spoken words
python3 tools/script_text.py projects/x/script.md --stats    # words per section vs target
```

Run `--stats` before recording. If a section is "too long", cut words. Don't plan to talk faster.

## Draft voiceover (Piper, offline AI voice)

```bash
tools/voice-draft.sh projects/x/script.md
tools/voice-draft.sh projects/x/script.md --voice en_US-ryan-high --speed 1.15
```

- Free and runs on your Mac, so nothing is uploaded. Voices download on first use into `.voices/`.
- Hear all the voices at https://rhasspy.github.io/piper-samples/ (there are many English accents and other languages).
- Settings: `[tts]` in config (voice, speed, sentence_pause).
- Use it as a **placeholder** for timing. Your own voice builds a much stronger connection with viewers. If you ever publish with an AI voice, check the platform's AI-content disclosure rules.

## Draft voiceover in your own voice (voice cloning)

`tools/voice-clone` copies your voice from a few recordings, then reads any script in it. It uses Chatterbox, a free model that runs on your Mac (Apple GPU). Nothing gets uploaded.

**One-time install** (about 2 GB, plus a 3 GB model download the first time you use it):

```bash
tools/setup.sh --voice-clone
```

**1. Give it your voice.** Any audio or video of you talking works (`.m4a` voice memos, `.wav`, `.mov`). Best results come from:

- 15–60 seconds in total, in your normal "video" voice and energy
- a quiet room, no music, only you talking
- a few different clips (it cleans them, removes long pauses and keeps the best stretch)

Not sure what to say? Read [`docs/voice-sample-script.md`](voice-sample-script.md): six short clips in English, Tagalog and Taglish (about 2 minutes). It opens in the teleprompter too.

```bash
tools/voice-clone add me ~/Desktop/voice1.m4a ~/Desktop/voice2.m4a
tools/voice-clone ref me          # listen to the reference it picked
```

Run `add me <more clips>` any time to add samples and rebuild the reference.

**2. Read a script in your voice:**

```bash
tools/voice-clone say projects/x/script.md
tools/voice-clone say projects/x/script.md --speed 1.1           # a bit faster
tools/voice-clone say projects/x/script.md --exaggeration 0.7    # more energy
tools/voice-clone say --text "Quick test, does this sound like me?"
```

Output: `script_clone-vo.wav`, plus `script_clone-vo.json` with when each script row starts and ends. Put the WAV on A1 in Kdenlive.

**Fixing a bad line:** every run with the same seed gives the same take. To re-roll only some rows, use `--rows 3,7 --seed 2 --out fix.wav`. Then drop `fix.wav` over those lines in Kdenlive.

| If it sounds…      | Try                                                  |
| ------------------ | ---------------------------------------------------- |
| Flat or bored      | `--exaggeration 0.7`                                 |
| Rushed             | `--cfg-weight 0.3` (slower, more deliberate)         |
| Not quite like you | Add more (and cleaner) clips with `add me ...`       |
| Weird on one line  | `--rows N --seed 1` (then 2, 3…) until it's right    |
| Echoey or noisy    | Record new samples somewhere quieter (blankets help) |

Settings: `[voice_clone]` in config. Chatterbox adds an inaudible watermark that marks the audio as AI-made. Use this for drafts and timing, and only clone **your own** voice (or a voice you have permission to use). If you publish with it, follow the platform's AI-content disclosure rules.

## Teleprompter

```bash
python3 tools/teleprompter.py projects/x/script.md
```

This opens in your browser.

| Key   | Action                               |
| ----- | ------------------------------------ |
| Space | Start / pause                        |
| ↑ / ↓ | Faster / slower                      |
| + / - | Bigger / smaller text                |
| ← / → | Previous / next section              |
| M     | Mirror (for glass teleprompter rigs) |
| R     | Back to top                          |
| F     | Fullscreen                           |

Settings are in `[teleprompter]`: font size, speed, mirror, line width and reading-line position. Put the browser window right under your camera so your eyes stay close to the lens.

## Clean voice

```bash
tools/clean-voice.sh recording.wav
tools/clean-voice.sh recording.mov --denoise 20      # noisy room
```

The chain runs: highpass (removes rumble) → noise reduction → optional de-esser → compressor (evens out volume) → loudness normalization. Settings are in `[clean_voice]`.

## Recording tips

- **Room:** small, with soft things around (a closet full of clothes is great). Avoid empty rooms with bare walls.
- **Mic:** 10-15 cm from your mouth, slightly off to the side to avoid "p" pops. Any USB mic beats a laptop mic.
- **Levels:** peaks around -12 to -6 dB while recording. Never let it hit 0 (clipping can't be fixed).
- **Record 10 s of silence** first (room tone). It helps with noise reduction and filling gaps.
- **Flubbed a line?** Pause, then say the whole sentence again. `cut-silence.sh` removes the pause, and you delete the bad take in Kdenlive.
- Sip water and stand up for more energy.

## OBS Studio (screen + mic recording)

It's installed at `/Applications/OBS.app`.

**One-time setup:**

1. **Settings → Video:** Base and Output resolution 1920x1080, FPS 30 (or match your style).
2. **Settings → Output → Recording:** Format **MKV** (survives crashes), Encoder **Apple VT H264 Hardware**, Quality: high.
3. **Settings → Advanced:** turn on **Automatically remux to MP4**, so you get an MP4 for Kdenlive.
4. **Settings → Audio:** pick your mic. In the Audio Mixer, set the mic on its own track (Advanced Audio Properties → Tracks) so voice and system sound stay separate.
5. **Sources:** add **macOS Screen Capture** (one window or the whole display), plus **Audio Input Capture** (mic). Grant screen-recording permission when macOS asks.
6. **Settings → Hotkeys:** set start/stop recording keys.

**For tech demos:**

- Make the terminal or editor font **big** (18-24 pt) and use a dark theme that matches your `[brand]`.
- Record at 1920x1080, but use a window around 1280x720 so text stays big after scaling.
- Hide desktop clutter, notifications (turn on Focus mode) and personal info.
- Run the recording through `tools/prep.sh` before editing (constant frame rate).
