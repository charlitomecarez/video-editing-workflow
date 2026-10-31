#!/usr/bin/env python3
"""Turn a script.md into a clean, readable HTML page and open it in the browser.

Examples:
  python3 tools/script_view.py projects/2026-10-31-my-video/script.md
  python3 tools/script_view.py video-scripts/2026-11-01-x.md --theme light --no-open

Voiceover is shown big, on-screen text as highlighted captions, shots and notes smaller,
with word counts and estimated seconds per section. Works for both script layouts
(sections and av-table). Colors and fonts come from [brand]; defaults from [script_view].
Writes <name>_view.html next to the script (git-ignored). The .md stays the source:
edit the .md, then run this again.
"""
import argparse
import html
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import load, load_styles  # noqa: E402

LABEL = re.compile(r"^\*\*([^*]+?):\*\*\s*(.*)$")
LIST_ITEM = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")
TIMING = re.compile(r"\s*\(([^()]*)\)\s*$")


# ---------- inline markdown ----------

def inline(text):
    codes = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w])_(?!\s)(.+?)(?<!\s)_(?![\w])", r"<em>\1</em>", text)
    text = re.sub(r"\[CHECK([^\]]*)\]", r'<mark class="check">CHECK\1</mark>', text)
    text = re.sub(r"\[( |x|X)\]", lambda m: f'<input type="checkbox"{" checked" if m.group(1) != " " else ""}>', text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def plain_words(lines):
    text = re.sub(r"[`*_\[\]()|#>]", " ", " ".join(lines))
    return len([w for w in text.split() if re.search(r"\w", w)])


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-") or "x"


def field_kind(label):
    low = label.lower()
    if "voiceover" in low or "dialogue" in low or low in ("hear", "vo"):
        return "vo"
    if "on-screen" in low or "onscreen" in low:
        return "ost"
    if "shot" in low or "b-roll" in low or low == "see":
        return "shots"
    if "note" in low:
        return "notes"
    return "kv"


# ---------- blocks ----------

def render_table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    if len(cells) > 1 and all(re.fullmatch(r":?-{2,}:?", c) for c in cells[1] if c):
        head, body = cells[0], cells[2:]
    else:
        head, body = None, cells
    cls = [slug(h) for h in head] if head else []
    out = ['<div class="table-wrap"><table>']
    if head:
        out.append("<thead><tr>" + "".join(f'<th class="c-{c}">{inline(h)}</th>' for h, c in zip(head, cls)) + "</tr></thead>")
    out.append("<tbody>")
    words = 0
    for r in body:
        out.append("<tr>" + "".join(
            f'<td class="c-{cls[i] if i < len(cls) else ""}">{inline(c)}</td>' for i, c in enumerate(r)) + "</tr>")
        if head and "hear" in cls:
            i = cls.index("hear")
            if i < len(r):
                words += plain_words([r[i]])
    out.append("</tbody></table></div>")
    return "".join(out), words


def render_list(items):
    """items: [(indent, marker, text)] -> nested <ul>/<ol>."""
    out, stack = [], []
    for indent, marker, text in items:
        tag = "ol" if marker[0].isdigit() else "ul"
        while stack and indent < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
        if not stack or indent > stack[-1][0]:
            out.append(f"<{tag}>")
            stack.append((indent, tag))
        else:
            out.append("</li>")
        m = LABEL.match(text)
        body = f'<span class="k">{inline(m.group(1))}</span> {inline(m.group(2))}' if m else inline(text)
        out.append(f"<li>{body}")
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def render_blocks(lines, wps):
    """Render markdown lines. Returns (html, spoken word count)."""
    out, words, i = [], 0, 0
    while i < len(lines):
        line = lines[i]
        s = line.strip()
        if not s or s == "---":
            i += 1
        elif s.startswith("|"):
            j = i
            while j < len(lines) and lines[j].strip().startswith("|"):
                j += 1
            h, w = render_table(lines[i:j])
            out.append(h)
            words += w
            i = j
        elif LIST_ITEM.match(line):
            items = []
            while i < len(lines) and (m := LIST_ITEM.match(lines[i])):
                items.append((len(m.group(1)), m.group(2), m.group(3)))
                i += 1
            out.append(render_list(items))
        elif m := LABEL.match(s):
            label, rest = m.group(1), m.group(2)
            j = i + 1
            while j < len(lines) and not LABEL.match(lines[j].strip()):
                j += 1
            body = ([rest] if rest else []) + lines[i + 1:j]
            kind = field_kind(label)
            inner, w = render_blocks(body, wps)
            if kind == "vo":
                n = plain_words([b for b in body if b.strip()])
                words += n
                out.append(f'<div class="field vo"><div class="label">{inline(label)}<span class="count">{n} words · ~{round(n / wps)}s</span></div>{inner}</div>')
            elif kind == "kv":
                out.append(f'<p class="kvline"><span class="k">{inline(label)}:</span> {inner.removeprefix("<p>").removesuffix("</p>")}</p>'
                           if inner.startswith("<p>") and inner.count("<p>") == 1 else
                           f'<div class="field kv"><div class="label">{inline(label)}</div>{inner}</div>')
                words += w
            else:
                out.append(f'<div class="field {kind}"><div class="label">{inline(label)}</div>{inner}</div>')
            i = j
        else:
            para = []
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith("|") \
                    and not LIST_ITEM.match(lines[i]) and not LABEL.match(lines[i].strip()) and lines[i].strip() != "---":
                para.append(lines[i].strip())
                i += 1
            text = " ".join(para)
            if re.fullmatch(r"_[^_].*_", text):
                out.append(f'<p class="hint">{inline(text[1:-1])}</p>')
            else:
                out.append(f"<p>{inline(text)}</p>")
    return "".join(out), words


# ---------- document ----------

def parse(md):
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S)
    doc = {"title": "Script", "pre": [], "parts": []}
    cur = doc["pre"]
    for line in md.splitlines():
        if line.startswith("# ") and doc["title"] == "Script" and not doc["parts"]:
            doc["title"] = line[2:].strip()
        elif line.startswith("## "):
            doc["parts"].append({"title": line[3:].strip(), "lines": [], "cards": []})
            cur = doc["parts"][-1]["lines"]
        elif line.startswith("### ") and doc["parts"]:
            doc["parts"][-1]["cards"].append({"title": line[4:].strip(), "lines": [], "subs": []})
            cur = doc["parts"][-1]["cards"][-1]["lines"]
        elif line.startswith("#### ") and doc["parts"] and doc["parts"][-1]["cards"]:
            card = doc["parts"][-1]["cards"][-1]
            card["subs"].append({"title": line[5:].strip(), "lines": []})
            cur = card["subs"][-1]["lines"]
        else:
            cur.append(line)
    return doc


