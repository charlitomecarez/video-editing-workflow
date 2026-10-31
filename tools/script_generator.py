#!/usr/bin/env python3
"""Create a video script template for a topic, timed to an editing style.

Examples:
  python3 tools/script_generator.py "3 budget meal tips nobody tells you" --style short-form
  python3 tools/script_generator.py "Kdenlive for beginners" --style tutorial --seconds 600

Writes video-scripts/<date>-<slug>.md with timed sections, a shot list,
and editing notes from styles/styles.json. Fill in the lines yourself, or
run `/script <topic>` in Claude Code to have Claude write the full script.
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STYLES = json.loads((ROOT / "styles" / "styles.json").read_text())


def ts(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def build(topic, style_key, seconds):
    s = STYLES[style_key]
    total = seconds or s["target_seconds"]
    lines = [
        f"# {topic}",
        "",
        f"- **Style:** {s['name']} (`{style_key}`)",
        f"- **Length:** ~{ts(total)} | **Format:** {s['aspect']}, {s['resolution']} @ {s['fps']} fps",
        f"- **Created:** {dt.date.today()}",
        "- **Status:** draft",
        "",
        "## Hook options",
        "",
        "1. ",
        "2. ",
        "3. ",
        "",
        "## Script",
        "",
    ]
    t = 0.0
    for section, pct, note in s["structure"]:
        dur = total * pct
        lines += [
            f"### {section} ({ts(t)}–{ts(t + dur)}, ~{round(dur)}s)",
            f"_{note}_",
            "",
            "**Voiceover / dialogue:**",
            "",
            "**On-screen text:**",
            "",
            "**Shots / B-roll:**",
            "",
        ]
        t += dur
    shots = max(1, round(total / s["avg_shot_seconds"]))
    lines += [
        "## Shot list",
        "",
        "| # | Shot | Type (A-roll / B-roll / screen) | Done |",
        "|---|------|------|------|",
        "| 1 | | | [ ] |",
        "",
        "## Editing notes (from style)",
        "",
        f"- **Pacing:** ~{s['avg_shot_seconds']}s per shot (about {shots} cuts total)",
        f"- **Captions:** {s['captions']}",
        f"- **Music:** {s['music']}",
        f"- **Transitions:** {s['transitions']}",
        f"- **Color:** {s['color']}",
        "",
        "## Kdenlive checklist",
        "",
        f"- [ ] Project profile set to {s['resolution']} @ {s['fps']} fps",
        "- [ ] Footage prepped (`tools/prep.sh`) and proxies on",
        "- [ ] Silences cut (`tools/cut-silence.sh`) and reviewed",
        "- [ ] B-roll, text, music added",
        "- [ ] Subtitles generated (`tools/subtitles.sh`) and checked",
        "- [ ] Audio levels: voice around -6 dB peak, music under it",
        "- [ ] Rendered and watched once fully before posting",
        "",
        "## Post",
        "",
        "- **Title:**",
        "- **Description:**",
        "- **Hashtags / tags:**",
        "- **Thumbnail idea:**",
        "",
    ]
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("topic")
    p.add_argument("--style", default="short-form", choices=sorted(STYLES))
    p.add_argument("--seconds", type=int, help="override the style's target length")
    p.add_argument("--stdout", action="store_true", help="print instead of saving")
    a = p.parse_args()

    md = build(a.topic, a.style, a.seconds)
    if a.stdout:
        print(md)
        return
    out = ROOT / "video-scripts" / f"{dt.date.today()}-{slugify(a.topic)}.md"
    if out.exists():
        raise SystemExit(f"{out.relative_to(ROOT)} already exists. Delete it or change the topic.")
    out.write_text(md)
    print(f"Created {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
