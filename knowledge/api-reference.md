# Seedance 2.0 (BytePlus ModelArk) — API Reference

This is a consolidated developer reference for the **Dreamina Seedance 2.0 series** video-generation models on **BytePlus ModelArk**. It covers the four task endpoints, asset rules, generation modes, prompt templates, joint audio generation, output handling, code samples, and known gotchas. Sources: ModelArk docs pages 1520757 (Create), 1521309 (Retrieve), 2291680 (Tutorial), 2222480 (Prompt guide).

---

## 1. Overview

The Seedance 2.0 series is a multimodal video-generation model family that can produce video clips from text, image, video, and audio references — including **native joint audio + video** generation in a single call (the model produces visuals and a synchronized soundtrack — voice/dubbing/SFX/music — in one shot).

**Model IDs**

| Model | Model ID | Notes |
| --- | --- | --- |
| Dreamina Seedance 2.0 | `dreamina-seedance-2-0-260128` | Full model. Supports 480p / 720p / 1080p. |
| Dreamina Seedance 2.0 Fast | `dreamina-seedance-2-0-fast-260128` | Faster / cheaper. **No 1080p.** |

Other Seedance models referenced in the same docs (legacy / for context): `seedance-1-0-pro`, `seedance-1-0-pro-fast`, `seedance-1-0-lite-i2v`, `seedance-1-0-lite-t2v`, `seedance-1-5-pro` (the only one supporting **draft mode**). This reference focuses on **2.0 series**.

**Capabilities** of 2.0 series:

- Text-to-Video (T2V), Image-to-Video (I2V), Reference-to-Video (R2V), Video-to-Video (V2V).
- Native joint audio-video output (`generate_audio: true`) — voice, ambient SFX, music, dialogue, language matched to prompt language; subtitles synchronized.
- Multimodal input: up to 9 reference images, up to 3 reference videos (≤15 s combined), up to 3 reference audio clips. Total 12 files per request.
- Video editing: add / remove / modify elements; extend forward / backward; track-completion (stitching).
- Prompt languages: English (all models) and Chinese (Seedance 2.0 / 2.0 Fast). Other languages partially supported via dialogue/subtitle text in prompts.
- Real-human-face uploads are **blocked** — see `Trusted outputs as input assets` workaround in §4.

---

## 2. Authentication & Base URL

```
Base URL : https://ark.ap-southeast.bytepluses.com/api/v3
Auth     : Authorization: Bearer $ARK_API_KEY      (only API Key auth supported)
Content-Type: application/json
```

Get / manage API keys at the BytePlus ModelArk console (`console.byteplus.com/ark/region:ark+ap-southeast-1/apikey`). The user already has `ARK_API_KEY` exported.

Region: AP-Southeast-1 (Singapore). All paths in this doc are relative to the base URL above.

---

## 3. Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST`   | `/contents/generations/tasks`        | Create a video generation task (async). |
| `GET`    | `/contents/generations/tasks/{id}`   | Retrieve task status / result. |
| `GET`    | `/contents/generations/tasks`        | List recent tasks. |
| `DELETE` | `/contents/generations/tasks/{id}`   | Cancel a queued task or permanently delete a finished record. |

Tasks are async. The standard flow is **POST -> poll GET until `status` is terminal -> download `content.video_url` within 24 h.**

### 3.1 POST /contents/generations/tasks — Create

Returns immediately with `{ "id": "cgt-..." }`. The task ID is retained for **7 days** from `created_at`.

#### 3.1.1 Top-level request body

