---
name: publishing
description: Use when preparing a finished video for posting (export settings, titles, captions, descriptions, hashtags, thumbnails, cross-posting) or when reviewing results after posting.
---

# Publishing

## Before posting
1. Check the export with `ffprobe`: resolution, fps and duration must fit the platform limits in `docs/platform-specs.md`.
2. Short-form: burn captions (`tools/burn-captions.sh`) unless the platform's own captions will be used.
3. Thumbnails: use the `graphics-thumbnails` skill (`tools/thumbnails.sh` for frames, `tools/cutout.sh` for subjects, `tools/graphic thumbnail-*` / `cover-vertical` to compose). Good thumbnails show a clear face or emotion, one subject, high contrast and 3-5 words of text at most.
4. Fill in the script's Post section for each platform in `[creator].platforms`:
   - Title/caption: put the hook first and keep the important words at the start
   - Hashtags: 3-5 specific ones plus 1-2 broad ones. No banned or irrelevant tags.
   - YouTube description: the first 2 lines matter most, then add chapters (`0:00 Intro`) for videos over 3 minutes
5. Set the script's Status to `posted`.

## Cross-posting
- Export once without platform watermarks, then post the same file everywhere.
- For a 16:9 master, use `tools/vertical.sh --mode blur` (or recut in Kdenlive with a vertical profile for the best result).

## After ~7 days
Fill in the Results table in the script. Compare it with past videos:
- Low average watch % → the hook or pacing is weak. Suggest a tighter edit or shorter style next time.
- Good watch % but low views → the topic or title is the problem. Feed this back into `topic-research`.
- Lots of comments → make a follow-up video.
