# Video Generation Pipeline — agent instructions

Seedance 2.0 video generation via BytePlus ModelArk. Read [README.md](./README.md) for
layout and CLI usage.

**Every generation costs real money.** That fact drives most of the rules below.

## Read before calling the API

`knowledge/gotchas.md` — hard restrictions and money traps, written from the PermitNav
production run. Not optional. The most common ways to waste credits are all in there:
mode mutual exclusion (`first_frame`/`last_frame` cannot coexist with `reference_image`),
no real human faces as references, no `flex` tier on 2.0, no 1080p on 2.0-fast, and
output URLs that expire in **24 hours**.

Also available: `knowledge/api-reference.md` (full API contract),
`knowledge/prompt-guide.md` (prompt formula and modes), `library/README.md` (pack anatomy
and the `asset://` workaround).

## Spending rules

- **Never run a real generation without Nick's explicit go.** `--dry-run` is free and
  prints exactly what would be sent — use it to validate any command you construct.
- Iterate on `--fast` at 720p. Full model at 1080p is for finals only.
- Same seed + same inputs is deterministic, so a good `--fast` take can guide the final.
- There is **no balance endpoint**. Balance is console-only:
  <https://console.byteplus.com/finance> (BytePlus, region ap-southeast-1). Don't claim to
  know the remaining balance — you can't.
- `seedance.py` prints `usage.completion_tokens` after every success; ~109k for one 720p
  clip is the budgeting yardstick.

## Operational

- API key resolution: `$ARK_API_KEY` → repo `.env` → `~/Documents/Claude/Projects/SeedDance/.env`.
  The working key already lives at the third location on Nick's Mac. **Never print the key,
  never copy it into a file in this repo, never commit `.env`.**
- `output/` is gitignored and holds downloaded results. The client downloads immediately
  because URLs expire — a finished task you didn't download is money gone.
- Task IDs and the List endpoint only reach back **7 days**.
- Prompt files are sent **verbatim, whole file**. A stray heading or note at the top of a
  prompt file goes to the model as prompt text.
- Requires `python3` with `requests`. There is no `package.json`; this is not a Node project
  despite the `web/` folder (a static screening page).

## Library packs

One folder per reusable element under `library/<category>/<name>/`, with `refs/` and a
`card.md` carrying the canonical prompt wording. Copy `<category>/_template/` to start one.
New categories are just new folders. Packs compose — person + place + motion is one
`--pack` flag each, and the client prints the `Image 1..N` numbering map before sending.

## Git

Remote `https://github.com/weeeha/Video-Generation-Pipeline.git`; current branch
`scaffold/repo-structure`. Feature branch + PR; never push to `main`.

Grown out of `permit-nav-team/video-generation`. PermitNav itself is no longer active work
— that repo is reference material only.

<!-- BEGIN:generation-family -->
## Sibling repos

This repo is one of six related repos for AI-generated film work: images, 3D models, 3D
previs, video, audio, and continuity repair. They stay separate on purpose (different stacks,
no shared code). The same block sits in all six AGENTS.md files between the
`generation-family` markers; change it in all six or in none.

| Repo | Local folder (always quote) | What it does | Stack |
|---|---|---|---|
| Film Design System | `~/ClaudeCode Projects/Image Generation Pipeline ` (trailing space) | Canon of characters, props and settings with curated reference images; image generation against it | Next.js, SQLite, Gemini |
| 3D Models | `~/ClaudeCode Projects/3D Models` | Text-to-3D through Meshy, a three.js viewer and gallery, Blender and procedural models | Next.js, react-three-fiber, Meshy API |
| Scene Builder 3D | `~/ClaudeCode Projects/scene-builder-3d` | Shot-first 3D previs: build a set, place characters, frame shots with a camera, play the scene back | Vite, React, three.js, browser-only |
| Video Generation Pipeline | `~/ClaudeCode Projects/Video Generation Pileline` ("Pileline" is the real folder name) | Seedance and Runway clients; reference packs in `library/` | Python CLI |
| Audio Generation Pipeline | `~/ClaudeCode Projects/Audio-Generation-Pipeline` | Speech (Qwen3-TTS, Higgs Audio v2), voice cloning, sound effects, on the Mac Studio and the Art PC | Python, shell, PowerShell |
| Continuity Lab | `~/ClaudeCode Projects/Video Lab` | Find and repair inconsistencies between generated video shots | Next.js, SQLite, ffmpeg |

GitHub, all under `weeeha/`: `Image-Generation-Pipeline-` (trailing dash), `scene-builder-3d`,
`Video-Generation-Pipeline` and `Audio-Generation-Pipeline` are public; `3d-models-playground`
(the 3D Models repo) and `Video-Lab` are private.

### How they connect

No code or data path links them yet; files move by hand. Known, planned and wanted links:

- **Image → video (planned).** The Film Design System spec names Seedance reference-to-video
  as a later consumer of its canon. The video repo's `library/<category>/<name>/` packs
  (`refs/` + `card.md`) hold the same kind of thing as folders, so an export from the canon
  would land there.
- **3D Models → Scene Builder 3D and video (wanted).** 3D Models generates GLB files through
  Meshy, and Scene Builder 3D stores props as GLB. Nick wants generated models usable as
  previs props and as Seedance references; no step connects them yet. 3D Models also holds
  3D-printing work (toys, sculpture), which is unrelated to film.
- **Scene Builder 3D → video (planned).** Its roadmap milestone M9 exports a shot as a
  provider-neutral zip (grey guide clip, first frame, camera path, prompt) for manual upload,
  with Seedance as the first target. Its idle prototype, `weeeha/Scene-Builder-v2` (folder
  `Scene Builder V2 (3d editor)`), already packaged shots for Seedance.
- **Video → Continuity Lab.** The Lab imports existing clips into a project folder. Its own
  generation backend (`seedance-fal`, via fal.ai) is planned for its plan 5 and is separate
  from the BytePlus client in the video repo.
- **Audio → video (open).** Seedance 2.5 accepts audio references and the audio repo makes
  voices and effects, but no step connects them. The audio repo also serves OpenClaw's
  Speaker agent, which is unrelated to film work.

### Working across repos

- Read the sibling's own AGENTS.md (or README) before changing it. Spend rules differ: image,
  3D and video generations cost money and need Nick's go; audio runs on the Art PC GPU and
  can pause llama-server while it runs.
- Don't copy code between repos. When a shared format appears (a canon export, say),
  document it in both repos it connects and update this block.
- Branch per task in each repo; never push to `main`.
<!-- END:generation-family -->
