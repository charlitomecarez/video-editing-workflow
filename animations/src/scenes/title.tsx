// Animated title / keyword pop-in. Change the text and timings, then render.
import {makeScene2D, Rect, Txt} from '@motion-canvas/2d';
import {all, createRef, easeOutBack, waitFor} from '@motion-canvas/core';
import {brand} from '../brand';

export default makeScene2D(function* (view) {
  view.fill(brand.bg);
  const pill = createRef<Rect>();
  const label = createRef<Txt>();

  view.add(
    <Rect
      ref={pill}
      layout
      padding={[30, 70]}
      radius={999}
      fill={brand.bg2}
      stroke={brand.accent}
      lineWidth={8}
      scale={0}
    >
      <Txt ref={label} text="Your topic" fill={brand.fg} fontFamily={brand.fontHeading} fontSize={120} />
    </Rect>,
  );

  yield* pill().scale(1, 0.35, easeOutBack); // pop in
  yield* waitFor(0.8);
  yield* label().text('explained fast', 0.6); // text morphs
  yield* waitFor(0.8);
  yield* all(pill().scale(0, 0.25), pill().rotation(-8, 0.25)); // pop out
});
