---
name: personality-voice
description: Use whenever writing, rewriting or punching up any spoken words (scripts, hooks, voiceover, captions, titles), or when the user asks for jokes, humor, punchlines, personality, a "bestfriend" tone, or less cringe.
---

# Personality and humor

## Load first
1. The profile at `[personality].profile` (default `personality/bestfriend.md`). It's the source of truth for voice, the humor toolkit and anti-cringe rules.
2. `[personality]` settings: humor_level (a style's own `humor_level` overrides it), joke_every_seconds, profanity, dark_humor, self_deprecating, meme_cutaways, punch_at.
3. `[creator]`: audience, language (Taglish = natural code-switching), avoid.
4. `personality/inspirations.md`: the user's own notes on creators they like. Use the **techniques** they describe. Never reuse those creators' catchphrases, show names, intros, specific jokes or bits.
5. `personality/bits.md`: the user's recurring bits. Use at most one per video, and only if it hasn't been used in the last 2 videos (check the "Used in" column).

## Process (always in this order)
1. **Facts pass:** write the clear, accurate, useful version with no jokes. Mark anything unverified `[CHECK]`.
2. **Voice pass:** rewrite it as the profile's person talking to a best friend. Use contractions and short sentences, react to your own facts, use "you."
3. **Punch-up pass:** add humor at the configured density (script seconds ÷ joke_every_seconds ≈ number of jokes). Mix at least 3 different techniques from the toolkit. Put punchlines at the end of sentences. Use visual punchlines in the See column when `meme_cutaways` is on (describe the visual specifically).
4. **Cringe pass:** run `python3 tools/cringe_check.py <script>` and fix everything. Then apply the 4-question cringe test from the profile to every joke, and cut any joke that fails or that the video doesn't need.
5. **Accuracy check:** confirm no joke changed or blurred a fact.

## Humor level guide
| Level | Feel |
|---|---|
| 0 | No jokes. Warm and clear. |
| 1 | Occasional light aside, mostly informative |
| 2 | Friendly, a smile every 30-40 s |
| 3 | Genuinely funny, a laugh every ~20 s |
| 4 | Joke-dense, every section has a laugh, deadpan and visual gags |
| 5 | Unhinged and chaotic, but the facts must still survive |

## Hard rules
- Information survives every joke. If a joke makes something unclear, the joke goes.
- Punch up (at companies, hype, bad ideas, yourself), never down. No jokes about appearance, identity, ethnicity, disability or intelligence. No dunking on real private people.
- Respect the `profanity` setting exactly. `bleeped` means mark it with `[BLEEP]` for the edit.
- No dark humor unless `dark_humor = true`. Even then, never about real tragedies or victims.
- Real people and companies: jokes about public actions are fine. Never invent quotes, events or claims about them.
- Don't write "(laughs)", "lol", emoji or stage directions for jokes into the Hear column. Delivery notes go in Notes.
- Taglish: switch where a Filipino friend naturally would, with English for tech terms. Never a stiff translation.

## When showing the user
Show 2-3 of the best jokes with the technique each uses, so they learn the toolkit. Offer a spicier or milder version if they're unsure about the level.
