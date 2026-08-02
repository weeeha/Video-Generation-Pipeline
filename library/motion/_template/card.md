# <Motion name>

**One-line:** <e.g. "slow push-in dolly, ~5s, waist height, ends in medium close-up">
**Type:** camera move | subject motion | VFX

## Canonical phrase

<!-- Words matter most for motion refs — the model needs the move described ALONGSIDE the
     clip. This is the sentence to paste into prompts: -->

<e.g. "Reference the camera movement from Video 1 — a slow, steady dolly-in over 5 seconds,
waist height, ending in a medium close-up, keeping the scene consistent.">

## Clips

Clips live in `urls.txt` (video can't be committed-and-sent — the API takes hosted URLs or
`asset://` IDs only; ≤3 clips and ≤15s combined per request). Mirror them here for humans:

| # | Source | What it shows | Expires |
|---|--------|---------------|---------|
| 1 | <https://… or asset://…> | <the move> | <asset:// = 30 days after generation> |

## Notes

<!-- Where the clip came from / how to regenerate it when the asset:// expires. -->
