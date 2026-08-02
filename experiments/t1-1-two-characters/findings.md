# T1.1 — Two characters, one shot

**Setup:** `--pack people/nova --pack people/miles --pack places/warm-kitchen` (8/9 ref
slots: nova 1–3, miles 4–6, kitchen 7–8), 8s, fast @720p, seed 42, native audio with
scripted two-line exchange. Prompt: [shot-two-shot.md](shot-two-shot.md) (includes an
explicit "do not blend their facial features" instruction).

**Takes:**

| take | task id | tokens | verdict | note |
|---|---|---|---|---|
| 1 | cgt task in state.json (t1-1-two-shot-t1) | 173,700 | **KEEP** | pass on first roll |

**Verdict: PASS.** Zero identity bleed across the full clip — Nova keeps her face/hair/
cream sweater, Miles keeps his face/beard/round amber glasses (glasses present in every
sampled frame). Kitchen holds its element language (cream shakers, subway tile, farmhouse
sink, hood, fridge, island + stools) and the window-left light, with layout rearranged
(consistent with "refs anchor, words steer"). Scripted action (mug handoff → shared laugh)
executed. Dialogue turn-taking verified by local whisper transcription: "Fresh pot"
[0.0–2.0], "You're a lifesaver" [3.6–5.6] — correct order, natural pacing, no overlap.

**Cost datapoint (T3.3):** fast @720p ≈ **21.7k tokens/second** (8s = 173.7k; 5s clips =
108.9k). Linear in duration.

**Feeds:**
- Two-hander scenes are viable → capstone dialogue scene is realistic.
- Strong distinct identity anchors (glasses/beard vs. none) likely helped — test
  similar-looking characters before relying on this for ensemble casts.
- Master frame from this clip seeds T1.2 (shot/reverse-shot).
- knowledge/gotchas.md: add tokens/second figure + two-character pass.
