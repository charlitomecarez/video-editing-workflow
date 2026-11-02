# Stock Video and Memes

`tools/stock.py` finds moving footage for your B-roll and reaction clips for your punchlines, puts them in the project with the right file name, and logs where each one came from.

## Get the free API keys (once, 5 minutes)

| Source          | What it has                                      | Sign up                                                    | Put in `.env.local` |
| --------------- | ------------------------------------------------ | ---------------------------------------------------------- | ------------------- |
| Pexels          | Stock video, free for monetized use, no credit   | [pexels.com/api](https://www.pexels.com/api/) (instant)     | `PEXELS_API_KEY=…`  |
| Pixabay         | Stock video, free for monetized use, no credit   | [pixabay.com/api/docs](https://pixabay.com/api/docs/) (log in, key is on that page) | `PIXABAY_API_KEY=…` |
| GIPHY           | Meme / reaction GIFs (rights unknown, see below) | [developers.giphy.com](https://developers.giphy.com/dashboard/) → Create an App → API | `GIPHY_API_KEY=…`   |
| Wikimedia Commons | Free-licensed video (mostly news and government footage) | no key needed | |

`.env.local` is git-ignored, so the keys never get committed.

## Stock video (safe to monetize)

```bash
python3 tools/stock.py find "traffic jam night"
python3 tools/stock.py get 3 --project projects/<video> --row 19 --name jam-night --seconds 4
```

`get` downloads the clip, cuts it to `--seconds` (from `--start`), turns it into a clean 1920x1080 clip with no sound, and saves it as `footage/broll/19-jam-night.mp4`. The rough cut puts it on row 19. To replace a photo in a second version, use its exact name: `--dir graphics/v2 --as 19-1-photo-december-434-000`. The clip takes the photo's place and cue.

Search in English, with simple words: what's in the shot, not what it means ("cars stuck in traffic", "man honking car horn", "crowded bus"). Pexels and Pixabay have few clips of the Philippines specifically, so mix them with your own phone clips for places people recognize.

## Memes for punchlines

```bash
python3 tools/stock.py find "facepalm" --memes
python3 tools/stock.py get 2 --project projects/<video> --row 15 --name facepalm
```

**API limit:** a GIPHY beta key allows 100 calls an hour. The tool counts its calls in `.cache/giphy-calls.json` and stops at `[stock].giphy_calls_per_hour` (90), and every search is cached for 24 h, so searching the same words again is free. Downloading the GIFs themselves doesn't count.

**Rights are unknown.** Most meme GIFs are clips from movies, TV or other creators. GIPHY's license covers showing GIFs inside apps, not putting them in your monetized video. Short reaction clips used as commentary are common on YouTube, but they can still get a video claimed. So:

- Every meme is logged in the project's `CREDITS-stock.md` as **UNKNOWN**, and saved as `NN-meme-….mp4`.
- Keep them short (default 2 s, looped if the GIF is shorter), one per punchline, **after** the line lands.
- **Safer option first:** stock reaction clips are licensed and often just as funny. Try `find "man facepalm"`, `find "woman shrugging"`, `find "frustrated driver"` without `--memes`.
- Turn memes off completely with `[stock].allow_unknown_rights = false`.

**Tenor:** Google shut down the Tenor API in June 2026, so the tool can't search it. You can still download from tenor.com in your browser and bring the file in:

```bash
python3 tools/stock.py add ~/Downloads/facepalm.gif --source Tenor --page https://tenor.com/view/… \
    --project projects/<video> --row 15 --name facepalm
```

`add` works for any file (your own phone clip too: add `--rights ok --source "my phone"`).

## Which punchlines get a meme?

Follow the same rule as sound effects (`docs/sound-effects.md`): a meme marks a joke, it isn't the joke. About one every 15–20 seconds at most, never over a serious fact, and never on the call to action. A meme and a comedic sound effect on the same beat is fine (the sound answers the line, the picture reacts to it).

Settings: `[stock]` in config.
