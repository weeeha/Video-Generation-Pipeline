# Experiments

Capability tests for the film pipeline — design doc:
[docs/superpowers/specs/2026-08-02-film-capability-tests-design.md](../docs/superpowers/specs/2026-08-02-film-capability-tests-design.md).

One folder per experiment: `tN-M-<slug>/` holding the prompt files used, and a
`findings.md` in this shape:

```
# tN.M — <name>
Setup: refs/packs/params used
Takes: | take | task id | tokens | verdict | note |
Verdict: PASS / PARTIAL / FAIL — one paragraph
Feeds: what changed in knowledge/, library/, or the workflow because of this
```

Rules: iterate on `--fast` @720p with pinned seeds; log every take including rejects
(retake rate IS a measurement — T3.3); download everything immediately; winners only
re-render at 1080p.

| ID | Experiment | Status | Spend |
|----|-----------|--------|-------|
| T1.1 | Two characters, one shot | **PASS** (take 1) | 173.7k |
| T1.2 | Shot / reverse-shot | **PASS** (take 2 + recipe) | 326.7k |
| T1.3 | World change | queued | — |
| T1.4 | Voice consistency | queued | — |
| T1.5 | Style lock | queued | — |
| T2.1 | Sketch → video | waiting on sketch | — |
| T2.2 | You-track (performance/composite) | waiting on footage | — |
| T2.3 | Blender scenes | waiting on Blender open | — |
| T3.1 | First+last match cut | queued | — |
| T3.2 | V2V retakes | queued | — |
| Capstone | 60–90s film scene | after tiers | — |
