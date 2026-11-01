#!/usr/bin/env bash
# Install everything the workflow needs. Safe to run again any time (skips what's installed).
# Usage: tools/setup.sh [--no-apps] [--voice-clone]
#   --no-apps      skip Kdenlive / OBS
#   --voice-clone  also install voice cloning (Chatterbox, ~2 GB of Python packages + ~3 GB model on first use)
set -euo pipefail
cd "$(dirname "$0")/.."
apps=true; clone=false
for a in "$@"; do
  case "$a" in --no-apps) apps=false ;; --voice-clone) clone=true ;; esac
done
step() { printf "\n\033[1m==> %s\033[0m\n" "$1"; }

command -v brew >/dev/null || { echo "Install Homebrew first: https://brew.sh"; exit 1; }

step "Command-line tools (Homebrew)"
for f in ffmpeg ffmpeg-full auto-editor openai-whisper uv node; do
  if brew list --formula "$f" >/dev/null 2>&1 || { [[ $f == node ]] && command -v node >/dev/null; }; then
    echo "  ✓ $f"
  else
    brew install "$f"
  fi
done

if $apps; then
  step "Apps"
  [[ -d /Applications/kdenlive.app ]] && echo "  ✓ Kdenlive" || brew install --cask kdenlive
  [[ -d /Applications/OBS.app ]] && echo "  ✓ OBS Studio" || brew install --cask obs
  [[ -d "/Applications/Google Chrome.app" ]] && echo "  ✓ Google Chrome (graphics engine)" \
    || echo "  - No Google Chrome: the graphics engine will use Playwright's Chromium (set [graphics].browser = \"chromium\")"
fi

step "Python tools (.venv: rembg, Piper)"
[[ -x .venv/bin/python ]] || uv venv --python 3.12 .venv
uv pip install --python .venv -q -r requirements.txt && echo "  ✓ rembg, piper-tts"

if $clone || [[ -x .venv-voice/bin/python ]]; then
  step "Voice cloning (.venv-voice: Chatterbox)"
  [[ -x .venv-voice/bin/python ]] || uv venv --python 3.11 .venv-voice
  uv pip install --python .venv-voice -q chatterbox-tts "setuptools<81" && echo "  ✓ chatterbox-tts (tools/voice-clone)"
fi

step "Graphics engine (Playwright, Shiki, Mermaid)"
npm install --silent && echo "  ✓ node packages"
if ! [[ -d "/Applications/Google Chrome.app" ]]; then npx playwright install chromium; fi

step "Animations (Motion Canvas)"
(cd animations && npm install --silent && node sync-brand.mjs) && echo "  ✓ Motion Canvas"

step "Check"
tools/doctor.sh || true
