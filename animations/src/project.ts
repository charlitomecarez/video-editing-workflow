import {makeProject} from '@motion-canvas/core';
import {Code, LezerHighlighter} from '@motion-canvas/2d';
import {parser} from '@lezer/javascript';

import title from './scenes/title?scene';
import codeDemo from './scenes/code-demo?scene';
import diagram from './scenes/diagram?scene';

// Syntax highlighting for <Code> (TypeScript / JSX)
Code.defaultHighlighter = new LezerHighlighter(parser.configure({dialect: 'jsx ts'}));

// Scenes play in this order. Add your own in src/scenes/ and list them here.
export default makeProject({
  scenes: [title, codeDemo, diagram],
});