| Field | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `model` | string | yes | — | Model ID (e.g. `dreamina-seedance-2-0-260128`) or an endpoint ID. |
| `content` | object[] | yes | — | Array of input items (text / image / video / audio / draft\_task). Combinations below. |
| `generate_audio` | boolean | no | `true` (2.0/2.0-fast/1.5-pro) | `true` = video output has synchronized audio. `false` = silent. |
| `resolution` | string | no | `720p` (2.0/2.0-fast/1.5-pro/1.0-lite); `1080p` (1.0-pro/pro-fast) | `480p`, `720p`, `1080p`. **2.0-fast does not support 1080p.** |
| `ratio` | string | no | `adaptive` (2.0/2.0-fast/1.5-pro) | `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, `adaptive`. |
| `duration` | integer | no | `5` | Seconds. **2.0/2.0-fast: [4, 15]** (or set to `auto` for smart selection). 1.0-pro/pro-fast/lite: [2, 12]. 1.5-pro: [4, 12]. |
| `frames` | integer | no | — | Mutually exclusive with `duration` (`frames` wins if both set). **Not supported by 2.0/2.0-fast/1.5-pro.** Range `[29, 289]` matching `25 + 4n` (n positive int). Formula: `frames = duration × 24`. |
| `seed` | integer | no | `-1` (random) | `[-1, 2^32 - 1]`. Same seed + same inputs → deterministic. |
| `camera_fixed` | boolean | no | `false` | **Not supported by 2.0/2.0-fast.** When supported, appends a fix-camera instruction to the prompt. |
| `watermark` | boolean | no | `false` | `true` = stamp watermark on output. |
| `return_last_frame` | boolean | no | `false` | If `true`, the Retrieve response includes `content.last_frame_url` (PNG, same dims as video). Use to chain multi-segment generations. |
| `callback_url` | string | no | — | HTTPS URL to receive task-completion callbacks. Body matches the Retrieve response. Status values: `queued`, `running`, `succeeded`, `failed`, `expired`. |
| `service_tier` | string | no | `default` | `default` = online inference (lower latency, lower RPM/concurrency). `flex` = offline inference, higher TPD, **50% of online price** (2.0/2.0-fast do **not** support `flex`). Cannot be modified after submit. |
| `execution_expires_after` | integer | no | `172800` (48 h) | Seconds before a non-terminal task auto-expires. Range `[3600, 259200]`. Counted from `created_at`. |
| `safety_identifier` | string | no | — | Stable hashed end-user ID (e.g. SHA-256 of email). Aids platform abuse detection without exposing PII. Echoed in the Retrieve response. |
| `draft` | boolean | no | `false` | **Seedance 1.5 pro only.** Generate a 480p preview video; reuse its task ID later for a final render. |

##### Parameter-passing styles (Upgrade Instructions)

The **new (recommended)** style passes `resolution`, `ratio`, `duration`, `frames`, `seed`, `camera_fixed`, `watermark` as top-level JSON fields with strict validation. The **legacy** style appends them to the text prompt as `--rs 720p --rt 16:9 --dur 5 --seed 11 --cf false --wm true` (or long forms `--resolution`, `--ratio`, `--duration`, `--seed`, `--camera_fixed`, `--watermark`); legacy uses lenient validation (bad params are silently ignored).

#### 3.1.2 `content[]` item types

The `content` array accepts items of these `type` values. Mix per supported combinations.

**Supported combinations** (per content array):

- Text (only)
- Text (optional) + image
- Text (optional) + video
- Text (optional) + image + audio
- Text (optional) + image + video
- Text (optional) + video + audio
- Text (optional) + image + video + audio
- Sample task ID (Seedance 1.5 pro draft mode only)

> **Mutually exclusive scenarios:** Image-to-video (first frame), Image-to-video (first & last frame), and Multimodal reference-to-video (reference image / video / audio) are **three mutually exclusive scenarios** — do not mix `first_frame` / `last_frame` roles with `reference_image` roles in one request.

> **Audio cannot be input alone.** Every request that includes a reference audio item must also include at least one reference image or reference video item.

##### Text item

```json
{ "type": "text", "text": "<prompt>" }
```

- `text` (string, required): the prompt. Chinese + English supported (2.0 / 2.0-fast). English prompts ≤ 1000 words is recommended; long prompts can be truncated.
- See §6 for prompt templates.

##### Image item

```json
{
  "type": "image_url",
  "image_url": { "url": "<URL | data: | asset://...>" },
  "role": "first_frame | last_frame | reference_image"
}
```

- `image_url.url` (string, required): public HTTPS URL **or** Base64 data URI `data:image/<format>;base64,<...>` (format must be lowercase) **or** asset URI `asset://<ASSET_ID>` from the digital character / authorized-real-person library.
- `role` (string, conditionally required) — see decision matrix below.

