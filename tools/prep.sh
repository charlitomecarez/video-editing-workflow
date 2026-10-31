#!/usr/bin/env bash
# Convert footage (phone HEVC, variable frame rate, etc.) into edit-friendly
# constant-frame-rate H.264 with loudness-normalized audio.
# Usage: tools/prep.sh <input> [fps=30]
# Output: <name>_prep.mp4 next to the input
set -euo pipefail
in="${1:?usage: tools/prep.sh <input> [fps]}"
fps="${2:-30}"
out="${in%.*}_prep.mp4"
ffmpeg -hide_banner -i "$in" \
  -vf "fps=$fps,format=yuv420p" -c:v libx264 -preset medium -crf 18 \
  -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart "$out"
echo "Prepped: $out"
