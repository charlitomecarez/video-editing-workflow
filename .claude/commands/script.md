---
description: Write a full video script for a topic
argument-hint: "<title>" [style] [project folder]
---

Write a video script for: $ARGUMENTS

If no topic is given, use the current video from `python3 tools/planner.py current --json` (its title, hook, format and notes).

Use the `video-scriptwriting` and `personality-voice` skills. If no style is given, pick the best one from `python3 tools/vwconfig.py styles` and explain why in one line. If a matching folder exists in `projects/`, save the script there with `--project`.
