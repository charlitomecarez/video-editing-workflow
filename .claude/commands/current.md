---
description: Show the video I'm working on now (from the Content Planner) and do its next step
argument-hint: [video title, id or project folder]
---

Find the video to work on: $ARGUMENTS

1. Run `python3 tools/planner.py current --json` (or `python3 tools/planner.py show "<arguments>" --json` if I named a video).
2. Tell me in two or three lines: the title, the stage, and the next step. Include the hook and open tasks if there are any.
3. If the next step has a `command`, offer to run it now. If the video has no `projectSlug` yet and the step needs a project folder, offer `/new` with its title first.
4. If nothing is in progress, show `python3 tools/planner.py ideas` and ask which one to start.
