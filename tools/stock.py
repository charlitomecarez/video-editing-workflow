#!/usr/bin/env python3
"""Stock video and meme clips for B-roll and punchlines.

  find "words"          Search free stock video you can monetize: Pexels, Pixabay (free licenses,
                        no credit needed) and Wikimedia Commons (CC0 / public domain / CC BY only).
  find "words" --memes  Search reaction GIFs on GIPHY. Rights UNKNOWN: most memes are clips from
                        movies and TV. Logged and flagged so you decide (see docs/stock-footage.md).
  get N                 Download result N from the last search, trim it, convert it to a clean
                        1920x1080 clip with no sound, save it where the rough cut finds it, and log
                        source + license in the project's CREDITS-stock.md.
  add FILE              Same, for a file you downloaded yourself, e.g. a GIF from tenor.com (Tenor
                        closed its API in June 2026, so it can only be used by hand).

Examples:
  python3 tools/stock.py find "traffic jam night"
  python3 tools/stock.py get 3 --project projects/<video> --row 19 --name jam-night --seconds 4
  python3 tools/stock.py find "facepalm" --memes
  python3 tools/stock.py get 1 --project projects/<video> --dir graphics/v2 --as 15-3-meme-facepalm
  python3 tools/stock.py add ~/Downloads/facepalm.gif --source Tenor --page https://tenor.com/view/... \
      --project projects/<video> --row 15 --name facepalm

API keys (free, instant) go in .env.local: PEXELS_API_KEY, PIXABAY_API_KEY, GIPHY_API_KEY.
Wikimedia Commons needs no key. Settings: [stock] in config.toml.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load  # noqa: E402

UA = "video-editing-workflow/1.0 (personal video tool)"
CACHE = ROOT / ".cache" / "stock-search.json"          # the last search (what `get N` picks from)
SEARCHES = ROOT / ".cache" / "stock-searches.json"     # every search of the last 24 h
OK_COMMONS = re.compile(r"^(CC0|Public domain|PDM|CC BY \d|CC BY-\d|CC-BY-\d)", re.I)


def cfg():
    return load().get("stock", {})


def die(msg):
    raise SystemExit(msg)


def key(name):
    if os.environ.get(name):
        return os.environ[name]
    env = ROOT / ".env.local"
    if env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith(name + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def fetch(url, timeout, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ------------------------------------------------------------------ sources
# Each returns dicts: title, author, seconds, w, h, url (file), page, source, license, license_url,
# credit_needed, rights ("ok" or "unknown")

def s_pexels(q, c, n):
    k = key("PEXELS_API_KEY")
    if not k:
        raise LookupError("no PEXELS_API_KEY")
    d = fetch("https://api.pexels.com/v1/videos/search?" + urllib.parse.urlencode(
        {"query": q, "orientation": "landscape", "size": "medium", "per_page": n}), c.get("timeout", 15),
        {"Authorization": k})
    out = []
    for v in d.get("videos", []):
        files = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("width")]
        # Smallest file that is still at least Full HD wide, else the biggest
        hd = sorted([f for f in files if f["width"] >= 1920], key=lambda f: f["width"]) or sorted(files, key=lambda f: -f["width"])
        if not hd:
            continue
        f = hd[0]
        out.append({"title": re.sub(r"[-_/]+", " ", v["url"].rstrip("/").split("/")[-1]).strip(),
                    "author": v["user"]["name"], "seconds": v.get("duration", 0), "w": f["width"], "h": f["height"],
                    "url": f["link"], "page": v["url"], "source": "Pexels", "license": "Pexels License",
                    "license_url": "https://www.pexels.com/license/", "credit_needed": False, "rights": "ok"})
    return out


def s_pixabay(q, c, n):
    k = key("PIXABAY_API_KEY")
    if not k:
        raise LookupError("no PIXABAY_API_KEY")
    d = fetch("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": k, "q": q[:100], "per_page": max(3, n), "safesearch": "true", "video_type": "film"}), c.get("timeout", 15))
    out = []
    for v in d.get("hits", []):
        vid = next((v["videos"][s] for s in ("large", "medium") if v["videos"].get(s, {}).get("url")), None)
        if not vid:
            continue
        out.append({"title": v.get("tags", "")[:60], "author": v.get("user", ""), "seconds": v.get("duration", 0),
                    "w": vid["width"], "h": vid["height"], "url": vid["url"], "page": v["pageURL"], "source": "Pixabay",
                    "license": "Pixabay Content License", "license_url": "https://pixabay.com/service/license-summary/",
                    "credit_needed": False, "rights": "ok"})
    return out


def s_commons(q, c, n):
    d = fetch("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{q} filetype:video",
         "gsrnamespace": 6, "gsrlimit": n, "prop": "imageinfo", "iiprop": "url|size|extmetadata|mime"}), c.get("timeout", 15))
    out = []
    for pg in (d.get("query", {}).get("pages", {}) or {}).values():
        ii = pg["imageinfo"][0]
        m = ii.get("extmetadata", {})
        lic = m.get("LicenseShortName", {}).get("value", "")
        if not OK_COMMONS.match(lic) or "SA" in lic.upper().replace("CC0", ""):
            continue   # CC0 / public domain / CC BY only: ShareAlike would bind the whole video
        out.append({"title": pg["title"][5:], "author": re.sub("<[^>]+>", "", m.get("Artist", {}).get("value", "")).strip() or "unknown",
                    "seconds": float(ii.get("duration", 0) or 0), "w": ii.get("width", 0), "h": ii.get("height", 0),
                    "url": ii["url"], "page": ii.get("descriptionurl", ""), "source": "Wikimedia Commons", "license": lic,
                    "license_url": m.get("LicenseUrl", {}).get("value", ""), "credit_needed": lic.upper().startswith("CC BY"),
                    "rights": "ok"})
    return out


CALLS = ROOT / ".cache" / "giphy-calls.json"


def giphy_budget(c):
    """GIPHY keys allow a limited number of API calls per hour (beta keys: 100). Count every call
    and stop before the limit, so a busy session never gets the key blocked. GIF files themselves
    come from GIPHY's media servers and don't count."""
    limit = int(c.get("giphy_calls_per_hour", 90))
    now = time.time()
    calls = [t for t in (json.loads(CALLS.read_text()) if CALLS.exists() else []) if now - t < 3600]
    if len(calls) >= limit:
        wait = int(3600 - (now - min(calls))) // 60 + 1
        raise LookupError(f"GIPHY limit reached ({len(calls)}/{limit} calls this hour), try again in ~{wait} min")
    calls.append(now)
    CALLS.parent.mkdir(parents=True, exist_ok=True)
    CALLS.write_text(json.dumps(calls))
    return limit - len(calls)


def s_giphy(q, c, n):
    k = key("GIPHY_API_KEY")
    if not k:
        raise LookupError("no GIPHY_API_KEY")
    left = giphy_budget(c)
    print(f"(GIPHY API call: {left} left this hour)", file=sys.stderr)
    d = fetch("https://api.giphy.com/v1/gifs/search?" + urllib.parse.urlencode(
        {"api_key": k, "q": q[:50], "limit": min(n, 50), "rating": c.get("giphy_rating", "pg-13"), "lang": "en"}),
        c.get("timeout", 15))
    out = []
    for g in d.get("data", []):
        o = g.get("images", {}).get("original", {})
        if not o.get("mp4"):
            continue
        out.append({"title": g.get("title") or g.get("slug", ""), "author": g.get("username") or "unknown",
                    "seconds": 0, "w": int(o.get("width", 0)), "h": int(o.get("height", 0)), "url": o["mp4"],
                    "page": g.get("url", ""), "source": "GIPHY", "license": "rights unknown (GIPHY)",
                    "license_url": "https://support.giphy.com/hc/en-us/articles/360020027752", "credit_needed": False,
                    "rights": "unknown", "orig_source": g.get("source_tld", ""),
                    "preview": (g.get("images", {}).get("480w_still") or g.get("images", {}).get("original_still") or {}).get("url", "")})
    return out


SOURCES = {"pexels": s_pexels, "pixabay": s_pixabay, "commons": s_commons, "giphy": s_giphy}


def mmss(s):
    s = int(round(s or 0))
    return f"{s // 60}:{s % 60:02d}" if s else "?"


def cmd_find(a, c):
    names = a.source.split(",") if a.source else (c.get("meme_sources", ["giphy"]) if a.memes else c.get("sources", ["pexels", "pixabay", "commons"]))
    if a.memes and not c.get("allow_unknown_rights", True):
        die("Memes are off: [stock].allow_unknown_rights = false. Use stock reaction clips instead (find \"facepalm\").")
    # Every search is kept 24 h (Pixabay asks for this, and GIPHY calls are limited): the same
    # words again reuse it without calling the API
    ck = f"{','.join(names)}|{a.query.lower().strip()}|{a.n}"
    store = json.loads(SEARCHES.read_text()) if SEARCHES.exists() else {}
    store = {k: v for k, v in store.items() if time.time() - v.get("at", 0) < 86400}
    if ck in store and not a.refresh:
        CACHE.write_text(json.dumps(store[ck], indent=1))
        return show(store[ck], cached=True)
    results, notes = [], []
    for name in names:
        fn = SOURCES.get(name)
        if not fn:
            notes.append(f"unknown source '{name}'")
            continue
        try:
            got = fn(a.query, c, a.n)
            results += got
            notes.append(f"{name}: {len(got)}")
        except LookupError as e:
            notes.append(f"{name}: skipped ({e}, see docs/stock-footage.md)")
        except Exception as e:   # one source being down shouldn't stop the search
            notes.append(f"{name}: unavailable ({type(e).__name__})")
    lo, hi = c.get("min_seconds", 2), c.get("max_seconds", 60)
    results = [r for r in results if not r["seconds"] or lo <= r["seconds"] <= hi]
    data = {"query": a.query, "sources": names, "at": time.time(), "notes": notes, "results": results[: a.n * len(names)]}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(data, indent=1))
    if results:
        store[ck] = data
        SEARCHES.write_text(json.dumps(store))
    show(data)


def show(data, cached=False):
    print(f'Search "{data["query"]}" ({", ".join(data["notes"])}){" (cached)" if cached else ""}\n')
    if not data["results"]:
        print("Nothing found. Try simpler words in English (\"traffic jam\", \"facepalm\", \"waiting\").")
        return
    for i, r in enumerate(data["results"], 1):
        flag = "  ⚠ rights unknown" if r["rights"] != "ok" else ("  credit needed" if r["credit_needed"] else "")
        print(f"{i:>2}. {r['title'][:60]} — {r['author'][:30]}  [{mmss(r['seconds'])}, {r['w']}x{r['h']}]")
        print(f"    {r['source']} · {r['license']}{flag}")
        print(f"    {r['page']}")
    if any(r["source"] == "Pexels" for r in data["results"]):
        print("\nVideos provided by Pexels (https://www.pexels.com)")
    print("\nUse one:  python3 tools/stock.py get <number> --project projects/<video> --row NN --name <what>")


def convert(src, out, c, start, seconds, loop):
    """Clean 1920x1080 clip, no sound, project fps. Short GIFs loop to fill `seconds`."""
    w, h = (int(x) for x in str(c.get("size", "1920x1080")).split("x"))
    fps = c.get("fps", 30)
    cmd = ["ffmpeg", "-v", "error", "-y"]
    if loop:
        cmd += ["-stream_loop", "-1"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", str(src)]
    if seconds:
        cmd += ["-t", str(seconds)]
    fit = c.get("meme_fit", "blur") if loop else c.get("fit", "cover")
    if fit == "cover":
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}"
    elif fit == "blur":
        # Whole clip in the middle over a blurred, zoomed copy of itself: fills the frame without cropping
        vf = (f"split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=40:2,"
              f"eq=brightness=-0.15[bg];[b]scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
              f"[bg][fg]overlay=(W-w)/2:(H-h)/2")
    else:
        vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color={c.get('pad_color', '#1e1e1e')}"
    cmd += ["-filter_complex" if fit == "blur" else "-vf", f"{vf},fps={fps},format=yuv420p", "-an", "-c:v", "libx264", "-crf", str(c.get("crf", 18)),
            "-preset", "medium", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)


def burn_caption(clip, text, tmp, c):
    """Same bold caption + shade as the photo-caption graphics, laid over the moving clip."""
    png = tmp / "cap.png"
    subprocess.run([str(ROOT / "tools" / "graphic"), "photo-caption", "--set", "mode=overlay", "--set", f"caption={text}",
                    "--set", f"dim={c.get('caption_dim', 0.25)}", "--transparent", "--out", str(png)],
                   check=True, stdout=subprocess.DEVNULL)
    tmpout = tmp / "captioned.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-i", str(png), "-filter_complex",
                    "[0:v][1:v]overlay=0:0,format=yuv420p", "-an", "-c:v", "libx264", "-crf", str(c.get("crf", 18)),
                    "-preset", "medium", "-movflags", "+faststart", str(tmpout)], check=True)
    tmpout.replace(clip)


def cmd_get(a, c):
    if not CACHE.exists():
        die('Search first: python3 tools/stock.py find "<words>"')
    data = json.loads(CACHE.read_text())
    if not 1 <= a.number <= len(data["results"]):
        die(f"Pick a number from 1 to {len(data['results'])} (last search: \"{data['query']}\")")
    r = data["results"][a.number - 1]
    if r["rights"] != "ok" and not c.get("allow_unknown_rights", True):
        die("This clip's rights are unknown and [stock].allow_unknown_rights = false.")
    place(a, c, r, Path(a.file).expanduser() if a.file else None)


def cmd_add(a, c):
    src = Path(a.file).expanduser()
    if not src.is_file():
        die(f"File not found: {src}")
    unknown = a.rights != "ok"
    r = {"title": src.stem, "author": a.author or "unknown", "seconds": 0, "w": 0, "h": 0, "url": "", "page": a.page or "",
         "source": a.source, "license": a.license or ("rights unknown" if unknown else "see source"), "license_url": "",
         "credit_needed": bool(a.credit), "rights": "unknown" if unknown else "ok", "local": True}
    a.number = 0
    place(a, c, r, src)


def place(a, c, r, local):
    if r["rights"] != "ok" and not c.get("allow_unknown_rights", True):
        die("This clip's rights are unknown and [stock].allow_unknown_rights = false.")
    proj = Path(a.project)
    if not proj.is_dir():
        die(f"No project at {proj}")
    folder = proj / (a.dir or c.get("dir", "footage/broll"))
    folder.mkdir(parents=True, exist_ok=True)
    if a.as_name:
        stem = a.as_name
    elif a.row:
        slug = re.sub(r"[^a-z0-9]+", "-", (a.name or r["title"]).lower()).strip("-")[:30]
        stem = f"{a.row:02d}-{'meme-' if r['rights'] != 'ok' and not slug.startswith('meme') else ''}{slug}"
    else:
        die("Say where it goes: --row NN (with --name) or --as <file name without extension>")
    out = folder / f"{stem}.mp4"
    if out.exists() and os.environ.get("FORCE") != "1":
        die(f"Output exists: {out} (FORCE=1 to overwrite)")
    loop = r["source"] == "GIPHY" or (local is not None and local.suffix.lower() in (".gif", ".webp"))
    seconds = a.seconds or (c.get("meme_seconds", 2.0) if loop else c.get("default_seconds", 0))
    if local is None:
        print(f"Downloading from {r['source']}: {r['title'][:60]}...")
    with tempfile.TemporaryDirectory() as t:
        if local is None:
            local = Path(t) / ("raw" + (Path(urllib.parse.urlparse(r["url"]).path).suffix or ".mp4"))
            req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=120) as resp, open(local, "wb") as f:
                    f.write(resp.read())
            except urllib.error.HTTPError as e:
                if e.code in (401, 403, 429):
                    die(f"{r['source']} refused the download ({e.code}). Open {r['page']}, download it by hand, "
                        f"then: python3 tools/stock.py get {a.number} ... --file <downloaded file>")
                raise
        convert(local, out, c, a.start, seconds, loop)
        if getattr(a, "caption", None):
            burn_caption(out, a.caption, Path(t), c)
    log_credit(proj, out, r, a)
    print(f"Saved {out}")
    if r["rights"] != "ok":
        print("⚠ Rights unknown (meme). Logged in CREDITS-stock.md. Keep it short, and swap it for a stock "
              "reaction clip if the video gets claimed.")
    elif r["credit_needed"]:
        print(f"Credit needed in the description: see {proj / 'CREDITS-stock.md'}")


def log_credit(proj, out, r, a):
    f = proj / "CREDITS-stock.md"
    if not f.exists():
        f.write_text("# Stock video and memes in this video\n\n"
                     "Written by `tools/stock.py`. **Rights** `ok` = free license that allows monetized use; "
                     "`UNKNOWN` = a meme from GIPHY: someone else's clip, use at your own risk.\n\n"
                     "| File | Source | Author | License | Rights | Link |\n|---|---|---|---|---|---|\n")
    rel = out.relative_to(proj)
    rights = "ok" if r["rights"] == "ok" else "**UNKNOWN**"
    # Re-running for the same file replaces its old entry
    keep = [ln for ln in f.read_text().splitlines(keepends=True)
            if not (ln.startswith(f"| `{rel}` |") or ln.startswith(f"> Credit for `{rel.name}`"))]
    f.write_text("".join(keep))
    with f.open("a") as fh:
        fh.write(f"| `{rel}` | {r['source']} | {r['author']} | {r['license']} | {rights} | {r['page']} |\n")
    if r["credit_needed"]:
        with f.open("a") as fh:
            fh.write(f"\n> Credit for `{rel.name}` (paste in the description): \"{r['title']}\" by {r['author']}, "
                     f"{r['license']} ({r['page']})\n\n")


def main():
    c = cfg()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("find", help="search stock video (or --memes)")
    f.add_argument("query")
    f.add_argument("--memes", action="store_true", help="search reaction GIFs (rights unknown)")
    f.add_argument("--source", help="comma list: pexels,pixabay,commons,giphy (default [stock].sources)")
    f.add_argument("-n", type=int, default=c.get("results", 8), help="results per source")
    f.add_argument("--refresh", action="store_true", help="ignore the 24 h search cache")
    g = sub.add_parser("get", help="download result N into the project")
    g.add_argument("number", type=int)
    g.add_argument("--project", required=True)
    g.add_argument("--row", type=int, help="script row: saved as NN-<name>.mp4 so the rough cut places it")
    g.add_argument("--name", help="short name for the file")
    g.add_argument("--as", dest="as_name", help="exact file name without extension, e.g. 15-3-meme-facepalm")
    g.add_argument("--dir", help="folder in the project (default [stock].dir, footage/broll)")
    g.add_argument("--start", type=float, default=0, help="start this many seconds into the clip")
    g.add_argument("--seconds", type=float, help="clip length (default: whole clip; memes [stock].meme_seconds)")
    g.add_argument("--file", help="a file you downloaded by hand (when the site refuses scripts)")
    g.add_argument("--caption", help="bold caption over the clip, same style as photo captions (*word* = accent)")
    d = sub.add_parser("add", help="use a file you downloaded yourself (e.g. a Tenor GIF)")
    d.add_argument("file")
    d.add_argument("--source", required=True, help="where it's from, e.g. Tenor, Pexels, my phone")
    d.add_argument("--page", help="link to the page you got it from")
    d.add_argument("--author")
    d.add_argument("--license", help="e.g. Pexels License, CC0 (default: rights unknown)")
    d.add_argument("--rights", choices=["unknown", "ok"], default="unknown",
                   help="ok only for free licenses or your own footage (default unknown)")
    d.add_argument("--credit", action="store_true", help="the license needs a credit in the description")
    for x in (d,):
        x.add_argument("--project", required=True)
        x.add_argument("--row", type=int)
        x.add_argument("--name")
        x.add_argument("--as", dest="as_name")
        x.add_argument("--dir")
        x.add_argument("--start", type=float, default=0)
        x.add_argument("--seconds", type=float)
        x.add_argument("--caption", help="bold caption over the clip (*word* = accent)")
    a = p.parse_args()
    {"find": cmd_find, "get": cmd_get, "add": cmd_add}[a.cmd](a, c)


if __name__ == "__main__":
    main()