| Scenario | Required role(s) | Image count | Supported models |
| --- | --- | --- | --- |
| Image-to-video, first frame | `first_frame` (or omit `role`) | 1 | All I2V models |
| Image-to-video, first **and** last frame | `first_frame` + `last_frame` | 2 | seedance 2.0, 1.5 pro, 1.0 pro, 1.0 lite i2v |
| Multimodal reference-to-video (R2V) | `reference_image` (each image) | 1–9 | seedance 2.0 (1–9), 1.0 lite i2v (1–4) |

Notes:
- First-frame and last-frame images can be the same.
- If the first / last image aspect ratios differ, the **first frame** image's aspect ratio takes precedence.
- For multi-image reference, prompts should disambiguate with `[Image 1]xxx, [Image 2]xxx`.

##### Video item (Seedance 2.0 / 2.0 fast only)

```json
{
  "type": "video_url",
  "video_url": { "url": "<URL | asset://...>" },
  "role": "reference_video"
}
```

- `video_url.url` (string, required): only **public URL** or `asset://<ASSET_ID>` — Base64 is **not supported** for video.
- `role` (string, conditionally required): currently only `reference_video`.
- Trust note: face-containing videos previously generated by 2.0 / 2.0 fast can be re-fed as input.

##### Audio item (Seedance 2.0 / 2.0 fast only)

```json
{
  "type": "audio_url",
  "audio_url": { "url": "<URL | data:audio/wav;base64,... | asset://...>" },
  "role": "reference_audio"
}
```

- `audio_url.url` (string, required): URL, Base64 data URI (`data:audio/<format>;base64,<...>`), or asset URI.
- `role` (string, conditionally required): currently only `reference_audio`.
- **Audio cannot be input alone** — must accompany at least one image or video.

##### Sample / Draft item (Seedance 1.5 pro only)

```json
{
  "type": "draft_task",
  "draft_task": { "id": "<draft task id>" }
}
```

When you pass a `draft_task` reference, the platform automatically reuses the draft's `model`, `content.text`, `content.image_url`, `generate_audio`, `seed`, `ratio`, `duration`, `frames`, `camera_fixed` to render the standard video; you may override any other parameter.

#### 3.1.3 Aspect-ratio pixel dimensions (Seedance 2.0 & 2.0 fast)

| Resolution | 16:9 | 4:3 | 1:1 | 3:4 | 9:16 | 21:9 |
| --- | --- | --- | --- | --- | --- | --- |
| 480p | 864×496 | 752×560 | 640×640 | 560×752 | 496×864 | 992×432 |
| 720p | 1280×720 | 1112×834 | 960×960 | 834×1112 | 720×1280 | 1470×630 |
| 1080p | 1920×1080 | 1664×1248 | 1440×1440 | 1248×1664 | 1080×1920 | 2206×946 |

(For Seedance 1.0 series the 16:9 720p value is 1248×704, etc. — see source for the legacy-model column. Verify in source.) When `ratio` is `adaptive`, the model picks based on prompt + first media (priority video > image); the chosen ratio appears in the Retrieve response's `ratio` field.

#### 3.1.4 Create response

```json
{ "id": "cgt-2026XXXXXX-XXXX" }
```

The ID is retained for 7 days from `created_at`. Use it with the Retrieve / Cancel endpoints.

### 3.2 GET /contents/generations/tasks/{id} — Retrieve

```
GET /api/v3/contents/generations/tasks/{id}
Authorization: Bearer $ARK_API_KEY
```

Path param: `id` (string, required) — the task ID returned from Create.

**Response shape**

| Field | Type | Notes |
| --- | --- | --- |
| `id` | string | |
| `model` | string | e.g. `dreamina-seedance-2-0-260128`. |
| `status` | string | `queued`, `running`, `cancelled`, `succeeded`, `failed`, `expired`. |
| `error` | object \| null | `{ code, message }` on failure. |
| `created_at` | int | unix seconds. |
| `updated_at` | int | unix seconds. |
| `content` | object | Present after success. |
| `content.video_url` | string | Output video URL — **valid 24 h, save it promptly.** |
| `content.last_frame_url` | string | Last frame PNG (24 h). Only if `return_last_frame: true` was set. |
| `seed` | int | |
| `resolution` | string | |
| `ratio` | string | Final ratio (resolved when `adaptive`). |
| `duration` | int | seconds — returned if `frames` was not specified. |
| `frames` | int | Returned if `frames` was specified. |
| `framespersecond` | int | |
| `generate_audio` | bool | |
| `safety_identifier` | string | echoed |
| `draft` | bool | only Seedance 1.5 pro. |
| `draft_task_id` | string | when generating a final video from a draft. |
| `service_tier` | string | actual tier used. |
| `execution_expires_after` | int | seconds. |
| `usage` | object | `{ completion_tokens, total_tokens }` — for video models input is always 0, so total = completion. |

