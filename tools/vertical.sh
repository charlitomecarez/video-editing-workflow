#!/usr/bin/env bash
# Make a vertical (default 1080x1920, 9:16) version of a horizontal video.
#
# Usage: tools/vertical.sh <input> [--mode crop|blur] [--size 1080x1920] [--blur 20]
#   crop = center-crop to fill the frame
#   blur = fit the whole frame over a blurred background
# Defaults come from [vertical] in config.toml. Output: <name>_vertical.mp4
. "$(dirname "$0")/_lib.sh"
need ffmpeg

mode=$(cfg vertical.mode); w=$(cfg vertical.width); h=$(cfg vertical.height)
blur=$(cfg vertical.blur_strength); crf=$(cfg render.crf); preset=$(cfg render.preset)
in=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode) mode="$2"; shift 2 ;;
    --size) w="${2%x*}"; h="${2#*x}"; shift 2 ;;
    --blur) blur="$2"; shift 2 ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) in="$1"; shift ;;
  esac
done
[[ -n "$in" ]] || { sed -n '2,8p' "$0"; exit 1; }
need_file "$in"
out="${in%.*}_vertical.mp4"
check_out "$out"

fill="scale=$w:$h:force_original_aspect_ratio=increase,crop=$w:$h"
case "$mode" in
  blur) vf="split[a][b];[a]$fill,boxblur=$blur[bg];[b]scale=$w:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2" ;;
  crop) vf="$fill" ;;
  *) echo "Unknown mode: $mode (use crop or blur)" >&2; exit 1 ;;
esac
echo "Making vertical video (${w}x${h}, mode=$mode)"
ffmpeg -hide_banner -loglevel warning -stats -y -i "$in" -filter_complex "$vf" \
  -c:v libx264 -crf "$crf" -preset "$preset" -c:a copy -movflags +faststart "$out"
echo "Vertical: $out"
