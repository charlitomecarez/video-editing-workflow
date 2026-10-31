#!/usr/bin/env bash
# Generate an .srt subtitle file with Whisper.
# Usage: tools/subtitles.sh <input> [model=small] [language=auto]
#   models: tiny, base, small, medium, large (bigger = slower, more accurate)
#   language: e.g. en, tl (Tagalog); omit to auto-detect
# Output: <name>.srt next to the input. Import it in Kdenlive via the Subtitles menu.
set -euo pipefail
in="${1:?usage: tools/subtitles.sh <input> [model] [language]}"
model="${2:-small}"
lang_args=()
[[ -n "${3:-}" ]] && lang_args=(--language "$3")
whisper "$in" --model "$model" "${lang_args[@]+"${lang_args[@]}"}" \
  --output_format srt --output_dir "$(dirname "$in")"
echo "Subtitles: ${in%.*}.srt"
