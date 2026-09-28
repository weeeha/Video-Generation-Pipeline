# Mtl63 Seedance 2.0 workflow slate

All new clips use the fast model at 720p, 21:9, five seconds, native audio, and seed `6301` unless a test requires a distinct seed. Existing establishing and walk clips are retained as baselines.

| Test | Mode | Purpose | Pass criteria |
|---|---|---|---|
| T01 | T2V | Prompt-only world generation | coherent Montreal-scale machine relic; stable camera; no face gate |
| T02 | R2V, one image | Robot identity and mechanical action | preserves robot design; glass and arm remain plausible |
| T03 | R2V, two packs | Character plus location composition | visor stays opaque; suit and rooftop remain recognizable |
| T04 | I2V, first frame | Continue a prior character shot | spatial continuity from the existing walk last frame |
| T05 | I2V, first and last frames | Exact-pose bridge | starts and ends near supplied robot frames without a cut |
| T06 | V2V | Continue/edit a generated robot take | preserves robot and room while extending the action |

No direct face-visible reference is sent in this slate. The already-documented privacy rejection remains the compliance test result.