**Status flow**

```
queued -> running -> succeeded | failed | expired
queued -> cancelled    (only queued can be cancelled)
```

### 3.3 GET /contents/generations/tasks — List

```
GET /api/v3/contents/generations/tasks?page_num=&page_size=&filter.status=&filter.task_ids=&filter.model=&filter.service_tier=
```

| Param | Type | Notes |
| --- | --- | --- |
| `page_num` | int [1, 500] | |
| `page_size` | int [1, 500] | |
| `filter.status` | string | `queued`, `running`, `cancelled`, `succeeded`, `failed`, `expired`. |
| `filter.task_ids` | string[] | Repeat the param: `filter.task_ids=id1&filter.task_ids=id2`. |
| `filter.model` | string | Model ID. |
| `filter.service_tier` | string | `default` (online) or `flex` (offline). Default value `default`. |

Constraint: only the **past 7 days** are queryable (UTC, T-7 to T window).

Response: `{ "total": <int>, "items": [ ...same shape as Retrieve... ] }`.

### 3.4 DELETE /contents/generations/tasks/{id} — Cancel / Delete

```
DELETE /api/v3/contents/generations/tasks/{id}
```

Behavior:

| Pre-state | Effect |
| --- | --- |
| `queued` | status flips to `cancelled` (task removed from queue). |
| `running` | **cannot be cancelled / deleted.** |
| `succeeded`, `failed`, `cancelled`, `expired` | record permanently deleted; subsequent Retrieve / List calls won't find it. |

No response body.

---

## 4. Asset rules

### 4.1 Per-asset constraints

| Modality | Format | Per-file size | Dimension | Aspect ratio | Other |
| --- | --- | --- | --- | --- | --- |
| Image | jpeg, png, webp, bmp, tiff, gif (1.5-pro also: heic, heif) | ≤ 30 MB | width & height ∈ [300, 6000] px | width/height ∈ (0.4, 2.5) | — |
| Video | mp4, mov | ≤ 50 MB | width & height ∈ [300, 6000] px; total pixels ∈ [640×640, 2206×946] | width/height ∈ [0.4, 2.5] | Resolution 480p / 720p / 1080p; FPS ∈ [24, 60]; duration **per clip** ∈ [2, 15] s. Codecs: H.264/AVC, H.265/HEVC video; AAC, MP3 audio. |
| Audio | mp3, wav | ≤ 15 MB | — | — | duration **per clip** ∈ [2, 15] s. |

### 4.2 Per-request budget

- Total **request body** ≤ 64 MB (do not Base64-encode large files — use URLs).
- Up to **9 images**, **3 videos with combined total ≤ 15 s**, **3 audio**. Up to **12 files** per request.
- Image counts by scenario: I2V first-frame = 1; I2V first+last = 2; R2V (multimodal) = 1–9 (Seedance 2.0) / 1–4 (1.0 lite i2v).

### 4.3 Asset URI inputs

Three ways to supply `url`:

1. **Public HTTPS URL.**
2. **Base64 data URI** — `data:image/png;base64,<...>`, `data:audio/wav;base64,<...>`. Format token must be lowercase. Not for videos. Avoid for large files.
3. **Asset ID** — `asset://<ASSET_ID>`. Three sources:
    - **Digital character library** (preset avatars). Browse / activate at `console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision?modelId=seedance-2-0-260128&tab=GenVideo`.
    - **Authorized real-person assets** — register after passing real-person verification.
    - **Trusted prior outputs** — original face-containing outputs your account generated in the **last 30 days** with allow-listed models can be re-fed as input assets to Seedance 2.0 (`asset://...`). This is the workaround for the real-face restriction below.

### 4.4 Real-human-face restriction

