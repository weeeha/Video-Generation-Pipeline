#!/usr/bin/env bash
# Cut the three Mtl63 Silo No. 5 test shots into one clip with short dissolves.
#
# Reads output/silo5-s01.mp4, silo5-s02.mp4, silo5-s03.mp4 (the names the slate README
# uses) and writes output/silo5-assembly.mp4. Dissolve length is 12 frames at 24 fps
# (0.5 s) on both picture and native audio; offsets come from the real clip durations
# so a 4.96 s clip does not leave a hold frame.
#
# Usage: bash pipeline/post/assemble_silo5.sh [out.mp4] [clip1 clip2 clip3]
set -euo pipefail

OUT="${1:-output/silo5-assembly.mp4}"
if [ "$#" -ge 4 ]; then
  CLIPS=("$2" "$3" "$4")
else
  CLIPS=(output/silo5-s01.mp4 output/silo5-s02.mp4 output/silo5-s03.mp4)
fi
XF=0.5   # seconds; 12 frames at 24 fps

for c in "${CLIPS[@]}"; do
  [ -f "$c" ] || { echo "missing clip: $c" >&2; exit 1; }
done

dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"; }
D1=$(dur "${CLIPS[0]}")
D2=$(dur "${CLIPS[1]}")
# xfade offset = where the dissolve starts on the running timeline
OFF1=$(python3 -c "print(round($D1 - $XF, 3))")
OFF2=$(python3 -c "print(round($D1 + $D2 - 2 * $XF, 3))")

ffmpeg -v error -y \
  -i "${CLIPS[0]}" -i "${CLIPS[1]}" -i "${CLIPS[2]}" \
  -filter_complex "
    [0:v][1:v]xfade=transition=fade:duration=$XF:offset=$OFF1[v01];
    [v01][2:v]xfade=transition=fade:duration=$XF:offset=$OFF2[v];
    [0:a][1:a]acrossfade=d=$XF[a01];
    [a01][2:a]acrossfade=d=$XF[a]" \
  -map "[v]" -map "[a]" \
  -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p \
  -c:a aac -b:a 192k -movflags +faststart \
  "$OUT"

echo "wrote $OUT ($(dur "$OUT") s)"
