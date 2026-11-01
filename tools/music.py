#!/usr/bin/env python3
"""Background music you're allowed to use (and monetize).

Two ways to get a track:

  find / get   Search open music libraries for tracks whose license allows commercial use:
               CC0 (public domain, no credit needed) or CC BY (free, credit the artist).
               Sources: Openverse (WordPress's open media search: Jamendo, Freesound, ccMixter...)
               and ccMixter directly. The license and a ready-to-paste credit line are saved
               next to the track.
  make         Generate an ORIGINAL track on your Mac from code (no samples, nothing copied).
               You own it outright: no credit, no Content ID claims.

Then put it under the video:

  mix          Add the track under a finished video: looped to length, lowered, ducked
               under your voice, faded out. (The rough cut already puts audio/music.* on A2.)

Examples:
  python3 tools/music.py find "chill lofi"
  python3 tools/music.py get 2 --project projects/<video>        # -> audio/music.mp3 + music-license.md
  python3 tools/music.py make --mood lofi --project projects/<video>
  python3 tools/music.py make --mood upbeat --bpm 118 --seed 4 --out ~/Desktop/test.wav
  python3 tools/music.py mix projects/<video>/export/final.mp4    # uses the project's audio/music.*

Settings: [music] in config.toml. Outputs never overwrite unless FORCE=1.
"""
import argparse
import array
import http.client
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load  # noqa: E402

# ccMixter sometimes sends a header line over 64 KB, which Python's HTTP client refuses by default
http.client._MAXLINE = max(getattr(http.client, "_MAXLINE", 65536), 1 << 22)

UA = "video-editing-workflow/1.0 (+https://github.com/charlitomecarez/video-editing-workflow)"
CACHE = ROOT / ".cache" / "music-search.json"
SR = 44100


def cfg():
    return load().get("music", {})


def die(msg):
    raise SystemExit(msg)


def check_out(p):
    if p.exists() and os.environ.get("FORCE") != "1":
        die(f"Output exists: {p} (run again with FORCE=1 to overwrite)")


