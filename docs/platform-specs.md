# Platform Specs

> Platforms change their limits often. Treat these as starting points and check each platform's current help pages before relying on exact numbers.

| Platform | Aspect | Resolution | Frame rate | Typical length | Notes |
|---|---|---|---|---|---|
| TikTok | 9:16 | 1080x1920 | 30 (or 60) | 15-60 s performs well, longer allowed | Captions burned in or native |
| YouTube Shorts | 9:16 (or 1:1) | 1080x1920 | 30 / 60 | Up to ~3 min | Vertical or square only, or it isn't a Short |
| Instagram Reels | 9:16 | 1080x1920 | 30 | 15-90 s sweet spot | Cover image is cropped to 4:5 on the profile grid |
| Facebook Reels | 9:16 | 1080x1920 | 30 | 15-90 s | Same file as IG usually works |
| YouTube (long) | 16:9 | 1920x1080 or 3840x2160 | Match footage (24/30/60) | 8-15 min common | Add chapters, end screen in last 5-20 s |

## Safe zones for vertical video (1080x1920)
App buttons and captions cover parts of the screen. Keep important text and faces inside the middle:
- **Top ~250 px:** username, search and tabs
- **Bottom ~350 px:** caption, music and progress bar
- **Right ~150 px:** like, comment and share buttons

For burned-in captions, set `[captions].margin_v` high enough to clear the bottom zone (try 150-250 with a 1920-tall video). Check it on your phone before posting.

## Audio
- Target about **-14 LUFS** integrated loudness for social and YouTube (`[prep].loudness`).
- Keep voice clearly above music. Music should sit 15-25 dB under the voice.

## Export settings (Kdenlive / ffmpeg)
- H.264 (MP4), AAC audio at 48 kHz, 192 kbps or more
- Same frame rate as the project. Don't convert 30 to 60.
- High quality (CRF around 18). Platforms re-compress anyway, so start from a good file.

## Thumbnails and covers
| Platform | Size |
|---|---|
| YouTube | 1280x720 (16:9), under 2 MB |
| Shorts / Reels / TikTok | Pick a frame in-app, or upload a 1080x1920 cover. Keep text in the center 1080x1350 area. |
