#!/usr/bin/env python3
"""Sound effects for the edit: an original library you own, plus Myinstants (opt-in, rights unknown).

  python3 tools/sfx.py build                 # (re)generate the original library in sfx/ (safe to monetize)
  python3 tools/sfx.py list                  # every sound: what it's for, its mood, where it comes from
  python3 tools/sfx.py play whoosh           # listen to one
  python3 tools/sfx.py find "bruh"           # search Myinstants (10 searches/min, rights UNKNOWN)
  python3 tools/sfx.py get 3 --name bruh     # add result 3 to the library as "bruh" (logged in sfx/LICENSES.md)

Use them in a script's Notes column:  sfx:whoosh on "First quarter"
The rough cut puts each one on track A3 exactly on that word (or just before / after it, per sound),
and its report checks there aren't too many or too few. Rules for choosing: docs/sound-effects.md.
Settings: [sfx] in config.toml.
"""
import argparse
import array
import json
import math
import os
import random
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import wave
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load  # noqa: E402

SR = 44100
UA = "video-editing-workflow/1.0 (+https://github.com/charlitomecarez/video-editing-workflow)"
CACHE = ROOT / ".cache" / "sfx-search.json"


def cfg():
    c = load().get("sfx", {})
    d = Path(c.get("dir", "sfx"))
    c["dir"] = d if d.is_absolute() else ROOT / d
    return c


def die(msg):
    raise SystemExit(msg)


# ------------------------------------------------------------------ original sounds (stdlib synthesis)

def env_exp(t, rate):
    return math.exp(-t * rate)


def noise_lp(n, rng, cutoff_fn):
    """Noise through a one-pole low-pass whose cutoff (Hz) can move over time: whooshes, risers."""
    out, y = [], 0.0
    for k in range(n):
        fc = cutoff_fn(k / SR)
        a = 1 - math.exp(-2 * math.pi * fc / SR)
        y += a * (rng.uniform(-1, 1) - y)
        out.append(y)
    return out


def hp(sig):
    out, prev = [], 0.0
    for v in sig:
        out.append(v - prev)
        prev = v
    return out


def s_pop(rng):
    n = int(0.09 * SR)
    ph, out = 0.0, []
    for k in range(n):
        t = k / SR
        ph += 2 * math.pi * (300 + 700 * math.exp(-t * 60)) / SR
        out.append(math.sin(ph) * env_exp(t, 45) * min(1, k / 40))
    return out


def s_click(rng):
    n = int(0.012 * SR)
    return [v * env_exp(k / SR, 400) for k, v in enumerate(hp([rng.uniform(-1, 1) for _ in range(n)]))]


def s_whoosh(rng, dur=0.55, peak=0.32, down=False):
    n = int(dur * SR)
    def cut(t):
        x = t / dur
        return 400 + 5200 * (math.sin(math.pi * x) ** 2 if not down else (1 - x) ** 1.5)
    sig = noise_lp(n, rng, cut)
    out = []
    for k, v in enumerate(sig):
        t = k / SR
        e = (t / peak) ** 2 if t < peak else math.exp(-(t - peak) * 9)
        out.append(v * e * 2.2)
    return out


def s_ding(rng):
    n = int(1.3 * SR)
    f = 1318.5
    return [sum(a * math.sin(2 * math.pi * f * m * k / SR) * env_exp(k / SR, d)
                for m, a, d in ((1, 1, 3), (2.76, 0.4, 5), (5.4, 0.18, 8))) * min(1, k / 30) for k in range(n)]


def s_impact(rng):
    n = int(1.0 * SR)
    ph, out = 0.0, []
    for k in range(n):
        t = k / SR
        ph += 2 * math.pi * (38 + 70 * math.exp(-t * 14)) / SR
        out.append(math.sin(ph) * env_exp(t, 3.5) + rng.uniform(-1, 1) * 0.35 * env_exp(t, 30))
    return out


def s_riser(rng):
    dur = 1.6
    n = int(dur * SR)
    sig = noise_lp(n, rng, lambda t: 300 + 7000 * (t / dur) ** 2)
    ph, out = 0.0, []
    for k, v in enumerate(sig):
        t = k / SR
        ph += 2 * math.pi * (180 + 900 * (t / dur) ** 2) / SR
        out.append((v * 1.4 + 0.25 * math.sin(ph)) * (t / dur) ** 2 * min(1, (dur - t) * 40))
    return out


