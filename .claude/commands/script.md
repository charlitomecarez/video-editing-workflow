---
description: Write a full video script for a topic
argument-hint: "<title>" [style]
---

Write a video script for: $ARGUMENTS

1. If no style is given, pick the best one from `styles/styles.json` and say why.
2. Run `python3 tools/script_generator.py "<title>" --style <style>` to create the template.
3. Fill in the template completely:
   - 3 hook options (strongest first)
   - Voiceover lines for each section, sized to the section's time (about 2.5 spoken words per second)
   - On-screen text and specific B-roll ideas for each section
   - A full shot list
   - Post section: title, description, 5-10 hashtags and a thumbnail idea
4. Write in a natural, spoken tone. Use short sentences.
5. Show me the hook options and ask if I want changes.
