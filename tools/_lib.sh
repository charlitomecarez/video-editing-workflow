# Shared helpers for the shell tools. Source it: . "$(dirname "$0")/_lib.sh"
set -euo pipefail
TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# cfg <key> -> value from config.toml / config.local.toml
cfg() { python3 "$TOOLS_DIR/vwconfig.py" get "$1"; }

need() {
  command -v "$1" >/dev/null 2>&1 || { echo "Missing '$1'. Run tools/doctor.sh for install help." >&2; exit 1; }
}

need_file() {
  [[ -f "$1" ]] || { echo "File not found: $1" >&2; exit 1; }
}

# Print the path of an ffmpeg that has the subtitles filter (libass).
# Homebrew's default ffmpeg lacks it; the keg-only ffmpeg-full has it.
ffmpeg_libass() {
  local c
  for c in ffmpeg "$(brew --prefix ffmpeg-full 2>/dev/null)/bin/ffmpeg"; do
    if command -v "$c" >/dev/null 2>&1 && "$c" -hide_banner -filters 2>/dev/null | grep -q " subtitles "; then
      command -v "$c"; return 0
    fi
  done
  return 1
}

# Refuse to overwrite outputs unless FORCE=1
check_out() {
  if [[ -e "$1" && "${FORCE:-0}" != "1" ]]; then
    echo "Output exists: $1 (run again with FORCE=1 to overwrite)" >&2; exit 1
  fi
}
