# Voice Sample Script

Read this to give `tools/voice-clone` your voice. Six short clips, about 2 minutes in total: three in English, two in Tagalog and one in Taglish.

Open it in the teleprompter:

```bash
python3 tools/teleprompter.py docs/voice-sample-script.md
```

## Before you record

- **Quiet, soft room.** A closet or a bedroom with the door closed. No fan, aircon, TV or music.
- **Same mic as your videos**, about a hand's width (10 to 15 cm) from your mouth.
- **Your normal video voice.** Talk like you're explaining it to a friend, not reading it out. Change words if something feels unnatural to say.
- **One clip per section.** Name the files `01-en-explain.m4a`, `02-en-story.m4a`, and so on. iPhone Voice Memos is fine.
- **Messed up?** Stop and record that clip again from the start. Small "uh"s are fine. They sound human.
- Leave about 1 second of silence at the start and end of each clip.

When you're done, send me the files (or tell me the folder). I'll run `tools/voice-clone add me <files>` and do a test in both languages.

## Script

### 01 · English, explaining (calm)

**Voiceover:**

Okay, so here's the thing nobody tells you about learning to code.
The hard part isn't the syntax.
It's sitting with a problem for twenty minutes, not knowing why it's broken, and not giving up.
That feeling? Totally normal. Everyone has it.
Even the people who make it look easy.

### 02 · English, telling a story (more energy)

**Voiceover:**

Last week I tried to fix one tiny bug before lunch. One.
Three hours later, I had rewritten half the app, and my coffee was cold.
The bug was still there.
And then I found it. A missing comma.
I just sat there, staring at the screen like it owed me money.

### 03 · English, questions and numbers

**Voiceover:**

Wait, how much does it cost?
Nine ninety-nine a month? For a to-do list?
Let me check something.
Version two point four came out on March fifteenth, and it's three times faster.
Okay. That's actually impressive. I'm a little annoyed, but it's impressive.

### 04 · Tagalog, kwento

**Voiceover:**

Alam mo yung pakiramdam na akala mo tapos ka na, tapos may isa pang error?
Ganun ako kahapon.
Ang tagal kong hinanap kung saan yung mali.
Kinain ko na yung merienda ko, nagtimpla ulit ng kape, nag-isip nang malalim.
Tapos nung nakita ko na, isang letra lang pala.

### 05 · Taglish, natural switching

**Voiceover:**

Grabe, sobrang bilis nito.
Like, nag-click lang ako ng isang button, tapos tapos na agad yung build.
Dati, inaabot ako ng limang minuto. Ngayon, sampung segundo na lang.
Honestly, hindi ko in-expect na ganito kaganda.
Sige na nga, aaminin ko na. Nagustuhan ko siya.

### 06 · Tagalog, reactions and questions

**Voiceover:**

Teka, seryoso ka ba? Libre talaga?
Walang bayad kahit isang piso?
Paano sila kumikita kung ganun?
Hmm. Parang may mali dito.
Sige, titingnan natin nang mabuti, isa-isa, para sigurado tayo.

## Why these lines

| Clip | What it teaches the clone                                                   |
| ---- | --------------------------------------------------------------------------- |
| 01   | Your calm, everyday explaining voice. This is what most scripts sound like. |
| 02   | Higher energy, pauses before a punchline, a deadpan ending                  |
| 03   | Questions going up at the end, numbers, a reaction                          |
| 04   | Your Tagalog sounds, rhythm and storytelling pace                           |
| 05   | How you switch between English and Tagalog mid-sentence                     |
| 06   | Tagalog questions and reactions                                             |

**About Tagalog:** the cloning model (Chatterbox) speaks English plus 22 other languages, but not Tagalog. Your Tagalog clips still help it learn what you sound like, but Tagalog lines it reads may come out with an English accent. Clips 01 to 03 matter most for English drafts.
