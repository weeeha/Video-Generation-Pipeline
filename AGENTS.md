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
