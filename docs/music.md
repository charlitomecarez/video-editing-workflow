# Background Music

`tools/music.py` gets you music you're allowed to use **and monetize**, then puts it under your video.

## Is it safe? The license rules

| License                            | Use it?    | What you must do                               |
| ---------------------------------- | ---------- | ---------------------------------------------- |
| CC0 / public domain                | ✅ yes     | Nothing (credit is still nice)                 |
| CC BY                              | ✅ yes     | Credit the artist in the description           |
| CC BY-SA                           | ⚠️ skipped | Your whole video would have to be CC BY-SA too |
| CC BY-NC (NonCommercial)           | ❌ skipped | Can't be used on a monetized channel           |
| CC BY-ND (NoDerivatives)           | ❌ skipped | Can't be edited or mixed                       |
| "Free" / "no copyright" on YouTube | ❌ never   | Often re-uploads with no real license          |

The tool only ever shows CC0, public domain and CC BY tracks. Settings: `[music]` in config.

## Option 1: make your own (safest)

```bash
python3 tools/music.py make --mood lofi --project projects/<video>
python3 tools/music.py make --mood upbeat --seed 4 --project projects/<video>
```

Composes an **original** loop on your Mac from code: chords, bass, drums and a light melody. No samples, no one else's recording, so there's nothing to credit and nothing for Content ID to match. Moods: `lofi`, `chill`, `upbeat`, `tense`. Same `--seed` = same track; change it for a new one. It's simple background music, not a hit single, but it sits well under a voice.

## Option 2: find a track by a real artist

```bash
python3 tools/music.py find "chill piano"
python3 tools/music.py get 2 --project projects/<video>
```

Searches **Openverse** (WordPress's open media search: Jamendo, Freesound, ccMixter and more) and **ccMixter**. Click the "listen" link to hear a track first.

Some libraries (ccMixter) only allow downloads from the track's page, not from scripts. Then `get` tells you which page to open. Download the file there, then:

```bash
python3 tools/music.py get 2 --file ~/Downloads/<file>.mp3 --project projects/<video>
```

Either way you get `audio/music.<ext>` plus `audio/music-license.md` with the artist, license, source and **the credit line to paste in your description**. Keep that file (it's committed to git): it's your proof if a claim ever shows up.

**Content ID:** some open-licensed tracks get registered by mistake. If YouTube shows a claim, dispute it with "I have a license" and paste the license link and source page from `music-license.md`. Tracks from ccMixter "ccPlus" artists are skipped by default because they're likelier to be registered (`[music].allow_ccplus`).

## Put it under the video

- **Rough cut:** `/roughcut` puts `audio/music.*` on track A2 automatically: looped, lowered (`[rough_cut].music_level_db`) and faded out.
- **A finished export:** `mix` adds it to the final file and **ducks** it (the music dips while you talk and comes back in the pauses):

```bash
python3 tools/music.py mix projects/<video>/export/final.mp4          # -> final_music.mp4
python3 tools/music.py mix final.mp4 --level -12                      # louder music
python3 tools/music.py mix final.mp4 --no-duck --music other.wav
```

The video picture is copied untouched; only the audio is remixed.

## In Kdenlive (by hand)

1. Drag `audio/music.*` into the Project Bin, then onto track **A2**.
2. Right-click it → **Audio Correction → Volume**, set about **-18 dB**.
3. To fade out: drag the small circle at the clip's top-right corner to the left.
