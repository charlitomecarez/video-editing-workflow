#!/usr/bin/env bash
# Make a draft voiceover with Piper (free, offline AI voice), so you can time
# the edit before recording your real voice.
#
# Usage: tools/voice-draft.sh <script.md | text.txt> [--voice en_US-lessac-medium] [--speed 1.0] [--out file.wav]
#   script.md -> reads the Hear column / Voiceover lines (tools/script_text.py)
#   speed     -> 1.0 normal, 1.15 faster, 0.9 slower
# Defaults come from [tts] in config.toml. Voices download on first use into [tts].voices_dir.
# Browse voices (and hear samples): https://rhasspy.github.io/piper-samples/
# Output: <name>_draft-vo.wav next to the input. Put it on A1 in Kdenlive and edit to it.
. "$(dirname "$0")/_lib.sh"
VENV="$TOOLS_DIR/../.venv/bin"
[[ -x "$VENV/piper" ]] || { echo "Piper not installed. Run: tools/setup.sh" >&2; exit 1; }

voice=$(cfg tts.voice); speed=$(cfg tts.speed); vdir=$(cfg tts.voices_dir)
silence=$(cfg tts.sentence_pause); out=""; in=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --voice) voice="$2"; shift 2 ;;
    --speed) speed="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    -h|--help) sed -n '2,11p' "$0"; exit 0 ;;
    *) in="$1"; shift ;;
  esac
done
[[ -n "$in" ]] || { sed -n '2,11p' "$0"; exit 1; }
need_file "$in"
[[ "$vdir" = /* ]] || vdir="$TOOLS_DIR/../$vdir"
mkdir -p "$vdir"
out="${out:-${in%.*}_draft-vo.wav}"
check_out "$out"

if [[ ! -f "$vdir/$voice.onnx" ]]; then
  echo "Downloading voice $voice..."
  "$VENV/python" -m piper.download_voices --download-dir "$vdir" "$voice"
fi

if [[ "$in" == *.md ]]; then
  text=$(python3 "$TOOLS_DIR/script_text.py" "$in")
else
  text=$(cat "$in")
fi
# Piper: length_scale < 1 is faster, so invert the speed
length=$(python3 -c "print(round(1/float('$speed'), 3))")
echo "Synthesizing $(echo "$text" | wc -w | tr -d ' ') words with $voice (speed $speed)"
printf '%s\n' "$text" | "$VENV/piper" -m "$vdir/$voice.onnx" --length-scale "$length" \
  --sentence-silence "$silence" -f "$out"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out")
printf 'Draft voiceover: %s (%.0fs)\n' "$out" "$dur"
