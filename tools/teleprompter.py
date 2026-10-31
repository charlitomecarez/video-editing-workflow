#!/usr/bin/env python3
"""Open a script in a teleprompter in your browser, for reading while you record.

Examples:
  python3 tools/teleprompter.py projects/x/script.md
  python3 tools/teleprompter.py notes.txt --speed 50 --size 64 --mirror

Controls: Space = start/pause · ↑/↓ = speed · +/- = text size · M = mirror (for glass
teleprompters) · R = back to top · F = fullscreen · ←/→ = previous/next section
Defaults come from [teleprompter] in config.toml. Writes <name>_teleprompter.html next to the input.
"""
import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_text import extract  # noqa: E402
from vwconfig import load  # noqa: E402

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>Teleprompter</title>
<style>
:root{--size:__SIZE__px}
*{margin:0;box-sizing:border-box}
html,body{background:#000;color:#fff;font-family:-apple-system,Helvetica,Arial,sans-serif}
#text{max-width:__WIDTH__ch;margin:0 auto;padding:50vh 6vw;font-size:var(--size);line-height:1.45;font-weight:600}
#text.mirror{transform:scaleX(-1)}
h2{font-size:.45em;color:#ffd400;text-transform:uppercase;letter-spacing:.1em;margin:1.4em 0 .4em}
p{margin:0 0 .5em}
#guide{position:fixed;left:0;right:0;top:__GUIDE__%;height:calc(var(--size)*1.5);border-top:2px solid rgba(255,212,0,.5);
  border-bottom:2px solid rgba(255,212,0,.5);background:rgba(255,212,0,.06);pointer-events:none}
#hud{position:fixed;bottom:12px;right:16px;font:14px monospace;color:#888;background:rgba(0,0,0,.7);padding:6px 10px;border-radius:6px}
</style></head><body><div id="guide"></div><div id="text">__BODY__</div>
<div id="hud"></div>
<script>
let speed=__SPEED__, running=false, last=null, pos=0;
const t=document.getElementById('text'), hud=document.getElementById('hud');
if(__MIRROR__) t.classList.add('mirror');
function show(){hud.textContent=(running?'▶':'❚❚')+' speed '+speed+' px/s · size '+parseInt(getComputedStyle(document.documentElement).getPropertyValue('--size'))+'px · Space M R F ↑↓ +- ←→'}
function frame(ts){if(running){if(last!==null){pos+=speed*(ts-last)/1000;window.scrollTo(0,pos)}last=ts;requestAnimationFrame(frame)}else last=null}
document.addEventListener('keydown',e=>{
  const r=document.documentElement, size=parseInt(getComputedStyle(r).getPropertyValue('--size'));
  if(e.code==='Space'){e.preventDefault();running=!running;pos=window.scrollY;if(running)requestAnimationFrame(frame)}
  else if(e.key==='ArrowUp'){e.preventDefault();speed+=5}
  else if(e.key==='ArrowDown'){e.preventDefault();speed=Math.max(5,speed-5)}
  else if(e.key==='+'||e.key==='='){r.style.setProperty('--size',(size+4)+'px')}
  else if(e.key==='-'){r.style.setProperty('--size',Math.max(16,size-4)+'px')}
  else if(e.key==='m'||e.key==='M'){t.classList.toggle('mirror')}
  else if(e.key==='r'||e.key==='R'){pos=0;window.scrollTo(0,0)}
  else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():r.requestFullscreen()}
  else if(e.key==='ArrowRight'||e.key==='ArrowLeft'){
    e.preventDefault();const hs=[...document.querySelectorAll('h2')];const y=window.scrollY+innerHeight*__GUIDE__/100;
    const target=e.key==='ArrowRight'?hs.find(h=>h.offsetTop>y+5):hs.reverse().find(h=>h.offsetTop<y-5);
    if(target){pos=target.offsetTop-innerHeight*__GUIDE__/100;window.scrollTo(0,pos)}}
  show()});
show();
</script></body></html>"""


def main():
    cfg = load().get("teleprompter", {})
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script", help="script.md or a plain .txt file")
    p.add_argument("--speed", type=int, default=cfg.get("speed", 40), help="scroll speed in px/s")
    p.add_argument("--size", type=int, default=cfg.get("font_size", 56), help="text size in px")
    p.add_argument("--mirror", action="store_true", default=cfg.get("mirror", False))
    p.add_argument("--no-open", action="store_true")
    a = p.parse_args()

    src = Path(a.script)
    raw = src.read_text(encoding="utf-8")
    body = []
    if src.suffix == ".md":
        last = object()
        for b in extract(raw):
            if b["section"] != last:
                body.append(f"<h2>{html.escape(b['section'] or '')}</h2>")
                last = b["section"]
            body.append(f"<p>{html.escape(b['text'])}</p>")
        if not body:
            raise SystemExit("No narration found in the script. Fill in the Hear column / Voiceover lines first.")
    else:
        body = [f"<p>{html.escape(par.strip())}</p>" for par in raw.split("\n") if par.strip()]

    page = (PAGE.replace("__BODY__", "\n".join(body)).replace("__SIZE__", str(a.size))
            .replace("__SPEED__", json.dumps(a.speed)).replace("__MIRROR__", json.dumps(a.mirror))
            .replace("__WIDTH__", str(cfg.get("line_width", 32))).replace("__GUIDE__", str(cfg.get("guide_position", 30))))
    out = src.with_name(src.stem + "_teleprompter.html")
    out.write_text(page, encoding="utf-8")
    print(f"Teleprompter: {out}")
    if not a.no_open:
        subprocess.run(["open", str(out)], check=False)


if __name__ == "__main__":
    main()
