#!/usr/bin/env python3
"""Create a video script template for a topic, timed to an editing style.

Examples:
  python3 tools/script_generator.py "3 budget meal tips nobody tells you"
  python3 tools/script_generator.py "Kdenlive for beginners" --style tutorial --seconds 600
  python3 tools/script_generator.py "My title" --project projects/2026-11-01-my-title

Writes <paths.scripts>/<date>-<slug>.md (or script.md inside --project). Sections, speaking
rate, hook count and checklist come from [script] in config.toml; timing and editing notes
come from the style. Run `/script <topic>` in Claude Code to have Claude write the lines.
"""
import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load, load_styles  # noqa: E402


def ts(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def script_format(s, sc, override=None):
    fmt = override or sc.get("format", "auto")
    if fmt == "auto":
        fmt = s.get("script_format", "sections")
    if fmt not in ("sections", "av-table"):
        raise SystemExit(f"Unknown script format '{fmt}' (use sections or av-table)")
    return fmt


def build(topic, style_key, s, total, cfg, fmt_override=None):
    sc, cr = cfg["script"], cfg["creator"]
    inc = set(sc["include"])
    wps = s.get("words_per_second", sc["words_per_second"])
    fmt = script_format(s, sc, fmt_override)
    out = [
        f"# {topic}",
        "",
        f"- **Style:** {s['name']} (`{style_key}`)",
        f"- **Length:** ~{ts(total)} (~{round(total * wps)} spoken words) | "
        f"**Format:** {s['aspect']}, {s['resolution']} @ {s['fps']} fps",
        f"- **Audience:** {cr['audience']} | **Tone:** {cr['tone']} | **Language:** {cr['language']}",
        f"- **Personality:** `{cfg.get('personality', {}).get('profile', '-')}` | **Humor level:** "
        f"{s.get('humor_level', cfg.get('personality', {}).get('humor_level', '-'))}/5",
        f"- **Created:** {dt.date.today()}",
        "- **Status:** draft  <!-- draft / filming / editing / posted -->",
        "",
    ]
    if "hooks" in inc:
        out += ["## Hook options", ""] + [f"{i}. " for i in range(1, sc["hook_options"] + 1)] + [""]
    if "script" in inc:
        out += ["## Script", ""]
        if fmt == "av-table":
            out += [
                "_One row per beat. **#** = row number (name your files `05-...` to put them on row 5), "
                "**See** = what's on screen (graphic, code, meme, clip), "
                "**Hear** = the voiceover line, **Notes** = asset source/link, SFX, timing._",
                "",
            ]
        t, row_n = 0.0, 0
        for section, pct, note in s["structure"]:
            dur = total * pct
            out += [
                f"### {section} ({ts(t)}–{ts(t + dur)}, ~{round(dur)}s, ~{round(dur * wps)} words)",
                f"_{note}_",
                "",
            ]
            if fmt == "av-table":
                # One row per visual, capped so long sections stay readable
                rows = max(2, min(20, round(dur / s["avg_shot_seconds"])))
                out += ["| # | See (on screen) | Hear (voiceover) | Notes |", "|---|---|---|---|"]
                out += [f"| {row_n + i + 1:02} | | | |" for i in range(rows)] + [""]
                row_n += rows
            else:
                out += [
                    "**Voiceover / dialogue:**",
                    "",
                    "**On-screen text:**",
                    "",
                    "**Shots / B-roll:**",
                    "",
                ]
            t += dur
    if "shot_list" in inc:
        out += [
            "## Shot list",
            "",
            "| # | Shot | Type (A-roll / B-roll / screen) | Done |",
            "|---|------|------|------|",
            "| 1 | | | [ ] |",
            "",
        ]
    if "editing_notes" in inc:
        cuts = max(1, round(total / s["avg_shot_seconds"]))
        out += [
            "## Editing notes (from style)",
            "",
            f"- **Pacing:** ~{s['avg_shot_seconds']}s per shot (about {cuts} cuts total)",
            f"- **Captions:** {s['captions']}",
            f"- **Music:** {s['music']}",
            f"- **Transitions:** {s['transitions']}",
            f"- **Color:** {s['color']}",
        ]
        out += [f"- **Visuals:** {s['visuals']}"] if s.get("visuals") else []
        out += [f"- **Sound effects:** {s['sound_effects']}"] if s.get("sound_effects") else []
        out += [""]
    if "checklist" in inc:
        out += ["## Edit checklist", "", f"- [ ] Kdenlive profile: {s['resolution']} @ {s['fps']} fps"]
        out += [f"- [ ] {item}" for item in sc["checklist"]] + [""]
    if "post" in inc:
        out += ["## Post", ""]
        for plat in cr["platforms"]:
            out += [f"### {plat}", "- **Title / caption:**", "- **Hashtags / tags:**", ""]
        out += ["- **Thumbnail / cover idea:**", ""]
    if "results" in inc:
        out += [
            "## Results (fill in ~7 days after posting)",
            "",
            "| Platform | Views | Avg watch % | Likes | Comments | Shares | Notes |",
            "|---|---|---|---|---|---|---|",
        ] + [f"| {p} | | | | | | |" for p in cr["platforms"]] + [""]
    return "\n".join(out)


def main():
    cfg = load()
    styles = load_styles()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("topic")
    p.add_argument("--style", default=cfg["script"]["default_style"], choices=sorted(styles))
    p.add_argument("--seconds", type=int, help="override the style's target length")
    p.add_argument("--format", choices=["sections", "av-table"],
                   help="script layout (default: [script].format, or the style's script_format)")
    p.add_argument("--project", help="save as script.md inside this project folder")
    p.add_argument("--stdout", action="store_true", help="print instead of saving")
    p.add_argument("--force", action="store_true", help="overwrite an existing file")
    a = p.parse_args()

    s = styles[a.style]
    md = build(a.topic, a.style, s, a.seconds or s["target_seconds"], cfg, a.format)
    if a.stdout:
        print(md)
        return
    if a.project:
        out = Path(a.project).resolve() / "script.md"
    else:
        out = ROOT / cfg["paths"]["scripts"] / f"{dt.date.today()}-{slugify(a.topic)}.md"
    if out.exists() and not a.force:
        raise SystemExit(f"{out} already exists. Use --force to overwrite.")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md)
    print(f"Created {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    main()
