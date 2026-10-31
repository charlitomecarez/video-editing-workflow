---
description: Start a new video from idea to project folder and script
argument-hint: "<title or idea>" [style]
---

Start a new video: $ARGUMENTS

1. If it's a rough idea rather than a title, suggest 3 titles using the `topic-research` skill and let me pick.
2. Pick or confirm the style.
3. Run `python3 tools/new_project.py "<title>" --style <style>`.
4. Write the script into the project folder using the `video-scriptwriting` skill (`--project <folder>`).
5. If the idea came from `topics/ideas.md`, tick it off.
6. Show me the shot list so I can start filming.