def s_rimshot(rng):
    out = [0.0] * int(1.4 * SR)

    def hit(at, f, decay, noise_amt):
        i0 = int(at * SR)
        for k in range(int(0.35 * SR)):
            t = k / SR
            v = math.sin(2 * math.pi * f * t) * env_exp(t, decay) + rng.uniform(-1, 1) * noise_amt * env_exp(t, 35)
            if i0 + k < len(out):
                out[i0 + k] += v * 0.8
    hit(0.0, 196, 18, 0.5)     # ba
    hit(0.16, 150, 16, 0.5)    # dum
    cym = hp(hp([rng.uniform(-1, 1) for _ in range(int(1.1 * SR))]))
    i0 = int(0.34 * SR)        # tss
    for k, v in enumerate(cym):
        if i0 + k < len(out):
            out[i0 + k] += v * 0.45 * env_exp(k / SR, 3.2)
    return out


def s_boing(rng):
    n = int(0.75 * SR)
    ph, out = 0.0, []
    for k in range(n):
        t = k / SR
        f = 220 * (1 + 0.45 * math.sin(2 * math.pi * 11 * t) * env_exp(t, 4)) * (1 + 0.6 * env_exp(t, 12))
        ph += 2 * math.pi * f / SR
        out.append((math.sin(ph) + 0.3 * math.sin(2 * ph)) * env_exp(t, 3.2) * min(1, k / 80))
    return out


def s_record_scratch(rng):
    n = int(0.45 * SR)
    ph, out = 0.0, []
    for k in range(n):
        t = k / SR
        speed = math.sin(2 * math.pi * 3.2 * t) * (1 - t / 0.45)          # forward-back motion
        ph += 2 * math.pi * (120 + 700 * abs(speed)) / SR
        saw = 2 * ((ph / (2 * math.pi)) % 1) - 1
        out.append((saw * 0.5 + rng.uniform(-1, 1) * 0.5 * abs(speed)) * min(1, (0.45 - t) * 30))
    return hp(out)


def s_sad_trombone(rng):
    notes = [(233.1, 0.38), (220.0, 0.38), (207.7, 0.38), (196.0, 1.1)]   # Bb A Ab G, last one wobbles
    out = []
    for i, (f, d) in enumerate(notes):
        ph = 0.0
        for k in range(int(d * SR)):
            t = k / SR
            vib = 1 + (0.03 * math.sin(2 * math.pi * 5.5 * t) if i == 3 else 0)
            ph += 2 * math.pi * f * vib / SR
            saw = sum(math.sin(ph * h) / h for h in range(1, 7))
            out.append(saw * min(1, t / 0.04) * min(1, (d - t) / 0.06) * (0.9 if i < 3 else env_exp(t, 1.2)))
    y, lp = 0.0, []
    for v in out:     # soften (muted brass)
        y += 0.18 * (v - y)
        lp.append(y)
    return lp


