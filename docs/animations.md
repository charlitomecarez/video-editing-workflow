# Animations (Motion Canvas)

[Motion Canvas](https://motioncanvas.io) (MIT license) makes animations from TypeScript code: animated code, diagrams, titles and charts. It's perfect for tech explainers, and Claude can write the scenes for you.

## Run it
```bash
cd animations
npm start            # opens the editor at http://localhost:9000
```
- The editor shows a live preview and timeline. Save a scene file and the preview updates instantly.
- **Render:** Video Settings (camera icon, left) → **RENDER**. Output goes to `animations/output/`.
  - The default exporter is **FFmpeg (MP4, 30 fps)**, for full-frame clips.
  - Want a transparent overlay for Kdenlive? Switch the exporter to **Image sequence (PNG)**, then in Kdenlive use Project Bin → Add Image Sequence.
- Brand colors and fonts come from `[brand]` in config. They sync automatically on `npm start` (or run `npm run brand`).

## Starter scenes (`animations/src/scenes/`)
| Scene | What it shows |
|---|---|
| `title.tsx` | A keyword pill that pops in, morphs its text, then pops out |
| `code-demo.tsx` | Code appearing line by line, a highlighted line, and an in-place edit |
| `diagram.tsx` | Two boxes popping in with an arrow drawing between them |

Scenes play in the order listed in `src/project.ts`. To make a clip from one scene only, set the **range** in Video Settings, or keep a project with just that scene.

## Core ideas
```tsx
const box = createRef<Rect>();
view.add(<Rect ref={box} width={300} height={300} fill={brand.accent} scale={0} />);

yield* box().scale(1, 0.4, easeOutBack);          // animate a property over 0.4 s
yield* all(box().x(300, 1), box().rotation(90, 1)); // several things at once
yield* sequence(0.1, a().opacity(1, .3), b().opacity(1, .3)); // staggered
yield* waitFor(1);                                 // hold
```
Code animations (`<Code>`):
```tsx
yield* code().code.append(`\nnewLine();`, 0.6);    // type new code
yield* code().selection(lines(2, 3), 0.4);           // highlight lines
yield* code().code.replace(code().findFirstRange('old'), 'new', 0.6); // edit in place
yield* code().code(`completely different code`, 0.8); // morph to new code
```
Docs: https://motioncanvas.io/docs. Run `/animate "what you want"` in Claude Code and Claude writes the scene.

## Syncing to your voiceover
1. Put your voiceover file in `animations/src/audio/voice.wav` (create the folder; audio is git-ignored).
2. In `src/project.ts`: add `import voice from './audio/voice.wav';` and `audio: voice` inside `makeProject({ ... })`.
3. The timeline shows the waveform, so you can match `waitFor()` times to the words. The editor also supports **time events** (`yield* waitUntil('logo')`) that you drag on the timeline.

## Alternatives
- **Kdenlive keyframes:** fine for simple pop-ins and slides (see `docs/tech-explainer-style.md`).
- **Manim** (Python, MIT): great for math-heavy animation, but harder to set up. Not installed here.
- **Remotion** (React): powerful, but uses a source-available license (free for individuals and small teams). Not installed here.
