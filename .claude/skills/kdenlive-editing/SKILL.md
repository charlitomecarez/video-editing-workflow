---
name: kdenlive-editing
description: Use when the user asks how to do something in Kdenlive (cutting, effects, titles, keyframes, color, audio, rendering, proxies, crashes) or needs a step-by-step editing walkthrough. Also covers safely reading or editing .kdenlive project files.
---

# Kdenlive editing coach

The user is a beginner on macOS (Apple Silicon) using Kdenlive 26.x. Explain one step at a time, using exact menu paths and shortcuts. Wait for them to confirm a step before giving the next big one.

## Before you answer

- Check the style in `styles/styles.json` (and `styles/custom/`) for the video they're editing. Your advice should match its pacing, captions, music and color notes.
- For deeper reference, use `docs/kdenlive-guide.md`.

## Core shortcuts (macOS)

| Action                                              | Shortcut            |
| --------------------------------------------------- | ------------------- |
| Play / pause                                        | Space               |
| Play backward / forward (faster when pressed again) | J / L, K to stop    |
| Cut at playhead (selected clip)                     | Shift+R             |
| Razor tool / selection tool                         | X / S               |
| Set in / out point in clip monitor                  | I / O               |
| Insert / overwrite clip to timeline                 | V / B               |
| Add marker                                          | M                   |
| Ripple delete selection                             | Shift+Delete        |
| Zoom timeline                                       | Cmd + / Cmd -       |
| Undo / redo                                         | Cmd+Z / Cmd+Shift+Z |
| Render                                              | Cmd+Enter           |

## Common tasks

- **Project profile:** Project → Project Settings → Video profile. Match the style's resolution and fps. Pick "Vertical HD 30fps" for 9:16.
- **Proxies (smooth playback):** Project Settings → Proxy → Enable. Then right-click the clips in Project Bin → Proxy Clip.
- **Punch-in zoom:** Effects → search "Transform" → drag onto clip → set size to 110-120%. Add keyframes for animated zooms.
- **Text:** Project Bin → right-click → Add Title Clip. For captions, use the Subtitles track (Project → Subtitles → Import Subtitle File for .srt).
- **Speed ramp:** right-click clip → Time Remap, then add keyframes.
- **Color:** Effects → "Lift/Gamma/Gain" for basic correction, "Apply LUT" for a look. Use the Scopes panel (View → Waveform) to check exposure.
- **Voice cleanup:** audio effects "Noise suppressor for voice" → "Compressor" → "Loudness". Keep voice peaks around -6 dB.
- **Music under voice:** lower the music track, or keyframe its volume down while someone talks.
- **J/L cuts:** unlink audio and video (right-click → Ungroup), then extend the audio past the cut.
- **Render:** Project → Render → MP4-H264/AAC. Set the quality slider, then Render to File.

## Troubleshooting

- **Laggy playback:** turn on proxies, lower the preview resolution (monitor toolbar), and close other apps.
- **Audio out of sync with phone footage:** run `tools/prep.sh` first. Phone video is variable frame rate.
- **Crash:** Project → Open Backup File restores autosaves.
- **Missing clip (red):** use the Relink dialog when opening, or right-click the clip → Replace Clip.

## Editing .kdenlive files

These are MLT XML files. Before changing one:

1. Ask the user to close it in Kdenlive (or confirm it is closed).
2. Copy it to `<name>.kdenlive.bak-<date>`.
3. Make the smallest possible change. Never touch media paths unless relinking is the goal.
4. Tell them to reopen it and check the timeline.
