#!/usr/bin/env python3
"""Load the workflow config (config.toml + config.local.toml) and styles.

Command line:
  python3 tools/vwconfig.py show                 # merged config
  python3 tools/vwconfig.py get prep.crf         # one value (used by the shell tools)
  python3 tools/vwconfig.py styles               # list styles, including custom ones
  python3 tools/vwconfig.py style short-form     # one fully resolved style

In Python:
  from vwconfig import load, load_styles, ROOT
"""
import json
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load():
    cfg = tomllib.loads((ROOT / "config.toml").read_text())
    local = ROOT / "config.local.toml"
    if local.exists():
        cfg = _merge(cfg, tomllib.loads(local.read_text()))
    return cfg


def load_styles():
    """styles/styles.json + every styles/custom/*.json. A style can say
    "extends": "<other style>" to copy it and change only some fields."""
    styles = json.loads((ROOT / "styles" / "styles.json").read_text())
    for f in sorted((ROOT / "styles" / "custom").glob("*.json")):
        styles.update(json.loads(f.read_text()))

    def resolve(key, seen=()):
        s = styles[key]
        parent = s.get("extends")
        if not parent:
            return s
        if parent in seen or parent not in styles:
            raise SystemExit(f"Style '{key}' extends unknown or circular style '{parent}'")
        merged = _merge(resolve(parent, seen + (key,)), s)
        merged.pop("extends", None)
        return merged

    return {k: resolve(k) for k in styles}


def get(cfg, dotted):
    cur = cfg
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(dotted)
        cur = cur[part]
    return cur


def _fmt(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (list, dict)):
        return json.dumps(v)
    return str(v)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, *rest = argv
    if cmd == "show":
        print(json.dumps(load(), indent=2))
    elif cmd == "get" and rest:
        try:
            print(_fmt(get(load(), rest[0])))
        except KeyError:
            print(f"Unknown config key: {rest[0]}", file=sys.stderr)
            return 1
    elif cmd == "styles":
        for k, s in load_styles().items():
            print(f"{k:16} {s['name']}")
    elif cmd == "style" and rest:
        styles = load_styles()
        if rest[0] not in styles:
            print(f"Unknown style: {rest[0]}. Options: {', '.join(styles)}", file=sys.stderr)
            return 1
        print(json.dumps(styles[rest[0]], indent=2))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