def s_glitch(rng):
    out = []
    for _ in range(9):
        d = int(rng.uniform(0.012, 0.04) * SR)
        f = rng.choice([180, 360, 720, 1440, 2880])
        out += [(1 if (k * f // SR) % 2 else -1) * rng.uniform(0.4, 1) for k in range(d)]
        out += [0.0] * int(rng.uniform(0.0, 0.015) * SR)
    return out


def s_tick(rng):
    n = int(0.05 * SR)
    return [math.sin(2 * math.pi * 2400 * k / SR) * env_exp(k / SR, 120) for k in range(n)]


# name: (generator, use, mood, anchor, offset_s, gain_db)
#   anchor "start": the sound starts at the cue word (+offset); "end": it starts after the cue word ends
LIBRARY = {
    "pop": (s_pop, "a caption or graphic popping in", "neutral", "start", 0.0, -4),
    "click": (s_click, "UI moment: a screenshot, a cursor, a list item", "neutral", "start", 0.0, -6),
    "tick": (s_tick, "a quick count or a number ticking in", "neutral", "start", 0.0, -8),
    "whoosh": (lambda r: s_whoosh(r), "a new section or a big card sliding in (peaks on the word)", "energetic", "start", -0.3, -3),
    "whoosh-down": (lambda r: s_whoosh(r, 0.7, 0.18, True), "leaving a section, a let-down", "calm", "start", -0.15, -4),
    "ding": (s_ding, "a stat that matters, a fact landing, 'correct'", "positive", "start", 0.0, -6),
    "impact": (s_impact, "the big reveal: final score, the one number the video is about", "dramatic", "start", 0.0, -2),
    "riser": (s_riser, "build-up that ends right on the reveal word", "dramatic", "start", -1.6, -6),
    "rimshot": (s_rimshot, "after a pun or a groaner (once per video, max twice)", "comedic", "end", 0.08, -5),
    "boing": (s_boing, "something silly or a dumb mistake", "comedic", "end", 0.05, -6),
    "record-scratch": (s_record_scratch, "the twist: 'wait, what?' / the story turns", "comedic", "start", -0.1, -5),
    "sad-trombone": (s_sad_trombone, "a fail or a loss (not real tragedy)", "comedic", "end", 0.1, -7),
    "glitch": (s_glitch, "a chapter card, a hard topic switch", "energetic", "start", -0.05, -9),
}


def write_wav(path, samples, gain_db):
    peak = max(1e-9, max(abs(v) for v in samples))
    scale = 0.89 * 10 ** (gain_db / 20) / peak
    pcm = array.array("h", (int(max(-1, min(1, v * scale)) * 32767) for v in samples))
    tmp = path.with_suffix(".tmp.wav")
    with wave.open(str(tmp), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-ar", "48000", "-ac", "2", str(path)], check=True)
    tmp.unlink()


def load_lib(c):
    f = c["dir"] / "library.json"
    return json.loads(f.read_text()) if f.exists() else {}


def save_lib(c, lib):
    c["dir"].mkdir(parents=True, exist_ok=True)
    (c["dir"] / "library.json").write_text(json.dumps(lib, indent=2, ensure_ascii=False) + "\n")


def cmd_build(a, c):
    if not shutil.which("ffmpeg"):
        die("ffmpeg missing. Run tools/setup.sh")
    lib = load_lib(c)
    c["dir"].mkdir(parents=True, exist_ok=True)
    rng = random.Random(7)
    for name, (gen, use, mood, anchor, offset, gain) in LIBRARY.items():
        path = c["dir"] / f"{name}.wav"
        write_wav(path, gen(rng), gain)
        lib[name] = {"file": path.name, "use": use, "mood": mood, "anchor": anchor, "offset": offset,
                     "source": "original", "license": "Original, generated by tools/sfx.py build. Yours, no credit needed."}
        print(f"  {name:<15} {use}")
    save_lib(c, lib)
    print(f"\n{len(LIBRARY)} original sounds in {c['dir']}/ (safe to monetize). Listen: python3 tools/sfx.py play <name>")


def cmd_list(a, c):
    lib = load_lib(c)
    if not lib:
        die("No library yet. Run: python3 tools/sfx.py build")
    for name, s in sorted(lib.items(), key=lambda kv: (kv[1]["source"] != "original", kv[1]["mood"], kv[0])):
        flag = "" if s["source"] == "original" else "  ⚠ rights unknown (Myinstants)"
        ok = "" if (c["dir"] / s["file"]).exists() else "  (file missing: run build)"
        print(f"{name:<16} {s['mood']:<10} {s['use']}{flag}{ok}")


def cmd_play(a, c):
    s = load_lib(c).get(a.name)
    if not s:
        die(f"No sound '{a.name}'. See: python3 tools/sfx.py list")
    subprocess.run(["afplay", str(c["dir"] / s["file"])])


# ------------------------------------------------------------------ Myinstants (opt-in)

def polite_wait(c):
    """Myinstants allows 10 anonymous requests a minute: keep at least 6.5 s between calls."""
    stamp = ROOT / ".cache" / "myinstants-last"
    stamp.parent.mkdir(parents=True, exist_ok=True)
    gap = c.get("myinstants_gap_seconds", 6.5)
    if stamp.exists():
        wait = gap - (time.time() - stamp.stat().st_mtime)
        if wait > 0:
            time.sleep(wait)
    stamp.touch()


def myinstants(url, c):
    polite_wait(c)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    token = os.environ.get("MYINSTANTS_TOKEN", "")
    env = ROOT / ".env.local"
    if not token and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("MYINSTANTS_TOKEN="):
                token = line.split("=", 1)[1].strip().strip('"\'')
    if token:
        req.add_header("Authorization", f"Token {token}")
    try:
        with urllib.request.urlopen(req, timeout=c.get("timeout", 20)) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            die("Myinstants says: too many requests (10 per minute without a token). Wait a minute and try again.")
        raise


def cmd_find(a, c):
    url = "https://www.myinstants.com/api/v1/instants/?" + urllib.parse.urlencode({"name": a.query})
    d = json.loads(myinstants(url, c))
    res = [{"name": r["name"], "slug": r["slug"], "url": r["sound"], "description": r.get("description", ""),
            "page": f"https://www.myinstants.com/en/instant/{r['slug']}/"} for r in d.get("results", []) if r.get("sound")]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({"query": a.query, "results": res}, indent=2))
    print(f'Myinstants "{a.query}": {d.get("count", len(res))} found, showing {len(res)}\n')
    for i, r in enumerate(res, 1):
        print(f"{i:>2}. {r['name']}   {r['page']}")
    print("\n⚠ Myinstants has NO license info: anyone uploads, and many sounds are clips from movies, TV, songs\n"
          "  or other creators. Those can get your video claimed or demonetized. Generic sounds (a ding, a\n"
          "  rimshot) are lower risk than anything recognizable. Prefer the original library (sfx.py list).\n"
          "Add one: python3 tools/sfx.py get <number> --name <short-name> --mood comedic --use \"what it's for\"")


def cmd_get(a, c):
    if not CACHE.exists():
        die('Search first: python3 tools/sfx.py find "<words>"')
    data = json.loads(CACHE.read_text())
    if not 1 <= a.number <= len(data["results"]):
        die(f"Pick 1 to {len(data['results'])}")
    r = data["results"][a.number - 1]
    lib = load_lib(c)
    name = a.name or r["slug"]
    if name in lib and lib[name]["source"] == "original":
        die(f"'{name}' is an original sound. Pick another --name.")
    raw = c["dir"] / f"{name}.download"
    c["dir"].mkdir(parents=True, exist_ok=True)
    raw.write_bytes(myinstants(r["url"], c))
    out = c["dir"] / f"{name}.wav"
    # Trim silence at the start so it lands on the word, even out the level
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,loudnorm=I=-18:TP=-2",
                    "-ar", "48000", "-ac", "2", str(out)], check=True)
    raw.unlink()
    lib[name] = {"file": out.name, "use": a.use or r["name"], "mood": a.mood, "anchor": a.anchor,
                 "offset": 0.0, "source": "myinstants", "page": r["page"],
                 "license": "UNKNOWN: user-uploaded on Myinstants. Check it isn't a clip from a movie, show, song or creator."}
    save_lib(c, lib)
    log = c["dir"] / "LICENSES.md"
    if not log.exists():
        log.write_text("# Sound effect sources\n\nOriginal sounds (`tools/sfx.py build`) are yours. Everything below "
                       "came from Myinstants and has **no license info**: check each one before monetizing.\n\n"
                       "| Name | Myinstants title | Page | Added |\n| --- | --- | --- | --- |\n")
    with open(log, "a") as f:
        f.write(f"| `{name}` | {r['name']} | {r['page']} | {date.today().isoformat()} |\n")
    print(f"Added '{name}' ({out}).\n⚠ Rights unknown, logged in {log}. The rough cut report lists every place it's used.")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="generate the original sound library")
    sub.add_parser("list", help="list sounds")
    s = sub.add_parser("play", help="listen to a sound")
    s.add_argument("name")
    s = sub.add_parser("find", help="search Myinstants (rights unknown)")
    s.add_argument("query")
    s = sub.add_parser("get", help="add a Myinstants result to the library")
    s.add_argument("number", type=int)
    s.add_argument("--name", help="short name to use in scripts, e.g. bruh")
    s.add_argument("--mood", default="comedic", help="neutral, positive, energetic, calm, dramatic or comedic")
    s.add_argument("--use", help="when to use it, e.g. 'disbelief after a dumb take'")
    s.add_argument("--anchor", default="end", choices=["start", "end"],
                   help="start = on the cue word, end = right after it (punchline stingers)")
    a = p.parse_args()
    {"build": cmd_build, "list": cmd_list, "play": cmd_play, "find": cmd_find, "get": cmd_get}[a.cmd](a, cfg())


if __name__ == "__main__":
    main()
