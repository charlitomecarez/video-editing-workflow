#!/usr/bin/env python3
"""Analyze the editing of a reference video: where every cut is, how long shots
last, and how the pace changes over the video. A free "scene cut detection".

Examples:
  python3 tools/analyze_cuts.py references/explainer.mp4
  python3 tools/analyze_cuts.py references/explainer.mp4 --frames          # + one frame per shot
  python3 tools/analyze_cuts.py references/explainer.mp4 --srt references/explainer.srt
                                   # + speaking rate (make the .srt with tools/subtitles.sh)

Output folder <name>_cuts/ next to the video (or --out DIR):
  report.md    stats, pace over time, shot-length histogram, suggested style values
  cuts.csv     every shot: number, start, end, length
  markers.srt  every shot as a subtitle. Import it in Kdenlive (Project → Subtitles)
               over the reference video to step through the cuts one by one
  frames/      one frame per shot (with --frames), to see what each shot shows

Defaults come from [analyze] in config.toml. Use it only on videos you're allowed
to have, for private study. Don't reupload other creators' work.
"""
import argparse
import csv
import json
import re
import statistics
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import load  # noqa: E402


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def detect_cuts(video, threshold):
    # Downscale for speed; scene scores barely change at low resolution.
    cmd = ["ffmpeg", "-hide_banner", "-nostats", "-i", str(video), "-an",
           "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(proc.stderr[-2000:])
    return [float(m) for m in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]


def shots_from_cuts(cuts, total, min_shot):
    bounds = [0.0]
    for c in sorted(cuts):
        if c - bounds[-1] >= min_shot and total - c >= min_shot:
            bounds.append(c)
    bounds.append(total)
    return [(bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]


def srt_time(t):
    ms = round(t * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def speaking_rate(srt_path):
    text = Path(srt_path).read_text(encoding="utf-8", errors="ignore")
    blocks = [b for b in re.split(r"\n\s*\n", text.strip()) if "-->" in b]
    words, spoken = 0, 0.0
    for b in blocks:
        lines = b.strip().splitlines()
        tline = next(i for i, ln in enumerate(lines) if "-->" in ln)
        a, z = [x.strip().replace(",", ".") for x in lines[tline].split("-->")]
        to_s = lambda x: sum(float(p) * 60 ** i for i, p in enumerate(reversed(x.split(":"))))  # noqa: E731
        spoken += max(0.0, to_s(z) - to_s(a))
        words += len(" ".join(lines[tline + 1:]).split())
    return words, spoken


def bar(n, scale):
    return "█" * max(1 if n else 0, round(n * scale))


def main():
    cfg = load().get("analyze", {})
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("video")
    p.add_argument("--threshold", type=float, default=cfg.get("threshold", 0.3),
                   help="scene-change sensitivity 0-1 (lower = more cuts)")
    p.add_argument("--min-shot", type=float, default=cfg.get("min_shot", 0.15),
                   help="merge cuts closer than this many seconds")
    p.add_argument("--frames", action="store_true", default=cfg.get("save_frames", False),
                   help="save one frame per shot")
    p.add_argument("--srt", help="transcript .srt of the video, to measure speaking rate")
    p.add_argument("--out", help="output folder (default: <name>_cuts/ next to the video)")
    a = p.parse_args()

    video = Path(a.video)
    if not video.exists():
        raise SystemExit(f"File not found: {video}")
    out = Path(a.out) if a.out else video.with_name(video.stem + "_cuts")
    out.mkdir(parents=True, exist_ok=True)

    total = duration(video)
    print(f"Detecting cuts in {video.name} ({mmss(total)}, threshold {a.threshold})...", flush=True)
    shots = shots_from_cuts(detect_cuts(video, a.threshold), total, a.min_shot)
    lengths = [e - s for s, e in shots]
    n = len(shots)

    with (out / "cuts.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["shot", "start", "end", "length"])
        for i, (s, e) in enumerate(shots, 1):
            w.writerow([i, f"{s:.3f}", f"{e:.3f}", f"{e - s:.3f}"])

    (out / "markers.srt").write_text("".join(
        f"{i}\n{srt_time(s)} --> {srt_time(e)}\nShot {i} ({e - s:.1f}s)\n\n"
        for i, (s, e) in enumerate(shots, 1)))

    if a.frames:
        (out / "frames").mkdir(exist_ok=True)
        print(f"Saving {n} frames...", flush=True)
        for i, (s, e) in enumerate(shots, 1):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{(s + e) / 2:.3f}", "-i", str(video),
                            "-frames:v", "1", "-vf", "scale=480:-2", "-q:v", "4",
                            str(out / "frames" / f"shot_{i:03}_{mmss(s).replace(':', 'm')}s.jpg")], check=False)

    avg = statistics.mean(lengths)
    med = statistics.median(lengths)
    r = [
        f"# Cut analysis: {video.name}",
        "",
        f"- **Duration:** {mmss(total)} ({total:.1f}s)",
        f"- **Shots:** {n} ({n - 1} cuts) → **{(n - 1) / total * 60:.0f} cuts per minute**",
        f"- **Shot length:** average **{avg:.2f}s**, median {med:.2f}s, "
        f"shortest {min(lengths):.2f}s, longest {max(lengths):.2f}s",
        f"- Settings: threshold {a.threshold}, min shot {a.min_shot}s",
        "",
        "> Scene detection catches hard cuts and big visual changes. Text or graphics popping onto "
        "an unchanged background may not count as a cut, so a graphics-heavy video can feel faster "
        "than these numbers. Try `--threshold 0.2` to catch more.",
        "",
    ]

    if a.srt:
        words, spoken = speaking_rate(a.srt)
        if words:
            r += [
                "## Speaking rate",
                "",
                f"- **{words} words** in {spoken:.0f}s of speech → **{words / spoken:.2f} words/second** "
                f"({words / spoken * 60:.0f} wpm)",
                f"- Over the full video: {words / total:.2f} words/second",
                f"- About {words / max(n, 1):.1f} words per shot",
                "",
            ]

    r += ["## Pace over the video", "", "| Part | Time | Cuts | Avg shot |", "|---|---|---|---|"]
    parts = 10
    for k in range(parts):
        lo, hi = total * k / parts, total * (k + 1) / parts
        inside = [e - s for s, e in shots if lo <= (s + e) / 2 < hi]
        cuts_in = sum(1 for s, _ in shots[1:] if lo <= s < hi)
        r.append(f"| {k * 10}-{(k + 1) * 10}% | {mmss(lo)}–{mmss(hi)} | {cuts_in} {bar(cuts_in, 0.5)} | "
                 f"{statistics.mean(inside):.2f}s |" if inside else
                 f"| {k * 10}-{(k + 1) * 10}% | {mmss(lo)}–{mmss(hi)} | {cuts_in} | (one long shot) |")
    r.append("")

    buckets = [(0, 0.5), (0.5, 1), (1, 2), (2, 4), (4, 8), (8, 1e9)]
    counts = [sum(1 for x in lengths if lo <= x < hi) for lo, hi in buckets]
    scale = 30 / max(counts) if max(counts) else 1
    r += ["## Shot lengths", "", "```"]
    for (lo, hi), c in zip(buckets, counts):
        label = f"{lo:g}-{hi:g}s" if hi < 1e9 else f"{lo:g}s+"
        r.append(f"{label:>8} {c:4} {bar(c, scale)}")
    r += ["```", "", "## Longest holds (where the edit slows down)", ""]
    for s, e in sorted(shots, key=lambda x: x[1] - x[0], reverse=True)[:5]:
        r.append(f"- {mmss(s)}–{mmss(e)} ({e - s:.1f}s)")

    suggestion = {"target_seconds": round(total), "avg_shot_seconds": round(med, 1)}
    if a.srt and words:
        suggestion["words_per_second"] = round(words / spoken, 2)
    r += [
        "",
        "## Suggested style values",
        "",
        "Put these in a custom style (`styles/custom/*.json`) to match this pacing:",
        "",
        "```json",
        json.dumps({"my-style": {"extends": "tech-explainer", **suggestion}}, indent=2),
        "```",
        "",
        "## How to study it",
        "",
        "1. In Kdenlive, add the reference video to the timeline and import `markers.srt` "
        "(Project → Subtitles → Import Subtitle File).",
        "2. Step through shot by shot (use the subtitle track to jump between shots).",
        "3. For each shot, ask: **what's on screen, what's being said, and why does the cut land here?**",
        "4. Write a few rows of a See | Hear | Notes table to reverse-engineer the script.",
        "",
    ]
    (out / "report.md").write_text("\n".join(r))
    print(f"{n} shots, avg {avg:.2f}s, median {med:.2f}s, {(n - 1) / total * 60:.0f} cuts/min")
    print(f"Report: {out / 'report.md'}")


if __name__ == "__main__":
    main()
