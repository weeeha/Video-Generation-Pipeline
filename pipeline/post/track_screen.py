"""Track the phone screen as the pure-black connected component containing a seed point.

Measured on this take, the screen is the only genuinely black thing in frame: its max
channel is <= 7, while the navy cabinets read 37 and the dark doorway 50-59. Thresholding
at 16 isolates the screen almost alone -- but "almost", so a global bounding box still
spans the frame and we need the connected component.

BFS runs inside a window around the seed rather than the whole frame: the component is
~20k pixels, so this stays fast, and it cannot leak into unrelated black regions far away.
The seed follows the previous frame's centroid, tracking slow hand drift.

Usage: track_black.py <frame_dir> <out.json> <n> <seed_x> <seed_y> [thresh] [win]
"""
import sys
import json
from collections import deque

import numpy as np
from PIL import Image

FRAME_DIR, OUT_JSON = sys.argv[1], sys.argv[2]
N = int(sys.argv[3])
seed = (int(sys.argv[4]), int(sys.argv[5]))
THRESH = int(sys.argv[6]) if len(sys.argv) > 6 else 16
WIN = int(sys.argv[7]) if len(sys.argv) > 7 else 260


def component(mask, sx, sy):
    """BFS from (sx, sy) over True pixels; returns list of (x, y)."""
    h, w = mask.shape
    if not mask[sy, sx]:
        return []
    seen = np.zeros_like(mask, dtype=bool)
    seen[sy, sx] = True
    q = deque([(sx, sy)])
    pts = []
    while q:
        x, y = q.popleft()
        pts.append((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((nx, ny))
    return pts


def nudge(mask, sx, sy):
    """Find the nearest masked pixel to the seed, searching outward."""
    h, w = mask.shape
    if 0 <= sx < w and 0 <= sy < h and mask[sy, sx]:
        return sx, sy
    for r in range(3, 80, 3):
        y0, y1 = max(0, sy - r), min(h, sy + r)
        x0, x1 = max(0, sx - r), min(w, sx + r)
        sub = mask[y0:y1, x0:x1]
        if sub.any():
            ys, xs = np.where(sub)
            k = len(xs) // 2
            return x0 + int(xs[k]), y0 + int(ys[k])
    return None


rows = []
for i in range(1, N + 1):
    arr = np.asarray(Image.open(f"{FRAME_DIR}/{i:04d}.png").convert("RGB"), dtype=np.int16)
    h, w = arr.shape[:2]
    full = arr.max(axis=2) <= THRESH

    sx, sy = seed
    wx0, wx1 = max(0, sx - WIN), min(w, sx + WIN)
    wy0, wy1 = max(0, sy - WIN), min(h, sy + WIN)
    win = full[wy0:wy1, wx0:wx1]

    got = nudge(win, sx - wx0, sy - wy0)
    if got is None:
        rows.append({"frame": i - 1, "found": False})
        continue
    pts = component(win, *got)
    if len(pts) < 400:
        rows.append({"frame": i - 1, "found": False})
        continue

    xs = np.array([p[0] for p in pts]) + wx0
    ys = np.array([p[1] for p in pts]) + wy0
    x0, x1 = int(xs.min()), int(xs.max())
    y0, y1 = int(ys.min()), int(ys.max())
    bw, bh = x1 - x0 + 1, y1 - y0 + 1
    rows.append({"frame": i - 1, "found": True, "x": x0, "y": y0, "w": bw, "h": bh,
                 "area": len(pts), "fill": round(len(pts) / (bw * bh), 3)})
    seed = (int(xs.mean()), int(ys.mean()))

json.dump(rows, open(OUT_JSON, "w"), indent=1)
f = [r for r in rows if r["found"]]
print(f"found {len(f)} of {len(rows)}")
if f:
    for label, r in (("first", f[0]), ("mid", f[len(f) // 2]), ("last", f[-1])):
        print(f"  {label}: x={r['x']} y={r['y']} w={r['w']} h={r['h']} "
              f"area={r['area']} fill={r['fill']}")
    print("  x", min(r['x'] for r in f), "..", max(r['x'] for r in f),
          " y", min(r['y'] for r in f), "..", max(r['y'] for r in f))
    print("  w", min(r['w'] for r in f), "..", max(r['w'] for r in f),
          " h", min(r['h'] for r in f), "..", max(r['h'] for r in f))
    print("  fill", min(r['fill'] for r in f), "..", max(r['fill'] for r in f))
miss = [r['frame'] for r in rows if not r['found']]
if miss:
    print("MISSING:", miss)
