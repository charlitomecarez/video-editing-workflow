---
name: topic-research
description: Use when brainstorming, researching or ranking video topic ideas, content calendars or series ideas for the user's niches.
---

# Topic research

## Inputs

- `[creator]` in config (audience, niches, platforms, avoid)
- `topics/niches.json`, `topics/formats.json`
- `topics/ideas.md` and the Content Planner inbox (`python3 tools/planner.py ideas`) (existing ideas; don't duplicate) and Results tables in past scripts (repeat what performed well)

## Process

1. Quick baseline: `python3 topics/topic_generator.py --niche <n> -n 20` for raw combinations.
2. Improve on it. Rewrite awkward titles, combine ideas and add angles the templates can't (personal stories, local or Filipino angles, current events, seasonal topics like holidays, payday or back-to-school).
3. If web search is available and the user wants trending ideas, check what's currently popular in the niche. Say where each trend came from and never invent trends.
4. Score each idea from 1 to 5 on: **Demand** (do people search or watch this?), **Ease** (can they film it with what they have?) and **Fit** (audience and niche). Sort by total.
5. Suggest a style key for each one, plus a one-line hook.

## Output

A table: rank | title | niche | style | hook | D/E/F scores. Ask which to keep, then append them to `topics/ideas.md` as `- [ ] [niche] Title (style)` under today's date.

## Series and calendars

When asked for a content plan, group ideas into series (3-5 related videos) and spread them across the week. Mix easy and harder-to-film videos so the posting schedule stays realistic.
