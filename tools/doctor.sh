#!/usr/bin/env bash
# Check that everything the workflow needs is installed and the config is valid.
# Usage: tools/doctor.sh
cd "$(dirname "$0")/.."
ok=0
pass() { printf "  \033[32m✓\033[0m %s\n" "$1"; }
fail() { printf "  \033[31m✗\033[0m %s\n      fix: %s\n" "$1" "$2"; ok=1; }

echo "Apps and tools"
[[ -d /Applications/kdenlive.app ]] && pass "Kdenlive" || fail "Kdenlive not found" "brew install --cask kdenlive"
for t in ffmpeg ffprobe auto-editor whisper; do
  pkg=$t; [[ $t == ffprobe ]] && pkg=ffmpeg; [[ $t == whisper ]] && pkg=openai-whisper
  command -v $t >/dev/null && pass "$t" || fail "$t missing" "brew install $pkg"
done
. tools/_lib.sh; set +e +u
ff=$(ffmpeg_libass) && pass "caption burning available ($ff)" \
  || fail "no ffmpeg with libass (needed only for tools/burn-captions.sh)" "brew install ffmpeg-full   (or burn captions in Kdenlive instead)"

echo "Python"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 11))' \
  && pass "python3 $(python3 -c 'import platform; print(platform.python_version())')" \
  || fail "Python 3.11+ needed (for tomllib)" "brew install python"

echo "Config"
python3 tools/vwconfig.py show >/dev/null 2>&1 && pass "config.toml loads" || fail "config.toml has an error" "python3 tools/vwconfig.py show"
[[ -f config.local.toml ]] && pass "config.local.toml found (your overrides)" || echo "  - no config.local.toml (optional: cp config.local.example.toml config.local.toml)"
python3 tools/vwconfig.py styles >/dev/null 2>&1 && pass "styles load ($(python3 tools/vwconfig.py styles | wc -l | tr -d ' ') styles)" || fail "styles have an error" "python3 tools/vwconfig.py styles"

echo
[[ $ok == 0 ]] && echo "All good." || echo "Fix the items marked ✗ above."
exit $ok
