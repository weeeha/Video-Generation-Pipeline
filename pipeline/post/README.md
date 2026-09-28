# Post-processing

Two things Seedance should not be asked to do, done in post instead: putting legible UI on a
phone screen, and making a clip loop without a snap.

## The black-screen trick

`knowledge/gotchas.md` says on-screen text is the least reliable feature and brand-critical
detail belongs in post. That applies to a phone screen too — but compositing normally needs
motion tracking, which we don't have.

The workaround is to make tracking unnecessary. Prompt the phone's screen as **switched fully
off, a flat matte-black rectangle**, and the model renders it at effectively zero luminance.
Measured on a recreation shot: the screen's max RGB channel was **≤ 7**, while the navy
cabinets right behind it sat at **37** and the dark doorway at **50–59**. Thresholding at 16
isolates the screen and almost nothing else.

That gives two things at once:

1. **Location** — the black connected component containing a seed point is the screen.
2. **A matte** — that same silhouette is the alpha channel. Rounded corners, the phone's tilt,
   and fingers overlapping the glass all come out correct for free, because fingers are
   skin-coloured and therefore not in the mask.

It only works if the screen is genuinely the darkest thing in frame. Check before compositing:

```bash
python3 pipeline/post/track_screen.py <frames_dir> screen.json <n> <seed_x> <seed_y>
```

Healthy output is a stable box with `fill` around 0.7+ and found on every frame. If the box
jumps around or `fill` drops, the screen isn't cleanly separable — a phone held at an angle
catches enough light to break it. Restage the shot rather than fighting it.

## Scripts

| Script | Does |
|--------|------|
| `make_screen.py` | Builds the phone-screen asset from a place pack's after-plate. Run from the repo root. |
| `track_screen.py` | Finds the screen in every frame; use it to verify separability before compositing. |
| `composite_screen.py` | Composites the screen asset onto the phone, using the black silhouette as alpha. |
| `make_loop.py` | Cross-dissolves a clip's tail into its head to produce a seamless loop. |

## Seamless loops

Generate longer than you ship. For a 5s loop, generate 6s and dissolve the extra second into
the head: the only remaining join is between two frames that were adjacent in the source.

```bash
ffmpeg -v error -y -i take.mp4 frames/%04d.png
python3 pipeline/post/make_loop.py frames loop 145 120 24
ffmpeg -y -framerate 24 -i loop/%04d.png -c:v libx264 -pix_fmt yuv420p \
       -crf 18 -preset slow -movflags +faststart -an out.mp4
```

Verify it rather than trusting it. A loop is seamless when the last→first frame difference is
no bigger than an ordinary frame-to-frame step. On a real client hero-video teardown that ratio
was **6.46×** (the visible snap); after this treatment it was **0.31×**.