def split_heading(title):
    m = TIMING.search(title)
    return (title[:m.start()].strip(), m.group(1)) if m else (title, "")


def target_words(timing, wps):
    if m := re.search(r"~\s*(\d+)\s*words", timing):
        return int(m.group(1))
    if m := re.search(r"~\s*(\d+)\s*s\b", timing):
        return round(int(m.group(1)) * wps)
    return None


def meter(n, target):
    if not target:
        return ""
    off = abs(n - target) / target
    cls = "ok" if off <= 0.10 else "warn" if off <= 0.25 else "bad"
    return f'<span class="meter {cls}" title="spoken words vs target">{n} / {target} words</span>'


def build(md, cfg, styles, theme):
    doc = parse(md)
    style_key = next((m.group(1) for m in re.finditer(r"`([\w-]+)`", "\n".join(doc["pre"])) if m.group(1) in styles), None)
    wps = (styles.get(style_key, {}).get("words_per_second") if style_key else None) or cfg["script"]["words_per_second"]

    # "- **Length:** x | **Format:** y" in the header -> one chip per field
    pre = []
    for line in doc["pre"]:
        if line.startswith("- ") and " | **" in line:
            pre += ["- " + part.strip() for part in line[2:].split(" | ")]
        else:
            pre.append(line)
    pre_html, _ = render_blocks(pre, wps)
    toc, body, total = [], [], 0
    for part in doc["parts"]:
        pid = slug(part["title"])
        toc.append(f'<li><a href="#{pid}">{inline(part["title"])}</a>')
        intro, w = render_blocks(part["lines"], wps)
        total += w
        cards_html, sub_toc = [], []
        for card in part["cards"]:
            name, timing = split_heading(card["title"])
            cid = f"{pid}-{slug(name)}"
            sub_toc.append(f'<li><a href="#{cid}">{inline(name)}</a>{f"<span>{html.escape(timing.split(",")[0])}</span>" if timing else ""}</li>')
            inner, cw = render_blocks(card["lines"], wps)
            subs = []
            for sub in card["subs"]:
                sname, stiming = split_heading(sub["title"])
                sh, sw = render_blocks(sub["lines"], wps)
                cw += sw
                subs.append(f'<div class="sub"><h4>{inline(sname)}{f"<span class=timing>{html.escape(stiming)}</span>" if stiming else ""}'
                            f'{meter(sw, target_words(stiming, wps)) if sw else ""}</h4>{sh}</div>')
            total += cw
            badge = f'<span class="timing">{html.escape(timing)}</span>' if timing else ""
            cards_html.append(f'<article class="card" id="{cid}"><h3>{inline(name)}{badge}{meter(cw, target_words(timing, wps)) if cw else ""}</h3>{inner}{"".join(subs)}</article>')
        if sub_toc:
            toc[-1] += f'<ul>{"".join(sub_toc)}</ul>'
        toc[-1] += "</li>"
        body.append(f'<section class="part part-{pid}" id="{pid}"><h2>{inline(part["title"])}</h2>{intro}{"".join(cards_html)}</section>')

    b = cfg.get("brand", {})
    stats = f'<div class="stats"><span><b>{total}</b> spoken words</span><span><b>~{total / wps / 60:.1f}</b> min at {wps} words/s</span></div>'
    page = PAGE
    for k, v in {
        "__TITLE__": html.escape(doc["title"]),
        "__THEME__": theme,
        "__FONTCSS__": f'<link rel="stylesheet" href="{html.escape(b["font_css"])}">' if b.get("font_css") else "",
        "__BG__": b.get("bg", "#0d1117"), "__BG2__": b.get("bg2", "#161b22"), "__FG__": b.get("fg", "#ffffff"),
        "__ACCENT__": b.get("accent", "#ffd400"), "__ACCENT2__": b.get("accent2", "#00e5ff"),
        "__FH__": b.get("font_heading", "Arial Black, sans-serif"), "__FB__": b.get("font_body", "Helvetica, Arial, sans-serif"),
        "__FC__": b.get("font_code", "Menlo, monospace"),
        "__TOC__": "".join(toc), "__PRE__": pre_html, "__STATS__": stats, "__BODY__": "".join(body),
    }.items():
        page = page.replace(k, v)
    return page


