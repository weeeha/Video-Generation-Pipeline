# T3.1 — First+last frame as a match-cut / bridge tool

**Setup:** `--first-frame` = Nova's wave-end frame (clip 1 last frame), `--last-frame` =
her at-the-counter mug frame (clip 2 last frame). Prompt describes the connecting
action. Fast @720p, 5s, seed 42. (I2V first+last mode — no reference packs allowed.)

**Takes:**

| take | tokens | verdict | note |
|---|---|---|---|
| 1 | 108,900 | **KEEP** | opens on pin-A composition, invents turn → profile walk → reach, lands a near-cut from pin-B |

**Verdict: PASS.** Both pins honored (close, not pixel-exact); the invented action is
physically sensible and correctly ordered. This is the bridge-shot tool: any two
approved frames — ends of existing takes, Blender renders, restyled stills — can be
connected with generated motion. Combined with last-frame chaining this gives
*bidirectional* continuity control.

**Feeds:** capstone shot-planning can pin both ends of risky shots; Blender renders
(T2.3) become pinnable anchors, not just references.