Seedance 2.0 series **do not** accept direct uploads of reference images or videos that contain real human faces. To work with real faces you must use one of: digital characters, authorized real-person assets, or trusted prior outputs (§4.3 (3)).

### 4.5 Referencing assets in prompts

Prompts refer to assets by **type + 1-based ordinal in the request body**: `Image 1`, `Image 2`, `Video 1`, `Audio 1`, etc. Numbering counts only items of that type in the order they appear in the `content` array. Asset IDs are **not** referenceable from the prompt — you must use the ordinal.

For multi-image / sequence references, **upload assets in the order you want them numbered**.

---

## 5. Generation modes

### 5.1 Text-to-Video (T2V)

Single text item in `content`. Pure prompt → video. Audio optionally generated via `generate_audio: true`.

### 5.2 Image-to-Video (I2V)

- **First frame:** one `image_url` with `role: first_frame` (or no role).
- **First and last frame:** two `image_url`s with `role: first_frame` and `role: last_frame`. They can be the same image.

### 5.3 Reference-to-Video (R2V) — multimodal

Combine `reference_image` (1–9), `reference_video` (1–3, ≤15 s combined), `reference_audio` (1–3) and a text prompt. Supports motion / camera / VFX / character / scene references — see §6 templates. Cannot be mixed with `first_frame`/`last_frame` roles.

### 5.4 Video-to-Video (V2V) — editing

A `reference_video` item plus a text prompt that says **add / remove / modify** elements, **extend forward or backward**, or **complete a track** (stitch multiple clips). See §6.5.

---

## 6. Official prompt templates (verbatim from the prompt guide)

### 6.1 Basic formula

> The logical foundation of your generation. Clearly define **"who"** is performing **"what action"**. Define the overall tone by describing the spatial background, lighting details, or specific visual style. Advanced instructions can include scene ambient sound effects to achieve an immersive, synchronized audiovisual output.

Use natural language. For multimodal references, *clearly specify the reference object* — e.g. "Use the composition of Image 1" or "Match the motion of Video 2".

### 6.2 Text rendering

**6.2.1 Slogans**

```
[Text Content] + [Timing] + [Positioning] + [Entrance/Appearance Style], [Visual Attributes (Color, Font, Size, Effects)], [Visual Style & Consistency]
```

**6.2.2 Subtitles**

```
Display subtitles at the bottom-center with the text. The subtitles must be perfectly synchronized with the [voiceover/dubbing/dialogue].
```

**6.2.3 Speech bubbles**

```
[Character] says, "[Dialogue]." Speech bubbles appear around the character containing the spoken text.
```

### 6.3 Image reference

**6.3.1 Multi-perspective subject reference**

```
Refer to/Extract/Combine/Use the [Subject] from [Image N] to generate [Scene Description], maintaining [consistency requirement].
```

**6.3.2 Multi-image reference**

```
Refer to / Extract / Combine / Follow the [Description of referenced elements] from [Image N] to generate [Scene Description].
```

Sub-types shown in the docs: logo reference, multi-subject reference, multi-element reference, multi-panel sequence reference, sequence reference. Upload images in the desired order; reference them as `Image 1`, `Image 2`, … `Image N`.

### 6.4 Video reference

**6.4.1 Motion reference**

```
Refer to the [Motion Description] from [Video N] to generate [Scene Description], keeping the motion [consistency requirement].
```

**6.4.2 Camera motion reference**

```
Refer to the [Camera Movement Description] from [Video N] to generate [Scene Description], keeping the camera movement [consistency requirement].
```

**6.4.3 Visual effects (VFX) reference**

```
Refer to the [VFX Effects Description] from [Video N] to generate [Scene Description], keeping the [consistency requirement].
```

### 6.5 Video editing

**6.5.1 Adding, removing, or modifying elements**

```
Adding:    At [Timestamp/Timing] and [Spatial Location] of [Video N], add [Description of intended element].
Removing:  Remove [Element to be deleted] from [Video N], keeping the rest of the video content unchanged.
Modifying: Replace [Description of element to be changed] in [Video N] with [Description of intended element].
```

**6.5.2 Extending videos**

```
- Extend [Video N] forward/backward + [Description of extended content]
- Generate content before/after [Video N] + [Description of extended content]
```

> The model automatically extracts the transition frames for seamless blending. The original segment is preserved — the new content is appended before or after.

