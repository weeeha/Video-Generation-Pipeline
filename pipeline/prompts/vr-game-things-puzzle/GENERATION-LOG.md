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
| `vrgtp-d01-cockpit-approach` | `01-cockpit-approach.md` | | | | | | |
| `vrgtp-d02-magnetic-connection` | `02-magnetic-connection.md` | | | | | | |
| `vrgtp-d03-three-piece-assembly` | `03-three-piece-assembly.md` | | | | | | |
| `vrgtp-d04-hero-reveal` | `04-hero-reveal.md` | | | | | | |

## Draft QA matrix

Score each category from 0-2. A draft must score at least 8/12 and pass every automatic rejection rule.

| Draft | Apache identity | Three-piece truth | Mechanical readability | Studio tone | Temporal stability | Edit usefulness | Total | Automatic rejection | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `d01` | | | | | | | | | |
| `d02` | | | | | | | | | |
| `d03` | | | | | | | | | |
| `d04` | | | | | | | | | |

## Final tasks

| Name | Source concept | Task ID | Model | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `vrgtp-f01-assembly` | | | | | | | |
| `vrgtp-f02-hero` | | | | | | | |

## Cost ledger

| Stage | Successful tasks | Estimated subtotal |
| --- | ---: | ---: |
| Drafts | | |
| Finals | | |
| Total | | |

## Export verification

| Check | Observed value | Result |
| --- | --- | --- |
| Duration 25-30 seconds | | |
| Resolution 1920x1080 | | |
| Frame rate 24 fps | | |
| H.264 and `yuv420p` | | |
| AAC stereo 48 kHz | | |
| Title and tagline | | |
| No forbidden product claims | | |
| No black frames or clipping | | |

## Disclosure

Concept footage from repository renders with Seedance cinematic visualization.
Generated footage is used only to visualize interactions already implemented
in the three-piece Apache vertical slice. It is not evidence of flight, combat,
native hand tracking, additional playable pieces, or other playable models.