PAGE = """<!doctype html>
<html lang="en" data-theme="__THEME__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>__FONTCSS__
<style>
:root{--accent:__ACCENT__;--accent2:__ACCENT2__;--fh:__FH__;--fb:__FB__;--fc:__FC__;
  --bg:#f6f7f9;--panel:#fff;--fg:#14171c;--muted:#5d6672;--line:#e2e5ea;--vo:#0f1216;--link:#0a66c2}
@media (prefers-color-scheme: dark){:root[data-theme="auto"]{--bg:__BG__;--panel:__BG2__;--fg:__FG__;--muted:#9aa4b2;--line:#2a313b;--vo:#f3f5f7;--link:var(--accent2)}}
:root[data-theme="dark"]{--bg:__BG__;--panel:__BG2__;--fg:__FG__;--muted:#9aa4b2;--line:#2a313b;--vo:#f3f5f7;--link:var(--accent2)}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 var(--fb);-webkit-font-smoothing:antialiased}
a{color:var(--link)}
code{font:.88em var(--fc);background:color-mix(in srgb,var(--muted) 15%,transparent);padding:.1em .35em;border-radius:4px}
.layout{display:grid;grid-template-columns:240px minmax(0,1fr);gap:40px;max-width:1180px;margin:0 auto;padding:40px 24px 120px}
nav{position:sticky;top:24px;align-self:start;max-height:calc(100vh - 48px);overflow:auto;font-size:14px}
nav ul{list-style:none;margin:0;padding:0}
nav>ul>li{margin:0 0 10px}
nav>ul>li>a{font-weight:700;color:var(--fg);text-decoration:none}
nav li ul{margin:6px 0 0;padding-left:12px;border-left:2px solid var(--line)}
nav li li{display:flex;justify-content:space-between;gap:8px;padding:2px 0}
nav li li a{color:var(--muted);text-decoration:none}
nav li li a:hover,nav>ul>li>a:hover{color:var(--fg)}
nav li li span{color:var(--muted);font-size:12px;white-space:nowrap;opacity:.7}
header h1{font:900 clamp(30px,5vw,48px)/1.05 var(--fh);margin:0 0 18px;letter-spacing:-.01em}
header h1::after{content:"";display:block;width:64px;height:6px;background:var(--accent);margin-top:14px;border-radius:3px}
header ul{list-style:none;padding:0;margin:0 0 14px;display:flex;flex-wrap:wrap;gap:8px}
header li{background:var(--panel);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font-size:13px}
header .k,.kvline .k,li .k{color:var(--muted);font-weight:600}
header p{color:var(--muted);font-size:14px;margin:4px 0}
.stats{display:flex;gap:18px;flex-wrap:wrap;margin:14px 0 0;font-size:14px;color:var(--muted)}
.stats b{color:var(--fg);font-size:18px}
section.part{margin-top:56px}
h2{font:900 13px/1 var(--fh);text-transform:uppercase;letter-spacing:.14em;color:var(--muted);margin:0 0 16px;padding-bottom:10px;border-bottom:1px solid var(--line)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:22px 24px;margin:0 0 18px}
.card h3{font:800 22px/1.2 var(--fh);margin:0 0 14px;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.sub{border-top:1px dashed var(--line);margin-top:20px;padding-top:18px}
.sub h4{font:800 17px/1.2 var(--fh);margin:0 0 12px;display:flex;flex-wrap:wrap;align-items:center;gap:10px}
.timing{font:600 12px var(--fb);color:var(--muted);background:var(--bg);border:1px solid var(--line);border-radius:999px;padding:3px 10px}
.meter{font:700 12px var(--fb);border-radius:999px;padding:3px 10px;margin-left:auto}
.meter.ok{background:color-mix(in srgb,#2ea043 18%,transparent);color:#2ea043}
.meter.warn{background:color-mix(in srgb,#d29922 20%,transparent);color:#d29922}
.meter.bad{background:color-mix(in srgb,#f85149 18%,transparent);color:#f85149}
.hint{color:var(--muted);font-style:italic;margin:-6px 0 12px}
.field{margin:14px 0}
.field .label{font:700 11px var(--fb);text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin-bottom:6px;display:flex;gap:10px;align-items:baseline}
.field p{margin:0 0 8px}
.count{font-weight:600;letter-spacing:0;text-transform:none;opacity:.8}
.vo{border-left:4px solid var(--accent);padding-left:16px}
.vo p{font-size:clamp(18px,2.1vw,21px);line-height:1.6;color:var(--vo);max-width:68ch;font-weight:500}
.ost p{display:inline;font:900 15px/1.9 var(--fh);text-transform:uppercase;letter-spacing:.02em;background:var(--accent);color:#111;padding:3px 10px;border-radius:6px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.shots,.notes{font-size:14.5px}
.shots .label::before{content:"▶";color:var(--accent2)}
.notes{background:color-mix(in srgb,var(--accent2) 9%,transparent);border-radius:10px;padding:10px 14px}
.notes .label{color:var(--fg)}
.kvline{margin:6px 0}
mark.check{background:#f85149;color:#fff;font:700 11px var(--fb);padding:2px 6px;border-radius:4px}
.part-hook-options ol{padding-left:0;list-style:none;counter-reset:h;display:grid;gap:10px}
.part-hook-options ol>li{counter-increment:h;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px 14px 54px;position:relative;font-size:17px}
.part-hook-options ol>li::before{content:counter(h);position:absolute;left:14px;top:12px;width:28px;height:28px;border-radius:50%;background:var(--accent);color:#111;font:900 15px/28px var(--fh);text-align:center}
.table-wrap{overflow-x:auto;margin:10px 0;border:1px solid var(--line);border-radius:12px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
tr:last-child td{border-bottom:0}
th{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:var(--muted);background:var(--bg)}
td.c-hear{font-size:16px;color:var(--vo);min-width:30ch}
td.c-see{color:var(--muted)}
input[type=checkbox]{accent-color:var(--accent);width:16px;height:16px;vertical-align:-3px}
ul,ol{padding-left:22px}
li{margin:3px 0}
section.part>ul{list-style:none;padding:0}
section.part>ul>li{padding:6px 0;border-bottom:1px solid var(--line)}
main{min-width:0;overflow-wrap:anywhere}
@media (max-width:860px){.layout{grid-template-columns:minmax(0,1fr);padding:24px 16px 80px;gap:0}nav{display:none}.card{padding:18px 16px}.meter{margin-left:0}}
@media print{:root{--bg:#fff;--panel:#fff;--fg:#000;--vo:#000;--muted:#555;--line:#ccc}nav{display:none}.layout{display:block;padding:0}.card{break-inside:avoid}}
</style></head>
<body><div class="layout">
<nav><ul>__TOC__</ul></nav>
<main><header><h1>__TITLE__</h1>__PRE____STATS__</header>__BODY__</main>
</div></body></html>
"""


def main():
    cfg = load()
    sv = cfg.get("script_view", {})
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script", type=Path)
    p.add_argument("--theme", choices=["auto", "dark", "light"], default=sv.get("theme", "auto"))
    p.add_argument("--out", type=Path, help="output file (default: <name>_view.html next to the script)")
    p.add_argument("--no-open", action="store_true", help="don't open it in the browser")
    a = p.parse_args()
    if not a.script.exists():
        raise SystemExit(f"{a.script} not found.")
    out = a.out or a.script.with_name(f"{a.script.stem}_view.html")
    out.write_text(build(a.script.read_text(), cfg, load_styles(), a.theme))
    print(f"Wrote {out}")
    if sv.get("open", True) and not a.no_open:
        subprocess.run(["open", str(out)], check=False)


if __name__ == "__main__":
    main()
