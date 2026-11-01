#!/usr/bin/env bash
# Check that everything the workflow needs is installed and the config is valid.
# Usage: tools/doctor.sh      (fix problems with: tools/setup.sh)
cd "$(dirname "$0")/.."
ok=0
pass() { printf "  \033[32m✓\033[0m %s\n" "$1"; }
fail() { printf "  \033[31m✗\033[0m %s\n      fix: %s\n" "$1" "$2"; ok=1; }
opt()  { printf "  \033[33m-\033[0m %s\n      optional: %s\n" "$1" "$2"; }

echo "Apps"
[[ -d /Applications/kdenlive.app ]] && pass "Kdenlive" || fail "Kdenlive not found" "brew install --cask kdenlive"
[[ -x /Applications/kdenlive.app/Contents/MacOS/melt ]] && pass "melt (Kdenlive's render engine, used for rough cut previews)" || opt "melt not found" "reinstall Kdenlive, or set [rough_cut].melt"
[[ -d /Applications/OBS.app ]] && pass "OBS Studio (screen recording)" || opt "OBS Studio not found" "brew install --cask obs"
[[ -d "/Applications/Google Chrome.app" ]] && pass "Google Chrome (graphics engine)" || opt "No Google Chrome" "set [graphics].browser = \"chromium\" and run: npx playwright install chromium"

echo "Video and audio tools"
for t in ffmpeg ffprobe auto-editor whisper; do
  pkg=$t; [[ $t == ffprobe ]] && pkg=ffmpeg; [[ $t == whisper ]] && pkg=openai-whisper
  command -v $t >/dev/null && pass "$t" || fail "$t missing" "brew install $pkg"
done
. tools/_lib.sh; set +e +u
ff=$(ffmpeg_libass) && pass "caption burning ($ff)" \
  || opt "no ffmpeg with libass (only needed for tools/burn-captions.sh)" "brew install ffmpeg-full   (or burn captions in Kdenlive)"

echo "Python"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' \
  && pass "python3 $(python3 -c 'import platform; print(platform.python_version())')" \
  || fail "Python 3.11+ needed (for tomllib)" "brew install python"
[[ -x .venv/bin/rembg ]] && pass "rembg (tools/cutout.sh)" || fail "rembg missing" "tools/setup.sh"
[[ -x .venv/bin/piper ]] && pass "Piper TTS (tools/voice-draft.sh)" || fail "Piper missing" "tools/setup.sh"
[[ -x .venv-voice/bin/python ]] && pass "Voice cloning (tools/voice-clone)" || opt "voice cloning not installed" "tools/setup.sh --voice-clone"
[[ -x tools/graphics/animated/node_modules/.bin/hyperframes ]] && pass "Animated graphics (tools/graphic --animate)" || opt "animated graphics not installed" "tools/setup.sh --animated-graphics"

echo "Node"
command -v node >/dev/null && pass "node $(node -v)" || fail "node missing" "brew install node"
[[ -d node_modules/playwright && -d node_modules/shiki && -d node_modules/mermaid ]] \
  && pass "graphics engine (tools/graphic)" || fail "graphics engine not installed" "tools/setup.sh"
[[ -d animations/node_modules/@motion-canvas/core ]] \
  && pass "Motion Canvas (animations/)" || fail "Motion Canvas not installed" "tools/setup.sh"

echo "Config"
python3 tools/vwconfig.py show >/dev/null 2>&1 && pass "config.toml loads" || fail "config.toml has an error" "python3 tools/vwconfig.py show"
[[ -f config.local.toml ]] && pass "config.local.toml found (your overrides)" || opt "no config.local.toml" "cp config.local.example.toml config.local.toml"
python3 tools/vwconfig.py styles >/dev/null 2>&1 && pass "styles load ($(python3 tools/vwconfig.py styles | wc -l | tr -d ' ') styles)" || fail "styles have an error" "python3 tools/vwconfig.py styles"
logo=$(python3 tools/vwconfig.py get brand.logo 2>/dev/null)
[[ -z "$logo" || -f "$logo" ]] && pass "brand settings" || fail "brand.logo file not found: $logo" "fix [brand].logo in config.local.toml"

echo
[[ $ok == 0 ]] && echo "All good." || echo "Fix the items marked ✗ above (most are fixed by tools/setup.sh)."
exit $ok
