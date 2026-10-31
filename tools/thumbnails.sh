#!/usr/bin/env bash
# Pull evenly spaced frames from a video to pick a thumbnail from.
#
# Usage: tools/thumbnails.sh <video> [--count 12] [--width 1280] [--out DIR]
# Defaults come from [thumbnails] in config.toml.
# Output: <DIR>/thumb_01.jpg ...
#   Default DIR: the project's thumbnails/ folder (for videos in projects/<video>/export/),
#   otherwise a <name>_thumbs/ folder beside the video.
. "$(dirname "$0")/_lib.sh"
need ffmpeg; need ffprobe

count=$(cfg thumbnails.count); width=$(cfg thumbnails.width); outdir=""
in=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --count) count="$2"; shift 2 ;;
    --width) width="$2"; shift 2 ;;
    --out) outdir="$2"; shift 2 ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) in="$1"; shift ;;
  esac
done
[[ -n "$in" ]] || { sed -n '2,8p' "$0"; exit 1; }
need_file "$in"

if [[ -z "$outdir" ]]; then
  parent="$(dirname "$(dirname "$in")")"
  if [[ -d "$parent/thumbnails" ]]; then outdir="$parent/thumbnails"; else outdir="${in%.*}_thumbs"; fi
fi
mkdir -p "$outdir"
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
rate=$(python3 -c "print($count / max(float('$dur'), 0.1))")
ffmpeg -hide_banner -loglevel error -y -i "$in" \
  -vf "fps=$rate,scale=$width:-2" -frames:v "$count" -q:v 2 "$outdir/thumb_%02d.jpg"
echo "Saved $count frames to $outdir"
