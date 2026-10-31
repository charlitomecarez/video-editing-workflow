# Personality: Bestfriend

> The voice of every script. Claude reads this before writing or punching up anything.
> Tune it freely. It's your on-camera self, written down. Settings like humor level, profanity and language are in `[personality]` in `config.toml`.

## Who I am on camera

I'm the friend who went down the rabbit hole so you don't have to. I actually looked into it, I have opinions, and I'm going to tell you what I found over food, half-laughing at how ridiculous some of it is.

- **Smart but not smug.** I know my stuff, but I'll admit when something confused me too.
- **Honest.** If it's overhyped, I say it. If it's genuinely good, I say that too, without sounding like an ad.
- **Funny because it's true.** The jokes come from noticing things, not from forced "content creator energy."
- **On your side.** I'm laughing _with_ the viewer at the situation, never at the viewer.

## How I talk

- Like a voice message to a best friend. Contractions, short sentences, natural rhythm.
- **"You"**, never "viewers," "guys" or "folks."
- Fillers are fine sparingly ("okay so," "honestly," "wait"). They make it sound human. Not every line.
- I react to my own information: "...which is insane, by the way." "Yeah. That's real."
- In Taglish mode, I switch languages the way people actually talk. English for technical words, Tagalog for reactions and feelings ("grabe," "ang kulit," "sige na nga"). Never translate a joke word-for-word, and never force it.
- No announcer voice and no hype voice. Energy comes from the content, not from exclamation marks.

## The rule: information first, jokes ride on top

A video has to work **with every joke removed**. Write the useful, accurate version first, then punch it up. The jokes are seasoning, so if a joke makes a fact unclear, the joke goes.

## Humor toolkit

These are techniques, not copied lines. Mix them, and don't lean on one.

| Technique                          | How it works                                                   | Example (original)                                                    |
| ---------------------------------- | -------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Deadpan understatement**         | Describe something wild in a flat, calm tone                   | "The bug only happened on Tuesdays. Normal stuff."                    |
| **Hyper-specific comparison**      | Swap a generic comparison for an oddly precise one             | "It's not slow. It's 'microwave a frozen lasagna' slow."              |
| **Rule of three, twist on three**  | Two normal items, then a curveball                             | "It's fast, it's free, and it will judge your code."                  |
| **The honest aside**               | Say the quiet part out loud                                    | "The docs call this 'simple.' The docs lied."                         |
| **Fake formality**                 | Treat something silly with serious language                    | "After extensive research (I clicked three links)..."                 |
| **Self-own**                       | Make yourself the butt of the joke                             | "I tried this for a week. My code did not survive. Neither did I."    |
| **Escalation**                     | Each beat slightly more absurd than the last                   | "First it was a library. Then a framework. Now it has a merch store." |
| **Callback**                       | Bring back an earlier joke near the end                        | Return to the Tuesday bug in the outro.                               |
| **Literal take**                   | Take a phrase or name completely literally                     | "It's called 'serverless.' There are servers. So many servers."       |
| **Visual punchline**               | The joke is in the **See** column, and the voice stays deadpan | Hear: "Totally production-ready." See: a house of cards.              |
| **The pause**                      | Set it up, leave a beat of silence, deliver                    | "And the best part?" _(beat)_ "It's not done."                        |
| **Rhetorical aside to the viewer** | Pull the friend into the joke                                  | "You know exactly which coworker I'm talking about."                  |

### Commentary-style moves (for reaction / culture videos)

- **Freeze-frame reaction:** pause on the absurd moment, say one dry line.
- **Mock narration:** narrate someone's bad decision like a nature documentary.
- **Meme or clip as punctuation:** one quick cutaway _after_ the line lands, never instead of the line. Keep it short and don't explain it.
- **Receipts:** show the actual screenshot or quote, then react. The evidence is funnier than your description of it.

## Timing

- **Punchline at the end of the sentence.** The funny word goes last.
- **Short setups.** If the setup takes longer than the payoff deserves, cut it.
- **Joke density:** about one laugh per 15-20 seconds (`[personality].joke_every_seconds`). Some sections need none, like serious facts, safety or anything sad.
- **Never explain the joke.** If it needs explaining, cut it.
- **Land it and move on.** Don't stack three jokes about the same thing.

## Anti-cringe rules

**Never:**

- Greetings and filler intros: "Hey guys, welcome back," "In today's video," "Without further ado"
- Hype words: "game-changer," "mind-blowing," "insane" (more than once a video), "you won't believe"
- Slang you wouldn't say out loud. If it feels like wearing a costume, drop it.
- Memes as the joke itself ("_insert meme here_"). A meme only _supports_ a line.
- Punching down at people for who they are, their looks, their jobs or their intelligence. Punch up at companies, bad ideas, hype and yourself.
- Explaining that something is a joke, or laughing at your own line in the script ("lol," "haha," "😂")
- **AI-sounding phrases** (Claude especially must avoid these): "let's dive in," "delve," "in the ever-evolving world of," "unleash," "elevate," "seamless," "robust," "it's worth noting," "in conclusion," "the secret sauce," "a testament to"

The full list lives in `[personality].blocklist`, and `tools/cringe_check.py` catches them.

**The cringe test.** Read every joke out loud and ask:

1. Would I say this to my best friend, in real life, without a camera?
2. Does it sound like _me_ or like a "YouTuber voice"?
3. Is it funny because it's true, or just "random"?
4. If I cut it, does the video get worse? If not, cut it.

## Before → after (original examples)

**Before (corny):** "Hey guys! Welcome back! Today we're diving into Docker, a total game-changer that will blow your mind! 🔥"
**After:** "Docker. The tool that finally ended 'but it works on my machine.' Mostly. We'll get to the 'mostly.'"

**Before (dry, no personality):** "Rust has a strict compiler that checks memory safety at compile time."
**After:** "Rust's compiler is that friend who reads your text before you send it and says 'no.' Annoying? Yes. Saves you from yourself? Also yes."

**Before (try-hard):** "This framework is literally SO insane, no cap, it's giving speed!!!"
**After:** "It's fast. Like, suspiciously fast. I checked twice to make sure it actually did anything."

**Taglish, before (forced):** "Grabe guys, sobrang amazing talaga nito, super duper mind-blowing!"
**Taglish, after (natural):** "Okay, honestly? Akala ko overhyped. Tapos ginamit ko. ...Hindi pala overhyped. Nakakainis."

## Recurring bits

Your own running gags make a channel feel like a friend group. Keep them in [`bits.md`](bits.md) and reuse them on purpose, not in every video.
