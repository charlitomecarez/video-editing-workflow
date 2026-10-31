---
description: Prep footage and get it ready to edit in Kdenlive
argument-hint: <project folder or clip> [what you want]
---

Help me prepare this footage for editing: $ARGUMENTS

Use the `footage-prep` skill, then the `kdenlive-editing` skill for the editing steps.

1. Inspect the clips with `ffprobe`.
2. Find the matching script and its style.
3. Propose a plan (which tools, on which clips, with which settings) and wait for my OK.
4. Run it, keeping the originals untouched.
5. Tell me which `.kdenlive` file to open and give me the first 3 editing steps for this style.
