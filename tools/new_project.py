#!/usr/bin/env python3
"""Start a new video project folder (and optionally its script).

Examples:
  python3 tools/new_project.py "Budget meals"
  python3 tools/new_project.py "Budget meals" --style short-form --script

Creates <paths.projects>/<date>-<slug>/ with the subfolders from [project].folders
in config.toml, plus a notes.md. --script also creates script.md inside it.
"""
import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load, load_styles  # noqa: E402
from script_generator import slugify  # noqa: E402


def main():
    cfg = load()
    styles = load_styles()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("title")
    p.add_argument("--style", default=cfg["script"]["default_style"], choices=sorted(styles))
    p.add_argument("--script", action="store_true", help="also create script.md")
    a = p.parse_args()

    name = slugify(a.title)
    if cfg["project"]["date_prefix"]:
        name = f"{dt.date.today()}-{name}"
    proj = ROOT / cfg["paths"]["projects"] / name
    if proj.exists():
        raise SystemExit(f"{proj.relative_to(ROOT)} already exists.")
    for folder in cfg["project"]["folders"]:
        (proj / folder).mkdir(parents=True)
    s = styles[a.style]
    (proj / "notes.md").write_text(
        f"# {a.title}\n\n"
        f"- **Style:** `{a.style}`. Set the Kdenlive profile to {s['resolution']} @ {s['fps']} fps\n"
        f"- **Kdenlive project:** save it as `{name}.kdenlive` in this folder\n\n"
        "## Notes\n\n"
    )
    print(f"Created {proj.relative_to(ROOT)}/ with: {', '.join(cfg['project']['folders'])}", flush=True)
    if a.script:
        subprocess.run([sys.executable, str(ROOT / "tools" / "script_generator.py"), a.title,
                        "--style", a.style, "--project", str(proj)], check=True)
    print(f"Put raw clips in {proj.relative_to(ROOT)}/footage/")


if __name__ == "__main__":
    main()
