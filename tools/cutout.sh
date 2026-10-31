#!/usr/bin/env bash
# Remove the background from an image (you, a product, a logo) with rembg.
# Use the result as the "subject" in a thumbnail: tools/graphic thumbnail-bold --set subject=<cutout>
#
# Usage: tools/cutout.sh <image...> [--model isnet-general-use]
#   models: u2net, isnet-general-use, u2net_human_seg, birefnet-portrait (people, best quality)
# Default model comes from [cutout] in config.toml. The first run of each model downloads it
# (~50-900 MB) to ~/.u2net. Output: <name>_cutout.png next to each input.
. "$(dirname "$0")/_lib.sh"
REMBG="$TOOLS_DIR/../.venv/bin/rembg"
[[ -x "$REMBG" ]] || { echo "rembg not installed. Run: tools/setup.sh" >&2; exit 1; }

model=$(cfg cutout.model); inputs=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --model) model="$2"; shift 2 ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) inputs+=("$1"); shift ;;
  esac
done
[[ ${#inputs[@]} -gt 0 ]] || { sed -n '2,9p' "$0"; exit 1; }
for in in "${inputs[@]}"; do
  need_file "$in"
  out="${in%.*}_cutout.png"
  check_out "$out"
  echo "Removing background from $in (model=$model)"
  "$REMBG" i -m "$model" "$in" "$out"
  echo "Cutout: $out"
done
