// Optional animated graphics: turns a filled template into a HyperFrames composition and
// renders it as a short MP4 next to the PNG (01-1-cap-42.png -> 01-1-cap-42.mp4).
// Used by tools/graphic --animate (or [graphics].animate = true). Off by default.
//
// A template animates when it has an animate.js. That file runs after the template's own
// script, with these in scope:
//   tl                       the paused GSAP timeline (times are in seconds)
//   D                        clip length before the hold ([graphics].animate_seconds)
//   pop(el, at)              scale-bounce an element in
//   counters(selector, at, duration)   count the numbers inside the selection up from 0
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const PKG = path.join(ROOT, "tools", "graphics", "animated");
const HF = path.join(PKG, "node_modules", ".bin", "hyperframes");
const GSAP = path.join(PKG, "node_modules", "gsap", "dist", "gsap.min.js");

export const canAnimate = (tplDir) => fs.existsSync(path.join(tplDir, "animate.js"));

export function checkInstalled() {
  if (!fs.existsSync(HF) || !fs.existsSync(GSAP))
    throw new Error("Animated graphics aren't installed. Run: tools/setup.sh --animated-graphics");
  try {
    execFileSync("ffmpeg", ["-version"], { stdio: "ignore" });
  } catch {
    throw new Error("Animated graphics need FFmpeg. Run: tools/setup.sh");
  }
}

// The renderer only uses fonts it can find: declare the local ones the templates use
function fontFaces(brand) {
  const names = new Set([
    "Arial Black",
    "Impact",
    "Arial Rounded MT Bold",
    "Helvetica Neue",
    "Arial",
    "Menlo",
  ]);
  for (const k of ["font_heading", "font_body", "font_code"])
    for (const f of String(brand[k] ?? "").split(","))
      if (f.trim() && !/^(sans-serif|serif|monospace|system-ui)$/.test(f.trim()))
        names.add(f.trim().replace(/^["']|["']$/g, ""));
  return [...names].map((f) => `@font-face{font-family:"${f}";src:local("${f}")}`).join("");
}

const HELPERS = `
  const tl = gsap.timeline({ paused: true });
  function pop(el, at) {
    tl.fromTo(el, { scale: 0.55, opacity: 0, y: 30 }, { scale: 1.07, opacity: 1, y: 0, duration: 0.13, ease: "power2.out" }, at)
      .to(el, { scale: 1, duration: 0.12, ease: "power2.inOut" }, at + 0.13);
  }
  // Tweens the text itself (no callbacks), so any frame can be rendered on its own
  function counters(sel, at, dur) {
    document.querySelectorAll(sel).forEach((el) => {
      el.innerHTML = el.innerHTML.replace(/\\d+/g, (n) => '<span class="num" data-to="' + n + '">' + n + "</span>");
    });
    document.querySelectorAll(sel + " .num").forEach((n) => {
      const w = n.getBoundingClientRect().width;   // keep the final width so the line doesn't jitter
      n.style.cssText = "display:inline-block;text-align:center;width:" + w + "px";
      tl.fromTo(n, { innerText: 0 }, { innerText: +n.dataset.to, snap: { innerText: 1 }, duration: dur, ease: "power2.out" }, at);
    });
  }
`;

// html: the filled template (images already embedded as data: URLs), same as the PNG render
export function renderClip({ html, tplDir, out, width, height, brand, cfg }) {
  const secs = Number(cfg.animate_seconds ?? 1.5);
  const hold = Math.max(secs, Number(cfg.animate_hold_seconds ?? 10));
  const fps = Number(cfg.animate_fps ?? 30);
  const anim = fs.readFileSync(path.join(tplDir, "animate.js"), "utf8");
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "vw-anim-"));
  try {
    fs.copyFileSync(GSAP, path.join(dir, "gsap.min.js"));
    const css =
      `<style>${fontFaces(brand)}` +
      // The template's <body> is the stage; the composition root copies its layout
      `#root{position:absolute;inset:0;display:inherit;flex-direction:inherit;align-items:inherit;` +
      `justify-content:inherit;padding:inherit}.hl{display:inline-block}</style>`;
    let page = html.replace(/<base [^>]*>/i, "");
    page = page.replace(/<head>/i, `<head>${css}<script src="gsap.min.js"></script>`);
    page = page.replace(
      /(<body[^>]*>)/i,
      `$1<div id="root" data-composition-id="main" data-start="0" data-duration="${secs}" ` +
        `data-width="${width}" data-height="${height}">`,
    );
    page = page.replace(
      /<\/body>/i,
      `<script>const D = ${secs};${HELPERS}\n${anim}\n` +
        `window.__timelines = window.__timelines || {}; window.__timelines["main"] = tl; tl.seek(0);</script></div></body>`,
    );
    fs.writeFileSync(path.join(dir, "index.html"), page);
    const raw = path.join(dir, "anim.mp4");
    execFileSync(
      HF,
      ["render", "--fps", String(fps), "-q", String(cfg.animate_quality ?? "looks"), "-o", raw],
      {
        cwd: dir,
        stdio: ["ignore", "ignore", "pipe"],
        env: { ...process.env, HYPERFRAMES_NO_TELEMETRY: "1", DO_NOT_TRACK: "1" },
      },
    );
    // Hold the last frame so the clip covers long slots (the rough cut trims it to fit)
    execFileSync("ffmpeg", [
      "-v",
      "error",
      "-y",
      "-i",
      raw,
      "-vf",
      `tpad=stop_mode=clone:stop_duration=${hold - secs}`,
      "-c:v",
      "libx264",
      "-crf",
      "16",
      "-pix_fmt",
      "yuv420p",
      "-r",
      String(fps),
      "-an",
      out,
    ]);
    return out;
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}