def fetch_json(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def mmss(s):
    s = int(round(s or 0))
    return f"{s // 60}:{s % 60:02d}"


# ------------------------------------------------------------------ find / get

def search_openverse(q, c):
    lic = ",".join(x for x in c.get("licenses", ["cc0", "by"]) if x in ("cc0", "by", "pdm"))
    url = "https://api.openverse.org/v1/audio/?" + urllib.parse.urlencode(
        {"q": q, "license": lic, "category": "music", "page_size": 20, "mature": "false"})
    out = []
    for r in fetch_json(url, c.get("timeout", 15)).get("results", []):
        lic_id = (r.get("license") or "").lower()
        if lic_id not in ("cc0", "by", "pdm"):
            continue   # never NC / ND / SA
        out.append({
            "source": f"Openverse ({r.get('source') or r.get('provider')})",
            "title": r.get("title") or "Untitled", "artist": r.get("creator") or "Unknown",
            "license": "CC0" if lic_id == "cc0" else "Public domain" if lic_id == "pdm" else f"CC BY {r.get('license_version') or ''}".strip(),
            "license_url": r.get("license_url") or "", "page": r.get("foreign_landing_url") or "",
            "url": r.get("url"), "ext": (r.get("filetype") or "mp3").lower(),
            "seconds": (r.get("duration") or 0) / 1000, "credit_needed": lic_id == "by",
            "attribution": r.get("attribution") or "", "flag": "",
        })
    return out


def search_ccmixter(q, c):
    url = "https://ccmixter.org/api/query?" + urllib.parse.urlencode(
        {"f": "json", "tags": "instrumental", "search": q, "search_type": "any", "lic": "by", "sort": "rank",
         "limit": 100})
    out = []
    for r in fetch_json(url, c.get("timeout", 15)):
        if "/licenses/by/" not in (r.get("license_url") or ""):
            continue   # only plain CC BY (no NC, no SA)
        files = [f for f in r.get("files", []) if f.get("download_url", "").endswith(".mp3")] or r.get("files", [])
        if not files:
            continue
        f = files[0]
        ps = f.get("file_format_info", {}).get("ps", "0:00")
        mins, _, secs = ps.partition(":")
        ccplus = bool(r.get("upload_extra", {}).get("ccplus"))
        ver = re.search(r"by/([\d.]+)", r["license_url"])
        out.append({
            "source": "ccMixter", "title": r.get("upload_name") or "Untitled",
            "artist": r.get("user_real_name") or r.get("user_name") or "Unknown",
            "license": f"CC BY {ver.group(1) if ver else ''}".strip(),
            "license_url": r.get("license_url"), "page": r.get("file_page_url") or "",
            "url": f["download_url"], "ext": f["download_url"].rsplit(".", 1)[-1].lower(),
            "seconds": int(mins or 0) * 60 + int(secs or 0), "credit_needed": True, "attribution": "",
            # ccPlus artists also sell licenses, so the track is more likely to be in Content ID
            "flag": "ccplus" if ccplus else "",
        })
    if not cfg().get("allow_ccplus", False):
        out = [x for x in out if x["flag"] != "ccplus"]
    return out


SOURCES = {"openverse": search_openverse, "ccmixter": search_ccmixter}


def cmd_find(a, c):
    lo, hi = a.min if a.min is not None else c.get("min_seconds", 60), a.max if a.max is not None else c.get("max_seconds", 600)
    results, notes = [], []
    for name in c.get("sources", ["openverse", "ccmixter"]):
        fn = SOURCES.get(name)
        if not fn:
            notes.append(f"unknown source '{name}' in [music].sources")
            continue
        try:
            got = fn(a.query, c)
            results += got
            notes.append(f"{name}: {len(got)}")
        except Exception as e:   # one library being down shouldn't stop the search
            notes.append(f"{name}: unavailable ({type(e).__name__})")
    results = [r for r in results if r["url"] and (not r["seconds"] or lo <= r["seconds"] <= hi)]
    # Public domain first (no credit needed), then the rest in source order
    results.sort(key=lambda r: r["credit_needed"])
    results = results[: a.n]
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps({"query": a.query, "results": results}, indent=2))
    print(f'Search "{a.query}" ({", ".join(notes)})\n')
    if not results:
        print("Nothing found that's safe to use. Try other words (e.g. 'piano', 'ambient', 'hip hop'), "
              "or generate your own: python3 tools/music.py make")
        return
    for i, r in enumerate(results, 1):
        credit = "no credit needed" if not r["credit_needed"] else "credit the artist"
        print(f"{i:>2}. {r['title']} — {r['artist']}  [{mmss(r['seconds'])}]")
        print(f"    {r['license']} ({credit}) · {r['source']}")
        print(f"    listen: {r['page'] or r['url']}")
    print("\nDownload one:  python3 tools/music.py get <number> --project projects/<video>")


def credit_line(r):
    if not r["credit_needed"]:
        return f'Music: "{r["title"]}" by {r["artist"]} ({r["license"]}, public domain)'
    return f'Music: "{r["title"]}" by {r["artist"]}, licensed under {r["license"]} ({r["license_url"]}). Source: {r["page"]}'


def target_paths(a, ext):
    if a.out:
        out = Path(a.out).expanduser()
        return out, out.with_name(out.stem + "-license.md")
    if not a.project:
        die("Say where to save it: --project projects/<video> (or --out file)")
    adir = Path(a.project) / "audio"
    adir.mkdir(parents=True, exist_ok=True)
    return adir / f"music.{ext}", adir / "music-license.md"


def existing_music(project):
    return sorted(p for p in (Path(project) / "audio").glob("music.*") if p.suffix.lower() in (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".aac"))


