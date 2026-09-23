#!/bin/zsh
# Export EP1 figures (web/figures.html) to analysis/figures/*.png with headless Chrome.
#   zsh analysis/export_figures.sh            # serves web/ on 127.0.0.1:8766 if nothing is there yet
set -euo pipefail
HERE=${0:A:h}
WEB=$HERE/../web
OUT=$HERE/figures
PORT=8766
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$OUT"

if ! curl -s -o /dev/null "http://127.0.0.1:$PORT/figures.html"; then
  (cd "$WEB" && python3 -m http.server $PORT --bind 127.0.0.1 >/dev/null 2>&1) &
  SERVER=$!
  trap 'kill $SERVER' EXIT
  sleep 1
fi

for spec in A:16x9 A:9x16 C:16x9 C:9x16 D:16x9 E:16x9 A:3x4 G:3x4 D:3x4 K:3x4 T:3x4; do
  fig=${spec%%:*}; ratio=${spec##*:}
  case $ratio in
    16x9) size=1920,1080 ;;
    9x16) size=1080,1920 ;;
    3x4)  size=1080,1440 ;;
  esac
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --window-size=$size --virtual-time-budget=8000 \
    --screenshot="$OUT/$fig-$ratio.png" "http://127.0.0.1:$PORT/figures.html?fig=$fig&ratio=$ratio" 2>/dev/null
  echo "$OUT/$fig-$ratio.png"
done
