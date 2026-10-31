#!/usr/bin/env python3
"""Generate video topic ideas from niches and title formats.

Examples:
  python3 topics/topic_generator.py                       # uses [topics] + [creator].niches from config
  python3 topics/topic_generator.py --niche food -n 5     # 5 food ideas
  python3 topics/topic_generator.py --niche food --niche tech --style talking-head --save
  python3 topics/topic_generator.py --topic "air fryer"   # ideas for any topic, even one not in niches.json
  python3 topics/topic_generator.py --list                # show niches

Edit topics/niches.json (niches and sub-topics) and topics/formats.json (title formats)
to change what it produces. For smarter, trend-aware ideas, run `/topics <niche>` in Claude Code.
"""
import argparse
import datetime as dt
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from vwconfig import ROOT, load, load_styles  # noqa: E402

NICHES = json.loads((ROOT / "topics" / "niches.json").read_text())
FORMATS = json.loads((ROOT / "topics" / "formats.json").read_text())


def is_short(style):
    return "9:16" in style.get("aspect", "")


def generate(topics, count, short, rng):
    formats = FORMATS["short" if short else "long"]
    combos = [(n, t, f) for n, t in topics for f in formats]
    rng.shuffle(combos)
    year = dt.date.today().year
    ideas, seen = [], set()
    for n, t, f in combos:
        title = f.format(t=t, year=year)
        title = title[0].upper() + title[1:]
        if title not in seen:
            seen.add(title)
            ideas.append({"niche": n, "topic": t, "title": title})
        if len(ideas) >= count:
            break
    return ideas


def main():
    cfg = load()
    styles = load_styles()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--niche", action="append", choices=sorted(NICHES), help="repeat for several niches")
    p.add_argument("--topic", action="append", help="use your own topic(s) instead of niches.json")
    p.add_argument("-n", "--count", type=int, default=cfg["topics"]["count"])
    p.add_argument("--style", default=cfg["topics"]["style"], choices=sorted(styles))
    p.add_argument("--seed", type=int, help="repeatable results")
    p.add_argument("--save", action="store_true", help=f"append ideas to {cfg['paths']['ideas']}")
    p.add_argument("--list", action="store_true", help="list niches and exit")
    a = p.parse_args()

    if a.list:
        for n, ts in NICHES.items():
            print(f"{n:10} {', '.join(ts)}")
        return

    if a.topic:
        pool = [("custom", t) for t in a.topic]
    else:
        niches = a.niche or cfg["creator"]["niches"] or list(NICHES)
        bad = [n for n in niches if n not in NICHES]
        if bad:
            raise SystemExit(f"Unknown niche(s) in config: {bad}. Options: {', '.join(NICHES)}")
        pool = [(n, t) for n in niches for t in NICHES[n]]

    ideas = generate(pool, a.count, is_short(styles[a.style]), random.Random(a.seed))
    for i, idea in enumerate(ideas, 1):
        print(f"{i:2}. [{idea['niche']}] {idea['title']}")

    if a.save:
        out = ROOT / cfg["paths"]["ideas"]
        out.parent.mkdir(parents=True, exist_ok=True)
        new = not out.exists()
        with out.open("a") as f:
            if new:
                f.write("# Topic ideas\n\nTick an idea off when you make it.\n")
            f.write(f"\n## {dt.date.today()} ({a.style})\n\n")
            f.writelines(f"- [ ] [{x['niche']}] {x['title']} ({a.style})\n" for x in ideas)
        print(f"\nSaved to {out.relative_to(ROOT)}")
    print(f'\nNext: python3 tools/script_generator.py "<title>" --style {a.style}')


if __name__ == "__main__":
    main()
