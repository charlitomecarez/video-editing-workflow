// Animated diagram: boxes pop in and an arrow draws between them.
import {Line, makeScene2D, Rect, Txt} from '@motion-canvas/2d';
import {createRef, easeOutBack, sequence, waitFor} from '@motion-canvas/core';
import {brand} from '../brand';

function Box(props: {x: number; label: string; refTo: ReturnType<typeof createRef<Rect>>}) {
  return (
    <Rect
      ref={props.refTo}
      x={props.x}
      width={420}
      height={180}
      radius={20}
      fill={brand.bg2}
      stroke={brand.accent}
      lineWidth={6}
      scale={0}
    >
      <Txt
        text={props.label}
        fill={brand.fg}
        fontFamily={brand.fontBody}
        fontWeight={700}
        fontSize={56}
      />
    </Rect>
  );
}

export default makeScene2D(function* (view) {
  view.fill(brand.bg);
  const client = createRef<Rect>();
  const server = createRef<Rect>();
  const arrow = createRef<Line>();

  view.add(
    <>
      <Box x={-450} label="Client" refTo={client} />
      <Box x={450} label="Server" refTo={server} />
      <Line
        ref={arrow}
        points={[
          [-230, 0],
          [230, 0],
        ]}
        stroke={brand.accent2}
        lineWidth={10}
        endArrow
        arrowSize={28}
        end={0}
      />
    </>,
  );

  yield* sequence(0.15, client().scale(1, 0.35, easeOutBack), server().scale(1, 0.35, easeOutBack));
  yield* arrow().end(1, 0.6);
  yield* waitFor(1.5);
});
