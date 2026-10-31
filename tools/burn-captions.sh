#!/usr/bin/env bash
# Burn subtitles permanently into the video (for TikTok / Reels / Shorts, where
# viewers watch muted). Style comes from [captions] in config.toml.
#
# Usage: tools/burn-captions.sh <video> [subtitles.srt] [--font "Arial Black"] [--size 18] [--margin 60]
#   If no .srt is given, uses <video>.srt (create it with tools/subtitles.sh).
# Output: <name>_captioned.mp4
. "$(dirname "$0")/_lib.sh"
need ffmpeg

font=$(cfg captions.font); size=$(cfg captions.size); color=$(cfg captions.color)
ocolor=$(cfg captions.outline_color); outline=$(cfg captions.outline)
margin=$(cfg captions.margin_v); bold=$(cfg captions.bold)
crf=$(cfg render.crf); preset=$(cfg render.preset)
pos=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --font) font="$2"; shift 2 ;;
    --size) size="$2"; shift 2 ;;
    --margin) margin="$2"; shift 2 ;;
    -h|--help) sed -n '2,8p' "$0"; exit 0 ;;
    *) pos+=("$1"); shift ;;
  esac
done
[[ ${#pos[@]} -ge 1 ]] || { sed -n '2,8p' "$0"; exit 1; }
in="${pos[0]}"; srt="${pos[1]:-${in%.*}.srt}"
need_file "$in"; need_file "$srt"
out="${in%.*}_captioned.mp4"
check_out "$out"

FF=$(ffmpeg_libass) || {
  echo "Your ffmpeg can't burn captions (no libass). Install the full build, which" >&2
  echo "sits alongside the normal one:  brew install ffmpeg-full" >&2
  echo "Or burn them in Kdenlive: import the .srt on the Subtitles track and render." >&2
  exit 1; }

b=0; [[ "$bold" == "true" ]] && b=1
style="FontName=$font,FontSize=$size,PrimaryColour=$color,OutlineColour=$ocolor,BorderStyle=1,Outline=$outline,Shadow=0,Bold=$b,Alignment=2,MarginV=$margin"
# Escape the path for the ffmpeg filter syntax
esc=$(printf '%s' "$srt" | sed -e "s/\\\\/\\\\\\\\/g" -e "s/:/\\\\:/g" -e "s/'/\\\\'/g")
echo "Burning captions from $srt"
"$FF" -hide_banner -loglevel warning -stats -y -i "$in" \
  -vf "subtitles='$esc':force_style='$style'" \
  -c:v libx264 -crf "$crf" -preset "$preset" -c:a copy -movflags +faststart "$out"
echo "Captioned: $out"
