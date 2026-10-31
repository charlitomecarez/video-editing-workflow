#!/usr/bin/env bash
# Remove silences with auto-editor. By default it exports a Kdenlive project
# so you can review every cut on the timeline.
#
# Usage: tools/cut-silence.sh <input> [--margin 0.2s] [--threshold 4%] [--export kdenlive|default]
#   margin    = padding kept around speech (bigger = less choppy)
#   threshold = audio level counted as silence (raise if room noise is loud)
#   export    = kdenlive -> <name>_cut.kdenlive, default -> <name>_cut.mp4
# Defaults come from [silence] in config.toml.
. "$(dirname "$0")/_lib.sh"
need auto-editor

margin=$(cfg silence.margin); threshold=$(cfg silence.threshold); export_as=$(cfg silence.export)
in=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --margin) margin="$2"; shift 2 ;;
    --threshold) threshold="$2"; shift 2 ;;
    --export) export_as="$2"; shift 2 ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) in="$1"; shift ;;
  esac
done
[[ -n "$in" ]] || { sed -n '2,10p' "$0"; exit 1; }
need_file "$in"

if [[ "$export_as" == "kdenlive" ]]; then
  out="${in%.*}_cut.kdenlive"; exp=(--export kdenlive)
else
  out="${in%.*}_cut.mp4"; exp=()
fi
check_out "$out"
echo "Cutting silence (margin=$margin threshold=$threshold export=$export_as)"
auto-editor "$in" --edit "audio:threshold=$threshold" --margin "$margin" \
  "${exp[@]+"${exp[@]}"}" --no-open -o "$out"
echo "Done: $out"
