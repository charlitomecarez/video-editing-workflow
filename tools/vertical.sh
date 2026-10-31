#!/usr/bin/env bash
# Make a 9:16 (1080x1920) version of a horizontal video.
# Usage: tools/vertical.sh <input> [mode=crop]
#   crop = center-crop to fill the frame
#   blur = fit the whole frame over a blurred background
# Output: <name>_vertical.mp4 next to the input
set -euo pipefail
in="${1:?usage: tools/vertical.sh <input> [crop|blur]}"
mode="${2:-crop}"
out="${in%.*}_vertical.mp4"
if [[ "$mode" == "blur" ]]; then
  vf="split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=20[bg];[b]scale=1080:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2"
else
  vf="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
fi
ffmpeg -hide_banner -i "$in" -filter_complex "$vf" -c:v libx264 -crf 18 -preset medium \
  -c:a copy -movflags +faststart "$out"
echo "Vertical: $out"
