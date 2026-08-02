# T3.2 — V2V surgical retakes

**Setup:** target = the unprompted Apple logo from T1.3's cafe clip. Input video via
public raw.githubusercontent URL (asset:// blocked until the Asset Service is activated
on the account — probe documented in gotchas). Fast @720p, 5s, seed 42.

**Takes:**

| take | tokens | verdict | note |
|---|---|---|---|
| 1 (asset:// probe) | 0 | BLOCKED | clean 400: "account has not activated the Asset Service" — free discovery |
| 2 ("remove the glowing logo…") | 216,900 | REJECT* | **inverted**: logo got bigger and actually glowing — naming the artifact rendered it |
| 3 ("lid is completely blank brushed aluminum, no logo…") | 216,900 | **KEEP** | lid clean; scene preserved closely |

*kept as evidence — the best demonstration of the negation trap we have.

**Verdict: PASS on take 3, with three rules:**
1. **End-state phrasing only.** Describe what the shot should contain, never what to
   remove — "remove the glowing X" reads as "render a glowing X".
2. **Preservation is loose, not surgical.** V2V regenerates the scene close-but-not-
   identical (background details drift). Right tool for object swaps and content fixes
   where minor drift is invisible in a cut; frame-exact cleanup belongs in post.
3. **V2V costs ~2× T2V** — 216.9k for a 5s fast edit (~43.4k/s vs 21.7k/s). A retake
   of a 90%-good shot is still cheaper than re-rolling a scene, but it's not cheap.

**Feeds:** gotchas (all three rules); the end-state principle generalizes to ALL
prompting, not just V2V.
