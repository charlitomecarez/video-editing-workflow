# Projects

One folder per video, created with `python3 tools/new_project.py "Title"`:

```
projects/2026-11-01-budget-meals/
  footage/      raw clips (+ _prep / _cut versions)
  audio/        music, voiceover, sound effects
  graphics/     logos, overlays, LUTs
  export/       renders
  thumbnails/   thumbnail candidates
  reel/         reel.json plan, reel.mp4, reel.srt, cover (60 s summary)
  notes.md
  script.md
  2026-11-01-budget-meals.kdenlive
```

Only `.md`, `.kdenlive`, `.srt` and `.json` files are committed. **Video, audio and images are git-ignored**, so back up footage separately (external drive or cloud).
