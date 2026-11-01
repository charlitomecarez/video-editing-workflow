---
description: Add background music you're allowed to monetize (find an open-licensed track or make an original one)
argument-hint: [project] [mood or search words]
---

Add background music to: $ARGUMENTS

Follow `docs/music.md`. If no project is given, use `python3 tools/planner.py current`.

1. Ask (or infer from the words given) whether they want an **original** track (`make`, safest, no credit) or a **real artist's** track (`find` / `get`, CC0 or CC BY only). Suggest a mood that fits the video's tone.
2. `make`: `python3 tools/music.py make --mood <mood> --project <project>`. Offer two or three seeds if they want options.
3. `find`: run the search, show the results with their license, and let them pick. If `get` says the library only allows downloads from its page, give them the link and the `--file` command. Never try to get around a blocked download.
4. Show the credit line from `audio/music-license.md` when the license needs one, and remind them to paste it in the description.
5. Then either rebuild the rough cut (music goes on A2) or, for a finished export, `python3 tools/music.py mix <export>`.

Never use tracks marked NonCommercial, NoDerivatives or ShareAlike, or "no copyright" re-uploads from YouTube.
