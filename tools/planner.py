#!/usr/bin/env python3
"""Read (and lightly update) the Content Planner app's data in Appwrite.

The planner (github.com/charlitomecarez/content-planner) is where videos and ideas
live. This tool lets Claude see what you're working on right now.

  python3 tools/planner.py current            # the video to work on now + its next step
  python3 tools/planner.py list               # every video in the pipeline, most urgent first
  python3 tools/planner.py list --stage edit  # only one stage (idea, script, record, ...)
  python3 tools/planner.py ideas              # the idea inbox
  python3 tools/planner.py show <id|slug|title words>
  python3 tools/planner.py link <video> <project-folder>   # set projectSlug
  python3 tools/planner.py done <video> <step-id>          # tick a checklist step, e.g. script.draft
  python3 tools/planner.py sync [video] [--dry-run]        # tick every step whose result is in the project folder

Ticking the last step of a stage moves the video to the next stage, like the app does.
sync runs by itself after every Claude Code reply (Stop hook in .claude/settings.json).

Add --json to any read command for machine-readable output.

Connection settings are in [planner] in config.toml. The API key is a secret: put it in
.env.local (git-ignored) as APPWRITE_API_KEY=... or export it. It needs rows.read
(and rows.write for link/done).
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vwconfig import ROOT, load  # noqa: E402

# Mirrors src/lib/stages.ts in content-planner. Keep the ids in sync with the app.
STAGES = [
    ("idea", "Idea", [("idea.hook", "Write the hook in one line", None), ("idea.format", "Pick the format and platforms", None)]),
    ("script", "Script", [("script.draft", "Draft the script", "/script"), ("script.punchup", "Punch it up", "/punchup"), ("script.read", "Read it out loud once", None)]),
    ("record", "Record", [("record.voice", "Record voice and footage", "/record"), ("record.prep", "Prep the footage", "/edit"), ("record.broll", "Collect B-roll", None)]),
    ("edit", "Edit", [("edit.graphics", "Make the graphics", "/graphics"), ("edit.roughcut", "Build the rough cut", "/roughcut")]),
    ("polish", "Polish", [("polish.kdenlive", "Polish the edit in Kdenlive", None), ("polish.thumbnail", "Make the thumbnail", "/thumbnail"), ("polish.export", "Export the final video", None)]),
    ("publish", "Publish", [("publish.meta", "Write the title, description and captions", "/publish"), ("publish.upload", "Upload and schedule", None), ("publish.reel", "Cut the reel", "/reel")]),
    ("published", "Published", []),
]
STAGE_IDS = [s[0] for s in STAGES]
NEEDS_PROJECT = {"/record", "/edit", "/graphics", "/roughcut", "/thumbnail", "/publish", "/reel"}


# ---------- connection ----------

def read_env_file(path):
    out = {}
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                out[k.strip()] = v.strip().strip("\"'")
    return out


class Planner:
    def __init__(self, cfg):
        p = cfg.get("planner", {})
        self.endpoint = p.get("endpoint", "").rstrip("/")
        self.project = p.get("project_id", "")
        self.db = p.get("database_id", "planner")
        key_var = p.get("api_key_env", "APPWRITE_API_KEY")
        self.key = os.environ.get(key_var) or read_env_file(ROOT / ".env.local").get(key_var, "")
        if not self.endpoint or not self.project:
            raise SystemExit("Set [planner] endpoint and project_id in config.toml or config.local.toml.")
        if not self.key:
            raise SystemExit(
                f"No API key. Put {key_var}=... in .env.local (git-ignored) or export it.\n"
                "Make one in Appwrite: your project > Overview > API keys, scopes rows.read (+ rows.write for link/done)."
            )

    def _req(self, method, path, query=None, body=None):
        url = f"{self.endpoint}{path}"
        if query:
            url += "?" + urllib.parse.urlencode(query, doseq=True)
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            "X-Appwrite-Project": self.project,
            "X-Appwrite-Key": self.key,
            "Content-Type": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            try:
                msg = json.load(e).get("message", "")
            except Exception:
                msg = ""
            raise SystemExit(f"Appwrite {e.code}: {msg or e.reason}")
        except urllib.error.URLError as e:
            raise SystemExit(f"Can't reach Appwrite at {self.endpoint}: {e.reason}")

    def rows(self, table):
        out, cursor = [], None
        while True:
            q = [json.dumps({"method": "limit", "values": [500]}), json.dumps({"method": "orderAsc", "attribute": "$createdAt"})]
            if cursor:
                q.append(json.dumps({"method": "cursorAfter", "values": [cursor]}))
            page = self._req("GET", f"/tablesdb/{self.db}/tables/{table}/rows", {"queries[]": q})
            out += page["rows"]
            if len(page["rows"]) < 500:
                return out
            cursor = page["rows"][-1]["$id"]

    def update(self, table, row_id, data):
        return self._req("PATCH", f"/tablesdb/{self.db}/tables/{table}/rows/{row_id}", body={"data": data})


# ---------- logic (mirrors the app) ----------

def to_video(r):
    posts = []
    for x in r.get("posts") or []:
        try:
            posts.append(json.loads(x))
        except (ValueError, TypeError):
            pass
    return {
        "id": r["$id"], "title": r["title"], "stage": r.get("stage") or "idea",
        "format": r.get("format") or "long", "platforms": r.get("platforms") or [],
        "publishDate": r.get("publishDate"), "priority": r.get("priority", 1) if r.get("priority") is not None else 1,
        "hook": r.get("hook") or "", "notes": r.get("notes") or "",
        "projectSlug": r.get("projectSlug") or "", "doneSteps": r.get("doneSteps") or [],
        "posts": posts, "createdAt": r["$createdAt"], "updatedAt": r["$updatedAt"],
    }


def parse_iso(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def days_from(iso):
    return (parse_iso(iso).astimezone().date() - dt.date.today()).days


def urgency(v):
    """Same as the app: late first, then soonest publish date, then priority."""
    days = days_from(v["publishDate"]) if v["publishDate"] else 60
    return days * 10 - v["priority"] * 15


def steps_for(stage_id, fmt):
    steps = next(s[2] for s in STAGES if s[0] == stage_id)
    return [s for s in steps if not (fmt == "short" and s[0] == "publish.reel")]


def command_for(cmd, slug, cfg):
    if not cmd:
        return None
    if slug and cmd in NEEDS_PROJECT:
        return f"{cmd} {cfg['paths']['projects']}/{slug}"
    return cmd


def next_action(v, cfg):
    if v["stage"] == "published":
        return {"kind": "done"}
    for sid, label, cmd in steps_for(v["stage"], v["format"]):
        if sid not in v["doneSteps"]:
            return {"kind": "step", "step": sid, "label": label, "command": command_for(cmd, v["projectSlug"], cfg)}
    nxt = STAGE_IDS[STAGE_IDS.index(v["stage"]) + 1]
    return {"kind": "advance", "to": nxt, "label": f"Move it to {nxt.title()} in the planner"}


def advanced_stage(v, done):
    """Same rule as the app: once every step of the stage is ticked, move to the next stage.
    Keeps going while later stages are complete too. Never moves backwards."""
    stage = v["stage"]
    while stage != "published":
        steps = [s[0] for s in steps_for(stage, v["format"])]
        if not all(s in done for s in steps):
            break
        stage = STAGE_IDS[STAGE_IDS.index(stage) + 1]
    return stage


# ---------- sync: tick steps from what's in the project folder ----------

MEDIA_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi",
             ".wav", ".mp3", ".m4a", ".aac", ".flac", ".ogg", ".aif", ".aiff"}
VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm", ".avi"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _files(d, exts=None):
    if not d.is_dir():
        return []
    return [f for f in d.iterdir() if f.is_file() and not f.name.startswith(".")
            and (exts is None or f.suffix.lower() in exts)]


def detect_steps(folder, v):
    """Steps whose result exists on disk (or in the planner row). Only ever adds."""
    found = set()
    if v["hook"].strip():
        found.add("idea.hook")
    if v["platforms"]:
        found.add("idea.format")
    if (folder / "script.md").is_file():
        found.add("script.draft")
    recs = [f for f in _files(folder / "footage", MEDIA_EXT)] + \
           [f for f in _files(folder / "audio", MEDIA_EXT) if f.stem.lower().startswith("voice")]
    if any(not re.search(r"_(prep|clean|cut)$", f.stem) for f in recs):
        found.add("record.voice")
    if any(re.search(r"_(prep|clean)$", f.stem) for f in recs):
        found.add("record.prep")
    if _files(folder / "footage" / "broll", MEDIA_EXT | IMAGE_EXT):
        found.add("record.broll")
    if any(re.match(r"\d{2}-", f.name) for f in _files(folder / "graphics", IMAGE_EXT | VIDEO_EXT)):
        found.add("edit.graphics")
    if any(f.name.endswith("-roughcut.kdenlive") for f in _files(folder, {".kdenlive"})):
        found.add("edit.roughcut")
    if _files(folder / "export", VIDEO_EXT):
        found |= {"polish.kdenlive", "polish.export"}   # an export means the edit is finished
    # thumbnails.sh writes thumb_NN.jpg candidates; a designed thumbnail has any other name
    if any(not re.fullmatch(r"thumb_\d+", f.stem) for f in _files(folder / "thumbnails", IMAGE_EXT)):
        found.add("polish.thumbnail")
    if v["posts"]:
        found.add("publish.upload")
    if _files(folder / "reel", VIDEO_EXT):
        found.add("publish.reel")
    return found


def sync_video(api, v, cfg, dry=False):
    """Tick detected steps and advance the stage. Returns a list of change descriptions."""
    p = cfg.get("planner", {})
    folder = ROOT / cfg["paths"]["projects"] / v["projectSlug"]
    allowed = set(p.get("auto_steps", []))
    new = sorted((detect_steps(folder, v) & allowed) - set(v["doneSteps"]))
    done = v["doneSteps"] + new
    stage = advanced_stage(v, set(done)) if p.get("auto_advance", True) else v["stage"]
    changes = []
    labels = {sid: label for _, _, steps in STAGES for sid, label, _ in steps}
    if new:
        changes.append("ticked " + ", ".join(labels.get(s, s) for s in new))
    if stage != v["stage"]:
        changes.append(f"moved {v['stage']} -> {stage}")
    if changes and not dry:
        data = {"doneSteps": done}
        if stage != v["stage"]:
            data["stage"] = stage
        api.update("videos", v["id"], data)
    return changes


def enrich(v, cfg, tasks=None):
    v = dict(v)
    v["next"] = next_action(v, cfg)
    folder = ROOT / cfg["paths"]["projects"] / v["projectSlug"] if v["projectSlug"] else None
    v["projectFolder"] = str(folder.relative_to(ROOT)) if folder else None
    v["projectFolderExists"] = bool(folder and folder.is_dir())
    if tasks is not None:
        v["openTasks"] = [
            {"title": t["title"], "due": t.get("due")} for t in tasks
            if t.get("videoId") == v["id"] and not t.get("done")
        ]
    return v


def find(videos, needle):
    n = needle.lower()
    for test in (lambda v: v["id"] == needle, lambda v: v["projectSlug"] == needle, lambda v: n in v["title"].lower()):
        hits = [v for v in videos if test(v)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            raise SystemExit("More than one video matches: " + ", ".join(f"{v['title']} ({v['id']})" for v in hits))
    raise SystemExit(f"No video matches '{needle}'.")


# ---------- output ----------

def when(v):
    if not v["publishDate"]:
        return "no date"
    d = days_from(v["publishDate"])
    return "today" if d == 0 else "tomorrow" if d == 1 else f"{-d} days late" if d < 0 else f"in {d} days"


def print_video(v, full=False):
    pr = {0: "low", 1: "normal", 2: "high"}.get(v["priority"], v["priority"])
    print(f"{v['title']}")
    print(f"  stage: {v['stage']}   format: {v['format']}   priority: {pr}   publish: {when(v)}")
    if v["projectFolder"]:
        print(f"  project: {v['projectFolder']}" + ("" if v["projectFolderExists"] else "  (folder not created yet)"))
    nx = v["next"]
    if nx["kind"] == "step":
        print(f"  next: {nx['label']}" + (f"  ->  {nx['command']}" if nx["command"] else ""))
    elif nx["kind"] == "advance":
        print(f"  next: {nx['label']}")
    if full:
        if v["hook"]:
            print(f"  hook: {v['hook']}")
        if v["platforms"]:
            print(f"  platforms: {', '.join(v['platforms'])}")
        if v["doneSteps"]:
            print(f"  done steps: {', '.join(v['doneSteps'])}")
        for t in v.get("openTasks", []):
            print(f"  task: {t['title']}" + (f" (due {t['due'][:10]})" if t.get("due") else ""))
        if v["notes"]:
            print("  notes:\n    " + v["notes"].replace("\n", "\n    "))
        print(f"  id: {v['id']}")


def out(data, as_json, printer):
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        printer(data)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("current", "list", "ideas", "show"):
        sp = sub.add_parser(name)
        sp.add_argument("--json", action="store_true")
        if name == "list":
            sp.add_argument("--stage", choices=STAGE_IDS)
            sp.add_argument("--all", action="store_true", help="include ideas and published")
        if name == "show":
            sp.add_argument("video")
    sp = sub.add_parser("link")
    sp.add_argument("video")
    sp.add_argument("folder")
    sp = sub.add_parser("done")
    sp.add_argument("video")
    sp.add_argument("step")
    sp = sub.add_parser("sync", help="tick steps whose result exists in the project folder, then advance the stage")
    sp.add_argument("video", nargs="?", help="one video (id, slug, title words or project folder); default: every linked video")
    sp.add_argument("--dry-run", action="store_true", help="show what would change without saving")
    sp.add_argument("--hook", action="store_true", help="for the Claude Code Stop hook: silent unless something changed, never fails")
    a = p.parse_args()

    cfg = load()
    if a.cmd == "sync" and a.hook:
        return hook_sync(cfg)
    api = Planner(cfg)
    videos = [to_video(r) for r in api.rows("videos")]

    if a.cmd in ("current", "show"):
        tasks = api.rows("tasks")
        if a.cmd == "current":
            active = sorted((v for v in videos if v["stage"] not in ("idea", "published")), key=urgency)
            if not active:
                if a.json:
                    print("null")
                else:
                    print("Nothing in progress. Start an idea from the planner's Ideas page, or run: python3 tools/planner.py ideas")
                return
            v = active[0]
        else:
            v = find(videos, a.video)
        out(enrich(v, cfg, tasks), a.json, lambda d: print_video(d, full=True))

    elif a.cmd == "list":
        if a.stage:
            vs = [v for v in videos if v["stage"] == a.stage]
        elif a.all:
            vs = videos
        else:
            vs = [v for v in videos if v["stage"] not in ("idea", "published")]
        vs = [enrich(v, cfg) for v in sorted(vs, key=urgency)]

        def show_list(items):
            if not items:
                print("No videos.")
            for i, v in enumerate(items):
                if i:
                    print()
                print_video(v)
        out(vs, a.json, show_list)

    elif a.cmd == "ideas":
        ideas = sorted((v for v in videos if v["stage"] == "idea"), key=lambda v: v["createdAt"], reverse=True)
        ideas.sort(key=lambda v: v["priority"], reverse=True)
        ideas = [enrich(v, cfg) for v in ideas]

        def show_ideas(items):
            if not items:
                print("The idea inbox is empty.")
            for v in items:
                star = "*" if v["priority"] >= 2 else " "
                print(f"{star} {v['title']}" + (f"  —  {v['hook']}" if v["hook"] else ""))
        out(ideas, a.json, show_ideas)

    elif a.cmd == "link":
        v = find(videos, a.video)
        slug = Path(a.folder).name
        api.update("videos", v["id"], {"projectSlug": slug})
        print(f"Linked '{v['title']}' to {cfg['paths']['projects']}/{slug}")

    elif a.cmd == "done":
        v = find(videos, a.video)
        valid = [s[0] for st in STAGES for s in st[2]]
        if a.step not in valid:
            raise SystemExit(f"Unknown step '{a.step}'. Steps: {', '.join(valid)}")
        if a.step in v["doneSteps"]:
            print(f"'{a.step}' was already ticked on '{v['title']}'.")
            return
        done = v["doneSteps"] + [a.step]
        data = {"doneSteps": done}
        stage = advanced_stage(v, set(done)) if cfg.get("planner", {}).get("auto_advance", True) else v["stage"]
        if stage != v["stage"]:
            data["stage"] = stage
        api.update("videos", v["id"], data)
        print(f"Ticked '{a.step}' on '{v['title']}'." + (f" Stage done: moved to {stage.title()}." if "stage" in data else ""))

    elif a.cmd == "sync":
        if a.video:
            vs = [find(videos, Path(a.video).name if "/" in a.video else a.video)]
        else:
            vs = [v for v in videos if v["projectSlug"] and v["stage"] != "published"]
        projects = ROOT / cfg["paths"]["projects"]
        any_change = False
        for v in vs:
            if not v["projectSlug"] or not (projects / v["projectSlug"]).is_dir():
                if a.video:
                    print(f"'{v['title']}' has no project folder here, nothing to check.")
                continue
            changes = sync_video(api, v, cfg, dry=a.dry_run)
            if changes:
                any_change = True
                print(f"{'[dry run] ' if a.dry_run else ''}{v['title']}: " + "; ".join(changes))
        if not any_change:
            print("Planner is up to date.")


def hook_sync(cfg):
    """Run from the Claude Code Stop hook. Quiet and safe: no project folders = no network call."""
    if not cfg.get("planner", {}).get("auto_sync", True):
        return
    projects = ROOT / cfg["paths"]["projects"]
    if not projects.is_dir() or not any(d.is_dir() and not d.name.startswith(".") for d in projects.iterdir()):
        return
    try:
        api = Planner(cfg)
        msgs = []
        for v in (to_video(r) for r in api.rows("videos")):
            if v["projectSlug"] and v["stage"] != "published" and (projects / v["projectSlug"]).is_dir():
                changes = sync_video(api, v, cfg)
                if changes:
                    msgs.append(f"{v['title']}: " + "; ".join(changes))
    except (SystemExit, Exception) as e:   # never break the session over the planner
        print(json.dumps({"systemMessage": f"Planner sync skipped: {e}"}))
        return
    if msgs:
        print(json.dumps({"systemMessage": "Content Planner updated. " + " | ".join(msgs)}))


if __name__ == "__main__":
    main()
