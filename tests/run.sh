#!/bin/bash
# Test tools for Bramble's Snack Heist. Each one opens index.html in headless Chrome with ?test,
# which seeds every random roll and turns off saving, so the same build always gives the same result.
#
#   tests/run.sh shots [git-ref]   Render every area in the morning, at dusk and at night into tests/out/new.
#                                  With a ref (HEAD, HEAD~1, a commit), also render that version into
#                                  tests/out/old and write tests/out/report.html comparing the two.
#                                  (Versions from before test mode existed can't be rendered.)
#   tests/run.sh shot pond@19.5 [scene]
#                                  Render one area at one hour to tests/out/new/pond@19.5.png; a scene
#                                  (wary, mud, bend: see SCENES in index.html) sets up a moment first.
#   tests/run.sh sim [seeds]       Simulate a whole day (default: seeds 7, 11 and 23) and list campers who
#                                  are very late, stuck, piled up, or walking through water or walls.
#   tests/run.sh gaps              List trail stretches and patches of woods with no landmark in view.
#   tests/run.sh audio [place@h]   Render the music and ambience offline at each place (or one), measure levels,
#                                  masking, low end and key, and save a spectrogram per place to tests/out/audio.
set -euo pipefail
cd "$(dirname "$0")/.."
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
OUT=tests/out
AREAS=(den lookout meadow camp shack ranger sunset amphi rv pond mill arch falls shore homestead)
HOURS=(9 19.6 22.5)
EXTRA=(pond@13 amphi@19 camp@21.5)

chrome() {
  local profile; profile=$(mktemp -d)
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --mute-audio --no-first-run \
    --force-device-scale-factor=1 --window-size=1024,768 --user-data-dir="$profile" \
    --virtual-time-budget=4000 "$@" 2>/dev/null || true
  rm -rf "$profile"
}
page() { echo "file://$PWD/$1?test&$2"; }
text_report() { chrome --dump-dom "$(page index.html "$1")" | python3 -c '
import sys, html, re
m = re.search(r"<pre id=\"testReport\">(.*?)</pre>", sys.stdin.read(), re.S)
print(html.unescape(m.group(1)) if m else "No report: the page did not finish. Open index.html?test&'"$1"' in a browser to see the error.")'; }
render_all() { # html-file out-dir
  mkdir -p "$2"
  local specs=() jobs=0
  for a in "${AREAS[@]}"; do for h in "${HOURS[@]}"; do specs+=("$a@$h"); done; done
  specs+=("${EXTRA[@]}")
  for s in "${specs[@]}"; do
    chrome --screenshot="$2/$s.png" "$(page "$1" "shot=$s")" >/dev/null &
    jobs=$((jobs + 1)); if (( jobs % 4 == 0 )); then wait; fi
  done
  wait
  echo "Rendered ${#specs[@]} shots into $2"
}

case "${1:-}" in
  shots)
    rm -rf "$OUT/new" "$OUT/old"
    render_all index.html "$OUT/new"
    if [[ -n "${2:-}" ]]; then
      git show "$2:index.html" > "$OUT/old.html"
      render_all "$OUT/old.html" "$OUT/old"
      python3 -I tests/compare.py "$OUT/old" "$OUT/new" "$OUT/report.html"
    fi ;;
  shot)
    name="$2${3:+-$3}"; mkdir -p "$OUT/new"
    chrome --screenshot="$OUT/new/$name.png" "$(page index.html "shot=$2${3:+&scene=$3}")" >/dev/null
    echo "$OUT/new/$name.png" ;;
  sim) for seed in ${2:-7 11 23}; do echo "== seed $seed"; text_report "sim&seed=$seed"; echo; done ;;
  gaps) text_report gaps ;;
  audio)
    rm -rf "$OUT/audio"; mkdir -p "$OUT/audio"
    port=8766; python3 -I tests/receiver.py $port & server=$!
    profile=$(mktemp -d)
    "$CHROME" --headless=new --disable-gpu --mute-audio --no-first-run --user-data-dir="$profile" --remote-debugging-port=0 \
      "http://127.0.0.1:$port/index.html?test&audio=${2:-all}" >/dev/null 2>&1 & browser=$!
    python3 -c "import os, time; [time.sleep(.5) for _ in range(240) if not os.path.exists('$OUT/audio/done')]"
    kill $browser $server 2>/dev/null || true; wait 2>/dev/null || true; rm -rf "$profile"
    if [[ -f "$OUT/audio/report.txt" ]]; then cat "$OUT/audio/report.txt"; echo "Figures: $OUT/audio/*.png"; else echo "No report: open http://127.0.0.1:$port/index.html?test&audio=all with tests/receiver.py running to see the error."; fi ;;
  *) sed -n '2,17p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