def cmd_get(a, c):
    if not CACHE.exists():
        die("Search first: python3 tools/music.py find \"<words>\"")
    data = json.loads(CACHE.read_text())
    if not 1 <= a.number <= len(data["results"]):
        die(f"Pick a number from 1 to {len(data['results'])} (from your last search, \"{data['query']}\")")
    r = data["results"][a.number - 1]
    src = Path(a.file).expanduser() if a.file else None
    if src and not src.is_file():
        die(f"File not found: {src}")
    out, lic = target_paths(a, (src.suffix.lstrip(".").lower() if src else r["ext"]))
    if a.project and not a.out:
        for old in existing_music(a.project):
            if old != out and os.environ.get("FORCE") != "1":
                die(f"The project already has {old.name}. Run again with FORCE=1 to replace it (it gets renamed, not deleted).")
            if old != out:
                old.rename(old.with_name(old.stem + "-old" + old.suffix))
    check_out(out)
    if src:
        shutil.copy2(src, out)
    else:
        print(f"Downloading {r['title']} — {r['artist']}...")
        req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=max(60, c.get("timeout", 15))) as resp, open(out, "wb") as f:
                shutil.copyfileobj(resp, f)
        except urllib.error.HTTPError as e:
            out.unlink(missing_ok=True)
            if e.code in (401, 403, 429):
                # The library wants people to download from its page, not from scripts. Respect that.
                where = f"--project {a.project}" if a.project else f"--out {a.out}"
                die(f"{r['source']} only allows downloads from the track's page.\n"
                    f"  1. Open {r['page']} and download the file\n"
                    f"  2. Then: python3 tools/music.py get {a.number} --file ~/Downloads/<file> {where}\n"
                    "The license and credit line are written the same way.")
            raise
    write_license(lic, [
        f"# Background music: {r['title']}", "",
        f"- **Artist:** {r['artist']}",
        f"- **License:** {r['license']} ({r['license_url'] or 'public domain'})",
        f"- **Source:** {r['source']}, {r['page']}",
        f"- **File:** `{out.name}` (downloaded {__import__('datetime').date.today().isoformat()})",
        "",
        "## Credit (paste in the video description)" if r["credit_needed"] else "## Credit (not required, but nice)",
        "", credit_line(r), "",
        "## If YouTube shows a copyright claim",
        "",
        "Some open-licensed tracks get registered in Content ID by mistake. Dispute the claim and choose "
        "\"I have a license\", pasting the license link and the source page above. Keep this file.",
    ])
    print(f"Saved {out}\nLicense + credit line: {lic}")
    if r["credit_needed"]:
        print(f"\nPut this in the video description:\n  {credit_line(r)}")


def write_license(path, lines):
    if path.exists() and os.environ.get("FORCE") != "1":
        path = path.with_name(path.stem + "-new.md")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ------------------------------------------------------------------ make (original music)

NOTE = {n: i for i, n in enumerate("C C# D D# E F F# G G# A A# B".split())}
# mood -> bpm, swing, scale intervals, chord progression (scale degrees, 0-based), feel
MOODS = {
    "lofi":   {"bpm": 82, "swing": 0.14, "key": "A", "minor": True, "prog": [[5, 0, 2], [4, 6, 1], [3, 5, 0], [2, 4, 6]],
               "kick": [0, 2.5], "snare": [1, 3], "hat": 0.5, "chord": "keys", "lp": 4200, "crackle": True},
    "chill":  {"bpm": 90, "swing": 0.08, "key": "D", "minor": False, "prog": [[0, 2, 4], [5, 0, 2], [3, 5, 0], [4, 6, 1]],
               "kick": [0, 2], "snare": [3], "hat": 1.0, "chord": "pad", "lp": 6000, "crackle": False},
    "upbeat": {"bpm": 114, "swing": 0.0, "key": "C", "minor": False, "prog": [[0, 2, 4], [4, 6, 1], [5, 0, 2], [3, 5, 0]],
               "kick": [0, 1, 2, 3], "snare": [1, 3], "hat": 0.5, "chord": "pluck", "lp": 9000, "crackle": False},
    "tense":  {"bpm": 100, "swing": 0.0, "key": "E", "minor": True, "prog": [[0, 2, 4], [5, 0, 2], [2, 4, 6], [6, 1, 3]],
               "kick": [0, 1.5, 2.5], "snare": [1, 3], "hat": 0.5, "chord": "pad", "lp": 5000, "crackle": False},
}
MAJOR, MINOR = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


