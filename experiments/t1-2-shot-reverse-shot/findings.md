# T1.2 — Shot / reverse-shot

**Setup:** master = T1.1 two-shot; its 4.0s frame attached as `Image 9` on top of the
usual 8 pack refs. Two singles generated concurrently ("continuing the exact scene from
Image 9"), each with its character's line, opposing eyelines directed in text.
Fast @720p, 5s, seed 42.

**Takes:**

| take | task id | tokens | verdict | note |
|---|---|---|---|---|
| miles single t1 | cgt-20260803064501-krll8 | 108,900 | **KEEP** | eyeline screen-left ✓, correct (master-side) background |
| nova single t1 | cgt-20260803064516-sd886 | 108,900 | REJECT | camera never crossed the axis — same hood/fridge wall as miles' single; "reverse" silently ignored |
| nova single t2 | cgt-20260803065130-qq2vf | 108,900 | **KEEP** | axis crossed: window/sink wall behind her, eyeline screen-right; sliver of range at frame edge (acceptable) |

**Verdict: PASS (with recipe).** The three shots cut into a working scene
(`output/t1-2-scene-cut.mp4`: her single → his single → master's laughing tail; dialogue
order preserved, room tone survives the cuts at rough-cut quality).

**The capability limit found:** a master frame attached as a reference anchors
*composition AND camera axis*. Passive reverse language ("she looks camera-right, the
other wall behind her") loses to the reference. What works: explicit axis-cross
direction — "the camera has crossed to the opposite side and now shoots from where the
man stands", plus naming what IS behind her now, plus "the range hood and refrigerator
are NOT visible because they are behind the camera". One retake to learn it.

**Incidental:** state.json race between concurrent generates found here (miles' entry
clobbered, KeyError after a successful render; clip recovered free via `status`). Fixed
in the client with flock'd atomic updates, stress-verified.

**Feeds:**
- prompt-guide: new "Coverage" section with the axis-cross recipe.
- gotchas: master-frames-anchor-axis + the 21.7k tokens/sec constant.
- Retake data (T3.3): 4 generations → 3 keepers (1.33 gens/keeper incl. the learning take).
- Cards: singles logged as trusted outputs for both characters.
