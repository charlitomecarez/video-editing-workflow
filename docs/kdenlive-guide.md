# Kdenlive Beginner Guide

A practical guide to Kdenlive 26.x on macOS.

## The interface
| Panel | What it's for |
|---|---|
| **Project Bin** (top left) | All your imported clips, titles and sequences |
| **Clip Monitor** | Preview a bin clip and set in/out points before adding it |
| **Project Monitor** | Preview of the timeline (your actual edit) |
| **Timeline** (bottom) | Video tracks (V1, V2...) on top, audio tracks (A1, A2...) below |
| **Effects / Compositions** | Drag effects onto clips and transitions between tracks |

Higher video tracks appear on top. Put B-roll and text on V2 and V3 above your main footage on V1.

## First project, step by step
1. **New project:** File → New. Choose the profile that matches your style (for example "HD 1080p 30 fps" or a vertical 1080x1920 profile).
2. **Save right away:** File → Save As → `projects/<video>/<video>.kdenlive`.
3. **Import:** drag files from Finder into the Project Bin.
4. **Turn on proxies** for phone or 4K footage: Project → Project Settings → Proxy.
5. **Rough cut:** drag the main clip to V1/A1. Play it with Space and cut with Shift+R at each mistake. Select the bad parts and press Delete, then remove the gaps (right-click gap → Remove Space).
   - Faster: run `tools/cut-silence.sh` first and open the generated `_cut.kdenlive`.
6. **B-roll:** drag clips onto V2 above the moment they illustrate. Mute their audio if needed.
7. **Text:** Project Bin → right-click → Add Title Clip, then drag it to V3.
8. **Music:** drag to A2. Lower it with the Volume effect, or keyframe it down while someone talks.
9. **Subtitles:** Project → Subtitles → Import Subtitle File (from `tools/subtitles.sh`).
10. **Color and audio polish:** see the effects table below.
11. **Render:** Project → Render → MP4-H264/AAC → Render to File → save into `export/`.

## Polishing an auto rough cut

`tools/rough_cut.py` (or `/roughcut`) gives you `<video>-roughcut.kdenlive` with everything already on the timeline:

| Track | What's on it |
|---|---|
| V2 Graphics | your `graphics/NN-*` and `footage/broll/NN-*` files, each starting when row NN is spoken |
| V1 Recording | camera or screen recording, best take of each line |
| A1 Voice | your voice (the cleaned version if you ran clean-voice.sh) |
| A2 Music | `audio/music.*`, already quieter and faded out |

Colored flags on the ruler are **guides**: purple = script section, orange = ad-lib (something you said that isn't in the script), red = check this. Jump between them with Timeline → Guides, or the Guides panel (View → Guides).

1. Double-click the `.kdenlive` file (or Kdenlive → File → Open).
2. Press **Space** and watch it once from start to finish. Don't fix anything yet, just note the times.
3. Ad-lib you don't want: click the clip on V1, press **Delete**, then right-click the empty gap → **Remove Space**. Do the same on A1 if the audio clip stays behind (V1 and A1 clips are grouped, so usually both go).
4. A graphic shows too early or late: drag it left/right on V2. Drag its edges to make it shorter or longer.
5. Add life: right-click a graphic → Add Effect → Transform, or use the Pop In from the edit checklist.
6. Captions: Project → Subtitles → Import Subtitle File → `roughcut/roughcut.srt`.
7. Save with **File → Save As** under a new name (for example `<video>.kdenlive`), so rebuilding the rough cut never overwrites your edits.

## Keyframes (animating anything)
1. Select a clip with an effect (for example Transform).
2. In the effect panel, click the keyframe button (◇) to add a keyframe at the playhead.
3. Move the playhead, change the value, and a second keyframe is added.
4. Right-click a keyframe to change the easing (smooth vs linear).

## Useful effects
| Goal | Effect | Tip |
|---|---|---|
| Zoom in or out | Transform | 110-120% punch-ins hide jump cuts |
| Crop | Crop, Scale & Tilt | Reframe horizontal to vertical |
| Fix exposure / white balance | Lift/Gamma/Gain, White Balance | Check with View → Waveform |
| Film look | Apply LUT | Download free .cube LUTs |
| Blur (faces, background) | Box Blur, Obscure | Keyframe Obscure to follow movement |
| Green screen | Chroma Key: Advanced | Light the screen evenly |
| Clean voice | Noise suppressor for voice, Compressor, Loudness | Apply on the voice track |
| Fade in / out | Fade In / Fade Out (video & audio) | Or drag the clip's corner handles |
| Speed | Right-click → Change Speed, or Time Remap | Time Remap gives smooth ramps |

## Transitions
- Between clips on the **same track**: overlap the clips, then right-click → Insert a mix (crossfade).
- Between **tracks**: Compositions → drag "Dissolve" / "Wipe" between V1 and V2 clips.
- For most modern content, **use hard cuts**. Save transitions for scene or time changes.

## Render settings cheat sheet
| Use | Preset | Notes |
|---|---|---|
| YouTube / social | MP4-H264/AAC | Quality around 80-90%, matching the project fps |
| Highest quality master | MP4-H265 or ProRes (if available) | Large files, good for archiving |
| Quick preview | MP4-H264/AAC with lower quality | Fast, for checking edits |

## When things go wrong
| Problem | Fix |
|---|---|
| Choppy playback | Proxies on, lower monitor preview resolution |
| Audio drifts out of sync | Footage is variable frame rate. Run `tools/prep.sh` and replace the clip |
| Crash / lost work | Project → Open Backup File |
| Red "missing" clips | Relink when prompted, or right-click → Replace Clip |
| Render is the wrong size | Check Project Settings profile matches the target |
