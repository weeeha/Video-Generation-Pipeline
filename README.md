# Video Generation Pipeline

Seedance 2.0 (ByteDance, via BytePlus ModelArk) video generation for Nick's projects:
a reusable CLI client, a **people/** library for consistent characters across videos,
and the **knowledge/** that makes prompts and API calls work on the first try.

Grown out of the proven PermitNav brand-film pipeline
([permit-nav-team/video-generation](https://github.com/permit-nav-team/video-generation)).

## Layout

```
knowledge/            everything we know about Seedance 2.0
  api-reference.md    full BytePlus ModelArk API contract (endpoints, params, limits)
  prompt-guide.md     how to write prompts that work (formula, modes, audio, text)
  gotchas.md          hard-won operational lessons — read before burning credits
people/               character library for Reference-to-Video (R2V)
  _template/          copy this folder to create a new person
pipeline/
  seedance.py         the client: generate / status / wait / list / cancel
  prompts/            prompt files (sent verbatim — the whole file is the prompt)
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

# R2V with a person from the library (their refs attach as Image 1..N)
python3 pipeline/seedance.py generate --prompt-file my-scene.md --person nova --name nova-cafe

# Chain a follow-up clip from the previous clip's last frame (same person, same scene)
python3 pipeline/seedance.py generate --prompt "Continue from the opening frame — ..." --first-frame output/nova-cafe.last.png --name nova-cafe-2

# See what would be sent without spending anything
python3 pipeline/seedance.py generate --prompt "..." --dry-run

# Task management
python3 pipeline/seedance.py list
python3 pipeline/seedance.py status <task-id or name>
python3 pipeline/seedance.py wait   <task-id or name>
python3 pipeline/seedance.py cancel <task-id>
```

Defaults: full model (`dreamina-seedance-2-0-260128`), 1080p, 16:9, 5s, native audio ON,
last-frame capture ON (for chaining). `--fast` switches to the fast model (720p max, cheaper).

## The people system (R2V)

Each folder in `people/` is one character: numbered reference images in `refs/` plus a
`card.md` with the canonical description to use in prompts. `--person <name>` attaches the
refs in order, so `refs/01-*.png` is `Image 1` in your prompt. Full rules in
[people/README.md](people/README.md) — including the real-human-face restriction and the
`asset://` workaround.

## Costs & balance

- There is **no balance endpoint** on the inference API. Check balance in the console:
  <https://console.byteplus.com/finance> (BytePlus account, region ap-southeast-1).
- Order of magnitude: one 720p 16:9 clip ≈ ~109k completion tokens (from the official docs).
  `seedance.py` prints `usage.completion_tokens` after every successful task.
- `--dry-run` before spending; `--fast` while iterating; 1080p full model only for finals.
