---
description: Prep footage for editing in Kdenlive
argument-hint: <project folder or clip> [what you want]
---

Help me prepare this footage for editing: $ARGUMENTS

1. List the clips and check them with `ffprobe` (resolution, fps, duration, audio).
2. Find the matching script in `video-scripts/` and its style in `styles/styles.json`.
3. Propose a plan before running anything: which clips to prep (`tools/prep.sh`), cut silences on (`tools/cut-silence.sh`), make vertical (`tools/vertical.sh`) or subtitle (`tools/subtitles.sh`).
4. After I approve, run the steps and keep the originals untouched.
5. Tell me which `.kdenlive` file to open and what to check first.

Never edit a `.kdenlive` file while I might have it open in Kdenlive. Ask first, and save a backup copy before editing it.
