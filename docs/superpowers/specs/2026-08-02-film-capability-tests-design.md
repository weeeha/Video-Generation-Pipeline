# Film Capability Tests — Design

**Date:** 2026-08-02 · **Status:** approved (Nick, option 1)
**Deadline driver:** 6,694,422 Seedance 2.0 tokens expire **2026-08-06 23:59 UTC+8**.
**Strategic question answered by these tests:** is this pipeline good enough to buy more
2.0 packs and produce Nick's three films (Highfleet, Mtl, Exodus — loglines pending)?
R2V references (the whole `library/` system) are 2.0-only; the 1.x fallback packs
(10M tokens, valid to 2028) cannot run this workflow.

## Goal

Prove (or disprove) every capability a full narrative film needs, cheaply and in
isolation, before spending on real sequences. Every experiment leaves reusable assets
(library packs, `asset://` refs, knowledge entries) and logs takes-per-keeper for cost
modeling.

## Already settled — no testing

Single-character R2V consistency; within-scene chaining (I2V last-frame); native ambient
audio; on-screen text → burn in post; ffmpeg assembly; ops rules (24h URLs, 7-day tasks,
seed pinning). Sources: this repo's Nova/warm-kitchen runs + the PermitNav production run.

## Tier 1 — world coherence (~1.5M tokens)

| ID | Test | Protocol | Pass looks like |
|----|------|----------|-----------------|
| T1.1 | Two characters, one shot | Cast 2nd character (Miles). Attach nova(3) + miles(3) + warm-kitchen(2) refs = 8/9. One interaction beat with dialogue turn-taking, 8s. Retake at new seed if identities bleed. | Both stay on-model; no face averaging; dialogue alternates correctly |
| T1.2 | Shot / reverse-shot | Master two-shot (T1.1 output) → generate matching singles: "same scene as Image N (master frame), now a close-up on the man, eyeline camera-left". Check background + light + eyeline continuity across 3 shots. | The three shots cut together as one scene |
| T1.3 | Character survives world change | Nova at night / outdoors / new wardrobe (2–3 shots). | Identity holds outside her home lighting/outfit |
| T1.4 | Voice consistency | Same character speaks in two separately generated shots. Compare voices. | Verdict: native dialogue viable vs. ElevenLabs dub-in-post |
| T1.5 | Style lock | One style anchor (repeated palette/look phrase + style ref image) across 3 different-content shots. | Look reads as one film |

## Tier 2 — authoring inputs (~1.6M) — needs Nick's inputs

| ID | Test | Protocol |
|----|------|----------|
| T2.1 | Sketch → video | Nick's sketch: (a) raw as reference_image; (b) sketch → Seedream keyframe → first_frame; (c) sketch → GPT Image 2 keyframe → first_frame. Winner re-runs 1080p. |
| T2.2 | You-track: performance | (a) face-visible clip → document rejection; (b) face-covered take → motion ref onto Nova; (c) green-screen composite: locked-off take of Nick + generated background plate, key + composite in post; (d) Nick starts real-person verification in console (his action; unlocks face-as-asset:// if approved in time). |
| T2.3 | Blender scene consistency | Script distinctive two-room set via Blender MCP; render 3–4 angles/room; (a) renders as place refs → generate unrendered angle; (b) render as first_frame + cinematic restyle. Renders also become composite plates for T2.2c and permanent places/ packs. |

Input dependencies: sketch photo + performance clips → `~/Downloads`; Blender open with
MCP addon; loglines ×3 (for theming + capstone).

## Tier 3 — efficiency (~550k)

| ID | Test | Payoff |
|----|------|--------|
| T3.1 | First+last frame as match-cut tool | Action continuity across cuts |
| T3.2 | V2V surgical retakes (remove/replace element; extend) | Fix 90%-good shots for one clip's cost |
| T3.3 | Retake-rate logging (passive, all tests) | Real cost multiplier for film budgeting |

## Capstone — integration (~1.6M)

60–90s two-character dialogue scene from one of the three films: 6–8 shots, one location,
shot/reverse-shot coverage, one style anchor, audio per T1.4 verdict, assembled with
ffmpeg. Pass = it cuts together as cinema. This is the go/no-go artifact for buying more
2.0 packs.

## Budget

T1 ~1.5M · T2 ~1.65M · T3 ~0.55M · capstone ~1.6M · retake buffer ~1.0M ≈ **6.3M of 6.69M**.
Iteration on `--fast` @720p seed-pinned; only winners re-render 1080p full model.
All spend logged per-experiment in `experiments/*/findings.md`.

## Structure & flow

`experiments/tN-M-<slug>/` = prompt files + findings.md (setup, takes table, verdict,
what-it-feeds). Verdicts flow into `knowledge/gotchas.md` / `prompt-guide.md`; assets into
`library/`; film work later into `films/<name>/`.

## Authenticity thesis (Nick's requirement)

The films must be provably an artist's work, not "just generated": Nick literally
in frame via green-screen composite over generated/Blender worlds (T2.2c), his body
performance transferred to characters (T2.2b), face-driven work via official verification
(T2.2d), plus published side-by-side making-ofs as proof of craft.

## Attack order

1. T1.1–T1.2 (no inputs needed) → 2. Nick's tests as inputs land (T2.x) →
3. T1.3–T1.5 + T3 → 4. capstone Wed with everything learned → 5. any surplus →
library harvest (motion refs, B-roll).
