#!/usr/bin/env node
// Render HTML templates in graphics/templates/ to PNG: thumbnails, code cards,
// slates, covers and diagrams. Brand colors and fonts come from [brand] in config.toml.
//
// Usage:
//   tools/graphic <template> [--set key=value ...] [--data vals.json] [--out file.png]
//                 [--size 1280x720] [--transparent | --opaque] [--open]
//   tools/graphic --batch jobs.json      # many graphics in one go
//   tools/graphic --list                 # templates and their fields
//
// Values that are paths to image files become embedded images. In text fields,
// *word* highlights a word in the accent color and \n starts a new line.
import { chromium } from "playwright";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const TPL_DIR = path.join(ROOT, "graphics", "templates");
const CFG = JSON.parse(execFileSync("python3", [path.join(ROOT, "tools", "vwconfig.py"), "show"], { encoding: "utf8" }));
const BRAND = CFG.brand ?? {};
const GCFG = CFG.graphics ?? {};
const IMG_EXT = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif", ".svg": "image/svg+xml" };
const CODE_EXT = { ".js": "js", ".mjs": "js", ".ts": "ts", ".tsx": "tsx", ".jsx": "jsx", ".py": "python", ".rs": "rust", ".go": "go", ".sh": "bash", ".json": "json", ".html": "html", ".css": "css", ".sql": "sql", ".java": "java", ".c": "c", ".cpp": "cpp", ".rb": "ruby", ".php": "php", ".swift": "swift", ".kt": "kotlin", ".yaml": "yaml", ".yml": "yaml", ".toml": "toml", ".md": "markdown" };

function die(msg) { console.error(msg); process.exit(1); }

function listTemplates() {
  return fs.readdirSync(TPL_DIR).filter((d) => fs.existsSync(path.join(TPL_DIR, d, "template.html"))).sort();
}

function loadTemplate(name) {
  const dir = path.join(TPL_DIR, name);
  if (!fs.existsSync(path.join(dir, "template.html"))) die(`Unknown template "${name}". Options: ${listTemplates().join(", ")}`);
  const meta = fs.existsSync(path.join(dir, "template.json")) ? JSON.parse(fs.readFileSync(path.join(dir, "template.json"), "utf8")) : {};
  return { dir, meta, html: fs.readFileSync(path.join(dir, "template.html"), "utf8") };
}

function resolvePath(v, baseDir) {
  if (typeof v !== "string" || !v || v.includes("\n") || v.length > 1024) return null;
  const p = path.resolve(baseDir, v.replace(/^~(?=\/)/, os.homedir()));
  return fs.existsSync(p) && fs.statSync(p).isFile() ? p : null;
}

function asImage(v, baseDir) {
  const p = resolvePath(v, baseDir);
  const type = p && IMG_EXT[path.extname(p).toLowerCase()];
  return type ? `data:${type};base64,${fs.readFileSync(p).toString("base64")}` : null;
}

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const fmt = (s) => esc(s).replace(/\\n|\n/g, "<br>").replace(/\*(.+?)\*/g, '<span class="hl">$1</span>');