**6.5.3 Completing tracks (stitching)**

```
[Video 1] + [Transition Description] + followed by [Video 2] + [Transition Description] + followed by [Video 3] ...
```

> **Input limit:** Seedance 2.0 series supports a maximum of **3 video clips** as input, total combined duration ≤ **15 seconds**.
> **Smart trimming:** During generation, the model will automatically trim the connecting segments of the start and end clips, retaining only the necessary frames to ensure a seamless and logical synthesis.

---

## 7. Joint audio generation

Set `generate_audio: true` (default) and describe what you want to hear in the prompt. The 2.0 / 2.0-fast models can produce, in a single pass:

- **Voiceover / dubbing / dialogue** — write the spoken line in quotes inside the prompt, e.g. `"You always arrive right on time."` Multiple speakers / multiple languages supported (the prompt guide shows English + Korean dialogue).
- **Ambient sound effects** — e.g. `Include intense background music`, `golden particle effects with chime sound`.
- **Background music / score** — describe genre / mood (`upbeat synth`, `cinematic orchestral`).
- **SFX** synced to on-screen events (footsteps, impacts, foley).

You can also pass a **reference audio** (`role: reference_audio`) to bias the audio style — the prompt guide example references `Audio 1` for background music while keeping the visuals from `Image 1` + `Video 1`.

**Subtitle synchronization:** when the prompt requests subtitles (template §6.2.2), the rendered subtitles are time-aligned with the generated voiceover/dubbing/dialogue automatically.

Set `generate_audio: false` for a silent video (smaller file, faster).

---

## 8. Output

- **Aspect ratios:** `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`, `adaptive`.
- **Resolutions:** `480p`, `720p`, `1080p`. `1080p` is **not** supported by 2.0-fast, nor by Seedance 1.0 lite reference image-based generation.
- **Durations:** 2.0 / 2.0-fast = `[4, 15]` seconds (or `auto` for smart selection). 1.5-pro = `[4, 12]`. 1.0-pro / pro-fast / lite = `[2, 12]`. With `frames`: integer in `[29, 289]` matching `25 + 4n`.
- **Frame rate:** 24 fps default (input video FPS support [24, 60]).
- **URL retention:** `content.video_url` and `content.last_frame_url` from the Retrieve response are **valid for 24 hours** — download / re-host promptly.
- **Last frame:** request with `return_last_frame: true` then read `content.last_frame_url` from the Retrieve response (PNG, same dims as video). Use it to chain consecutive multi-segment generations.

---

## 9. Code samples

> All examples assume `ARK_API_KEY` is exported. Replace the model ID with `dreamina-seedance-2-0-fast-260128` for the Fast variant.

### 9.1 cURL — Create (R2V multimodal: tea example)

```bash
curl -X POST "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  -d '{
    "model": "dreamina-seedance-2-0-260128",
    "content": [
      {
        "type": "text",
        "text": "Use the first-person POV framing from Video 1 throughout, and use Audio 1 as the background music. Show the tea-pouring sequence with the cups from Image 1 and Image 2 on a wooden table at golden hour."
      },
      { "type": "image_url", "image_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/r2v_tea_pic1.jpg" }, "role": "reference_image" },
      { "type": "image_url", "image_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/r2v_tea_pic2.jpg" }, "role": "reference_image" },
      { "type": "video_url", "video_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_video/r2v_tea_video1.mp4" }, "role": "reference_video" },
      { "type": "audio_url", "audio_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_audio/r2v_tea_audio1.mp3" }, "role": "reference_audio" }
    ],
    "generate_audio": true,
    "ratio": "16:9",
    "duration": 8,
    "resolution": "720p",
    "watermark": false,
    "return_last_frame": true
  }'
```

Response:

```json
{ "id": "cgt-2026XXXXXX-XXXX" }
```

### 9.2 cURL — Retrieve (poll)

```bash
curl -X GET "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/cgt-2026XXXXXX-XXXX" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ARK_API_KEY"
```

### 9.3 Python — official BytePlus SDK (recommended)

