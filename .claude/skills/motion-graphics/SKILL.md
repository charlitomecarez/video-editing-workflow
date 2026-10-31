---
name: motion-graphics
description: Use when the user wants an animated graphic, animated code, animated diagram, kinetic title or any Motion Canvas scene for a video.
---

# Motion graphics (Motion Canvas)

Project: `animations/` (Motion Canvas 3.17, TypeScript/TSX). Guide: `docs/animations.md`. Docs: https://motioncanvas.io/docs

## Writing a scene

1. Create `animations/src/scenes/<name>.tsx` with `export default makeScene2D(function* (view) { ... })`.
2. Import colors and fonts with `import {brand} from '../brand';` and set `view.fill(brand.bg)`. Never hardcode colors.
3. Register it in `animations/src/project.ts` (`import x from './scenes/<name>?scene'` and add it to `scenes`). If the user wants only this clip, put it first or tell them to set the range.
4. Match the style's pacing (`styles/styles.json`): tech-explainer pop-ins take 0.25-0.35 s with `easeOutBack`, and holds last about 1-2 s per idea.
5. Keep text big (≥ 48 px at 1920x1080) and code ≤ 10 lines.

## Verify before handing over

```bash
cd animations && node sync-brand.mjs && npx tsc --noEmit
```

Fix every type error. Then tell the user: `cd animations && npm start`, select the scene, press play, and **RENDER** (MP4 by default, or the PNG image-sequence exporter for transparent overlays in Kdenlive).

## Useful APIs (3.x)

- Animate a property: `yield* node().prop(value, seconds, easing?)`
- Combine: `all(...)` runs together, `sequence(delay, ...)` staggers, `chain(...)` runs in order, `loop(n, i => ...)`
- Timing: `waitFor(s)`, `waitUntil('event-name')` (draggable on the timeline, good for syncing to a voiceover)
- `<Code>`: `code.append(text, s)`, `code.prepend`, `code.insert([line, col], text, s)`, `code.replace(range, text, s)`, `code.remove(range, s)`, `code(newCode, s)`, `selection(lines(a, b), s)`, `findFirstRange('text')`
- `<Line>`: `points`, `endArrow`, animate `end(0 → 1)` to draw it
- `<Txt>`: `text('new', s)` morphs text
- Layout: `<Rect layout direction="column" gap={20} padding={40}>`
