"""Composite the app render onto the phone's dark screen, frame by frame.

The trick that makes this hold up without motion tracking: the screen was generated as
*pure black* (max channel <= 7, against navy cabinets at 37), so the black connected
component IS the screen's exact silhouette in every frame. Using it as the alpha channel
gives rounded corners, the slight phone tilt, and finger occlusion for free -- the
fingers are skin-coloured, so they are not in the mask and stay on top.

Usage: composite.py <frame_dir> <screen.png> <out_dir> <n> <seed_x> <seed_y> [thresh]
"""
import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageFilter, ImageEnhance

FRAME_DIR, SCREEN_PNG, OUT_DIR = sys.argv[1], sys.argv[2], sys.argv[3]
N = int(sys.argv[4])
seed = (int(sys.argv[5]), int(sys.argv[6]))
THRESH = int(sys.argv[7]) if len(sys.argv) > 7 else 16
WIN = 260

os.makedirs(OUT_DIR, exist_ok=True)
screen_src = Image.open(SCREEN_PNG).convert("RGB")


def component_mask(full, sx, sy, w, h):
    """Boolean full-frame mask of the black component containing (sx, sy)."""
    wx0, wx1 = max(0, sx - WIN), min(w, sx + WIN)
    wy0, wy1 = max(0, sy - WIN), min(h, sy + WIN)
    win = full[wy0:wy1, wx0:wx1]
    lx, ly = sx - wx0, sy - wy0

    if not (0 <= lx < win.shape[1] and 0 <= ly < win.shape[0] and win[ly, lx]):
        got = None
        for r in range(3, 80, 3):
            y0, y1 = max(0, ly - r), min(win.shape[0], ly + r)
            x0, x1 = max(0, lx - r), min(win.shape[1], lx + r)
            sub = win[y0:y1, x0:x1]
            if sub.any():
                ys, xs = np.where(sub)
                k = len(xs) // 2
                got = (x0 + int(xs[k]), y0 + int(ys[k]))
                break
        if got is None:
            return None, None
        lx, ly = got

    seen = np.zeros_like(win, dtype=bool)
    seen[ly, lx] = True
    q = deque([(lx, ly)])
    pts = []
    while q:
        x, y = q.popleft()
        pts.append((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if (0 <= nx < win.shape[1] and 0 <= ny < win.shape[0]
                    and win[ny, nx] and not seen[ny, nx]):
                seen[ny, nx] = True
                q.append((nx, ny))
    if len(pts) < 400:
        return None, None

    mask = np.zeros((h, w), dtype=bool)
    mask[wy0:wy1, wx0:wx1] = seen
    xs = np.array([p[0] for p in pts]) + wx0
    ys = np.array([p[1] for p in pts]) + wy0
    return mask, (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()),
                  int(xs.mean()), int(ys.mean()))


missing = []
for i in range(1, N + 1):
    frame = Image.open(f"{FRAME_DIR}/{i:04d}.png").convert("RGB")
    w, h = frame.size
    arr = np.asarray(frame, dtype=np.int16)
    full = arr.max(axis=2) <= THRESH

    mask, box = component_mask(full, seed[0], seed[1], w, h)
    if mask is None:
        missing.append(i - 1)
        frame.save(f"{OUT_DIR}/{i:04d}.png")
        continue

    x0, y0, x1, y1, cx, cy = box
    seed = (cx, cy)
    bw, bh = x1 - x0 + 1, y1 - y0 + 1

    # The black core sits just inside the glass; grow a touch so the render reaches the bezel.
    pad_x, pad_y = max(1, round(bw * 0.06)), max(1, round(bh * 0.03))
    dx0, dy0 = x0 - pad_x, y0 - pad_y
    dw, dh = bw + pad_x * 2, bh + pad_y * 2

    render = screen_src.resize((dw, dh), Image.LANCZOS)
    layer = Image.new("RGB", (w, h), (0, 0, 0))
    layer.paste(render, (dx0, dy0))

    # Feather the silhouette so the edge does not alias against the bezel.
    alpha = Image.fromarray((mask * 255).astype(np.uint8), mode="L")
    alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))

    out = Image.composite(layer, frame, alpha)

    # A lit screen is brighter than its surroundings; lift it slightly inside the mask only.
    lifted = ImageEnhance.Brightness(out).enhance(1.06)
    out = Image.composite(lifted, out, alpha)

    out.save(f"{OUT_DIR}/{i:04d}.png")

print(f"composited {N - len(missing)} of {N} frames")
if missing:
    print("no screen found (left untouched):", missing)