function fill(html, vals) {
  // {{#key}}...{{/key}} only kept when key has a value
  html = html.replace(/\{\{#(\w+)\}\}([\s\S]*?)\{\{\/\1\}\}/g, (_, k, inner) => (vals[k] ? inner : ""));
  html = html.replace(/\{\{\{(\w+)\}\}\}/g, (_, k) => vals[k] ?? "");
  return html.replace(/\{\{(\w+)\}\}/g, (_, k) => (vals[k] == null ? "" : fmt(vals[k])));
}

function brandCss() {
  const b = BRAND;
  const imp = b.font_css ? `@import url("${b.font_css}");\n` : "";
  return `<style>${imp}:root{--bg:${b.bg ?? "#0d1117"};--fg:${b.fg ?? "#fff"};--accent:${b.accent ?? "#ffd400"};` +
    `--accent2:${b.accent2 ?? "#00e5ff"};--font-heading:${b.font_heading ?? "Arial Black, sans-serif"};` +
    `--font-body:${b.font_body ?? "Helvetica Neue, Arial, sans-serif"};--font-code:${b.font_code ?? "Menlo, monospace"};}` +
    `.hl{color:var(--accent);}</style>`;
}

async function prepare(tpl, raw, baseDir) {
  const vals = { ...(tpl.meta.defaults ?? {}), ...raw };
  if (!vals.logo && BRAND.logo) vals.logo = BRAND.logo;
  for (const [k, v] of Object.entries(vals)) {
    const img = asImage(v, k === "logo" && v === BRAND.logo ? ROOT : baseDir);
    if (img) vals[k] = img;
  }
  if (tpl.meta.code) {
    const file = resolvePath(vals.code, baseDir);
    if (file) {
      vals.lang ??= CODE_EXT[path.extname(file).toLowerCase()] ?? "text";
      vals.title ??= path.basename(file);
      vals.code = fs.readFileSync(file, "utf8").replace(/\s+$/, "");
    }
    const { codeToHtml } = await import("shiki");
    vals.code_html = await codeToHtml(String(vals.code ?? "").replace(/\\n/g, "\n"), {
      lang: vals.lang || "text",
      theme: vals.theme || BRAND.code_theme || "github-dark",
    });
  }
  if (tpl.meta.mermaid) {
    const file = resolvePath(vals.diagram, baseDir);
    if (file) vals.diagram = fs.readFileSync(file, "utf8");
    vals.diagram = String(vals.diagram ?? "").replace(/\\n/g, "\n");
  }
  return vals;
}

async function render(browser, job, baseDir) {
  const tpl = loadTemplate(job.template);
  const vals = await prepare(tpl, job.set ?? {}, baseDir);
  const [w, h] = String(job.size ?? tpl.meta.size ?? "1920x1080").split("x").map(Number);
  const transparent = job.transparent ?? tpl.meta.transparent ?? false;
  let html = fill(tpl.html, vals);
  html = html.replace(/<head>/i, `<head><base href="${pathToFileURL(tpl.dir + "/").href}">${brandCss()}`);

  const tmp = path.join(os.tmpdir(), `vw-graphic-${process.pid}-${Date.now()}.html`);
  fs.writeFileSync(tmp, html);
  const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: Number(job.scale ?? GCFG.scale ?? 1) });
  try {
    await page.goto(pathToFileURL(tmp).href, { waitUntil: "load" });
    if (tpl.meta.mermaid) {
      await page.addScriptTag({ path: path.join(ROOT, "node_modules", "mermaid", "dist", "mermaid.min.js") });
      await page.evaluate(async ({ text, brand }) => {
        // eslint-disable-next-line no-undef
        mermaid.initialize({
          startOnLoad: false, theme: "base",
          themeVariables: {
            background: "transparent", primaryColor: brand.bg2 ?? "#161b22", primaryTextColor: brand.fg ?? "#fff",
            primaryBorderColor: brand.accent ?? "#ffd400", lineColor: brand.accent2 ?? "#00e5ff",
            edgeLabelBackground: brand.bg ?? "#0d1117", clusterBkg: brand.bg ?? "#0d1117", clusterBorder: brand.accent2 ?? "#00e5ff",
            fontFamily: brand.font_body ?? "Helvetica Neue, Arial, sans-serif", fontSize: "28px",
          },
        });
        // eslint-disable-next-line no-undef
        const { svg } = await mermaid.render("vwdiagram", text);
        document.querySelector("#diagram").innerHTML = svg;
      }, { text: vals.diagram, brand: BRAND });
    }
    await page.evaluate(() => document.fonts.ready);
    let out = job.out ?? path.join(GCFG.output_dir ?? "graphics/out", `${job.template}-${Date.now()}.png`);
    out = path.resolve(baseDir, out);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    const opts = { path: out, omitBackground: transparent };
    if (tpl.meta.selector && vals.frame !== "full") await page.locator(tpl.meta.selector).screenshot(opts);
    else await page.screenshot(opts);
    const rel = path.relative(process.cwd(), out);
    console.log(`Saved ${rel.startsWith("..") ? out : rel}`);
    return out;
  } finally {
    await page.close();
    fs.rmSync(tmp, { force: true });
  }
}

async function launch() {
  const channel = GCFG.browser ?? "chrome";
  try {
    return await chromium.launch(channel === "chromium" ? {} : { channel });
  } catch {
    try { return await chromium.launch(); } catch {
      die(`Couldn't start a browser. Install Google Chrome, or run: npx playwright install chromium`);
    }
  }
}

function parseArgs(argv) {
  const a = { set: {}, positional: [] };
  for (let i = 0; i < argv.length; i++) {
    const x = argv[i];
    const next = () => { if (i + 1 >= argv.length) die(`${x} needs a value`); return argv[++i]; };
    if (x === "--set") { const kv = next(); const j = kv.indexOf("="); if (j < 1) die(`--set expects key=value, got "${kv}"`); a.set[kv.slice(0, j)] = kv.slice(j + 1); }
    else if (x === "--data") Object.assign(a.set, JSON.parse(fs.readFileSync(next(), "utf8")));
    else if (x === "--out" || x === "-o") a.out = next();
    else if (x === "--size") a.size = next();
    else if (x === "--scale") a.scale = next();
    else if (x === "--batch") a.batch = next();
    else if (x === "--transparent") a.transparent = true;
    else if (x === "--opaque") a.transparent = false;
    else if (x === "--open") a.open = true;
    else if (x === "--list") a.list = true;
    else if (x === "-h" || x === "--help") a.help = true;
    else if (x.startsWith("--") && x.includes("=")) { const [k, ...v] = x.slice(2).split("="); a.set[k] = v.join("="); }
    else a.positional.push(x);
  }
  return a;
}

async function main() {
  const a = parseArgs(process.argv.slice(2));
  if (a.help || (!a.list && !a.batch && !a.positional.length)) {
    console.log(fs.readFileSync(fileURLToPath(import.meta.url), "utf8").split("\n").slice(1, 14).map((l) => l.replace(/^\/\/ ?/, "")).join("\n"));
    return;
  }
  if (a.list) {
    for (const name of listTemplates()) {
      const { meta } = loadTemplate(name);
      console.log(`\n${name}  (${meta.size ?? "1920x1080"}${meta.transparent ? ", transparent" : ""})\n  ${meta.description ?? ""}`);
      for (const [k, d] of Object.entries(meta.fields ?? {})) console.log(`    ${k.padEnd(10)} ${d}`);
    }
    return;
  }
  let jobs, baseDir = process.cwd();
  if (a.batch) {
    jobs = JSON.parse(fs.readFileSync(a.batch, "utf8"));
    if (!Array.isArray(jobs)) die("Batch file must be a JSON array of {template, set, out, size}");
    baseDir = path.dirname(path.resolve(a.batch));
  } else {
    jobs = [{ template: a.positional[0], set: a.set, out: a.out, size: a.size, scale: a.scale, transparent: a.transparent }];
  }
  const browser = await launch();
  const outs = [];
  try {
    for (const job of jobs) outs.push(await render(browser, job, baseDir));
  } finally {
    await browser.close();
  }
  if (a.open) execFileSync("open", outs);
}

main().catch((e) => die(e.stack ?? String(e)));
