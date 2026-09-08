# Gotchas — read before burning credits

API quirks + lessons from the PermitNav production run (June 2026). Sources:
[api-reference.md §10](api-reference.md), `permit-nav-team/video-generation`.

## Money & retention

- **Output URLs live 24 hours.** `video_url` / `last_frame_url` expire — download immediately
  (`seedance.py` does this automatically). A "successful" task you forgot to download is money gone.
- **Task IDs live 7 days.** The List endpoint also only sees the past 7 days.
- **No balance API.** Balance is console-only: <https://console.byteplus.com/finance>.
- **`flex` (50% price) tier is NOT available on 2.0/2.0-fast** — `default` pricing only.
- **Seedance 2.5 costs ≈ +50% over 2.0** and has an **activation gate**: balance > USD 30,
  an AI Savings Plan ≥ the USD 30 tier, or a 2.5 resource pack — otherwise creates fail.
- One 720p clip ≈ ~109k completion tokens (order of magnitude for budgeting; 2.0 numbers).
- Iterate on `--fast` (or `--model mini`) at 720p; render finals on 2.5. Same seed + same
  inputs is deterministic, so a good fast take can guide the final.

## Hard restrictions

- **No real human faces as references.** Direct uploads of real-person photos/videos are
  rejected. Workarounds: the console's digital-character library, authorized real-person
  assets (verification required), or **trusted prior outputs** — face-containing videos YOUR
  account generated in the last 30 days can be re-fed via `asset://<ID>`.
- **Audio can never be the only reference on the 2.0 series** — pair it with an image or
  video. (2.5 allows audio-only references.)
- **Mode mutual exclusion:** `first_frame`/`last_frame` (I2V) and `reference_image` (R2V)
  cannot coexist in one request.
- **2.0/2.0-fast do NOT support:** `frames` (use `duration` 4–15 or `auto`), `camera_fixed`,
  `draft` mode (1.5-pro only), `flex` tier. **2.0-fast has no 1080p.**
- **Base64 never for video**; for images it's fine but keep the request body under 64MB
  (per-file caps: image 30MB, video 50MB, audio 15MB).
- Asset dimensions: images/videos 300–6000px per side, aspect between 0.4 and 2.5.
  Video clips: 2.0 → 2–15s each, ≤3 clips, ≤15s combined; 2.5 → 4–30s each (edit sources
  must be 4–30s), ≤10 clips, ≤30s combined.
- **2.5 task constraints bite.** Edit/extend/first-frame tasks require `ratio: adaptive`
  (edit also `duration: -1`), and edit/extend prompts MUST contain intent keywords
  ("edit/add/remove/replace", "extend/continue") or the task fails async with
  `InvalidParameter.TaskTypeMismatch` / `.TaskTypeConstraint`. `seedance.py` enforces the
  parameter side client-side; the keywords are on you.
- **2.5 1080p output is 10-bit H.265/HEVC** — some players/pipelines can't read it. VLC,
  mpv, QuickTime work; use 720p (or `--format mov`) when compatibility matters.

## 2.5 craft lessons (community, Sept 2026)

Collected from creator guides and reviews; sources in
[prompt-guide.md](prompt-guide.md#sources-community-craft-sept-2026). Rules for
applying them are in the prompt guide; this is the list of what bites.

- **2.0 prompts break on 2.5.** Testers report glitchy, visibly broken output when a
  working 2.0 prompt is re-run unchanged. Re-prompt with timeline blocks and scoped
  references; do not port.
- **30 seconds is time, not events.** Without timestamps the model spends the opening
  well and drifts or rushes the end. Always describe the final frame.
- **Morphing in fast action is still there** on 2.5 and no upscaler hides it. Slow the
  action down, or plan to cut around it.
- **Props render at the wrong scale** occasionally (a book the size of a suitcase), and
  **body proportions drift between shots** even when the face holds. QA silhouette,
  height, wardrobe, accessories and relative scale, not just the face. Small accessories
  vanish first.
- **Multi-character scenes are the weakest area:** relative scale and positioning wander.
  Lock positions in the prompt ("keep her in the left third of frame").
- **More references means more drift.** Two angle-matched images beat six. Mixing a
  frontal with a profile makes the model invent features.
- **Voice is inferred from the reference images** and the wording is fragile: "American"
  fixed an accent where "American English" pushed it British.
- **Input order is not shot order** when first-frame and omni references are mixed.
  Restate the sequence in the prompt text.
- **A 30s take usually holds several usable segments.** Cut around a flaw in post before
  paying for a regenerate; if 24 of 30 seconds work, fix that beat and keep the seed.
- **Draft on fast, finish on 2.5.** 2.5 wins on character consistency, expressions and
  dialogue scenes; one head-to-head still had 2.0 cleaner on mechanical product
  transformations, so test both for product work.

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

## Operational details

- Status flow: `queued → running → succeeded|failed|expired`; only `queued` tasks can be
  cancelled; DELETE on a finished task erases the record permanently.
- `expired` = task sat past `execution_expires_after` (default 48h) — rare, but re-submit.
- `ratio: adaptive` resolves from prompt + first media; read the final ratio from Retrieve.
- Watermark defaults **off**.
- English prompts: keep ≤1000 words — longer gets truncated.
- Errors come as `{ "error": { "code", "message" } }`; a `failed` task carries the same
  object in its Retrieve response.
