#!/usr/bin/env python3
"""Draft voiceover in YOUR voice (Chatterbox voice cloning, free, runs on your Mac).

1. Give it a few clips of you talking (any audio/video format, 10 s to a few minutes each):
     tools/voice-clone add me ~/Desktop/voice1.m4a ~/Desktop/voice2.wav
   It cleans them, removes long pauses and saves the best stretch as the reference
   in .voices/clone/me/ref.wav. Run `add` again with more clips to rebuild it.

2. Read a script (or any text) in that voice:
     tools/voice-clone say projects/x/script.md
     tools/voice-clone say projects/x/script.md --voice me --speed 1.1 --seed 7
     tools/voice-clone say --text "Quick test, does this sound like me?"
   Output: <script>_clone-vo.wav + <script>_clone-vo.json (start/end of every script row).

Other commands:
     tools/voice-clone list            # saved voices
     tools/voice-clone ref me          # play the reference clip it's using

Settings: [voice_clone] in config.toml. Installs with: tools/setup.sh --voice-clone
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load  # noqa: E402
from script_text import extract  # noqa: E402

SR = 24000  # Chatterbox's sample rate


def cfg():
    c = load().get("voice_clone", {})
    d = Path(c.get("voices_dir", ".voices/clone"))
    c["voices_dir"] = d if d.is_absolute() else ROOT / d
    return c


def np_():
    import numpy as np
    return np


# ---------- audio helpers (ffmpeg in, numpy arrays out) ----------

def decode(path, filters=None):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-ac", "1", "-ar", str(SR)]
    if filters:
        cmd += ["-af", filters]
    cmd += ["-f", "f32le", "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    return np_().frombuffer(raw, dtype="float32").copy()


def write_wav(path, audio, filters=None):
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-"]
    if filters:
        cmd += ["-af", filters]
    cmd += ["-c:a", "pcm_s16le", str(path)]
    subprocess.run(cmd, input=audio.astype("float32").tobytes(), check=True)


def speech_mask(audio, frame=0.02):
    """Per-frame True where someone is talking (simple energy gate)."""
    np = np_()
    n = int(SR * frame)
    frames = audio[: len(audio) // n * n].reshape(-1, n)
    db = 20 * np.log10(np.sqrt((frames ** 2).mean(axis=1)) + 1e-9)
    thresh = max(-50.0, np.percentile(db, 95) - 30)
    return db > thresh, n


def squeeze_pauses(audio, max_pause, keep_pause):
    """Trim the ends and shorten any pause longer than max_pause to keep_pause."""
    np = np_()
    mask, n = speech_mask(audio)
    if not mask.any():
        return audio[:0]
    # Pad the ends: soft sounds ("th", "f", "h") sit below the gate
    pad = int(0.1 * SR / n)
    first = max(0, int(np.argmax(mask)) - pad)
    last = min(len(mask), len(mask) - int(np.argmax(mask[::-1])) + pad)
    mask = mask.copy()
    mask[first:first + pad + 1] = mask[last - pad - 1:last] = True
    out, run_start = [], None
    for i in range(first, last):
        if mask[i]:
            if run_start is not None:
                gap = i - run_start
                keep = gap if gap * n / SR <= max_pause else int(keep_pause * SR / n)
                out.append(audio[run_start * n: (run_start + keep) * n])
                run_start = None
            out.append(audio[i * n: (i + 1) * n])
        elif run_start is None:
            run_start = i
    return np.concatenate(out)


def best_window(audio, seconds):
    """Start sample of the stretch of `seconds` with the most speech and no clipping."""
    np = np_()
    w = int(seconds * SR)
    if len(audio) <= w:
        return 0
    mask, n = speech_mask(audio)
    clip = np.abs(audio[: len(mask) * n].reshape(-1, n)).max(axis=1) > 0.98
    score = mask.astype(float) - 2 * clip
    wf = w // n
    sums = np.convolve(score, np.ones(wf), "valid")
    return int(np.argmax(sums)) * n


# ---------- commands ----------

def cmd_add(a, c):
    np = np_()
    vdir = c["voices_dir"] / a.name
    (vdir / "samples").mkdir(parents=True, exist_ok=True)
    existing = sorted((vdir / "samples").glob("*.wav"))
    clean = c.get("sample_filters", "highpass=f=70,afftdn=nf=-25,loudnorm=I=-18:TP=-2:LRA=11")
    for i, f in enumerate(a.files, start=len(existing) + 1):
        f = Path(f).expanduser()
        if not f.is_file():
            raise SystemExit(f"File not found: {f}")
        audio = squeeze_pauses(decode(f, clean), c.get("max_pause", 0.5), c.get("keep_pause", 0.3))
        dur = len(audio) / SR
        if dur < 2:
            print(f"  skip {f.name}: almost no speech found")
            continue
        out = vdir / "samples" / f"{i:02d}-{re.sub(r'[^A-Za-z0-9_-]+', '-', f.stem)}.wav"
        write_wav(out, audio)
        print(f"  + {f.name} -> {out.name} ({dur:.1f}s of speech)")

    samples = sorted((vdir / "samples").glob("*.wav"))
    if not samples:
        raise SystemExit("No usable samples. Record 10-60 s of you talking normally, in a quiet room.")
    gap = np.zeros(int(0.3 * SR), dtype="float32")
    allaudio = np.concatenate([x for s in samples for x in (decode(s), gap)])
    total = len(allaudio) / SR
    # Chatterbox copies the delivery from the first ~10 s of the reference and builds the
    # speaker identity from all of it: best 10 s first, then more of you up to ref_seconds.
    i, w = best_window(allaudio, 10), 10 * SR
    head, rest = allaudio[i:i + w], np.concatenate([allaudio[i + w:], allaudio[:i]])
    ref_s = float(c.get("ref_seconds", 30))
    ref = np.concatenate([head, gap, rest])[: int(ref_s * SR)]
    write_wav(vdir / "ref.wav", ref)
    (vdir / "voice.json").write_text(json.dumps(
        {"name": a.name, "samples": [s.name for s in samples], "speech_seconds": round(total, 1),
         "ref_seconds": round(len(ref) / SR, 1)}, indent=2))
    print(f"\nVoice '{a.name}': {total:.0f}s of speech from {len(samples)} clip(s). Reference: {vdir / 'ref.wav'} "
          f"({len(ref) / SR:.1f}s)")
    if total < 8:
        print("Tip: that's short. 15-60 s of natural talking clones much better.")
    print(f"Listen to it: tools/voice-clone ref {a.name}   Then: tools/voice-clone say <script.md> --voice {a.name}")


def cmd_list(a, c):
    d = c["voices_dir"]
    voices = sorted(p for p in d.glob("*/ref.wav")) if d.exists() else []
    if not voices:
        print("No cloned voices yet. Add one: tools/voice-clone add me <clip1> [clip2 ...]")
    for r in voices:
        meta = json.loads((r.parent / "voice.json").read_text()) if (r.parent / "voice.json").exists() else {}
        star = " (default)" if r.parent.name == c.get("voice") else ""
        print(f"{r.parent.name}{star}: {meta.get('speech_seconds', '?')}s of samples, "
              f"{len(meta.get('samples', []))} clip(s)")


def cmd_ref(a, c):
    ref = c["voices_dir"] / (a.name or c.get("voice", "me")) / "ref.wav"
    if not ref.exists():
        raise SystemExit(f"No reference at {ref}. Run: tools/voice-clone add <name> <clips>")
    print(ref)
    if shutil.which("afplay"):
        subprocess.run(["afplay", str(ref)])


def chunks(text, max_chars):
    """Split into sentences, then glue short ones together (very short inputs sound off)."""
    sents = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text.strip()) if s.strip()]
    out = []
    for s in sents:
        if out and (len(out[-1]) + len(s) + 1 <= max_chars) and (len(out[-1]) < 60 or len(s) < 25):
            out[-1] += " " + s
        else:
            out.append(s)
    # Hard-split anything still too long at commas, then words
    final = []
    for s in out:
        while len(s) > max_chars:
            cut = s.rfind(", ", 0, max_chars)
            cut = cut + 1 if cut > max_chars // 3 else s.rfind(" ", 0, max_chars)
            final.append(s[:cut].strip())
            s = s[cut:].strip()
        final.append(s)
    return final


def load_model(device_pref):
    import torch
    if device_pref == "auto":
        device = "mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = device_pref
    from chatterbox.tts import ChatterboxTTS
    print(f"Loading Chatterbox on {device} (first run downloads ~3 GB)...")
    return ChatterboxTTS.from_pretrained(device=device), device


def cmd_say(a, c):
    np = np_()
    name = a.voice or c.get("voice", "me")
    ref = c["voices_dir"] / name / "ref.wav"
    if not ref.exists():
        raise SystemExit(f"No voice '{name}' yet. Add it first: tools/voice-clone add {name} <clip1> [clip2 ...]")

    if a.text:
        beats = [{"row": 1, "section": None, "text": a.text}]
        out = Path(a.out or "clone-test_clone-vo.wav")
    else:
        src = Path(a.input)
        if not src.is_file():
            raise SystemExit(f"File not found: {src}")
        if src.suffix == ".md":
            beats = extract(src.read_text(encoding="utf-8"))
        else:
            beats = [{"row": i, "section": None, "text": t.strip()}
                     for i, t in enumerate(src.read_text(encoding="utf-8").split("\n\n"), 1) if t.strip()]
        if a.rows:
            want = {int(r) for r in a.rows.split(",")}
            beats = [b for b in beats if b["row"] in want]
        out = Path(a.out) if a.out else src.with_name(src.stem + "_clone-vo.wav")
    if not beats:
        raise SystemExit("No narration found. Fill in the Hear column / Voiceover lines first.")
    if out.exists() and not a.force:
        raise SystemExit(f"Output exists: {out} (run again with FORCE=1 to overwrite)")

    import torch
    model, device = load_model(c.get("device", "auto"))
    seed = a.seed if a.seed is not None else int(c.get("seed", 0))
    exag = a.exaggeration if a.exaggeration is not None else float(c.get("exaggeration", 0.5))
    cfgw = a.cfg_weight if a.cfg_weight is not None else float(c.get("cfg_weight", 0.5))
    temp = float(c.get("temperature", 0.8))
    sent_gap = np.zeros(int(float(c.get("sentence_pause", 0.2)) * SR), dtype="float32")
    beat_gap = np.zeros(int(float(c.get("beat_pause", 0.45)) * SR), dtype="float32")
    max_chars = int(c.get("max_chars", 250))

    model.prepare_conditionals(str(ref), exaggeration=exag)
    pieces, timing, t = [], [], 0.0
    words = sum(len(b["text"].split()) for b in beats)
    print(f"Speaking {words} words ({len(beats)} rows) as '{name}' "
          f"(exaggeration {exag}, cfg_weight {cfgw}, seed {seed})")
    for bi, b in enumerate(beats):
        start = t
        for ci, ch in enumerate(chunks(b["text"], max_chars)):
            torch.manual_seed(seed + bi * 100 + ci)
            wav = model.generate(ch, exaggeration=exag, cfg_weight=cfgw, temperature=temp)
            audio = wav.squeeze().detach().cpu().numpy().astype("float32")
            audio = squeeze_pauses(audio, 0.4, 0.25) if len(audio) else audio  # trim model's lead/tail silence
            if ci:
                pieces.append(sent_gap)
                t += len(sent_gap) / SR
            pieces.append(audio)
            t += len(audio) / SR
        timing.append({"row": b["row"], "section": b.get("section"), "start": round(start, 2),
                       "end": round(t, 2), "text": b["text"]})
        print(f"  row {b['row']:>3}  {start:6.1f}s  {b['text'][:60]}")
        if bi < len(beats) - 1:
            pieces.append(beat_gap)
            t += len(beat_gap) / SR

    speed = a.speed if a.speed is not None else float(c.get("speed", 1.0))
    filters = [c.get("output_filters", "loudnorm=I=-16:TP=-1.5:LRA=11")]
    if abs(speed - 1.0) > 0.01:
        filters.insert(0, f"atempo={speed}")
        for x in timing:
            x["start"], x["end"] = round(x["start"] / speed, 2), round(x["end"] / speed, 2)
    write_wav(out, np.concatenate(pieces), ",".join(f for f in filters if f))
    out.with_suffix(".json").write_text(json.dumps({"voice": name, "speed": speed, "seed": seed, "rows": timing},
                                                   indent=2, ensure_ascii=False))
    print(f"\nCloned voiceover: {out} ({t / speed:.0f}s)  timings: {out.with_suffix('.json').name}")
    print("Didn't like a line? Re-roll just those rows: --rows 3,7 --seed 2 --out fix.wav")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("add", help="add voice samples and build the reference")
    s.add_argument("name")
    s.add_argument("files", nargs="+")
    sub.add_parser("list", help="list saved voices")
    s = sub.add_parser("ref", help="play a voice's reference clip")
    s.add_argument("name", nargs="?")
    s = sub.add_parser("say", help="read a script or text in a cloned voice")
    s.add_argument("input", nargs="?", help="script.md or .txt")
    s.add_argument("--text", help="say this text instead of a file")
    s.add_argument("--voice")
    s.add_argument("--speed", type=float)
    s.add_argument("--seed", type=int)
    s.add_argument("--exaggeration", type=float, help="0.25 flat ... 0.5 normal ... 1.0 dramatic")
    s.add_argument("--cfg-weight", type=float, help="lower = slower, more deliberate pacing")
    s.add_argument("--rows", help="only these script rows, e.g. 3,7")
    s.add_argument("--out")
    a = p.parse_args()
    if a.cmd == "say" and not (a.input or a.text):
        s.error("give a script/text file or --text")
    a.force = __import__("os").environ.get("FORCE") == "1"
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg missing. Run tools/setup.sh")
    {"add": cmd_add, "list": cmd_list, "ref": cmd_ref, "say": cmd_say}[a.cmd](a, cfg())


if __name__ == "__main__":
    main()