```python
# pip install byteplus-python-sdk-v2
import os, time, sys, urllib.request
from byteplussdkarkruntime import Ark

client = Ark(
    base_url="https://ark.ap-southeast.bytepluses.com/api/v3",
    api_key=os.environ["ARK_API_KEY"],
)

def generate_seedance(content, **params):
    print("----- create request -----")
    create_result = client.content_generation.tasks.create(
        model="dreamina-seedance-2-0-260128",
        content=content,
        generate_audio=params.get("generate_audio", True),
        ratio=params.get("ratio", "16:9"),
        duration=params.get("duration", 5),
        resolution=params.get("resolution", "720p"),
        watermark=params.get("watermark", False),
        return_last_frame=params.get("return_last_frame", True),
    )
    print(create_result)

    task_id = create_result.id
    print("----- polling task status -----")
    while True:
        get_result = client.content_generation.tasks.get(task_id=task_id)
        status = get_result.status
        if status == "succeeded":
            print("----- task succeeded -----")
            print(get_result)
            return get_result
        elif status in ("failed", "expired", "cancelled"):
            print(f"----- task {status} -----")
            print(f"Error: {getattr(get_result, 'error', None)}")
            return get_result
        print(f"Current status: {status}, retrying in 30s...")
        time.sleep(30)

if __name__ == "__main__":
    content = [
        { "type": "text",
          "text": "Use the first-person POV framing from Video 1 throughout, and use Audio 1 as the background music. Show the tea-pouring sequence with the cups from Image 1 and Image 2 on a wooden table at golden hour." },
        { "type": "image_url", "image_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/r2v_tea_pic1.jpg" }, "role": "reference_image" },
        { "type": "image_url", "image_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_image/r2v_tea_pic2.jpg" }, "role": "reference_image" },
        { "type": "video_url", "video_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_video/r2v_tea_video1.mp4" }, "role": "reference_video" },
        { "type": "audio_url", "audio_url": { "url": "https://ark-doc.tos-ap-southeast-1.bytepluses.com/doc_audio/r2v_tea_audio1.mp3" }, "role": "reference_audio" },
    ]
    result = generate_seedance(content, duration=8, ratio="16:9", resolution="720p")
    if result.status == "succeeded":
        out = result.content.video_url
        # URL valid for 24 h — download immediately.
        urllib.request.urlretrieve(out, "out.mp4")
        print("Saved out.mp4")
    else:
        sys.exit(1)
```

### 9.4 Python — plain `requests` (no SDK)

```python
import os, time, sys, requests, urllib.request

API = "https://ark.ap-southeast.bytepluses.com/api/v3"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['ARK_API_KEY']}",
}

def create(content, **params):
    body = { "model": "dreamina-seedance-2-0-260128", "content": content, **params }
    r = requests.post(f"{API}/contents/generations/tasks", json=body, headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()["id"]

def retrieve(task_id):
    r = requests.get(f"{API}/contents/generations/tasks/{task_id}", headers=HEADERS, timeout=60)
    r.raise_for_status()
    return r.json()

def wait(task_id, interval=30, timeout_s=2400):
    start = time.time()
    while True:
        info = retrieve(task_id)
        st = info["status"]
        if st in ("succeeded", "failed", "cancelled", "expired"):
            return info
        if time.time() - start > timeout_s:
            raise TimeoutError(f"task {task_id} not done after {timeout_s}s")
        print(f"status={st} … sleeping {interval}s")
        time.sleep(interval)

if __name__ == "__main__":
    content = [
        { "type": "text", "text": "A cat batting at a ball of yarn, cinematic close-up, soft window light." },
    ]
    tid = create(content, generate_audio=True, ratio="16:9", duration=5, resolution="720p")
    print("task id:", tid)
    info = wait(tid)
    if info["status"] != "succeeded":
        print("failed:", info.get("error")); sys.exit(1)
    url = info["content"]["video_url"]
    urllib.request.urlretrieve(url, "out.mp4")
    print("saved out.mp4")
```

### 9.5 List + Cancel snippets

```bash
# list last 7 days, succeeded, page 1, 50 per page
curl -G "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks" \
  -H "Authorization: Bearer $ARK_API_KEY" \
  --data-urlencode "page_num=1" --data-urlencode "page_size=50" \
  --data-urlencode "filter.status=succeeded" \
  --data-urlencode "filter.model=dreamina-seedance-2-0-260128"

# cancel a queued task / delete a finished record
curl -X DELETE "https://ark.ap-southeast.bytepluses.com/api/v3/contents/generations/tasks/cgt-2026XXXXXX-XXXX" \
  -H "Authorization: Bearer $ARK_API_KEY"
```

