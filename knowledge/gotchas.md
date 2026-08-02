# Gotchas — read before burning credits

API quirks + lessons from the PermitNav production run (June 2026). Sources:
[api-reference.md §10](api-reference.md), `permit-nav-team/video-generation`.

## Money & retention

- **Output URLs live 24 hours.** `video_url` / `last_frame_url` expire — download immediately
  (`seedance.py` does this automatically). A "successful" task you forgot to download is money gone.
- **Task IDs live 7 days.** The List endpoint also only sees the past 7 days.
- **No balance API.** Balance is console-only: <https://console.byteplus.com/finance>.
- **`flex` (50% price) tier is NOT available on 2.0/2.0-fast** — `default` pricing only.
- One 720p clip ≈ ~109k completion tokens (order of magnitude for budgeting).
- Iterate on `--fast` at 720p; render finals on the full model. Same seed + same inputs is
  deterministic, so a good fast take can guide the final.

## Hard restrictions

- **No real human faces as references.** Direct uploads of real-person photos/videos are
  rejected. Workarounds: the console's digital-character library, authorized real-person
  assets (verification required), or **trusted prior outputs** — face-containing videos YOUR
  account generated in the last 30 days can be re-fed via `asset://<ID>`.
- **Audio can never be the only reference** — pair it with an image or video.
- **Mode mutual exclusion:** `first_frame`/`last_frame` (I2V) and `reference_image` (R2V)
  cannot coexist in one request.
- **2.0/2.0-fast do NOT support:** `frames` (use `duration` 4–15 or `auto`), `camera_fixed`,
  `draft` mode (1.5-pro only), `flex` tier. **2.0-fast has no 1080p.**
- **Base64 never for video**; for images it's fine but keep the request body under 64MB
  (per-file caps: image 30MB, video 50MB, audio 15MB).
- Asset dimensions: images/videos 300–6000px per side, aspect between 0.4 and 2.5;
  video clips 2–15s each, ≤3 clips, ≤15s combined.

## Production lessons (PermitNav run)

- **On-screen text is unreliable** — it doubled a caption in production. Generate clean
  scenes and **burn captions in post** (ffmpeg) for anything brand-critical.
- **Last-frame chaining works.** `return_last_frame: true`, then feed the PNG as the next
  clip's `first_frame` with a prompt starting "Continue from the opening frame — the same
  woman at the same kitchen table…". Kept one actress + kitchen across three beats.
  Re-state palette/lighting each time or it drifts.
- **Native audio is good** — ambient + a described music cue came out usable; ElevenLabs was
  only needed for precise brand VO (Seedance VO timing is roughly right, not frame-exact).
- **Pin seeds** (`seed: 42`) once a look is close — makes retries comparable.
- **Cost constant:** fast @720p ≈ **21.7k tokens/second**, linear (5s = 108.9k, 8s = 173.7k).
- **Master frames anchor the camera axis.** A frame attached as a reference pins
  composition AND side; reverse angles need explicit axis-cross language — see
  prompt-guide "Coverage" (T1.2: passive reverse failed, explicit pass).
- **Two-character scenes work** (T1.1: zero identity bleed, correct dialogue
  turn-taking) — at least with strongly distinct character anchors.

## Operational details

- Status flow: `queued → running → succeeded|failed|expired`; only `queued` tasks can be
  cancelled; DELETE on a finished task erases the record permanently.
- `expired` = task sat past `execution_expires_after` (default 48h) — rare, but re-submit.
- `ratio: adaptive` resolves from prompt + first media; read the final ratio from Retrieve.
- Watermark defaults **off**.
- English prompts: keep ≤1000 words — longer gets truncated.
- Errors come as `{ "error": { "code", "message" } }`; a `failed` task carries the same
  object in its Retrieve response.
