# Video Generation Pipeline

Seedance 2.5 / 2.0 (ByteDance, via BytePlus ModelArk) video generation for Nick's projects:
a reusable CLI client, a **library/** of reference packs (consistent people, places,
motion across videos), and the **knowledge/** that makes prompts and API calls work on
the first try.

Grown out of the proven PermitNav brand-film pipeline
([permit-nav-team/video-generation](https://github.com/permit-nav-team/video-generation)).

## Layout

```
knowledge/            everything we know about Seedance 2.5 / 2.0
  api-reference.md    full BytePlus ModelArk API contract (endpoints, params, limits)
  prompt-guide.md     how to write prompts that work (formula, modes, audio, text)
  gotchas.md          hard-won operational lessons — read before burning credits
library/              reference packs for R2V — one folder per reusable element
  people/             characters          (refs/ images + card.md)
  places/             locations           (refs/ images + card.md)
  motion/             camera moves / subject motion / VFX (clips as URLs in urls.txt)
  <cat>/_template/    copy to start a new pack; new categories are just new folders
pipeline/
  seedance.py         the client: generate / status / wait / list / cancel
  prompts/            prompt files (sent verbatim — the whole file is the prompt)
                      example-r2v-25.md is the 2.5 sectioned format (timeline, scoped refs)
output/               downloaded results (gitignored; URLs expire in 24h so the
                      client downloads immediately)
```

## Setup

The client resolves `ARK_API_KEY` in this order — no setup needed on Nick's Mac:

1. `$ARK_API_KEY` environment variable
2. `.env` in this repo (see `.env.example`)
3. `~/Documents/Claude/Projects/SeedDance/.env` ← the working key already lives here

Requires `python3` with `requests`.

## Quickstart

```bash
# Text-to-Video: create → poll → download to output/cat-test.mp4
python3 pipeline/seedance.py generate --prompt "A cat batting at a ball of yarn, cinematic close-up, soft window light. Quiet room tone, gentle purring." --name cat-test --duration 4 --resolution 720p

# From a prompt file, fast model, vertical
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/example-t2v.md --fast --ratio 9:16 --name vertical-test

# R2V with library packs — character + location + camera move in one shot
python3 pipeline/seedance.py generate --prompt-file my-scene.md --pack people/nova --pack places/loft --pack motion/dolly-in --name nova-loft

# Chain a follow-up clip from the previous clip's last frame (same person, same scene)
python3 pipeline/seedance.py generate --prompt "Continue from the opening frame — ..." --first-frame output/nova-loft.last.png --name nova-loft-2

# See exactly what would be sent, spend nothing
python3 pipeline/seedance.py generate --prompt "..." --dry-run

# Task management
python3 pipeline/seedance.py list
python3 pipeline/seedance.py status <task-id or name>
python3 pipeline/seedance.py wait   <task-id or name>
python3 pipeline/seedance.py cancel <task-id>
```

Defaults: Seedance 2.5 (`dreamina-seedance-2-5-260628`), 1080p (10-bit HEVC on 2.5), 16:9,
5s, native audio ON, last-frame capture ON (for chaining). `--model 2.0|fast|mini` selects
the 2.0 series (`--fast` = shorthand for the fast model, 720p max, cheaper). 2.5 extras:
`--duration` up to 30s, `--task-type auto|edit|extend`, `--format mov`, audio-only
references, up to 30 images + 10 videos + 10 audio per request. Edit/extend/first-frame
tasks on 2.5 require `ratio: adaptive` — the client sets and enforces this for you.

## The reference library (R2V)

Each folder in `library/` is a **pack**: reference assets + a `card.md` with the canonical
wording to use in prompts. `--pack people/nova` attaches nova's refs as `Image 1..N`
(the client prints the numbering map before sending); packs compose, so person + place +
motion in one request is one flag each. Bare names work when unambiguous (`--pack nova`).
Full rules — pack anatomy, numbering, the real-face restriction and the `asset://`
workaround — in [library/README.md](library/README.md).

## Costs & balance

- There is **no balance endpoint** on the inference API. Check balance in the console:
  <https://console.byteplus.com/finance> (BytePlus account, region ap-southeast-1).
- Order of magnitude: one 720p 16:9 clip ≈ ~109k completion tokens (from the official docs).
  `seedance.py` prints `usage.completion_tokens` after every successful task.
- `--dry-run` before spending; iterate on `--fast` or `--model mini` at 720p; 2.5 1080p for
  finals. 2.5 costs ≈ +50% over 2.0 and needs the account gate (balance > USD 30, a savings
  plan, or a 2.5 resource pack) — see knowledge/gotchas.md.
