#!/usr/bin/env bash
# Remove silences with auto-editor and export a Kdenlive project
# so you can review every cut on the timeline.
# Usage: tools/cut-silence.sh <input> [margin=0.2s] [threshold=4%]
#   margin    = padding kept around speech (bigger = less choppy)
#   threshold = audio level counted as silence (raise if room noise is loud)
# Output: <name>_cut.kdenlive next to the input
set -euo pipefail
in="${1:?usage: tools/cut-silence.sh <input> [margin] [threshold]}"
margin="${2:-0.2s}"
threshold="${3:-4%}"
out="${in%.*}_cut.kdenlive"
auto-editor "$in" --edit "audio:threshold=$threshold" --margin "$margin" \
  --export kdenlive --no-open -o "$out"
echo "Open in Kdenlive: $out"
