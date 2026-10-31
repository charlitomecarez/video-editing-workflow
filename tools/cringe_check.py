#!/usr/bin/env python3
"""Flag corny, try-hard or AI-sounding writing in a script's narration.

Examples:
  python3 tools/cringe_check.py projects/x/script.md
  python3 tools/cringe_check.py draft.txt
  python3 tools/cringe_check.py projects/x/script.md --strict   # exit code 1 if anything is flagged

Checks (all configurable in [personality] in config.toml):
  - blocklisted phrases (greetings, hype words, AI tells, forced slang)
  - repeated intensifiers (literally, insane, crazy...)
  - too many exclamation marks
  - sentences too long to say in one breath
  - emoji / "lol" / "haha" in narration
  - three sentences in a row starting with the same word

It can't judge whether a joke is funny. That's the read-aloud test in personality/bestfriend.md.
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from script_text import extract  # noqa: E402
from vwconfig import load  # noqa: E402

EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿]")


def sentences(text):
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    return [s for s in parts if s]


def main():
    cfg = load().get("personality", {})
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("file", help="script.md or a plain text file")
    p.add_argument("--strict", action="store_true", help="exit 1 if anything is flagged")
    a = p.parse_args()

    src = Path(a.file)
    raw = src.read_text(encoding="utf-8")
    if src.suffix == ".md":
        beats = extract(raw)
        if not beats:
            raise SystemExit("No narration found. Fill in the Hear column / Voiceover lines first.")
        lines = [(b["section"] or "-", b["text"]) for b in beats]
    else:
        lines = [("-", ln.strip()) for ln in raw.splitlines() if ln.strip()]

    text = " ".join(t for _, t in lines)
    words = len(text.split())
    issues = []

    # 1. Blocklist
    for section, line in lines:
        low = line.lower()
        for phrase in cfg.get("blocklist", []):
            if re.search(r"(?<![a-z])" + re.escape(phrase.lower()) + r"(?![a-z])", low):
                issues.append(("cringe phrase", f'"{phrase}"', section, line))

    # 2. Intensifiers
    counts = Counter(w.strip(".,!?\"'").lower() for w in text.split())
    for word, limit in cfg.get("intensifiers", {}).items():
        if counts[word] > limit:
            issues.append(("overused word", f'"{word}" ×{counts[word]} (max {limit})', "-", ""))

    # 3. Exclamations
    excl = text.count("!")
    max_ex = cfg.get("max_exclamations_per_100", 1.0)
    if words and excl / words * 100 > max_ex:
        issues.append(("too hype", f"{excl} exclamation marks in {words} words "
                       f"(max {max_ex}/100 words). Let the content bring the energy.", "-", ""))

    # 4. Long sentences
    max_len = cfg.get("max_sentence_words", 22)
    for section, line in lines:
        for s in sentences(line):
            n = len(s.split())
            if n > max_len:
                issues.append(("long sentence", f"{n} words (max {max_len}). Split it.", section, s))

    # 5. Emoji / laughing at your own joke
    for section, line in lines:
        if EMOJI.search(line):
            issues.append(("emoji in narration", "you can't say an emoji out loud", section, line))

    # 6. Repeated openers
    all_s = [s for _, ln in lines for s in sentences(ln)]
    for i in range(len(all_s) - 2):
        first = [s.split()[0].lower().strip(",") for s in all_s[i:i + 3] if s.split()]
        if len(first) == 3 and len(set(first)) == 1:
            issues.append(("repetitive", f'3 sentences in a row start with "{first[0]}"', "-", all_s[i]))

    # Report
    print(f"Cringe check: {src.name} ({words} words, {len(all_s)} sentences)\n")
    if not issues:
        print("✓ Nothing flagged. Now do the read-aloud test (personality/bestfriend.md).")
        return 0
    seen = set()
    for kind, what, section, line in issues:
        key = (kind, what, line)
        if key in seen:
            continue
        seen.add(key)
        loc = f" [{section}]" if section != "-" else ""
        print(f"✗ {kind}: {what}{loc}")
        if line:
            print(f"    {line[:140]}{'…' if len(line) > 140 else ''}")
    print(f"\n{len(seen)} issue(s). Fix them, or ask Claude: /punchup <script>")
    return 1 if a.strict else 0


if __name__ == "__main__":
    sys.exit(main())
