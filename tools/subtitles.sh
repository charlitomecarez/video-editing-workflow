#!/usr/bin/env bash
# Generate subtitles with Whisper.
#
# Usage: tools/subtitles.sh <input> [--model small] [--language en] [--format srt] [--width 32] [--lines 2]
#   models: tiny, base, small, medium, large, turbo (bigger = slower, more accurate)
#   language: en, tl (Tagalog), ... ; empty = auto-detect
# Defaults come from [subtitles] in config.toml.
# Output: <name>.srt next to the input. Import it in Kdenlive via the Subtitles menu,
# or burn it in with tools/burn-captions.sh.
. "$(dirname "$0")/_lib.sh"
need whisper

model=$(cfg subtitles.model); lang=$(cfg subtitles.language); fmt=$(cfg subtitles.format)
width=$(cfg subtitles.max_line_width); lines=$(cfg subtitles.max_line_count)
in=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) model="$2"; shift 2 ;;
    --language) lang="$2"; shift 2 ;;
    --format) fmt="$2"; shift 2 ;;
    --width) width="$2"; shift 2 ;;
    --lines) lines="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) in="$1"; shift ;;
  esac
done
[[ -n "$in" ]] || { sed -n '2,10p' "$0"; exit 1; }
need_file "$in"

lang_args=(); [[ -n "$lang" ]] && lang_args=(--language "$lang")
echo "Transcribing with Whisper (model=$model language=${lang:-auto})"
echo "(The first run downloads the model, which can take a few minutes.)"
whisper "$in" --model "$model" "${lang_args[@]+"${lang_args[@]}"}" \
  --word_timestamps True --max_line_width "$width" --max_line_count "$lines" \
  --output_format "$fmt" --output_dir "$(dirname "$in")"
echo "Subtitles: ${in%.*}.$fmt"