class Track:
    """Mono float buffer that wraps around, so the loop is seamless (tails spill into the start)."""

    def __init__(self, seconds):
        self.n = int(seconds * SR)
        self.buf = array.array("d", bytes(8 * self.n))

    def add(self, start, samples):
        i0, n = int(start * SR), self.n
        b = self.buf
        for k, v in enumerate(samples):
            b[(i0 + k) % n] += v


def env_ad(k, n, attack, sr=SR):
    a = max(1, int(attack * sr))
    return k / a if k < a else (1 - (k - a) / max(1, n - a))


def tone(freq, dur, kind, vel):
    n = int(dur * SR)
    out = []
    w = 2 * math.pi * freq / SR
    for k in range(n):
        t = k / SR
        ph = w * k
        if kind == "keys":     # electric-piano-ish: sine + soft 2nd harmonic, slow tremolo, exp decay
            v = (math.sin(ph) + 0.25 * math.sin(2 * ph) + 0.08 * math.sin(3 * ph)) * math.exp(-2.2 * t)
            v *= 0.85 + 0.15 * math.sin(2 * math.pi * 4.5 * t)
            v *= min(1, k / 200)
        elif kind == "pad":    # slow attack, soft detuned sines
            v = (math.sin(ph) + 0.6 * math.sin(ph * 1.003) + 0.3 * math.sin(2 * ph * 0.998)) * 0.6
            v *= min(1, t / 0.6) * min(1, (dur - t) / 0.5)
        elif kind == "pluck":  # bright, quick decay
            v = sum(math.sin(ph * h) / h for h in (1, 2, 3, 4)) * math.exp(-6 * t) * min(1, k / 60)
        elif kind == "bass":
            v = (math.sin(ph) + 0.15 * math.sin(2 * ph)) * min(1, k / 150) * min(1, (dur - t) / 0.05)
        else:                  # lead: sine with gentle vibrato
            v = math.sin(ph + 0.004 * freq / 50 * math.sin(2 * math.pi * 5 * t)) * env_ad(k, n, 0.02)
        out.append(v * vel)
    return out


def drum(kind, rng):
    if kind == "kick":
        n = int(0.32 * SR)
        out, ph = [], 0.0
        for k in range(n):
            t = k / SR
            f = 45 + 110 * math.exp(-t * 30)
            ph += 2 * math.pi * f / SR
            out.append(math.sin(ph) * math.exp(-t * 9) * 0.95)
        return out
    if kind == "snare":
        n = int(0.22 * SR)
        prev, out = 0.0, []
        for k in range(n):
            t = k / SR
            noise = rng.uniform(-1, 1)
            hp = noise - prev   # crude high-pass
            prev = noise
            out.append((0.32 * hp + 0.28 * math.sin(2 * math.pi * 190 * t)) * math.exp(-t * 20))
        return out
    n = int(0.05 * SR)     # hat
    prev, out = 0.0, []
    for k in range(n):
        noise = rng.uniform(-1, 1)
        out.append((noise - prev) * math.exp(-k / SR * 80) * 0.16)
        prev = noise
    return out


