#!/usr/bin/env python3
"""Generate video topic ideas from niches and proven title formats.

Examples:
  python3 topics/topic_generator.py                      # 10 ideas, random niches
  python3 topics/topic_generator.py --niche food -n 5    # 5 food ideas
  python3 topics/topic_generator.py --style short-form --save
  python3 topics/topic_generator.py --list               # show niches

For smarter, trend-aware ideas, run `/topics <niche>` in Claude Code.
"""
import argparse
import datetime as dt
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NICHES = json.loads((ROOT / "topics" / "niches.json").read_text())

SHORT_FORMATS = [
    "3 {t} tips nobody tells you",
    "Stop doing this with {t}",
    "I tried {t} for 7 days. Here's what happened",
    "{t} in 30 seconds",
    "The biggest mistake beginners make with {t}",
    "{t}: expectation vs reality",
    "Rating {t} from 1 to 10",
    "One {t} hack that changed everything",
    "POV: you finally figured out {t}",
    "Watch this before you start {t}",
]

LONG_FORMATS = [
    "The complete beginner's guide to {t}",
    "I spent 30 days on {t}. Honest results",
    "{t}: 10 things I wish I knew sooner",
    "Every {t} mistake I made (so you don't have to)",
    "Is {t} worth it in {year}?",
    "{t} on a budget: what actually works",
    "How I'd start {t} if I had to begin again",
    "Testing viral {t} advice",
    "{t} explained simply",
    "A full day of {t}",
]


def generate(niche, count, style, seed=None):
    rng = random.Random(seed)
    formats = SHORT_FORMATS if style == "short-form" else LONG_FORMATS
    pool = [(n, t) for n, ts in NICHES.items() if niche in (None, n) for t in ts]
    combos = [(n, t, f) for n, t in pool for f in formats]
    rng.shuffle(combos)
    year = dt.date.today().year
    ideas = []
    for n, t, f in combos[:count]:
        title = f.format(t=t, year=year)
        ideas.append({"niche": n, "topic": t, "title": title[0].upper() + title[1:]})
    return ideas


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--niche", choices=sorted(NICHES), help="limit ideas to one niche")
    p.add_argument("-n", "--count", type=int, default=10)
    p.add_argument("--style", default="short-form", help="short-form uses short titles; anything else uses long-form titles")
    p.add_argument("--seed", type=int, help="repeatable results")
    p.add_argument("--save", action="store_true", help="append ideas to topics/ideas.md")
    p.add_argument("--list", action="store_true", help="list niches and exit")
    a = p.parse_args()

    if a.list:
        for n, ts in NICHES.items():
            print(f"{n:10} {', '.join(ts)}")
        return

    ideas = generate(a.niche, a.count, a.style, a.seed)
    for i, idea in enumerate(ideas, 1):
        print(f"{i:2}. [{idea['niche']}] {idea['title']}")

    if a.save:
        out = ROOT / "topics" / "ideas.md"
        with out.open("a") as f:
            f.write(f"\n## {dt.date.today()} ({a.style}{', ' + a.niche if a.niche else ''})\n\n")
            f.writelines(f"- [ ] [{x['niche']}] {x['title']}\n" for x in ideas)
        print(f"\nSaved to {out.relative_to(ROOT)}")
    print('\nNext: python3 tools/script_generator.py "<title>" --style ' + a.style)


if __name__ == "__main__":
    main()
