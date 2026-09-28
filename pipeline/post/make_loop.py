"""Turn a 6s take into a seamless ~5s loop by cross-dissolving its tail into its head.

The original hero video hard-cuts from a wide finished kitchen back to a tight derelict
one every 5 seconds. Generating one second of overlap and dissolving it away removes that
snap: the only real join left is src[L-1] -> src[L], which is continuous motion.

  out[i] = src[i]                                              for i >= overlap
  out[i] = src[i]*(i/overlap) + src[i+L]*(1 - i/overlap)       for i <  overlap

Usage: make_loop.py <in_dir> <out_dir> <n_src> <out_len> <overlap>
"""
import os
import sys

import numpy as np
from PIL import Image

IN_DIR, OUT_DIR = sys.argv[1], sys.argv[2]
N = int(sys.argv[3])
L = int(sys.argv[4])
OVER = int(sys.argv[5])

if L + OVER > N:
    sys.exit(f"need {L + OVER} source frames for out_len={L} overlap={OVER}, have {N}")

os.makedirs(OUT_DIR, exist_ok=True)

for i in range(L):
    base = Image.open(f"{IN_DIR}/{i + 1:04d}.png").convert("RGB")
    if i >= OVER:
        base.save(f"{OUT_DIR}/{i + 1:04d}.png")
        continue
    tail = Image.open(f"{IN_DIR}/{i + L + 1:04d}.png").convert("RGB")
    a = i / OVER
    blended = (np.asarray(base, dtype=np.float32) * a
               + np.asarray(tail, dtype=np.float32) * (1.0 - a))
    Image.fromarray(blended.round().astype(np.uint8)).save(f"{OUT_DIR}/{i + 1:04d}.png")

print(f"wrote {L} frames to {OUT_DIR} (overlap {OVER} frames dissolved)")
