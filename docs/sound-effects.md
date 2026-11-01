# Sound Effects

Sound effects make an edit feel alive, and too many make it feel cheap. The rule of thumb: **a sound should mark something the viewer should feel** (a turn, a reveal, a joke), never decorate every cut.

## The library

```bash
python3 tools/sfx.py build     # generate the original sounds (yours, safe to monetize)
python3 tools/sfx.py list      # what each one is for
python3 tools/sfx.py play rimshot
```

| Sound            | Mood      | Use it for                                            | Lands             |
| ---------------- | --------- | ----------------------------------------------------- | ----------------- |
| `pop`            | neutral   | A punchy one-word caption or a graphic popping in     | on the word       |
| `tick`           | neutral   | Numbers in a quick list or a recap run                | on the word       |
| `click`          | neutral   | A screenshot, a cursor, a UI moment                   | on the word       |
| `whoosh`         | energetic | A new section, the story switching sides              | peaks on the word |
| `glitch`         | energetic | A hard topic switch, a chapter card                   | on the word       |
| `whoosh-down`    | calm      | A let-down, leaving a high point                      | on the word       |
| `ding`           | positive  | A stat that matters landing                           | on the word       |
| `riser`          | dramatic  | Build-up that ends exactly on a reveal                | ends on the word  |
| `impact`         | dramatic  | THE reveal: the one number or fact the video is about | on the word       |
| `record-scratch` | comedic   | The twist: "wait, what?"                              | on the word       |
| `rimshot`        | comedic   | After a pun or a groaner                              | after the line    |
| `boing`          | comedic   | Something silly, a dumb mistake, a self-own           | after the line    |
| `sad-trombone`   | comedic   | A fail or a loss (a game, not a real tragedy)         | after the line    |

## Putting them in a script

In the **Notes** column of the row, name the sound and the word it belongs to:

```
| 15 | ... | Hindi 'yan ubos-oras. Ubos-Pacers na 'yan. | sfx:rimshot on "Ubos-Pacers na yan" |
```

The rough cut puts it on track **A3** at that word: on it, just before it (whoosh, riser) or right after the line (stingers), so the punchline is heard first and the sound answers it.

## The right amount

| Rule                                                               | Why                                              |
| ------------------------------------------------------------------ | ------------------------------------------------ |
| **4–10 per minute** (meme commentary: about 7)                     | Fewer feels flat, more feels like a soundboard   |
| **At least 2.5 s apart**                                           | Two sounds in a row cancel each other out        |
| **Comedic stingers at least 15 s apart**, ~1 per joke-heavy minute | A rare rimshot is funny, a constant one is noise |
| `rimshot` / `sad-trombone`: **twice per video, max**               | They stop being funny after that                 |
| `impact`: **once or twice**                                        | If everything is big, nothing is                 |
| Vary them: don't use the same sound 3 times in a row               | The ear notices patterns fast                    |

The rough cut report checks all of these (`## Sound effects on A3` → **Checks**) and tells you what's too close, too many or too few. Settings: `[sfx]` in config.

## When NOT to use one

- **Deadpan jokes:** the silence after the line _is_ the joke. A sound kills it.
- **Serious facts:** injuries, death, family, anything sad. No sound, not even a whoosh.
- **Over a meme or clip that has its own audio.**
- **Over the call to action** (the question to comment on): let the words land.
- **On every caption:** pick the punchiest ones.

## Myinstants (opt-in, rights unknown)

```bash
python3 tools/sfx.py find "bruh"
python3 tools/sfx.py get 2 --name bruh --mood comedic --use "disbelief after a dumb take"
```

Myinstants is a soundboard site: anyone uploads, and there is **no license information**. Many sounds are clips from movies, TV, songs or other YouTubers, which can get a video claimed or demonetized. Generic sounds (a ding, a rimshot) are lower risk than anything recognizable. Every Myinstants sound is logged in `sfx/LICENSES.md` and flagged in the rough cut report. Set `[sfx].allow_unknown_rights = false` to keep them out of the edit entirely.

The anonymous API allows 10 requests a minute (the tool waits between calls). For more, email developers@myinstants.com for a token and put it in `.env.local` as `MYINSTANTS_TOKEN`.