---

## 10. Error codes & gotchas

The Create page does not enumerate full error codes inline. For the canonical error code list, see the ModelArk **Error Codes** page: <https://docs.byteplus.com/en/docs/ModelArk/1299023>. Errors are returned in the standard ModelArk shape:

```json
{ "error": { "code": "<code>", "message": "<human readable>" } }
```

When `status: failed` in the Retrieve response, the same `error` object is included.

**Operational gotchas you actually need to know:**

- **24-hour URL retention.** `content.video_url` and `content.last_frame_url` expire 24 h after success. Always re-host (S3 / TOS) or download immediately.
- **7-day task ID retention.** Old IDs are unrecoverable.
- **Real-face restriction.** Direct uploads of real-person photos / videos are rejected. Use digital characters, authorized real-person assets, or 30-day trusted prior outputs (asset URIs).
- **Audio cannot be input alone.** Always pair audio with at least one image or video.
- **Mode mutual exclusion.** First-frame / first+last-frame / multimodal-reference are three mutually exclusive scenarios — don't combine `first_frame`/`last_frame` and `reference_image` in one request.
- **`duration` vs `frames`** are mutually exclusive (`frames` wins). `frames` is **not supported by 2.0 / 2.0-fast / 1.5-pro**, so for 2.0 use `duration`.
- **2.0-fast has no 1080p**. 2.0-fast / 2.0 do not support `flex` service tier (`default` only).
- **Draft mode is 1.5-pro only** — `draft: true` will fail on 2.0.
- **Expired vs cancelled.** `expired` happens when a task sits in `queued`/`running` past `execution_expires_after`. `cancelled` is only reachable from `queued` via DELETE.
- **Watermarks default off.** Set `watermark: true` if you want them.
- **Base64 not for video; not recommended for any large file.** Request body cap is 64 MB.
- **Adaptive ratio:** when `ratio: adaptive`, the model resolves it from the prompt + first media (priority: video > image). Read the resolved value from the Retrieve response's `ratio` field.
- **Service-tier downgrade unsupported.** Once a task is submitted, you cannot change `service_tier`.

---

## 11. Pricing / billing

Detailed pricing was not present on the rendered Create / Tutorial / Prompt-guide pages. Refer to:

- BytePlus pricing portal — <https://www.byteplus.com/en/pricing>
- ModelArk Model List — <https://docs.byteplus.com/en/docs/ModelArk/1330310> (rate limits + billing per model).
- `flex` (offline) tier is documented as **50% of the online price** with higher TPD; **2.0 / 2.0-fast do not support `flex`** so 2.0 series is `default`-priced only.
- Token usage for video models is reported in `usage.completion_tokens` (input is always 0). Sample value seen in docs: ~108,900 tokens for one 720p 16:9 clip — useful as an order-of-magnitude estimate.

(Pricing details: verify in source / console before relying on these numbers.)

---

## Appendix A — Quick reference of `role` enum

| Asset type | `role` values | Used for |
| --- | --- | --- |
| `image_url` | `first_frame` | I2V first-frame mode |
| `image_url` | `last_frame` | I2V first+last-frame mode (paired with `first_frame`) |
| `image_url` | `reference_image` | R2V multimodal references (1–9) |
| `video_url` | `reference_video` | V2V edit / extend / track-completion / R2V motion-camera-VFX reference |
| `audio_url` | `reference_audio` | R2V audio reference (must accompany image or video) |
| `draft_task` | n/a | Seedance 1.5 pro draft → final |

## Appendix B — Quick endpoint cheat sheet

```
POST   /api/v3/contents/generations/tasks            create
GET    /api/v3/contents/generations/tasks/{id}       retrieve
GET    /api/v3/contents/generations/tasks            list  (page_num,page_size,filter.*)
DELETE /api/v3/contents/generations/tasks/{id}       cancel queued / delete terminal
```

All require: `Authorization: Bearer $ARK_API_KEY`, `Content-Type: application/json`. Base URL: `https://ark.ap-southeast.bytepluses.com`.
