#!/usr/bin/env bash
# Montreal previs batch: one 5 s 720p clip per scene prompt, Seedance 2.5 only (pack tokens).
# Usage: scripts/run-montreal-previs.sh [prompt files...]   (default: all of pipeline/prompts/montreal/sc*.md)
# Runs 3 at a time. Each clip logs to output/mtl-scNN.log; a summary line prints as each finishes.
set -u
cd "$(dirname "$0")/.."
files=("$@"); [ ${#files[@]} -eq 0 ] && files=(pipeline/prompts/montreal/sc*.md)
run_one() {
  local f="$1" n
  n="mtl-$(basename "$f" .md | cut -d- -f1)"
  .venv/bin/python pipeline/seedance.py generate --prompt-file "$f" --name "$n" \
    --model full --duration 5 --resolution 720p --ratio 16:9 > "output/$n.log" 2>&1
  echo "$n exit=$? $(grep -io 'completion_tokens[^,}]*' "output/$n.log" | tail -1)"
}
for f in "${files[@]}"; do
  while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 5; done
  run_one "$f" &
done
wait
