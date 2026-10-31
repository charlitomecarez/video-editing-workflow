#!/usr/bin/env bash
# Convert footage (phone HEVC, variable frame rate, etc.) into edit-friendly
# constant-frame-rate H.264 with loudness-normalized audio.
#
# Usage: tools/prep.sh <input...> [--fps N] [--crf N] [--preset P] [--loudness LUFS] [--no-normalize]
# Defaults come from [prep] in config.toml. Output: <name>_prep.mp4 next to each input.
# Several inputs work: tools/prep.sh projects/x/footage/*.MOV
. "$(dirname "$0")/_lib.sh"
need ffmpeg

fps=$(cfg prep.fps); crf=$(cfg prep.crf); preset=$(cfg prep.preset)
loud=$(cfg prep.loudness); abr=$(cfg prep.audio_bitrate); norm=$(cfg prep.normalize_audio)
inputs=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --fps) fps="$2"; shift 2 ;;
    --crf) crf="$2"; shift 2 ;;
    --preset) preset="$2"; shift 2 ;;
    --loudness) loud="$2"; shift 2 ;;
    --no-normalize) norm=false; shift ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) inputs+=("$1"); shift ;;
  esac
done
[[ ${#inputs[@]} -gt 0 ]] || { sed -n '2,8p' "$0"; exit 1; }

for in in "${inputs[@]}"; do
  need_file "$in"
  out="${in%.*}_prep.mp4"
  check_out "$out"
  af=(); [[ "$norm" == "true" ]] && af=(-af "loudnorm=I=$loud:TP=-1.5:LRA=11")
  echo "Prepping $in (fps=$fps crf=$crf preset=$preset normalize=$norm)"
  ffmpeg -hide_banner -loglevel warning -stats -y -i "$in" \
    -vf "fps=$fps,format=yuv420p" -c:v libx264 -preset "$preset" -crf "$crf" \
    "${af[@]+"${af[@]}"}" -c:a aac -b:a "$abr" -ar 48000 \
    -movflags +faststart "$out"
  echo "Prepped: $out"
done
