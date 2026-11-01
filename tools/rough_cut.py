#!/usr/bin/env python3
"""Auto rough cut: raw recording + script -> a Kdenlive project you can polish.

  python3 tools/rough_cut.py projects/<video>
  python3 tools/rough_cut.py projects/<video> --source footage/take2.mov --place any-server-room.mp4=07

What it does:
  1. Transcribes the recording with Whisper (word timestamps, cached in roughcut/).
  2. Matches what you said to the script's Hear column / Voiceover lines.
     Repeated a line? The LAST full take is kept. False starts are dropped.
     Things you said that aren't in the script (ad-libs) are kept with a marker
     so you can decide, unless [rough_cut].adlibs = "drop".
  3. Cuts long pauses inside lines and leaves a short, even gap between lines.
  4. Builds <project>/<folder-name>-roughcut.kdenlive:
       V2  graphics/NN-*.png and footage/broll/NN-*.mp4, starting when row NN is spoken
       V1  your camera / screen recording
       A1  your voice (uses <name>_clean.wav from clean-voice.sh when it exists)
       A2  audio/music.* (looped, lowered, faded out)
       A3  sound effects cued in the script's Notes column: sfx:whoosh on "word" (tools/sfx.py)
       Guides: one per script section, plus ad-libs and anything that needs a look.
  5. Writes roughcut/report.md, roughcut/roughcut.srt (captions for the cut) and a
     quick preview video, roughcut/preview.mp4.

Materials named any-*.mp4 go into the project bin ("Unplaced B-roll") unless you
place them with --place FILE=ROW. Settings: [rough_cut] in config.toml.
"""
import argparse
import difflib
import json
import math
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load, load_styles  # noqa: E402
from script_text import extract  # noqa: E402

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi"}
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".aif", ".aiff"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".bmp", ".tif", ".tiff"}
FILLERS = {"um", "uh", "uhm", "erm", "ah", "oh", "hmm", "mm", "eh", "like", "okay", "ok", "so"}
NUM = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen " \
      "sixteen seventeen eighteen nineteen twenty".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n):
    """42 -> ['forty', 'two'], 145 -> ['one', 'hundred', 'forty', 'five'], 2918 -> ['two', 'thousand', ...].
    So '42 points' from Whisper matches 'forty-two points' in the script."""
    if n <= 20:
        return [NUM[n]]
    if n < 100:
        return [TENS[n // 10]] + ([NUM[n % 10]] if n % 10 else [])
    if n < 1000:
        return [NUM[n // 100], "hundred"] + (num_words(n % 100) if n % 100 else [])
    if n < 1_000_000:
        return num_words(n // 1000) + ["thousand"] + (num_words(n % 1000) if n % 1000 else [])
    return [str(n)]


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- text matching

def norm_tokens(text):
    t = text.lower()
    for a, b in (("c++", " c plus plus "), ("c#", " c sharp "), ("f#", " f sharp "), ("&", " and "),
                 ("%", " percent "), ("+", " plus "), ("’", "'"), ("‘", "'"), (".js", " js ")):
        t = t.replace(a, b)
    t = re.sub(r"\*+", "", t)              # markdown emphasis
    t = re.sub(r"'", "", t)                # don't -> dont
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", t)  # 2,918 -> 2918
    t = re.sub(r"[^\w\s]", " ", t)
    out = []
    for w in t.split():
        out.extend(num_words(int(w)) if w.isdigit() else [w])
    return out


def ratio(a, b):
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def covered(frag, ref):
    """Share of frag's tokens that also appear, in order, in ref."""
    if not frag:
        return 0.0
    m = difflib.SequenceMatcher(None, frag, ref, autojunk=False)
    return sum(b.size for b in m.get_matching_blocks()) / len(frag)


def same_word(a, b):
    return a == b or (len(a) > 3 and len(b) > 3 and a[:4] == b[:4])


class Take:
    __slots__ = ("score", "i", "j")

    def __init__(self, score, i, j):
        self.score, self.i, self.j = score, i, j   # words[i:j]


def find_takes(btok, toks, lo, hi, thr):
    """Non-overlapping windows of toks[lo:hi] that match the beat, sorted by position."""
    n = len(btok)
    if not n:
        return []
    anchors = btok[:3]
    cands = []
    for i in range(lo, min(hi, len(toks))):
        if not any(same_word(toks[i], a) for a in anchors):
            continue
        best = None
        for L in range(max(1, int(n * 0.6)), int(n * 1.35) + 2):
            if i + L > len(toks):
                break
            r = ratio(btok, toks[i:i + L])
            if best is None or r > best[0]:
                best = (r, L)
        if best and best[0] >= thr:
            # Trim the window to the first/last word that actually matches the line
            w = toks[i:i + best[1]]
            blocks = [b for b in difflib.SequenceMatcher(None, btok, w, autojunk=False).get_matching_blocks() if b.size]
            a = blocks[0].b
            z = blocks[-1].b + blocks[-1].size
            cands.append(Take(best[0], i + a, i + z))
    keep = []
    for c in sorted(cands, key=lambda c: -c.score):
        if all(c.j <= k.i or c.i >= k.j for k in keep):
            keep.append(c)
    return sorted(keep, key=lambda c: c.i)


# ---------------------------------------------------------------- media helpers

def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,width,height,r_frame_rate:format=duration",
                          "-of", "json", str(path)], capture_output=True, text=True)
    if out.returncode:
        raise SystemExit(f"ffprobe can't read {path}")
    d = json.loads(out.stdout)
    streams = d.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    # Single-frame "video" streams (cover art in mp3s) don't count
    is_video = bool(v) and path.suffix.lower() in VIDEO_EXT
    return {
        "duration": float(d.get("format", {}).get("duration") or 0),
        "video": is_video,
        "audio": any(s.get("codec_type") == "audio" for s in streams),
        "width": v.get("width") if v else None,
        "height": v.get("height") if v else None,
    }


def find_melt(cfg):
    for c in (cfg.get("melt", ""), "/Applications/kdenlive.app/Contents/MacOS/melt", shutil.which("melt") or ""):
        if c and Path(c).exists():
            return c
    return None


def pick_source(proj, explicit):
    """Return (video_path or None, audio_path, transcript_audio_path)."""
    if explicit:
        p = Path(explicit)
        p = p if p.is_absolute() else (proj / p if (proj / p).exists() else Path.cwd() / p)
        if not p.exists():
            raise SystemExit(f"Source not found: {explicit}")
        groups = {re.sub(r"_(prep|clean)$", "", p.stem): [p]}
    else:
        groups = {}
        for d in (proj / "footage", proj / "audio"):
            if not d.is_dir():
                continue
            for f in sorted(d.iterdir()):
                ext = f.suffix.lower()
                if not f.is_file() or ext not in VIDEO_EXT | AUDIO_EXT or f.stem.endswith("_cut"):
                    continue
                if d.name == "audio" and not f.stem.lower().startswith("voice"):
                    continue   # music, sfx
                groups.setdefault(re.sub(r"_(prep|clean)$", "", f.stem), []).append(f)
        if not groups:
            raise SystemExit(f"No recording found in {proj}/footage/ (or audio/voice.*). "
                             "Put your raw recording there, or pass --source.")
        if len(groups) > 1:
            names = "\n  ".join(str(fs[0].relative_to(proj)) for fs in groups.values())
            raise SystemExit("More than one recording found. Pick one with --source:\n  " + names)
    files = next(iter(groups.values()))
    stem = next(iter(groups))
    siblings = {f for f in files}
    for f in list(files):
        for cand in f.parent.glob(f"{stem}*"):
            if cand.suffix.lower() in VIDEO_EXT | AUDIO_EXT and not cand.stem.endswith("_cut"):
                siblings.add(cand)
    vids = [f for f in siblings if f.suffix.lower() in VIDEO_EXT]
    video = next((f for f in vids if f.stem.endswith("_prep")), None) or next((f for f in vids if f.stem == stem), None) \
        or (vids[0] if vids else None)
    clean = next((f for f in siblings if f.stem.endswith("_clean") and f.suffix.lower() in AUDIO_EXT), None)
    plain_audio = next((f for f in siblings if f.suffix.lower() in AUDIO_EXT and f != clean), None)
    audio = clean or video or plain_audio
    if audio is None:
        raise SystemExit("No usable audio in the recording.")
    if video and not probe(video)["video"]:
        video = None
    return video, audio


def transcribe(audio, outdir, rc, cfg):
    cache = outdir / "transcript.json"
    meta = outdir / "transcript.source"
    lang = rc.get("language") or cfg["subtitles"]["language"]
    stamp = f"{audio.resolve()}|{audio.stat().st_mtime_ns}|{lang}"
    if cache.exists() and meta.exists() and meta.read_text() == stamp:
        log(f"Using cached transcript: {cache}")
        return json.loads(cache.read_text())
    if not shutil.which("whisper"):
        raise SystemExit("Missing 'whisper'. Run tools/doctor.sh for install help.")
    model = rc.get("model") or cfg["subtitles"]["model"]
    log(f"Transcribing {audio.name} with Whisper (model={model} language={lang or 'auto'}). "
        "This takes about as long as the recording on a laptop.")
    tmp = outdir / "_whisper"
    tmp.mkdir(parents=True, exist_ok=True)
    cmd = ["whisper", str(audio), "--model", model, "--word_timestamps", "True",
           "--output_format", "json", "--output_dir", str(tmp), "--verbose", "False"]
    if lang:
        cmd += ["--language", lang]
    subprocess.run(cmd, check=True)
    data = json.loads((tmp / f"{audio.stem}.json").read_text())
    words = []
    for seg in data.get("segments", []):
        for w in seg.get("words", []):
            words.append({"w": w["word"].strip(), "s": float(w["start"]), "e": float(w["end"])})
    cache.write_text(json.dumps(words, ensure_ascii=False))
    meta.write_text(stamp)
    shutil.rmtree(tmp, ignore_errors=True)
    return words


# ---------------------------------------------------------------- alignment

def align(beats, words, rc):
    """Pick a take for each beat and classify the speech between them."""
    thr = rc["match_threshold"]
    # Token stream with a pointer back to the whisper word
    toks, owner = [], []
    for wi, w in enumerate(words):
        for t in norm_tokens(w["w"]):
            toks.append(t)
            owner.append(wi)
    btoks = [norm_tokens(b["text"]) for b in beats]
    horizon = rc.get("search_words", 400)

    # Whisper misspells names and non-English words ("Mayami", "pinanot"). Snap a transcript
    # word to the closest script word when they're nearly the same. Only used for matching.
    cutoff = rc.get("fuzzy_words", 0.8)
    vocab = sorted({t for bt in btoks for t in bt})
    known, snapped = set(vocab), {}

    def snap(t):
        if not cutoff or t in known or len(t) < 3:
            return t
        if t not in snapped:
            snapped[t] = (difflib.get_close_matches(t, vocab, 1, cutoff) or [t])[0]
        return snapped[t]

    toks = [snap(t) for t in toks]

    pos = 0
    for k, b in enumerate(beats):
        b["takes"], b["take"] = [], None
        takes = find_takes(btoks[k], toks, pos, pos + horizon + 4 * len(btoks[k]), thr)
        if not takes:
            continue
        nxt_start = None
        for m in range(k + 1, min(k + 3, len(beats))):
            t2 = find_takes(btoks[m], toks, takes[0].i + 1, takes[0].i + horizon, thr)
            if t2:
                nxt_start = t2[0].i
                break
        valid = [t for t in takes if nxt_start is None or t.i < nxt_start] or takes[:1]
        b["takes"] = valid
        b["take"] = valid[-1]
        pos = valid[-1].j

    # Convert token ranges to word ranges
    for b in beats:
        if b["take"]:
            b["w0"], b["w1"] = owner[b["take"].i], owner[b["take"].j - 1] + 1
            b["source"] = (words[b["w0"]]["s"], words[b["w1"] - 1]["e"])

    # Lines read in order: speech between two found lines that matches the missing line(s) between
    # them is that line, even if Whisper garbled it too much for the normal match. Flagged for a check.
    min_r = rc.get("infer_between", 0.4)
    if min_r:
        found_idx = [k for k, b in enumerate(beats) if b["take"]]
        for p_, n_ in zip([-1] + found_idx, found_idx + [len(beats)]):
            gap_beats = beats[p_ + 1:n_]
            if not gap_beats or p_ < 0 or n_ >= len(beats):
                continue
            a_w, z_w = beats[p_]["w1"], beats[n_]["w0"]
            if z_w <= a_w:
                continue
            utts = split_utterances(words, a_w, z_w, 0.45)
            ut = [[snap(t) for t in norm_tokens(" ".join(w["w"] for w in words[a:z]))] for a, z in utts]
            m, kb = len(utts), len(gap_beats)
            gt = [btoks[beats.index(b)] for b in gap_beats]
            # best[i][j]: best total score using utterances[i:] for gap_beats[j:]; each beat takes a run of utterances
            best = [[0.0] * (kb + 1) for _ in range(m + 1)]
            choice = [[None] * (kb + 1) for _ in range(m + 1)]
            for i in range(m - 1, -1, -1):
                for j in range(kb - 1, -1, -1):
                    opts = [(best[i + 1][j], ("skip_u",)), (best[i][j + 1], ("skip_b",))]
                    run = []
                    for e in range(i + 1, m + 1):
                        run = run + ut[e - 1]
                        r = ratio(gt[j], run)
                        if r >= min_r:
                            opts.append((r + best[e][j + 1], ("take", e, r)))
                    best[i][j], choice[i][j] = max(opts, key=lambda o: o[0])
            i = j = 0
            while i < m and j < kb:
                c = choice[i][j]
                if c[0] == "skip_u":
                    i += 1
                elif c[0] == "skip_b":
                    j += 1
                else:
                    b = gap_beats[j]
                    b["w0"], b["w1"] = utts[i][0], utts[c[1] - 1][1]
                    b["source"] = (words[b["w0"]]["s"], words[b["w1"] - 1]["e"])
                    b["take"] = Take(c[2], None, None)
                    b["takes"], b["inferred"] = [b["take"]], True
                    i, j = c[1], j + 1

    # Speech between consecutive chosen takes
    adlibs, dropped = [], []
    placed = [b for b in beats if b["take"]]
    bounds = [(0, None, placed[0] if placed else None)]
    bounds += [(placed[i]["w1"], placed[i], placed[i + 1] if i + 1 < len(placed) else None) for i in range(len(placed))]
    for start_w, prev, nxt in bounds:
        end_w = nxt["w0"] if nxt else len(words)
        if end_w <= start_w:
            continue
        utts = split_utterances(words, start_w, end_w, 0.45)
        started_retake = False
        attach = rc.get("attach_gap", 0.3)
        for n, (a, z) in enumerate(utts):
            text = " ".join(w["w"] for w in words[a:z])
            ut = norm_tokens(text)
            refs = [norm_tokens(x["text"]) for x in (prev, nxt) if x]
            is_retake = any(covered(ut, r) >= 0.6 for r in refs)
            content = [t for t in ut if t not in FILLERS]
            item = {"w0": a, "w1": z, "text": text, "s": words[a]["s"], "e": words[z - 1]["e"]}
            short = len(content) < rc["adlib_min_words"]
            # A short bit with no pause before/after a line is that line's first or last word(s),
            # misheard by Whisper (e.g. "Mayamipa" = "sa Miami pa"). Keep it with the line.
            if attach and short and not is_retake and not started_retake:
                # A longer pause is fine when the bit sounds like the line's last words (a beat before a punchline)
                tail = norm_tokens(prev["text"])[-len(ut):] if prev and ut else []
                sounds_like_tail = tail and ratio(" ".join(ut), " ".join(tail)) >= 0.6
                gap_prev = words[a]["s"] - words[prev["w1"] - 1]["e"] if prev else 99
                if prev and n == 0 and (gap_prev <= attach or (sounds_like_tail and gap_prev <= rc.get("attach_similar_gap", 1.0))):
                    prev["w1"] = z
                    prev["source"] = (prev["source"][0], words[z - 1]["e"])
                    continue
                if nxt and n == len(utts) - 1 and words[nxt["w0"]]["s"] - words[z - 1]["e"] <= attach:
                    nxt["w0"] = a
                    nxt["source"] = (words[a]["s"], nxt["source"][1])
                    continue
            if is_retake:
                started_retake = True
                dropped.append({**item, "why": "retake / false start"})
            elif started_retake:
                dropped.append({**item, "why": "between takes"})
            elif prev is None or nxt is None:
                dropped.append({**item, "why": "before the first line" if prev is None else "after the last line"})
            elif len(content) < rc["adlib_min_words"]:
                dropped.append({**item, "why": "filler"})
            elif rc["adlibs"] == "keep":
                adlibs.append({**item, "after_row": prev["row"]})
            else:
                dropped.append({**item, "why": "ad-lib (adlibs = drop)"})
    return adlibs, dropped


def split_utterances(words, a, z, gap):
    out, cur = [], a
    for i in range(a + 1, z):
        if words[i]["s"] - words[i - 1]["e"] > gap:
            out.append((cur, i))
            cur = i
    out.append((cur, z))
    return out


def loudness_envelope(audio):
    """Loudness in dB per 10 ms frame of the recording (for snapping cuts to quiet moments)."""
    import array
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    a = array.array("h")
    a.frombytes(raw[: len(raw) // 2 * 2])
    hop, env = 160, []
    for i in range(0, len(a) - hop, hop):
        seg = a[i:i + hop]
        env.append(20 * math.log10(math.sqrt(sum(x * x for x in seg) / hop) / 32768 + 1e-9))
    return env


def quietest(env, lo, hi):
    """Time (s) of the quietest 10 ms frame between lo and hi."""
    i, j = max(0, int(lo * 100)), min(len(env), int(hi * 100))
    return min(range(i, j), key=lambda k: env[k]) / 100 if j > i else lo


def voice_edge(env, t, limit, direction, rc):
    """Whisper sometimes skips words (often names) right at the edge of a line, so the line would start
    after them. From time t, walk outward (direction -1 = earlier, +1 = later) while there's voice in the
    recording, until a real pause (0.2 s of quiet) or limit. Returns the new edge time."""
    reach = rc.get("voice_extend", 1.5)
    if not env or not reach:
        return t
    if not hasattr(voice_edge, "thr") or voice_edge.env is not env:
        speech = sorted(env)[len(env) * 3 // 4]   # typical loudness while talking
        voice_edge.thr, voice_edge.env = speech - rc.get("voice_threshold_db", 20), env
    thr, k = voice_edge.thr, int(t * 100)
    stop = int((max(limit, t - reach) if direction < 0 else min(limit, t + reach)) * 100)
    quiet, last_voice = 0, k
    while 0 <= k < len(env) and (k > stop if direction < 0 else k < stop):
        k += direction
        if env[k] > thr:
            quiet, last_voice = 0, k
        else:
            quiet += 1
            if quiet >= 20:
                break
    edge = (last_voice + (0 if direction < 0 else 1)) / 100
    # Only move for real missed speech, not a breath right next to the word
    return edge if abs(edge - t) >= 0.25 else t


def missing_edges(script_text, words, w0, w1):
    """(head, tail): does the take lack the script line's first / last word? Then Whisper probably
    skipped it, and the line may grow into the voice next to it (see voice_edge)."""
    st = norm_tokens(script_text)
    got = [t for w in words[w0:w1] for t in norm_tokens(w["w"])]
    if not st or not got:
        return False, False
    near = lambda a, b: same_word(a, b) or ratio(a, b) >= 0.6  # noqa: E731
    head = not any(near(st[0], g) for g in got[:3])
    tail = not any(near(st[-1], g) for g in got[-3:])
    return head, tail


def pieces_for(words, w0, w1, rc, env=None, grow=(False, False)):
    """Source time ranges for words[w0:w1], with long internal pauses cut out.
    With env, each cut moves to the quietest moment nearby (Whisper word times are often
    0.1-0.2 s off, which cuts words mid-syllable), but never into the neighbouring word."""
    pad, max_pause = rc["pad"], rc["max_pause"]
    win = rc.get("snap_to_quiet", 0) if env else 0
    spans, a = [], w0
    for i in range(w0 + 1, w1):
        if max_pause and words[i]["s"] - words[i - 1]["e"] > max_pause:
            spans.append((a, i))
            a = i
    spans.append((a, w1))
    out = []
    for a, z in spans:
        s = words[a]["s"] - pad
        e = words[z - 1]["e"] + pad
        if a > 0:   # don't reach into the previous word
            s = max(s, (words[a - 1]["e"] + words[a]["s"]) / 2)
        if z < len(words):
            e = min(e, (words[z - 1]["e"] + words[z]["s"]) / 2)
        if win:
            lo = max(s - win, words[a - 1]["e"] if a > 0 else 0.0)
            hi = min(e + win, words[z]["s"] if z < len(words) else e + win)
            s = quietest(env, lo, s + 0.03) if lo < s + 0.03 else s
            e = quietest(env, e - 0.03, hi) if hi > e - 0.03 else e
        if env and a == w0 and grow[0]:
            s0 = voice_edge(env, words[a]["s"], words[a - 1]["e"] + 0.05 if a > 0 else 0.0, -1, rc)
            s = min(s, s0 - pad) if s0 < words[a]["s"] else s
        if env and z == w1 and grow[1]:
            e0 = voice_edge(env, words[z - 1]["e"], words[z]["s"] - 0.05 if z < len(words) else 1e9, 1, rc)
            e = max(e, e0 + pad) if e0 > words[z - 1]["e"] else e
        out.append((max(0.0, s), e, a, z))
    return out


# ---------------------------------------------------------------- sound effects

SFX_RE = re.compile(r'sfx:([\w-]+)\s+on\s+"([^"]+)"')


def place_sfx(cfg, beats, cue_frame, fps, total, rdir):
    """Sound-effect cues from the script -> clips on A3, plus notes for the report.

    Each library sound knows its anchor: "start" lands on the cue word (+offset, e.g. a whoosh starts
    early so it peaks on the word); "end" lands right after the cue words (punchline stingers)."""
    sc = cfg.get("sfx", {})
    sdir = Path(sc.get("dir", "sfx"))
    sdir = sdir if sdir.is_absolute() else Path(__file__).resolve().parent.parent / sdir
    lib_file = sdir / "library.json"
    cues = [(b, name, word) for b in beats for name, word in SFX_RE.findall((b.get("notes") or "") + " " + (b.get("see") or ""))]
    if not cues:
        return [], []
    if not lib_file.exists():
        return [], ["Sound-effect cues found but no library: run `python3 tools/sfx.py build`"]
    lib = json.loads(lib_file.read_text())
    out_dir = rdir / "sfx"
    out_dir.mkdir(exist_ok=True)
    placed, notes, rendered = [], [], {}
    for b, name, word in cues:
        s = lib.get(name)
        where = f"row {b['row']:02} ({name} on \"{word}\")"
        if not s:
            notes.append(f"Unknown sound `{name}` in {where}. See `python3 tools/sfx.py list`.")
            continue
        src = sdir / s["file"]
        if not src.exists():
            notes.append(f"Missing file for `{name}`: run `python3 tools/sfx.py build`.")
            continue
        if s.get("source") != "original" and not sc.get("allow_unknown_rights", True):
            notes.append(f"Skipped `{name}` in {where}: rights unknown ([sfx].allow_unknown_rights = false).")
            continue
        f = cue_frame(word, b, end=s.get("anchor") == "end")
        if f is None:
            notes.append(f"Couldn't find \"{word}\" in the recording for {where}. Not placed.")
            continue
        pos = max(0, f + round(s.get("offset", 0) * fps))
        if name not in rendered:
            dst = out_dir / f"{name}.wav"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"volume={sc.get('level_db', -10)}dB",
                            "-ar", "48000", "-ac", "2", str(dst)], check=True)
            rendered[name] = (dst, max(1, round(media_seconds(dst) * fps)))
        dst, frames = rendered[name]
        placed.append({"name": name, "row": b["row"], "word": word, "pos": pos, "file": dst, "frames": frames,
                       "len": min(frames, total - pos), "mood": s.get("mood", ""), "source": s.get("source", "")})
    placed = [p for p in sorted(placed, key=lambda p: p["pos"]) if p["len"] > 0]
    for i in range(len(placed) - 1):   # one track: a sound can't run into the next one
        placed[i]["len"] = max(1, min(placed[i]["len"], placed[i + 1]["pos"] - placed[i]["pos"]))
    return placed, notes


def sfx_report(sfx, notes, cfg, fps, total):
    """Report lines: every sound, plus the "just right" checks (spacing, rate, comedic stingers)."""
    sc = cfg.get("sfx", {})
    if not sfx and not notes:
        return []
    L = ["", "## Sound effects on A3", ""]
    L += [f"- {mmss(p['pos'] / fps)}: `{p['name']}` on \"{p['word']}\" (row {p['row']:02})"
          + ("  ⚠ rights unknown" if p["source"] not in ("original", "") else "") for p in sfx]
    minutes = total / fps / 60
    rate = len(sfx) / minutes if minutes else 0
    lo, hi = sc.get("min_per_minute", 4), sc.get("max_per_minute", 10)
    checks = [f"**{len(sfx)} sounds, {rate:.1f} per minute** (aim for {lo}–{hi})"
              + (": too few, the edit may feel flat" if rate < lo else ": too many, they'll get annoying" if rate > hi else ": good")]
    gap = sc.get("min_gap_seconds", 2.5) * fps
    close = [(a, b) for a, b in zip(sfx, sfx[1:]) if b["pos"] - a["pos"] < gap]
    checks += [f"Too close ({(b['pos'] - a['pos']) / fps:.1f}s): `{a['name']}` row {a['row']:02} → `{b['name']}` row {b['row']:02}"
               for a, b in close]
    com = [p for p in sfx if p["mood"] == "comedic"]
    cgap = sc.get("comedic_min_gap_seconds", 15) * fps
    checks += [f"Comedic stingers too close: `{a['name']}` row {a['row']:02} and `{b['name']}` row {b['row']:02} "
               f"({(b['pos'] - a['pos']) / fps:.0f}s apart). Jokes land better when the sound is rare."
               for a, b in zip(com, com[1:]) if b["pos"] - a["pos"] < cgap]
    names = [p["name"] for p in sfx]
    for n in sorted(set(names)):
        if n in ("rimshot", "sad-trombone") and names.count(n) > 2:
            checks.append(f"`{n}` used {names.count(n)} times: it stops being funny after twice")
    unknown = [p for p in sfx if p["source"] not in ("original", "")]
    if unknown:
        checks.append(f"{len(unknown)} sound(s) from Myinstants (rights unknown): check they aren't clips from a movie, show, "
                      "song or creator before monetizing. See `sfx/LICENSES.md`.")
    return L + ["", "**Checks:**", ""] + [f"- {c}" for c in checks + notes]


# ---------------------------------------------------------------- materials

ROW_RE = re.compile(r"^(\d{1,3})(?:[-_ .]|$)")
ANY_RE = re.compile(r"^any(?:[-_ ]|$)", re.I)


def scan_materials(proj, places, tag="placeholder-", graphics_dir="graphics"):
    """Row materials. A placeholder (`NN-placeholder-what.png`) is skipped as soon as its
    replacement (`NN-what.<any ext>`, in the graphics folder or footage/broll/) exists."""
    found = []
    for d, kind in ((proj / graphics_dir, "graphic"), (proj / "footage" / "broll", "broll")):
        if not d.is_dir():
            continue
        for f in sorted(d.iterdir()):
            ext = f.suffix.lower()
            if not f.is_file() or ext not in IMAGE_EXT | VIDEO_EXT:
                continue
            m = ROW_RE.match(f.name)
            row = places.get(f.name)
            if row is None and m:
                row = int(m.group(1))
            if row is None and not ANY_RE.match(f.name):
                continue   # thumbnail photos etc.
            found.append({"path": f, "row": row, "kind": "image" if ext in IMAGE_EXT else "video", "name": f.name})
    if not tag:
        return found
    real = {m["path"].stem for m in found if tag not in m["path"].stem}
    out = []
    for m in found:
        pm = re.match(rf"^(\d{{1,3}}(?:-\d+)?-){re.escape(tag)}(.+)$", m["path"].stem)
        if pm:
            if pm.group(1) + pm.group(2) in real:
                continue   # replaced by the real asset
            m["placeholder"] = pm.group(1) + pm.group(2)
        out.append(m)
    return out


# ---------------------------------------------------------------- Kdenlive / MLT XML

class Mlt:
    def __init__(self, fps, root):
        self.fps, self.root, self.parts, self.n = fps, root, [], 0
        self.bin = []          # (xml id, kdenlive id, folder id)
        self.next_kid = 2

    def nid(self, prefix):
        self.n += 1
        return f"{prefix}{self.n}"

    def tc(self, frames):
        # Kdenlive writes clock times; MLT rounds them back to the same frame
        ms = round(frames * 1000 / self.fps)
        h, ms = divmod(ms, 3_600_000)
        m, ms = divmod(ms, 60_000)
        s, ms = divmod(ms, 1000)
        return f"{h:02}:{m:02}:{s:02}.{ms:03}"

    def rel(self, path):
        try:
            return str(Path(path).resolve().relative_to(self.root))
        except ValueError:
            return str(Path(path).resolve())

    def props(self, d, indent=4):
        sp = " " * indent
        return "\n".join(f"{sp}<property name={quoteattr(k)}>{escape(str(v))}</property>" for k, v in d.items())

    def element(self, tag, xid, props, attrs=""):
        self.parts.append(f'  <{tag} id="{xid}"{attrs}>\n{self.props(props)}\n  </{tag}>')
        return xid


def build_project(proj, out_path, fps, size, timeline, overlays, music, guides, title, sfx, guide_names):
    w, h = size
    total = timeline["frames"]
    x = Mlt(fps, proj.resolve())

    def bin_clip(path, kind, length, folder):
        kid = x.next_kid
        x.next_kid += 1
        props = media_props(path, kind, length)
        props.update({"kdenlive:id": kid, "kdenlive:clipname": Path(path).name, "kdenlive:folderid": folder})
        xid = x.element("producer" if kind == "image" else "chain", x.nid("bin"), props)
        x.bin.append(xid)
        return kid

    def media_props(path, kind, length):
        if kind == "image":
            return {"length": length, "eof": "pause", "resource": x.rel(path), "ttl": 25, "aspect_ratio": 1,
                    "meta.media.progressive": 1, "seekable": 1, "mlt_service": "qimage",
                    "kdenlive:duration": x.tc(length), "kdenlive:clip_type": 2}
        # No "length" here: on avformat chains it silences the audio when melt renders
        props = {"eof": "pause", "resource": x.rel(path), "mlt_service": "avformat-novalidate",
                 "seekable": 1, "kdenlive:clip_type": {"av": 0, "audio": 1, "video": 2}.get(kind, 0)}
        # vstream/astream count streams of that type (0 = first), unlike the absolute *_index
        if kind != "audio":
            props["vstream"] = 0
        if kind in ("av", "audio"):
            props["astream"] = 0
        if kind == "video":
            props["audio_index"] = -1
        if kind == "audio":
            props["video_index"] = -1
        return props

    def track_instance(path, kind, length, kid, part):
        props = media_props(path, kind, length)
        if kind != "image":
            props["set.test_audio"] = 0 if part == "audio" else 1
            props["set.test_video"] = 1 if part == "audio" else 0
        props["kdenlive:id"] = kid
        return x.element("producer" if kind == "image" else "chain", x.nid("producer" if kind == "image" else "chain"), props)

    folders = {"-1.10": "Recording", "-1.11": "Graphics", "-1.12": "B-roll", "-1.13": "Unplaced B-roll", "-1.14": "Music",
               "-1.15": "Sound effects"}

    # Black background track
    x.element("producer", "black_track", {"length": total, "eof": "continue", "resource": "black",
                                          "aspect_ratio": 1, "mlt_service": "color",
                                          "kdenlive:playlistid": "black_track", "mlt_image_format": "rgba",
                                          "set.test_audio": 0})

    def playlist(entries, audio, name_extra=None):
        pid = x.nid("playlist")
        body = []
        if audio:
            body.append('    <property name="kdenlive:audio_track">1</property>')
        cur = 0
        for e in entries:
            if e["pos"] > cur:
                body.append(f'    <blank length="{x.tc(e["pos"] - cur)}"/>')
            body.append(f'    <entry producer="{e["producer"]}" in="{x.tc(e["in"])}" out="{x.tc(e["out"])}">\n'
                        f'      <property name="kdenlive:id">{e["kid"]}</property>\n    </entry>')
            cur = e["pos"] + (e["out"] - e["in"] + 1)
        x.parts.append(f'  <playlist id="{pid}">\n' + "\n".join(body) + "\n  </playlist>" if body
                       else f'  <playlist id="{pid}"/>')
        return pid

    def track(name, entries, audio):
        p1 = playlist(entries, audio)
        p2 = playlist([], audio)
        tid = x.nid("tractor")
        hide = "video" if audio else "audio"
        extra = '\n    <property name="kdenlive:audio_track">1</property>' if audio else ""
        x.parts.append(f'  <tractor id="{tid}" in="{x.tc(0)}" out="{x.tc(total - 1)}">\n'
                       f'    <property name="kdenlive:track_name">{escape(name)}</property>{extra}\n'
                       f'    <property name="kdenlive:trackheight">69</property>\n'
                       f'    <property name="kdenlive:timeline_active">1</property>\n'
                       f'    <track hide="{hide}" producer="{p1}"/>\n    <track hide="{hide}" producer="{p2}"/>\n  </tractor>')
        return tid

    # --- recording (V1 + A1)
    rec = timeline["source"]
    a_src = timeline["audio"]
    rec_len = timeline["source_frames"]
    v_entries, a_entries = [], []
    if rec:
        kid_v = bin_clip(rec, "av" if a_src == rec else "video", rec_len, "10")
        inst_v = track_instance(rec, "av", rec_len, kid_v, "video")
    if a_src != rec:
        a_len = timeline["audio_frames"]
        kid_a = bin_clip(a_src, "audio", a_len, "10")
        inst_a = track_instance(a_src, "audio", a_len, kid_a, "audio")
    else:
        kid_a = kid_v
        inst_a = track_instance(rec, "av", rec_len, kid_v, "audio")
    for c in timeline["clips"]:
        if rec:
            v_entries.append({"producer": inst_v, "kid": kid_v, "pos": c["pos"], "in": c["in"], "out": c["out"]})
        a_entries.append({"producer": inst_a, "kid": kid_a, "pos": c["pos"], "in": c["in"], "out": c["out"]})

    # --- overlays (V2)
    o_entries = []
    for o in overlays:
        kind = o["kind"]
        length = o["src_frames"] if kind == "video" else max(o["dur"], round(5 * fps))
        kid = bin_clip(o["path"], "image" if kind == "image" else "video", length, "11" if kind == "image" else "12")
        inst = track_instance(o["path"], "image" if kind == "image" else "video", length, kid, "video")
        o_entries.append({"producer": inst, "kid": kid, "pos": o["pos"], "in": 0, "out": o["dur"] - 1})
    for u in timeline["unplaced"]:
        if u["kind"] == "video":
            bin_clip(u["path"], "video", u["src_frames"], "13")
        else:
            bin_clip(u["path"], "image", round(5 * fps), "13")

    # --- music (A2)
    m_entries = []
    if music:
        kid = bin_clip(music, "audio", total, "14")
        inst = track_instance(music, "audio", total, kid, "audio")
        m_entries.append({"producer": inst, "kid": kid, "pos": 0, "in": 0, "out": total - 1})

    # --- sound effects (A3)
    s_entries, sfx_kids = [], {}
    for e in sfx:
        if e["file"] not in sfx_kids:
            kid = bin_clip(e["file"], "audio", e["frames"], "15")
            sfx_kids[e["file"]] = (kid, track_instance(e["file"], "audio", e["frames"], kid, "audio"))
        kid, inst = sfx_kids[e["file"]]
        s_entries.append({"producer": inst, "kid": kid, "pos": e["pos"], "in": 0, "out": e["len"] - 1})

    # Track order = bottom audio first, then video upward (how Kdenlive saves it)
    audio_tracks = ([track("Sound effects", s_entries, True)] if s_entries else []) + \
        [track("Music", m_entries, True), track("Voice", a_entries, True)]
    n_audio = len(audio_tracks)
    tracks = audio_tracks + [track("Recording", v_entries, False), track("Graphics", o_entries, False)]

    # Sequence
    seq = "{" + str(uuid.uuid4()) + "}"
    trans = []
    for i, t in enumerate(tracks, start=1):
        if i <= n_audio:
            trans.append({"a_track": 0, "b_track": i, "mlt_service": "mix", "kdenlive_id": "mix",
                          "internal_added": 237, "always_active": 1, "accepts_blanks": 1, "sum": 1})
        else:
            trans.append({"a_track": 0, "b_track": i, "version": "0.1", "mlt_service": "frei0r.cairoblend",
                          "kdenlive_id": "frei0r.cairoblend", "internal_added": 237, "always_active": 1})
    groups = []
    for c in timeline["clips"]:
        if rec:
            groups.append({"children": [{"data": f"{n_audio - 1}:{c['pos']}", "leaf": "clip", "type": "Leaf"},
                                        {"data": f"{n_audio}:{c['pos']}", "leaf": "clip", "type": "Leaf"}],
                           "type": "AVSplit" if a_src == rec else "Normal"})
    seq_props = {
        "kdenlive:uuid": seq, "kdenlive:clipname": title, "kdenlive:duration": x.tc(total),
        "kdenlive:producer_type": 17, "kdenlive:id": 1, "kdenlive:clip_type": 0,
        "kdenlive:sequenceproperties.groups": json.dumps(groups, indent=1),
        "kdenlive:sequenceproperties.guides": json.dumps(guides, ensure_ascii=False, indent=1),
        "kdenlive:sequenceproperties.hasAudio": 1, "kdenlive:sequenceproperties.hasVideo": 1,
        "kdenlive:sequenceproperties.tracksCount": len(tracks), "kdenlive:sequenceproperties.activeTrack": n_audio,
        "kdenlive:sequenceproperties.zoom": 8, "kdenlive:sequenceproperties.position": 0,
    }
    tr_xml = "\n".join(
        f'    <transition id="{x.nid("transition")}">\n{x.props(t, 6)}\n    </transition>' for t in trans)
    x.parts.append(f'  <tractor id="{seq}" in="{x.tc(0)}" out="{x.tc(total - 1)}">\n{x.props(seq_props)}\n'
                   '    <track producer="black_track"/>\n'
                   + "\n".join(f'    <track producer="{t}"/>' for t in tracks) + "\n" + tr_xml + "\n  </tractor>")

    folder_props = {f"kdenlive:folder.{k}": v for k, v in folders.items()}
    colors = ["#9b59b6", "#3daee9", "#1abc9c", "#1cdc9a", "#c9ce3b", "#fdbc4b", "#f39c1f", "#f47750", "#da4453"]
    names = {v: k for k, v in guide_names.items()}
    categories = [{"color": c, "comment": names.get(i, f"Category {i + 1}"), "index": i} for i, c in enumerate(colors)]
    main_bin = {
        "kdenlive:docproperties.uuid": seq, "kdenlive:docproperties.version": "1.1",
        "kdenlive:docproperties.activetimeline": seq, "kdenlive:docproperties.opensequences": seq,
        "kdenlive:docproperties.profile": f"atsc_{h}p_{int(fps)}" if (w, h) == (1920, 1080) else "",
        "kdenlive:docproperties.seekOffset": 30000, "xml_retain": 1, **folder_props,
        "kdenlive:docproperties.guidesCategories": json.dumps(categories, indent=1),
    }
    entries = [f'    <entry producer="{seq}" in="{x.tc(0)}" out="{x.tc(total - 1)}"/>'] + \
              [f'    <entry producer="{b}" in="{x.tc(0)}"/>' for b in x.bin]
    x.parts.append(f'  <playlist id="main_bin">\n{x.props(main_bin)}\n' + "\n".join(entries) + "\n  </playlist>")
    x.parts.append(f'  <tractor id="{x.nid("tractor")}" in="{x.tc(0)}" out="{x.tc(total - 1)}">\n'
                   '    <property name="kdenlive:projectTractor">1</property>\n'
                   f'    <track producer="{seq}" in="{x.tc(0)}" out="{x.tc(total - 1)}"/>\n  </tractor>')

    fr = fps_fraction(fps)
    dar = (16, 9) if w * 9 == h * 16 else ((9, 16) if w * 16 == h * 9 else (w, h))
    head = ("<?xml version='1.0' encoding='utf-8'?>\n"
            f'<mlt LC_NUMERIC="C" version="7.22.0" producer="main_bin" root={quoteattr(str(proj.resolve()))}>\n'
            f'  <profile description="{w}x{h} {fps:g}fps" width="{w}" height="{h}" progressive="1" '
            f'sample_aspect_num="1" sample_aspect_den="1" display_aspect_num="{dar[0]}" display_aspect_den="{dar[1]}" '
            f'frame_rate_num="{fr[0]}" frame_rate_den="{fr[1]}" colorspace="709"/>\n')
    out_path.write_text(head + "\n".join(x.parts) + "\n</mlt>\n", encoding="utf-8")


def fps_fraction(fps):
    for num, den in ((24000, 1001), (30000, 1001), (60000, 1001)):
        if abs(fps - num / den) < 0.01:
            return num, den
    return round(fps), 1


# ---------------------------------------------------------------- outputs

def s_to_srt(t):
    ms = max(0, round(t * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def mmss(t):
    t = round(t, 1)   # so 59.96 shows as 1:00.0, not 0:60.0
    return f"{int(t // 60)}:{t % 60:04.1f}"


def write_srt(path, words, clips, fps, width, lines):
    """Captions on the cut timeline, built from the words that survived the cut."""
    timed = []
    for c in clips:
        off = c["pos"] / fps - c["in"] / fps
        for w in words[c["w0"]:c["w1"]]:
            timed.append((w["s"] + off, w["e"] + off, w["w"]))
    cues, cur = [], []
    limit = width * lines
    for i, (s, e, t) in enumerate(timed):
        text = " ".join(x[2] for x in cur + [(s, e, t)])
        gap = cur and s - cur[-1][1] > 0.6
        if cur and (len(text) > limit or gap):
            cues.append(cur)
            cur = []
        cur.append((s, e, t))
        if re.search(r"[.?!]$", t):
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)
    out = []
    for n, cue in enumerate(cues, 1):
        text = " ".join(x[2] for x in cue)
        if len(text) > width and lines > 1:
            words_ = text.split()
            best = min(range(1, len(words_)), key=lambda k: abs(len(" ".join(words_[:k])) - len(text) / 2), default=1)
            text = " ".join(words_[:best]) + "\n" + " ".join(words_[best:])
        out.append(f"{n}\n{s_to_srt(cue[0][0])} --> {s_to_srt(cue[-1][1])}\n{text}\n")
    path.write_text("\n".join(out), encoding="utf-8")


def music_bed(src, dst, seconds, rc):
    fade = rc["music_fade_seconds"]
    af = f"volume={rc['music_level_db']}dB"
    if fade > 0 and seconds > fade:
        af += f",afade=t=out:st={seconds - fade:.3f}:d={fade}"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{seconds:.3f}",
                    "-af", af, "-ar", "48000", "-ac", "2", str(dst)], check=True)


def media_seconds(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def render_preview(melt, kdenlive, out, total, fps, height, size):
    """Render with Kdenlive's own engine (melt). melt sometimes keeps running after
    the last frame without finishing the file; an interrupt makes it finalize."""
    import signal
    import time
    w, h = size
    pw = round(w * height / h / 2) * 2
    log(f"Rendering preview with Kdenlive's engine ({total / fps:.0f}s of video)...")
    errlog = out.with_suffix(".log")
    last = total - 1
    with open(errlog, "w") as err:
        proc = subprocess.Popen([melt, str(kdenlive), f"out={last}", "-consumer", f"avformat:{out}",
                                 f"width={pw}", f"height={height}",
                                 # Square pixels; otherwise melt falls back to a 16:15 (PAL) shape and pillarboxes
                                 "sample_aspect_num=1", "sample_aspect_den=1",
                                 f"display_aspect_num={pw}", f"display_aspect_den={height}",
                                 # Without these melt writes 25 fps and drops frames when it falls behind
                                 f"frame_rate_num={fps_fraction(fps)[0]}", f"frame_rate_den={fps_fraction(fps)[1]}",
                                 "real_time=-1", "vcodec=libx264", "preset=veryfast", "crf=26",
                                 "acodec=aac", "ab=128k", "terminate_on_pause=1"],
                                stdin=subprocess.DEVNULL, stdout=err, stderr=err)
        want, deadline = total / fps - 0.2, time.time() + max(180, 30 * total / fps)
        done_at = None
        while proc.poll() is None and time.time() < deadline:
            time.sleep(1)
            if done_at is None:
                tail = errlog.read_bytes()[-200:].decode(errors="ignore")
                frames = re.findall(r"Current Frame:\s+(\d+)", tail)
                if frames and int(frames[-1]) >= last:
                    done_at = time.time()
            elif time.time() - done_at > 2:
                proc.send_signal(signal.SIGINT)
                try:
                    proc.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    pass
                break
        if proc.poll() is None:
            proc.kill()
        proc.wait()
    if not out.exists() or media_seconds(out) < want:
        log(f"Preview render failed (the .kdenlive file is still fine to open). See {errlog}")
        return False
    errlog.unlink(missing_ok=True)
    return True


# ---------------------------------------------------------------- main

def main():
    cfg = load()
    rc = cfg["rough_cut"]
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("project", help="project folder (contains script.md)")
    p.add_argument("--script", help="script file (default: <project>/script.md)")
    p.add_argument("--source", help="recording to use (default: the one in footage/)")
    p.add_argument("--place", action="append", default=[], metavar="FILE=ROW",
                   help="put a material on a script row, e.g. any-server-room.mp4=07 (repeatable)")
    p.add_argument("--threshold", type=float, help=f"line match strictness 0-1 (default {rc['match_threshold']})")
    p.add_argument("--adlibs", choices=["keep", "drop"], help=f"default {rc['adlibs']}")
    p.add_argument("--language", help="Whisper language code for this video, e.g. tl or en "
                   "(default: [rough_cut].language, then [subtitles].language, then auto)")
    p.add_argument("--graphic-seconds", type=float, help="longest a graphic stays on screen, 0 = until the next "
                   "one (default: the style's graphic_seconds, then [rough_cut].max_graphic_seconds)")
    p.add_argument("--graphics", help="graphics folder inside the project (default: [rough_cut].graphics_dir, "
                   "usually graphics). Use another folder for a second version, e.g. graphics/v3")
    p.add_argument("--name", help="output name: <folder>-<name>.kdenlive (default: roughcut). Use a new name "
                   "to keep an earlier version, e.g. --name faceless. Its report, captions and preview go to "
                   "roughcut/<name>/")
    p.add_argument("--no-music", action="store_true")
    p.add_argument("--no-preview", action="store_true")
    p.add_argument("--retranscribe", action="store_true", help="ignore the cached transcript")
    p.add_argument("--force", action="store_true", help="overwrite an existing rough cut .kdenlive")
    a = p.parse_args()
    if a.threshold is not None:
        rc["match_threshold"] = a.threshold
    if a.adlibs:
        rc["adlibs"] = a.adlibs

    proj = Path(a.project).resolve()
    script = Path(a.script).resolve() if a.script else proj / "script.md"
    if a.script and not script.exists() and (proj / a.script).exists():
        script = proj / a.script   # a script name inside the project folder
    if not script.exists():
        raise SystemExit(f"No script at {script}. Pass --script.")
    md = script.read_text(encoding="utf-8")
    beats = extract(md)
    if not beats:
        raise SystemExit("The script has no narration yet (Hear column / Voiceover lines are empty).")

    # Timeline format from the script's style
    styles = load_styles()
    sm = re.search(r"\(`([\w-]+)`\)", md)
    style = styles.get(sm.group(1), {}) if sm else {}
    # A style can carry its own [rough_cut] settings (e.g. tighter pauses); command-line flags still win.
    for k, v in style.get("rough_cut", {}).items():
        if not (k == "match_threshold" and a.threshold is not None) and not (k == "adlibs" and a.adlibs):
            rc[k] = v
    video, audio = pick_source(proj, a.source)
    if not rc.get("use_video", True):
        video = None   # faceless: keep the recording's audio, black background instead of the camera
    pv = probe(video) if video else None
    if style.get("resolution"):
        size = tuple(int(v) for v in style["resolution"].lower().split("x"))
    elif pv and pv["width"]:
        size = (pv["width"], pv["height"])
    else:
        size = (1920, 1080)
    fps = float(style.get("fps") or 30)
    # Talking-head styles want the camera back between graphics; faceless ones hold each graphic.
    max_graphic = next(v for v in (a.graphic_seconds, style.get("graphic_seconds"),
                                   rc.get("max_graphic_seconds", 0)) if v is not None)

    outdir = proj / "roughcut"
    outdir.mkdir(exist_ok=True)
    # The transcript cache is shared; a named version keeps its own report, captions and preview
    rdir = outdir / a.name if a.name and a.name != "roughcut" else outdir
    rdir.mkdir(exist_ok=True)
    kd = proj / f"{proj.name}-{a.name or 'roughcut'}.kdenlive"
    if kd.exists() and not a.force:
        raise SystemExit(f"{kd.relative_to(proj.parent)} exists. Use --force to rebuild it "
                         "(save your own edits under a different name first).")

    log(f"Recording: {video.relative_to(proj) if video else '(none, voice only)'}"
        + (f" | voice: {audio.relative_to(proj)}" if audio != video else ""))
    if a.retranscribe:
        (outdir / "transcript.source").unlink(missing_ok=True)
    if a.language:
        rc["language"] = a.language
    words = transcribe(audio, outdir, rc, cfg)
    if not words:
        raise SystemExit("Whisper didn't hear any speech in the recording.")

    adlibs, dropped = align(beats, words, rc)
    found = [b for b in beats if b["take"]]
    if not found:
        raise SystemExit("Couldn't match any script line to the recording. Is it the right script? "
                         "Try --threshold 0.6.")

    # Segments in source order: chosen takes + kept ad-libs
    segs = [{"w0": b["w0"], "w1": b["w1"], "beat": b} for b in found]
    segs += [{"w0": x["w0"], "w1": x["w1"], "adlib": x} for x in adlibs]
    segs.sort(key=lambda s: s["w0"])

    src_dur = probe(audio)["duration"]
    src_frames = round((pv["duration"] if pv else src_dur) * fps)
    env = loudness_envelope(audio) if rc.get("snap_to_quiet") else None
    clips, pos = [], 0
    for s in segs:
        s["pos0"] = pos
        grow = missing_edges(s["beat"]["text"], words, s["w0"], s["w1"]) if "beat" in s else (False, False)
        for (ts, te, w0, w1) in pieces_for(words, s["w0"], s["w1"], rc, env, grow):
            fin, fout = round(ts * fps), min(round(te * fps) - 1, src_frames - 1)
            if fout < fin:
                continue
            clips.append({"pos": pos, "in": fin, "out": fout, "w0": w0, "w1": w1})
            pos += fout - fin + 1
        s["pos1"] = pos
        if "beat" in s:
            s["beat"]["t0"], s["beat"]["t1"] = s["pos0"], s["pos1"]
        else:
            s["adlib"]["t0"] = s["pos0"]
    total = pos

    def cue_frame(cue, b, end=False):
        """Timeline frame where the cue words are spoken inside beat b (end=True: where they finish), or None."""
        want = " ".join(norm_tokens(cue))
        n = max(1, len(want.split()))
        best = (0.0, None)
        for k in range(b["w0"], b["w1"]):
            got = " ".join(t for w in words[k:k + n] for t in norm_tokens(w["w"]))
            r = difflib.SequenceMatcher(None, want, got).ratio()
            if r > best[0]:
                best = (r, k)
        if best[0] < 0.6:
            return None
        k = best[1]
        if end:
            k = min(k + n - 1, b["w1"] - 1)
        t = words[k]["e"] if end else words[k]["s"]
        for c in clips:
            if c["w0"] <= k < c["w1"]:
                return min(c["pos"] + (c["out"] - c["in"]), max(c["pos"], c["pos"] + round(t * fps) - c["in"]))
        return None

    # Materials -> V2
    places = {}
    for item in a.place:
        if "=" not in item:
            raise SystemExit(f"--place needs FILE=ROW, got {item}")
        f, r = item.rsplit("=", 1)
        places[Path(f).name] = int(r)
    gdir = a.graphics or rc.get("graphics_dir", "graphics")
    if not (proj / gdir).is_dir():
        raise SystemExit(f"No graphics folder at {proj / gdir}")
    mats = scan_materials(proj, places, rc.get("placeholder_tag", "placeholder-"), gdir)
    by_row = {}
    unplaced = []
    for m in mats:
        if m["kind"] == "video":
            m["src_frames"] = max(1, round(probe(m["path"])["duration"] * fps))
        (by_row.setdefault(m["row"], []).append(m) if m["row"] is not None else unplaced.append(m))
    beat_rows = sorted(b["row"] for b in found)
    row_beat = {b["row"]: b for b in found}
    notes = []
    overlays = []
    min_f = round(rc["min_graphic_seconds"] * fps)
    for row in sorted(by_row):
        items = by_row[row]
        b = row_beat.get(row)
        if b:
            start, end = b["t0"], b["t1"]
        else:
            later = [r for r in beat_rows if r > row]
            earlier = [r for r in beat_rows if r < row]
            start = row_beat[later[0]]["t0"] if later else max(0, total - min_f)
            end = start + min_f
            # Unmatched speech sits between the neighbouring found lines: use that gap if there is one
            if earlier and later and row_beat[later[0]]["t0"] - row_beat[earlier[-1]]["t1"] >= min_f:
                start, end = row_beat[earlier[-1]]["t1"], row_beat[later[0]]["t0"]
            why = "not spoken in the recording" if any(x["row"] == row for x in beats) else "no voiceover on that row"
            notes.append(f"Row {row:02} ({', '.join(i['name'] for i in items)}): {why}, placed at {mmss(start / fps)} for "
                         f"{rc['min_graphic_seconds']}s. Check it.")
        span = max(end - start, min_f * len(items))
        each = span // len(items)
        # Default: share the row evenly. A cue in the See column (`file.png` ... on "word") puts
        # that file exactly where the word is spoken.
        starts = [start + n * each for n in range(len(items))]
        if b and b.get("see"):
            cues = dict(re.findall(r'`([^`]+)`[^`]*?\bon "([^"]+)"', b["see"]))
            cued = [cue_frame(cues[it["name"]], b) if it["name"] in cues else None for it in items]
            # Use the cues only when every cued file was found and they stay apart; else split evenly
            if any(it["name"] in cues for it in items) and all(
                    f is not None for it, f in zip(items, cued) if it["name"] in cues):
                trial = [f if f is not None else s0 for f, s0 in zip(cued, starts)]
                order = sorted(range(len(items)), key=lambda n: trial[n])
                trial_sorted = [trial[n] for n in order]
                if all(y - x >= min_f for x, y in zip(trial_sorted, trial_sorted[1:])):
                    items, starts = [items[n] for n in order], trial_sorted
        row_end = start + span
        for n, it in enumerate(items):
            s0 = starts[n]
            dur = (starts[n + 1] if n < len(items) - 1 else row_end) - s0
            if it["kind"] == "video":
                dur = min(dur, it["src_frames"])
            if max_graphic:
                dur = min(dur, round(max_graphic * fps))
            overlays.append({**it, "pos": s0, "dur": max(1, dur)})
    overlays.sort(key=lambda o: (o["pos"], o["row"]))
    # Every overlay gets at least min_graphic_seconds: push the next one later if needed
    for i in range(len(overlays) - 1):
        o, n = overlays[i], overlays[i + 1]
        floor = o["pos"] + min(min_f, o["dur"])
        if n["pos"] < floor:
            shift = floor - n["pos"]
            n["pos"] += shift
            n["dur"] = max(1, n["dur"] - shift)
    gap_fill = round(rc["fill_gaps_under"] * fps)
    for i, o in enumerate(overlays):
        if o["pos"] >= total:
            o["pos"], o["dur"] = max(0, total - min_f), min_f
        nxt = overlays[i + 1]["pos"] if i + 1 < len(overlays) else total
        end = o["pos"] + o["dur"]
        if end > nxt:
            o["dur"] = max(1, nxt - o["pos"])
        elif nxt - end <= gap_fill and o["kind"] == "image":
            o["dur"] = nxt - o["pos"]   # hold the graphic instead of flashing back to V1
        o["dur"] = min(o["dur"], total - o["pos"])
    overlays = [o for o in overlays if o["dur"] > 0]

    # Sound effects -> A3: `sfx:<name> on "word"` in a row's Notes (or See) column
    sfx, sfx_notes = place_sfx(cfg, found, cue_frame, fps, total, rdir)
    # A stinger after the last line needs a moment to play: hold the last graphic and let it finish
    need = max((p["pos"] + p["frames"] for p in sfx), default=0) - total
    tail = min(max(0, need), round(rc.get("stinger_tail_max", 3.0) * fps))
    if tail:
        total += tail
        for p in sfx:
            p["len"] = min(p["frames"], total - p["pos"])
        if overlays and overlays[-1]["kind"] == "image":
            overlays[-1]["dur"] = total - overlays[-1]["pos"]
        sfx_notes.append(f"Added {tail / fps:.1f}s at the end so the last sound effect can finish.")

    # Music -> A2 (pre-mixed bed: looped, lowered, faded)
    music = None
    if not a.no_music and rc["music"]:
        cands = sorted(f for f in (proj / "audio").glob("music*") if f.suffix.lower() in AUDIO_EXT) \
            if (proj / "audio").is_dir() else []
        if cands:
            music = rdir / "music-bed.wav"
            music_bed(cands[0], music, total / fps, rc)
            log(f"Music: {cands[0].name} (looped, {rc['music_level_db']} dB, fade out)")

    # Guides
    guides, last_sec = [], object()
    cat = rc["guide_categories"]
    for b in beats:
        if b["take"] and b["section"] != last_sec:
            guides.append({"comment": b["section"] or "Section", "pos": b["t0"], "type": cat["section"]})
            last_sec = b["section"]
    for x in adlibs:
        guides.append({"comment": f"Ad-lib (not in script): {x['text'][:60]}  keep?", "pos": x["t0"], "type": cat["adlib"]})
    for b in beats:
        if not b["take"]:
            later = [o["t0"] for o in beats if o["take"] and o["row"] > b["row"]]
            guides.append({"comment": f"Missing row {b['row']:02}: {b['text'][:60]}", "pos": later[0] if later else total - 1,
                           "type": cat["warning"]})
    for b in found:
        if b["take"].score < rc["match_threshold"] + 0.08:
            guides.append({"comment": f"Check row {b['row']:02}: take only {b['take'].score:.0%} like the script",
                           "pos": b["t0"], "type": cat["warning"]})
    guides.sort(key=lambda g: g["pos"])

    timeline = {"frames": total, "clips": clips, "source": video, "audio": audio,
                "source_frames": src_frames, "audio_frames": round(src_dur * fps), "unplaced": unplaced}
    for u in unplaced:
        if u["kind"] == "video":
            u.setdefault("src_frames", max(1, round(probe(u["path"])["duration"] * fps)))
    build_project(proj, kd, fps, size, timeline, overlays, music, guides, f"{proj.name} rough cut", sfx,
                  {"Section": cat["section"], "Ad-lib (keep?)": cat["adlib"], "Check this": cat["warning"]})

    sub = cfg["subtitles"]
    write_srt(rdir / "roughcut.srt", words, clips, fps, sub["max_line_width"], sub["max_line_count"])

    # Report
    raw = (pv["duration"] if pv else src_dur)
    L = [f"# Rough cut: {proj.name}", "",
         f"- **Project:** `{kd.name}` (open it in Kdenlive)",
         f"- **Recording:** `{(video or audio).relative_to(proj)}`" + (f", voice from `{audio.relative_to(proj)}`" if video and audio != video else ""),
         f"- **Length:** {mmss(total / fps)} cut from {mmss(raw)} raw "
         f"({len(found)}/{len(beats)} script lines, {len(adlibs)} ad-libs kept, {len(dropped)} bits removed)",
         f"- **Format:** {size[0]}x{size[1]} @ {fps:g} fps", "",
         "## Lines", "", "| Row | Section | Takes | Used take (raw) | Match | On timeline | Line |", "|---|---|---|---|---|---|---|"]
    for b in beats:
        line = b["text"].replace("|", "/")[:70]
        if b["take"]:
            L.append(f"| {b['row']:02} | {b['section'] or ''} | {len(b['takes'])} | {mmss(b['source'][0])}–{mmss(b['source'][1])} "
                     f"| {b['take'].score:.0%} | {mmss(b['t0'] / fps)} | {line} |")
        else:
            L.append(f"| {b['row']:02} | {b['section'] or ''} | 0 | **not found** | | | {line} |")
    if adlibs:
        L += ["", "## Ad-libs kept (marked on the timeline, delete the ones you don't want)", ""]
        L += [f"- {mmss(x['t0'] / fps)} (raw {mmss(x['s'])}), after row {x['after_row']:02}: \"{x['text']}\"" for x in adlibs]
    if dropped:
        L += ["", "## Removed", ""]
        L += [f"- raw {mmss(x['s'])}–{mmss(x['e'])} ({x['why']}): \"{x['text'][:90]}\"" for x in dropped]
    L += sfx_report(sfx, sfx_notes, cfg, fps, total)
    L += ["", "## Graphics & B-roll on V2", ""]
    L += [f"- {mmss(o['pos'] / fps)}–{mmss((o['pos'] + o['dur']) / fps)}: `{o['name']}` (row {o['row']:02})" for o in overlays] \
        or ["- none (name files `05-name.png` / `05-name.mp4` to put them on row 05)"]
    still = [o for o in overlays if o.get("placeholder")]
    if still:
        L += ["", "## Placeholders still in the video", "",
              "Add the real asset with the name shown (any image or video extension) in `graphics/` or "
              "`footage/broll/`, then rebuild. The placeholder is skipped automatically.", ""]
        L += [f"- {mmss(o['pos'] / fps)}: `{o['name']}` → add `{o['placeholder']}.*`" for o in still]
    if unplaced:
        L += ["", "## In the bin, not placed (\"Unplaced B-roll\" folder)", ""]
        L += [f"- `{u['name']}`: drag it onto the timeline, or rebuild with `--place {u['name']}=ROW`" for u in unplaced]
    if notes:
        L += ["", "## Check these", ""] + [f"- {n}" for n in notes]
    L += ["", "## Next in Kdenlive", "",
          "1. Watch it through once. Fix take choices: the raw times above tell you where the other takes are.",
          "2. Delete ad-libs you don't want (orange guides), then close the gaps (Timeline → Remove Space).",
          "3. Add Pop In / zoom to graphics on V2, sound effects on a new audio track.",
          "4. Captions: Subtitles menu → Import → `roughcut/roughcut.srt` (re-run subtitles.sh after big edits).", ""]
    (rdir / "report.md").write_text("\n".join(L), encoding="utf-8")

    preview = None
    if rc["preview"] and not a.no_preview:
        melt = find_melt(rc)
        if melt:
            pv_path = rdir / "preview.mp4"
            pv_path.unlink(missing_ok=True)
            if render_preview(melt, kd, pv_path, total, fps, rc["preview_height"], size):
                preview = pv_path
        else:
            log("Skipping preview: Kdenlive's melt not found.")

    log("")
    log(f"Rough cut: {mmss(total / fps)} from {mmss(raw)} raw. {len(found)}/{len(beats)} lines, "
        f"{len(adlibs)} ad-libs kept, {len(overlays)} graphics/B-roll placed, {len(unplaced)} unplaced.")
    missing = [b for b in beats if not b["take"]]
    if missing:
        log("Not found in the recording: rows " + ", ".join(f"{b['row']:02}" for b in missing))
    log(f"Open:    {kd}")
    log(f"Report:  {rdir / 'report.md'}")
    log(f"Captions:{rdir / 'roughcut.srt'}")
    if preview:
        log(f"Preview: {preview}")


if __name__ == "__main__":
    main()
