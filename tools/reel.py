#!/usr/bin/env python3
"""Cut a long-form video down to a ~60 s vertical summary reel, using only
clips from the video itself (no new recording).

Steps:
  1. python3 tools/reel.py transcript projects/x/export/final.mp4
       Timestamped transcript (runs Whisper first if there's no .srt yet).
  2. Pick the lines that summarize the video and save them as projects/x/reel/reel.json
       (Claude does this with /reel. See the example below.)
  3. python3 tools/reel.py build projects/x/reel/reel.json
       → reel/reel.mp4 (9:16, loudness-leveled, hook text), reel/reel.srt, and
         reel/reel_captioned.mp4 if captions can be burned in.

reel.json:
  {
    "source": "../export/final.mp4",          # relative to reel.json
    "mode": "blur",                            # blur (fit whole frame) or crop (fill), optional
    "hook_text": "TypeScript in *60 seconds*", # on-screen text for the first seconds, optional
    "segments": [
      {"start": 12.4, "end": 19.1, "note": "hook"},
      {"start": 63.0, "end": 78.2, "note": "point 1"}
    ]
  }

Defaults come from [reel] in config.toml.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load  # noqa: E402

TOOLS = ROOT / "tools"


def srt_to_s(t):
    h, m, rest = t.strip().replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(rest)


def s_to_srt(t):
    ms = max(0, round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def read_srt(path):
    cues = []
    for block in re.split(r"\n\s*\n", Path(path).read_text(encoding="utf-8", errors="ignore").strip()):
        lines = block.strip().splitlines()
        i = next((k for k, ln in enumerate(lines) if "-->" in ln), None)
        if i is None:
            continue
        a, b = lines[i].split("-->")
        text = " ".join(lines[i + 1:]).strip()
        if text:
            cues.append((srt_to_s(a), srt_to_s(b), text))
    return cues


def duration(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                         capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def has_audio(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    return bool(out.stdout.strip())


def fps(video):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate",
                          "-of", "csv=p=0", str(video)], capture_output=True, text=True, check=True)
    n, d = out.stdout.strip().split("/")
    return float(n) / float(d)


def cmd_transcript(a, cfg):
    video = Path(a.video)
    srt = Path(a.srt) if a.srt else video.with_suffix(".srt")
    if not srt.exists():
        print(f"No transcript yet. Running Whisper on {video.name} (first run downloads the model)...", file=sys.stderr)
        args = [str(TOOLS / "subtitles.sh"), str(video)]
        if cfg["reel"].get("language"):
            args += ["--language", cfg["reel"]["language"]]
        subprocess.run(args, check=True, stdout=sys.stderr)
    cues = read_srt(srt)
    if a.json:
        print(json.dumps([{"start": s, "end": e, "text": t} for s, e, t in cues], indent=1, ensure_ascii=False))
        return
    print(f"# Transcript of {video.name} ({mmss(duration(video))}), {len(cues)} lines")
    print("# Format: [start → end] seconds | text. Use these numbers in reel.json segments.\n")
    for s, e, t in cues:
        print(f"[{s:7.2f} → {e:7.2f}] {t}")


def retime_captions(cues, segments, pad):
    out, offset = [], 0.0
    for seg in segments:
        s, e = seg["start"], seg["end"]
        for cs, ce, text in cues:
            if ce <= s or cs >= e:
                continue
            ns, ne = max(cs, s) - s + offset, min(ce, e) - s + offset
            if ne - ns >= 0.25:
                out.append((ns, ne, text))
        offset += e - s
    return "".join(f"{i}\n{s_to_srt(s)} --> {s_to_srt(e)}\n{t}\n\n" for i, (s, e, t) in enumerate(out, 1))


def cmd_build(a, cfg):
    rc, rend = cfg["reel"], cfg["render"]
    plan_path = Path(a.plan).resolve()
    plan = json.loads(plan_path.read_text())
    base = plan_path.parent
    src = (base / plan["source"]).resolve()
    if not src.exists():
        raise SystemExit(f"Source video not found: {src}")
    segs = sorted(plan["segments"], key=lambda x: x["start"]) if plan.get("sort", False) else plan["segments"]
    total_src = duration(src)
    pad = float(rc.get("pad", 0.08))
    clean = []
    for i, sg in enumerate(segs, 1):
        s, e = float(sg["start"]) - pad, float(sg["end"]) + pad
        s, e = max(0.0, s), min(total_src, e)
        if e - s < 0.3:
            raise SystemExit(f"Segment {i} is too short or outside the video: {sg}")
        clean.append({"start": s, "end": e, "note": sg.get("note", "")})
    total = sum(x["end"] - x["start"] for x in clean)
    max_s = float(plan.get("max_seconds", rc.get("max_seconds", 60)))
    print(f"{len(clean)} segments, total {total:.1f}s (limit {max_s:.0f}s)")
    for i, x in enumerate(clean, 1):
        print(f"  {i:2}. {mmss(x['start'])}–{mmss(x['end'])}  {x['end'] - x['start']:5.1f}s  {x['note']}")
    if total > max_s + 0.5 and not a.allow_long:
        raise SystemExit(f"Reel is {total:.1f}s, over the {max_s:.0f}s limit. Trim segments (or pass --allow-long).")

    out_dir = Path(a.out_dir).resolve() if a.out_dir else base
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "reel.mp4"
    W, H = int(rc.get("width", 1080)), int(rc.get("height", 1920))
    mode = plan.get("mode", rc.get("mode", "blur"))
    audio = has_audio(src)

    # Hook text overlay, rendered with the graphics engine (no freetype needed in ffmpeg)
    hook_png = None
    hook_text = plan.get("hook_text", "")
    hook_secs = float(plan.get("hook_seconds", rc.get("hook_seconds", 2.5)))
    if hook_text and rc.get("hook_overlay", True):
        hook_png = out_dir / "hook.png"
        subprocess.run([str(TOOLS / "graphic"), "slate", "--size", f"{W}x{H}", "--transparent",
                        "--set", f"text={hook_text}", "--set", f"style={rc.get('hook_style', 'pill')}",
                        "--set", f"pos={rc.get('hook_position', 'top')}", "--out", str(hook_png)],
                       check=True, stdout=subprocess.DEVNULL)

    parts, labels = [], []
    for i, x in enumerate(clean):
        d = x["end"] - x["start"]
        parts.append(f"[0:v]trim=start={x['start']:.3f}:end={x['end']:.3f},setpts=PTS-STARTPTS[v{i}]")
        if audio:
            fade = min(0.04, d / 4)
            parts.append(f"[0:a]atrim=start={x['start']:.3f}:end={x['end']:.3f},asetpts=PTS-STARTPTS,"
                         f"afade=t=in:d={fade:.3f},afade=t=out:st={d - fade:.3f}:d={fade:.3f}[a{i}]")
            labels.append(f"[v{i}][a{i}]")
        else:
            labels.append(f"[v{i}]")
    parts.append(f"{''.join(labels)}concat=n={len(clean)}:v=1:a={1 if audio else 0}[vc]" + ("[ac]" if audio else ""))
    fill = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if mode == "blur":
        blur = int(cfg["vertical"].get("blur_strength", 20))
        parts.append(f"[vc]split[b1][b2];[b1]{fill},boxblur={blur}[bg];[b2]scale={W}:-2[fg];"
                     f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[vv]")
    elif mode == "crop":
        parts.append(f"[vc]{fill},setsar=1[vv]")
    else:
        raise SystemExit(f"Unknown mode '{mode}' (use blur or crop)")
    vlast = "vv"
    if hook_png:
        parts.append(f"[{vlast}][1:v]overlay=0:0:enable='between(t,0,{hook_secs})'[vh]")
        vlast = "vh"
    if audio:
        parts.append(f"[ac]loudnorm=I={cfg['prep'].get('loudness', -14)}:TP=-1.5:LRA=11[aout]")

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning", "-stats", "-y", "-i", str(src)]
    if hook_png:
        cmd += ["-loop", "1", "-t", f"{total:.3f}", "-i", str(hook_png)]
    cmd += ["-filter_complex", ";".join(parts), "-map", f"[{vlast}]"]
    if audio:
        cmd += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    cmd += ["-r", f"{min(fps(src), 60):.3f}", "-c:v", "libx264", "-crf", str(rend.get("crf", 18)),
            "-preset", str(rend.get("preset", "medium")), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    print(f"Building {W}x{H} reel (mode={mode}{', hook text' if hook_png else ''})...", flush=True)
    subprocess.run(cmd, check=True)

    # Captions: retime the source transcript onto the reel timeline
    srt_src = Path(plan["srt"]).resolve() if plan.get("srt") else src.with_suffix(".srt")
    if srt_src.exists():
        reel_srt = out_dir / "reel.srt"
        reel_srt.write_text(retime_captions(read_srt(srt_src), clean, pad))
        print(f"Captions: {reel_srt}", flush=True)
        if rc.get("burn_captions", True) and not a.no_captions:
            env = {**__import__("os").environ, "FORCE": "1"}
            r = subprocess.run([str(TOOLS / "burn-captions.sh"), str(out), str(reel_srt),
                                "--margin", str(rc.get("caption_margin_v", 70))], env=env)
            if r.returncode != 0:
                print("(Captions not burned in. Import reel.srt in Kdenlive instead, or brew install ffmpeg-full.)")
    else:
        print(f"No transcript at {srt_src.name}, so no captions. Run the transcript step first.")
    print(f"\nReel: {out} ({duration(out):.1f}s)")


def main():
    cfg = load()
    cfg.setdefault("reel", {})
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcript", help="timestamped transcript of the long video (runs Whisper if needed)")
    t.add_argument("video")
    t.add_argument("--srt", help="use this .srt instead of <video>.srt")
    t.add_argument("--json", action="store_true")
    b = sub.add_parser("build", help="build the reel from a reel.json plan")
    b.add_argument("plan")
    b.add_argument("--out-dir", help="default: the plan's folder")
    b.add_argument("--no-captions", action="store_true", help="don't burn captions in")
    b.add_argument("--allow-long", action="store_true", help="allow going over [reel].max_seconds")
    a = p.parse_args()
    {"transcript": cmd_transcript, "build": cmd_build}[a.cmd](a, cfg)


if __name__ == "__main__":
    main()
