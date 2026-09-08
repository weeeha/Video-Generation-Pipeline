# VR Game Things Puzzle promo generation log

## Environment preflight

| Check | Observed value |
| --- | --- |
| Execution date | 2026-08-06 |
| Pipeline worktree | `/Users/nickv/Documents/ChatGPT/Video Generation Pipeline/.worktrees/vr-game-things-puzzle-promo` |
| Unity source project | `/Users/nickv/VR-Game-Things-Puzzle/VR Game Things Puzzle` |
| Spend cap | USD 12 |
| Seedance draft limit | Four 5-second 720p Fast tasks |
| Seedance final limit | Two 5-second 1080p full-model tasks |
| API-key presence | Configured; value not printed |
| ffmpeg version | 8.1 |
| Unity capture status | Repository-render fallback. Open-source MCP reported zero instances; official MCP targeted `/Users/nickv/VR-Creative-Hub/VR-Creative-Hub`, so that unrelated project was left untouched. |

## Authentic capture

| Clip | Source type | Resolution | Duration | QA result |
| --- | --- | --- | --- | --- |
| `library.mp4` | Repository hero render with restrained push-in | 1920x1080 | 3.0s | Pass; concept footage |
| `grab.mp4` | Repository exploded render with restrained push-in | 1920x1080 | 5.0s | Pass; concept footage |
| `snap.mp4` | Repository exploded-to-assembled crossfade | 1920x1080 | 5.0s | Pass as transition; concept footage |
| `operation.mp4` | Repository hero render with restrained push-in | 1920x1080 | 4.0s | Pass; concept footage |

## Draft tasks

| Name | Prompt | Task ID | Model | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `vrgtp-d01-cockpit-approach` | `01-cockpit-approach.md` | `cgt-20260806145059-rj5cc` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Reject: malformed glove/cockpit interaction |
| `vrgtp-d02-magnetic-connection` | `02-magnetic-connection.md` | `cgt-20260806145151-7dsxq` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Pass; not promoted |
| `vrgtp-d03-three-piece-assembly` | `03-three-piece-assembly.md` | `cgt-20260806145221-c5vxs` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Selected assembly concept |
| `vrgtp-d04-hero-reveal` | `04-hero-reveal.md` | `cgt-20260806145308-2rx9p` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Reject: geometry and weapon-pod drift |

### Draft submission incident

The first multi-command submission continued after its tool cell appeared to
finish. Retrying the apparently missing names created three additional Fast
tasks before the local state was reconciled. Running Seedance tasks could not
be cancelled. All seven promo tasks were identified by prompt, inspected, and
reconciled before final generation. A simultaneous MTL task was identified by
its 21:9 output and restaurant-robot content, excluded from this promo, and not
counted in this ledger.

| Variant | Prompt | Task ID | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | ---: | ---: | --- |
| `connection-a` | `02-magnetic-connection.md` | `cgt-20260806145130-tt5b2` | Succeeded | 108,900 | USD 0.61 | Pass; not promoted |
| `assembly-b` | `03-three-piece-assembly.md` | `cgt-20260806145228-mxfgq` | Succeeded | 108,900 | USD 0.61 | Pass; not promoted |
| `hero-a` | `04-hero-reveal.md` | `cgt-20260806145241-vxlch` | Succeeded | 108,900 | USD 0.61 | Selected hero concept |

## Draft QA matrix

Score each category from 0-2. A draft must score at least 8/12 and pass every automatic rejection rule.

| Draft | Apache identity | Three-piece truth | Mechanical readability | Studio tone | Temporal stability | Edit usefulness | Total | Automatic rejection | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `d01` | 2 | 2 | 1 | 2 | 1 | 1 | 9 | Malformed glove/cockpit interaction | Reject |
| `d02a` | 2 | 2 | 0 | 2 | 2 | 1 | 9 | Connection action is not readable | Reject |
| `d02b` | 2 | 2 | 1 | 2 | 2 | 2 | 11 | None | Pass; not promoted |
| `d03a` | 2 | 2 | 2 | 2 | 2 | 2 | 12 | None | Select for final assembly |
| `d03b` | 2 | 1 | 2 | 2 | 2 | 2 | 11 | None | Pass; not promoted |
| `d04a` | 2 | 2 | 2 | 2 | 1 | 2 | 11 | None | Select for final hero |
| `d04b` | 1 | 2 | 1 | 2 | 1 | 1 | 8 | Added weapon geometry and shape drift | Reject |

## Final tasks

| Name | Source concept | Task ID | Model | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `vrgtp-f01-assembly` | `d03a` | `cgt-20260806150045-tkh2g` | `dreamina-seedance-2-0-260128` | Succeeded | 245,025 | USD 1.89 | Accept: readable three-piece assembly with stable Apache identity |
| `vrgtp-f02-hero` | `d04a` | `cgt-20260806150110-zqxnc` | `dreamina-seedance-2-0-260128` | Succeeded | 245,025 | USD 1.89 | Accept: clean assembled-model reveal without battlefield action |

### Historical Seedance 2.0 command pin

The recorded final tasks used `dreamina-seedance-2-0-260128`. Any future
dry-run or replay must explicitly pass `--model 2.0 --resolution 1080p
--duration 5 --ratio 16:9 --no-audio`, because the current `full` alias now
resolves to Seedance 2.5. This is a forward-looking instruction correction;
it does not rewrite the seven-draft retry incident as a compliant planned run.

```bash
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f01-assembly --dry-run
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f02-hero --dry-run
```

## Cost ledger

| Stage | Successful tasks | Estimated subtotal |
| --- | ---: | ---: |
| Drafts | 7 | USD 4.27 |
| Finals | 2 | USD 3.77 |
| Total | 9 | USD 8.04 |

## Export verification

| Check | Observed value | Result |
| --- | --- | --- |
| Duration 25-30 seconds | 29.000s | Pass |
| Resolution 1920x1080 | 1920x1080 | Pass |
| Frame rate 24 fps | 24/1 | Pass |
| H.264 and `yuv420p` | H.264, `yuv420p` | Pass |
| AAC stereo 48 kHz | AAC LC, 2 channels, 48,000 Hz | Pass |
| Title and tagline | Visually confirmed on final card | Pass |
| No forbidden product claims | Manifest claim scan and visual QA clean | Pass |
| No black frames or clipping | No 0.25s black interval; audio peak -32.6 dB | Pass |

Delivery: `output/vr-game-things-puzzle-promo/vr-game-things-puzzle-promo-v1.mp4`

SHA-256: `71f09155be4c79bc09999411d3c4eebc9a4f470fab97fb26b8964364cf1612a3`

## Disclosure

Concept footage from repository renders with Seedance cinematic visualization.
Generated footage is used only to visualize interactions already implemented
in the three-piece Apache vertical slice. It is not evidence of flight, combat,
native hand tracking, additional playable pieces, or other playable models.