def compose(mood, bpm, bars, seed):
    m = MOODS[mood]
    rng = random.Random(seed)
    beat = 60 / bpm
    total = bars * 4 * beat
    tr = Track(total)
    root = 57 + NOTE[m["key"]] - NOTE["A"]          # around A3
    scale = MINOR if m["minor"] else MAJOR
    deg = lambda d, octave=0: root + scale[d % 7] + 12 * (d // 7 + octave)  # noqa: E731
    swing = lambda pos: pos + (m["swing"] * beat if (pos / (beat / 2)) % 2 >= 1 - 1e-6 else 0)  # noqa: E731
    kit = {k: drum(k, rng) for k in ("kick", "snare", "hat")}
    prog = m["prog"][:]
    if seed % 2:
        prog = prog[1:] + prog[:1]                    # vary the start chord between seeds
    pent = [0, 2, 4, 7, 9] if not m["minor"] else [0, 3, 5, 7, 10]
    for bar in range(bars):
        t0 = bar * 4 * beat
        chord = prog[bar % len(prog)]
        # chords: held for the bar (keys/pad) or rhythmic stabs (pluck)
        hits = [0, 1.5, 2.5, 3.5] if m["chord"] == "pluck" else [0]
        for h in hits:
            dur = (4 * beat if m["chord"] != "pluck" else 0.45 * beat)
            for i, d in enumerate(chord + [chord[0] + 7]):
                tr.add(t0 + h * beat + i * 0.012, tone(midi_hz(deg(d)), dur, m["chord"], 0.14))
        # bass: root on 1 and 3 (8ths for tense)
        steps = [x * 0.5 for x in range(8)] if mood == "tense" else [0, 2, 2.75] if mood == "upbeat" else [0, 2]
        for s in steps:
            tr.add(t0 + s * beat, tone(midi_hz(deg(chord[0], -1)), (0.45 if mood == "tense" else 1.6) * beat, "bass", 0.22))
        # drums (sparser in the first bar of every 8, so the loop breathes)
        light = bar % 8 == 0
        for s in m["kick"]:
            tr.add(t0 + s * beat, kit["kick"])
        if not light:
            for s in m["snare"]:
                tr.add(t0 + s * beat, kit["snare"])
        step = m["hat"]
        pos = 0.0
        while pos < 4 - 1e-6:
            tr.add(t0 + swing(pos * beat) + rng.uniform(0, 0.006), [v * rng.uniform(0.6, 1.0) for v in kit["hat"]])
            pos += step
        # a sparse pentatonic melody in the second half of each 8 bars
        if bar % 8 >= 4:
            for s in sorted(rng.sample([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5], rng.choice([2, 3, 4]))):
                note = root + 12 + pent[rng.randrange(5)] + (12 if rng.random() < 0.2 else 0)
                tr.add(t0 + swing(s * beat), tone(midi_hz(note), 0.6 * beat, "lead", 0.06))
    if m["crackle"]:
        b = tr.buf
        for _ in range(int(total * 18)):
            k = rng.randrange(tr.n)
            b[k] += rng.uniform(-0.25, 0.25)
    # normalize
    peak = max(1e-9, max(abs(v) for v in tr.buf))
    return array.array("h", (int(v / peak * 0.85 * 32767) for v in tr.buf)), total, m


def cmd_make(a, c):
    mood = a.mood or c.get("mood", "lofi")
    if mood not in MOODS:
        die(f"Mood options: {', '.join(MOODS)}")
    bpm = a.bpm or c.get("bpm") or MOODS[mood]["bpm"]
    bars = a.bars or c.get("bars", 16)
    seed = a.seed if a.seed is not None else random.randrange(1000)
    out, lic = target_paths(a, "wav")
    if a.project and not a.out:
        for old in existing_music(a.project):
            if old != out and os.environ.get("FORCE") != "1":
                die(f"The project already has {old.name}. Run again with FORCE=1 to replace it (it gets renamed, not deleted).")
            if old != out:
                old.rename(old.with_name(old.stem + "-old" + old.suffix))
    check_out(out)
    print(f"Composing an original {mood} loop: {bpm} bpm, {bars} bars, seed {seed}...")
    pcm, total, m = compose(mood, bpm, bars, seed)
    raw = out.with_suffix(".raw.wav")
    import wave
    with wave.open(str(raw), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    # Mix polish with FFmpeg: tone, a little room, stereo width, even loudness
    fx = (f"lowpass=f={m['lp']},highpass=f=35,aecho=0.8:0.5:45|90:0.18|0.10,"
          f"pan=stereo|c0=c0|c1=c0,haas,acompressor=threshold=0.2:ratio=3:attack=10:release=150,"
          f"loudnorm=I={c.get('loudness', -16)}:TP=-1.5:LRA=7")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", fx, "-ar", "48000", str(out)], check=True)
    raw.unlink()
    write_license(lic, [
        f"# Background music: original {mood} loop", "",
        f"- **Made with:** `python3 tools/music.py make --mood {mood} --bpm {bpm} --bars {bars} --seed {seed}`",
        f"- **Length:** {mmss(total)} loop (the rough cut and `mix` repeat it to the video's length)",
        "- **License:** original work generated on this computer from code. No samples or third-party "
        "recordings, so there's nothing to credit and nothing for Content ID to match.",
        "", "Same command = same track. Change `--seed` for a different one.",
    ])
    print(f"Saved {out} ({mmss(total)} loop)\nNotes: {lic}")
    print("Not quite right? Try another --seed, or --mood " + " / ".join(x for x in MOODS if x != mood))


# ------------------------------------------------------------------ mix

def probe_seconds(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def cmd_mix(a, c):
    video = Path(a.video).expanduser()
    if not video.exists():
        die(f"Video not found: {video}")
    music = Path(a.music).expanduser() if a.music else None
    if not music:
        proj = next((p for p in [video.parent, *video.parents] if (p / "script.md").exists() or (p / "audio").is_dir()), None)
        found = existing_music(proj) if proj else []
        if not found:
            die("No --music given and no audio/music.* in the project. Get one first: find/get or make.")
        music = found[0]
    out = Path(a.out).expanduser() if a.out else video.with_name(video.stem + "_music" + video.suffix)
    check_out(out)
    dur = probe_seconds(video)
    level = a.level if a.level is not None else c.get("mix_level_db", -18)
    fade = c.get("fade_seconds", 2.0)
    duck = c.get("duck", True) and not a.no_duck
    m = f"[1:a]aresample=48000,volume={level}dB,afade=t=in:d=0.5,afade=t=out:st={max(0, dur - fade):.2f}:d={fade}[m]"
    if duck:
        # Music dips while you talk and comes back in the pauses
        graph = (f"[0:a]aresample=48000,asplit=2[v][sc];{m};"
                 f"[m][sc]sidechaincompress=threshold={c.get('duck_threshold', 0.03)}:ratio={c.get('duck_ratio', 6)}:"
                 f"attack=15:release=350[md];[v][md]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        graph = f"[0:a]aresample=48000[v];{m};[v][m]amix=inputs=2:duration=first:normalize=0[a]"
    print(f"Mixing {music.name} under {video.name} at {level} dB{' with ducking' if duck else ''}...")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-stream_loop", "-1", "-i", str(music),
                    "-filter_complex", graph, "-map", "0:v?", "-map", "[a]", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-t", f"{dur:.3f}", "-movflags", "+faststart", str(out)], check=True)
    print(f"Saved {out}")
    lic = music.with_name(music.stem + "-license.md")
    if lic.exists() and "## Credit (paste" in lic.read_text():
        print(f"Remember the credit line in the video description: see {lic}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("find", help="search open libraries for tracks you may use commercially")
    s.add_argument("query")
    s.add_argument("-n", type=int, default=10, help="how many results (default 10)")
    s.add_argument("--min", type=float, help="shortest track in seconds (default [music].min_seconds)")
    s.add_argument("--max", type=float, help="longest track in seconds (default [music].max_seconds)")
    s = sub.add_parser("get", help="download a result from your last search")
    s.add_argument("number", type=int)
    s.add_argument("--file", help="a file you downloaded yourself from the track's page")
    s.add_argument("--project")
    s.add_argument("--out")
    s = sub.add_parser("make", help="generate an original track you own")
    s.add_argument("--mood", help=f"{', '.join(MOODS)} (default [music].mood)")
    s.add_argument("--bpm", type=int)
    s.add_argument("--bars", type=int, help="loop length in bars (default [music].bars)")
    s.add_argument("--seed", type=int, help="same seed = same track (default: random, printed)")
    s.add_argument("--project")
    s.add_argument("--out")
    s = sub.add_parser("mix", help="put a track under a finished video (looped, lowered, ducked)")
    s.add_argument("video")
    s.add_argument("--music", help="track to use (default: the project's audio/music.*)")
    s.add_argument("--level", type=float, help="music level in dB (default [music].mix_level_db)")
    s.add_argument("--no-duck", action="store_true", help="don't lower the music while you talk")
    s.add_argument("--out")
    a = p.parse_args()
    if a.cmd in ("make", "mix") and not shutil.which("ffmpeg"):
        die("ffmpeg missing. Run tools/setup.sh")
    {"find": cmd_find, "get": cmd_get, "make": cmd_make, "mix": cmd_mix}[a.cmd](a, cfg())


if __name__ == "__main__":
    main()
