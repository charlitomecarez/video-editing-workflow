// Animated code: type, highlight and edit code on screen. Great for explaining APIs.
import {Code, lines, makeScene2D, Rect} from '@motion-canvas/2d';
import {createRef, DEFAULT, waitFor} from '@motion-canvas/core';
import {brand} from '../brand';

export default makeScene2D(function* (view) {
  view.fill(brand.bg);
  const code = createRef<Code>();

  view.add(
    <Rect layout padding={50} radius={24} fill={brand.bg2}>
      <Code
        ref={code}
        fontSize={44}
        fontFamily={brand.fontCode}
        code={'const user = await getUser(id);'}
      />
    </Rect>,
  );

  yield* waitFor(0.6);
  // Add lines one after another
  yield* code().code.append(`\nif (!user) throw new Error('nope');`, 0.6);
  yield* code().code.append(`\nreturn user.name;`, 0.6);
  yield* waitFor(0.4);
  // Highlight a line (others dim), then reset
  yield* code().selection(lines(1), 0.4);
  yield* waitFor(0.8);
  yield* code().selection(DEFAULT, 0.4);
  // Edit part of the code in place
  yield* code().code.replace(code().findFirstRange('user.name'), 'user.name.toUpperCase()', 0.6);
  yield* waitFor(1);
});
