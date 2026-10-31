#!/usr/bin/env python3
"""Pull the spoken narration out of a script.md (both script formats).

  av-table  -> the "Hear" column of every table row
  sections  -> the lines under **Voiceover / dialogue:**

Examples:
  python3 tools/script_text.py projects/x/script.md               # plain text, one line per beat
  python3 tools/script_text.py projects/x/script.md --sections    # with "## Section" headings
  python3 tools/script_text.py projects/x/script.md --json        # [{row, section, text, see}] for other tools
  python3 tools/script_text.py projects/x/script.md --stats       # word count vs target per section

Used by tools/voice-draft.sh and tools/teleprompter.py.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import load, load_styles  # noqa: E402

HEAD = re.compile(r"^###\s+(.+?)(?:\s+\((\d+:\d+)–(\d+:\d+),\s*~(\d+)s,\s*~(\d+)\s*words\))?\s*$")


def split_row(line):
    cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
    return cells


def extract(md):
    """Beats in order: {row, section, target, text, see}.

    row = the script row number: the "#" column when the table has one, otherwise
    the running count of table rows (or of voiceover lines in the sections format).
    """
    beats, section, target, in_script, in_vo = [], None, None, False, False
    cols, n = None, 0
    for line in md.splitlines():
        if line.startswith("## "):
            in_script = line.strip() == "## Script"
            in_vo = False
            continue
        if not in_script:
            continue
        m = HEAD.match(line)
        if m:
            section, target, in_vo, cols = m.group(1).strip(), (int(m.group(5)) if m.group(5) else None), False, None
            continue
        s = line.strip()
        if s.startswith("|"):
            cells = split_row(s)
            if cols is None:
                low = [c.lower() for c in cells]
                cols = {
                    "hear": next((i for i, c in enumerate(low) if c.startswith("hear")), None),
                    "see": next((i for i, c in enumerate(low) if c.startswith("see")), None),
                    "num": next((i for i, c in enumerate(low) if c in ("#", "no", "no.", "row")), None),
                }
                continue
            if set(s) <= set("|-: "):
                continue
            n += 1
            cell = lambda k: cells[cols[k]] if cols[k] is not None and cols[k] < len(cells) else ""  # noqa: E731
            num = cell("num")
            row = int(num) if num.isdigit() else n
            if cell("hear"):
                beats.append({"row": row, "section": section, "target": target,
                              "text": cell("hear").strip('"“” '), "see": cell("see")})
            continue
        if s.startswith("**"):
            in_vo = s.lower().startswith("**voiceover")
            rest = re.sub(r"^\*\*[^*]+\*\*\s*", "", s)
            if in_vo and rest:
                n += 1
                beats.append({"row": n, "section": section, "target": target, "text": rest, "see": ""})
            continue
        if in_vo and s and not s.startswith("_"):
            n += 1
            beats.append({"row": n, "section": section, "target": target,
                          "text": s.lstrip("-* ").strip('"“” '), "see": ""})
    return beats


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("script")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--sections", action="store_true", help="include section headings")
    g.add_argument("--json", action="store_true")
    g.add_argument("--stats", action="store_true", help="word counts vs target")
    a = p.parse_args()

    beats = extract(Path(a.script).read_text(encoding="utf-8"))
    if not beats:
        raise SystemExit("No narration found. Fill in the Hear column / Voiceover lines first.")
    if a.json:
        print(json.dumps(beats, indent=2, ensure_ascii=False))
    elif a.stats:
        cfg, styles = load(), load_styles()
        md = Path(a.script).read_text(encoding="utf-8")
        sm = re.search(r"\(`([\w-]+)`\)", md)
        wps = styles.get(sm.group(1), {}).get("words_per_second", cfg["script"]["words_per_second"]) if sm else cfg["script"]["words_per_second"]
        total, order = 0, []
        per = {}
        for b in beats:
            if b["section"] not in per:
                order.append(b["section"])
                per[b["section"]] = [0, b["target"]]
            per[b["section"]][0] += len(b["text"].split())
        print(f"{'Section':28} {'Words':>6} {'Target':>7}  Status")
        for sec in order:
            n, t = per[sec]
            total += n
            status = "" if not t else ("ok" if abs(n - t) <= t * 0.1 else ("too long" if n > t else "too short"))
            print(f"{(sec or '-')[:28]:28} {n:6} {t or '':>7}  {status}")
        print(f"\nTotal {total} words ≈ {total / wps:.0f}s at {wps} words/s")
    else:
        last = object()
        for b in beats:
            if a.sections and b["section"] != last:
                print(f"\n## {b['section']}\n")
                last = b["section"]
            print(b["text"])


if __name__ == "__main__":
    main()
