#!/usr/bin/env bash
# Clean up a voice recording: cut rumble, reduce background noise, even out
# volume and set loudness. Good first pass before Kdenlive.
#
# Usage: tools/clean-voice.sh <audio or video...> [--denoise 12] [--highpass 80] [--no-compress]
#   denoise   = noise reduction strength in dB (6 light, 12 normal, 20 strong)
#   highpass  = cut everything below this frequency in Hz (removes rumble / AC hum)
# Defaults come from [clean_voice] in config.toml.
# Output: <name>_clean.wav (audio) next to each input. Originals are untouched.
. "$(dirname "$0")/_lib.sh"
need ffmpeg

hp=$(cfg clean_voice.highpass); nr=$(cfg clean_voice.denoise); comp=$(cfg clean_voice.compress)
loud=$(cfg clean_voice.loudness); deess=$(cfg clean_voice.deess); inputs=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --denoise) nr="$2"; shift 2 ;;
    --highpass) hp="$2"; shift 2 ;;
    --no-compress) comp=false; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) inputs+=("$1"); shift ;;
  esac
done
[[ ${#inputs[@]} -gt 0 ]] || { sed -n '2,9p' "$0"; exit 1; }

chain="highpass=f=$hp,afftdn=nr=$nr:nf=-40:tn=1"
[[ "$deess" == "true" ]] && chain="$chain,deesser=i=0.4"
[[ "$comp" == "true" ]] && chain="$chain,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=2"
chain="$chain,loudnorm=I=$loud:TP=-1.5:LRA=7"

for in in "${inputs[@]}"; do
  need_file "$in"
  out="${in%.*}_clean.wav"
  check_out "$out"
  echo "Cleaning $in (highpass=${hp}Hz denoise=${nr}dB compress=$comp loudness=$loud)"
  ffmpeg -hide_banner -loglevel warning -stats -y -i "$in" -vn -af "$chain" -ar 48000 -c:a pcm_s16le "$out"
  echo "Clean: $out"
done
