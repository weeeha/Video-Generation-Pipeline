# VR Game Things Puzzle Seedance Promo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce one verified 25-30 second, 1080p hybrid promotional video for the implemented VR Game Things Puzzle AH-64 Apache Quest prototype.

**Architecture:** Work in an isolated Video Generation Pipeline worktree so concurrent MTL generations and task state cannot collide with this promo. Preserve the Unity repository as a read-only source, capture authentic prototype footage when the exact Unity project is available, generate four bounded Seedance Fast drafts and at most two full-model finals, then assemble a deterministic ffmpeg timeline with conventional titles and original mechanical sound design.

**Tech Stack:** Python 3, standard-library `unittest`, BytePlus ModelArk Seedance 2.0, the repository `pipeline/seedance.py` client, Unity 6000.3.18f1, OpenXR/XR Interaction Toolkit, ffmpeg/ffprobe.

## Global Constraints

- The paid Seedance generation cap is USD 12.
- Submit no more than four 5-second 720p Fast drafts and two 5-second 1080p Seedance 2.0 finals. Every final command must pass `--model 2.0`: `full` now resolves to Seedance 2.5.
- Do not pass `--seed`; current official Seedance 2.0 documentation does not support it.
- Use `--no-audio` for every Seedance task; the final soundtrack comes from authentic capture and original local sound design.
- Show exactly three playable pieces: cockpit, main rotor, and tail rotor.
- Do not imply combat, enemies, flight, controller-free hand tracking, a complete 13-piece playable assembly, multiplayer, painting, commerce, or other playable models.
- Do not modify, stage, discard, or commit any existing change in `/Users/nickv/VR-Game-Things-Puzzle/VR Game Things Puzzle`.
- Do not stage or commit the unrelated MTL files currently present in the main Video Generation Pipeline checkout.
- The final deliverable must be 1920x1080, 16:9, H.264, 24 or 30 fps, AAC stereo 48 kHz, and 25-30 seconds long.
- Every paid task must be dry-run first and logged with task ID, model, status, token usage, estimated cost, prompt path, and acceptance decision.

---

## File Structure

- `library/vehicles/apache-v1-promo/card.md` — canonical identity, truth boundary, reference numbering, and attribution notes.
- `library/vehicles/apache-v1-promo/refs/01-apache-studio.png` — finished Apache hero reference copied byte-for-byte from the Unity repository.
- `library/vehicles/apache-v1-promo/refs/02-apache-exploded.png` — prepared model structure reference copied byte-for-byte from the Unity repository.
- `library/vehicles/apache-v1-promo/refs/03-apache-assembled.png` — assembled prototype reference copied byte-for-byte from the Unity repository.
- `pipeline/prompts/vr-game-things-puzzle/01-cockpit-approach.md` — controlled cockpit-to-socket motion.
- `pipeline/prompts/vr-game-things-puzzle/02-magnetic-connection.md` — snap and material-reveal motion.
- `pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md` — cockpit/main-rotor/tail-rotor montage.
- `pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md` — completed-model hero motion.
- `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md` — task, usage, cost, QA, and disclosure record.
- `pipeline/promos/vr_game_things_puzzle/build.py` — validates a timeline manifest and builds the final ffmpeg command.
- `pipeline/promos/vr_game_things_puzzle/manifest.json` — stable shot order, durations, titles, and disclosure.
- `tests/test_vr_game_things_puzzle_promo.py` — manifest, duration, truth-boundary, and ffmpeg-command tests.
- `output/vr-game-things-puzzle-promo/source/` — authentic Unity capture and stills; ignored by Git.
- `output/vr-game-things-puzzle-promo/drafts/` — four 720p draft outputs and contact sheet; ignored by Git.
- `output/vr-game-things-puzzle-promo/finals/` — up to two accepted 1080p outputs; ignored by Git.
- `output/vr-game-things-puzzle-promo/vr-game-things-puzzle-promo-v1.mp4` — final deliverable; ignored by Git.

### Task 1: Add a deterministic promo assembler

**Files:**
- Create: `pipeline/promos/vr_game_things_puzzle/build.py`
- Create: `pipeline/promos/vr_game_things_puzzle/manifest.json`
- Create: `tests/test_vr_game_things_puzzle_promo.py`

**Interfaces:**
- Produces: `load_manifest(path: pathlib.Path) -> dict`, `validate_manifest(manifest: dict, repo: pathlib.Path) -> list[str]`, `timeline_duration(manifest: dict) -> float`, and `build_ffmpeg_command(manifest: dict, repo: pathlib.Path, output: pathlib.Path) -> list[str]`.
- Consumes: a JSON manifest containing `title`, `tagline`, `disclosure`, `fps`, `width`, `height`, and ordered `shots` with `path`, `duration`, and `kind`.

- [ ] **Step 1: Write manifest contract tests**

Create tests that require exact output dimensions, a 25-30 second duration, the approved title/tagline, only `unity`, `seedance`, or `title` shot kinds, and a disclosure whenever a Seedance shot exists:

```python
def test_manifest_matches_approved_delivery_contract(self):
    manifest = promo.load_manifest(MANIFEST)
    self.assertEqual((manifest["width"], manifest["height"]), (1920, 1080))
    self.assertIn(manifest["fps"], (24, 30))
    self.assertEqual(manifest["title"], "VR Game Things Puzzle")
    self.assertEqual(manifest["tagline"], "Build it. Then operate it.")
    self.assertGreaterEqual(promo.timeline_duration(manifest), 25.0)
    self.assertLessEqual(promo.timeline_duration(manifest), 30.0)
    self.assertTrue(any(shot["kind"] == "seedance" for shot in manifest["shots"]))
    self.assertIn("cinematic visualization", manifest["disclosure"].lower())
```

Add a second test requiring the narration/copy fields to exclude `combat`, `flight`, `hand tracking`, `13-piece`, `multiplayer`, `buy`, and `store purchase`.

- [ ] **Step 2: Run tests and verify RED**

Run:

```bash
python3 -m unittest tests/test_vr_game_things_puzzle_promo.py -v
```

Expected: import failure because `pipeline.promos.vr_game_things_puzzle.build` does not exist.

- [ ] **Step 3: Implement manifest parsing and validation**

Implement the four public functions. `validate_manifest` must return deterministic error strings for missing files, invalid dimensions, invalid fps, duration outside 25-30 seconds, unsupported shot kinds, missing disclosure, and forbidden claim words. `build_ffmpeg_command` must:

- scale/crop every source to 1920x1080 without stretching;
- trim each source to its manifest duration;
- normalize every source to the manifest fps and `yuv420p`;
- join shots with 0.25-second fades whose overlap is included in `timeline_duration`;
- generate conventional title/tagline text during the title shot;
- mix source audio when present with a restrained generated 55 Hz room hum and low-level pink noise;
- output H.264 video and AAC stereo 48 kHz audio.

The command must end with:

```python
["-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
 "-ar", "48000", "-ac", "2", "-movflags", "+faststart", str(output)]
```

- [ ] **Step 4: Create the approved manifest**

Use this exact shot contract:

```json
{
  "title": "VR Game Things Puzzle",
  "tagline": "Build it. Then operate it.",
  "disclosure": "Prototype footage with Seedance cinematic visualization.",
  "width": 1920,
  "height": 1080,
  "fps": 24,
  "transition": 0.25,
  "shots": [
    {"path": "output/vr-game-things-puzzle-promo/source/library.mp4", "duration": 3.0, "kind": "unity"},
    {"path": "output/vr-game-things-puzzle-promo/source/grab.mp4", "duration": 5.0, "kind": "unity"},
    {"path": "output/vr-game-things-puzzle-promo/source/snap.mp4", "duration": 5.0, "kind": "unity"},
    {"path": "output/vr-game-things-puzzle-promo/finals/final-assembly.mp4", "duration": 5.0, "kind": "seedance"},
    {"path": "output/vr-game-things-puzzle-promo/finals/final-hero.mp4", "duration": 5.0, "kind": "seedance"},
    {"path": "output/vr-game-things-puzzle-promo/source/operation.mp4", "duration": 4.0, "kind": "unity"},
    {"path": "output/vr-game-things-puzzle-promo/source/title.mp4", "duration": 3.5, "kind": "title"}
  ]
}
```

The 1.5 seconds of transition overlap produces a 29-second final timeline.

- [ ] **Step 5: Run tests and static checks**

Run:

```bash
python3 -m unittest tests/test_vr_game_things_puzzle_promo.py -v
python3 -m py_compile pipeline/promos/vr_game_things_puzzle/build.py
git diff --check
```

Expected: all tests pass, compilation succeeds, and no whitespace errors are reported.

- [ ] **Step 6: Commit**

```bash
git add pipeline/promos/vr_game_things_puzzle/build.py \
  pipeline/promos/vr_game_things_puzzle/manifest.json \
  tests/test_vr_game_things_puzzle_promo.py
git commit -m "Add reproducible VR puzzle promo assembler"
```

### Task 2: Add the Apache promo pack and prompt suite

**Files:**
- Create: `library/vehicles/apache-v1-promo/card.md`
- Create: `library/vehicles/apache-v1-promo/refs/01-apache-studio.png`
- Create: `library/vehicles/apache-v1-promo/refs/02-apache-exploded.png`
- Create: `library/vehicles/apache-v1-promo/refs/03-apache-assembled.png`
- Create: `pipeline/prompts/vr-game-things-puzzle/01-cockpit-approach.md`
- Create: `pipeline/prompts/vr-game-things-puzzle/02-magnetic-connection.md`
- Create: `pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md`
- Create: `pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md`
- Create: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`

**Interfaces:**
- Produces: a pack resolved by `--pack vehicles/apache-v1-promo` with Image 1 = finished studio, Image 2 = exploded structure, Image 3 = assembled prototype.
- Consumes: the three Apache PNGs in the Unity repository and the truth boundary in the approved design spec.

- [ ] **Step 1: Copy references without altering the Unity source**

Copy the three exact PNGs into the new pack. Compare source and destination SHA-256 values and require each pair to match.

- [ ] **Step 2: Write the canonical pack card**

Record the exact reference numbering, the three playable pieces, the quiet engineering-studio direction, the forbidden claims, and the source credit from `Documentation/CREDITS.md`. State that Image 2 documents model structure but must never be interpreted as thirteen playable pieces.

- [ ] **Step 3: Write the four exact prompts**

Each prompt must use this shared constraint block:

```text
Preserve the exact AH-64 Apache identity and proportions shown in the references. This is a tabletop VR engineering puzzle in a quiet dark blue-gray studio, not a battlefield. Only three pieces are playable: cockpit, main rotor, and tail rotor. Do not add parts, rotors, weapons, people, text, logos, enemies, explosions, flight, destruction, or camera shake. No watermark.
```

Prompt-specific actions:

- `01-cockpit-approach.md`: slow first-person product camera; one blue-gray virtual glove guides the gray cockpit toward a thin cyan socket; stop immediately before contact.
- `02-magnetic-connection.md`: macro view; cockpit moves the last few centimeters, aligns magnetically, seats once, cyan seam pulse, gray surface reveals the finished material; no bounce or repeated snap.
- `03-three-piece-assembly.md`: the already mostly assembled tabletop Apache remains fixed while only cockpit, main rotor, and tail rotor connect in that order; one readable action at a time; restrained mechanical precision.
- `04-hero-reveal.md`: completed tabletop Apache on the circular platform; slow 20-degree camera orbit; both rotors accelerate gently; one restrained non-projectile weapon-effect flash; the model never flies.

- [ ] **Step 4: Initialize the generation log**

Create sections for environment preflight, authentic capture, four draft tasks, draft QA matrix, two final tasks, cost ledger, export verification, and disclosure. Use empty Markdown table rows only for runtime values such as task IDs and token counts; do not use unresolved-marker text.

- [ ] **Step 5: Dry-run every prompt**

Run each prompt with `--pack vehicles/apache-v1-promo --fast --resolution 720p --duration 5 --ratio 16:9 --no-audio --dry-run`. Assert the redacted request contains the fast model, three `reference_image` roles, integer duration `5`, `generate_audio: false`, `watermark: false`, and no `seed` field.

- [ ] **Step 6: Commit**

```bash
git add library/vehicles/apache-v1-promo \
  pipeline/prompts/vr-game-things-puzzle
git commit -m "Add Apache promo references and Seedance prompts"
```

### Task 3: Capture authentic Unity prototype footage

**Files:**
- Create ignored media under: `output/vr-game-things-puzzle-promo/source/`
- Modify: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`

**Interfaces:**
- Produces stable source names: `library.mp4`, `grab.mp4`, `snap.mp4`, `operation.mp4`, plus opening/closing PNGs for Seedance first/last-frame control.
- Consumes the live `ApachePrototype.unity` scene only after the exact project root is verified.

- [ ] **Step 1: Verify project identity before control**

Require the live Unity project root to equal:

```text
/Users/nickv/VR-Game-Things-Puzzle/VR Game Things Puzzle
```

Require the active scene to be `Assets/Game/Scenes/ApachePrototype.unity` and the Console to contain zero compiler errors. If another project is connected, do not mutate it.

- [ ] **Step 2: Record the clean product flow**

Capture these authentic beats at 1920x1080 when available:

1. Library card and Start Assembly action, 3-4 seconds.
2. Gray cockpit grab and movement toward the socket, 5-6 seconds.
3. Magnetic snap and gray-to-finished material reveal, 5-6 seconds.
4. Completion Play action, rotor motion, and single restrained weapon effect, 4-6 seconds.

Do not alter scene files or save Unity changes during capture.

- [ ] **Step 3: Normalize captures**

Use ffmpeg to scale/crop each clip to 1920x1080, preserve source audio, normalize to 24 fps, and save the four stable filenames. Extract the exact start/end PNGs required by the first/last-frame draft commands.

- [ ] **Step 4: Validate captures**

Run ffprobe on every clip and require H.264-compatible video, 1920x1080 dimensions, 24 fps, and at least the manifest duration. Watch each clip once and record whether it is authentic capture or repository-render fallback.

- [ ] **Step 5: Fallback if live capture is unavailable**

Create the four stable source clips from the repository stills using restrained ffmpeg pan/zoom moves. Render `Concept footage` visibly in the title/disclosure plate and record the fallback in the generation log. Do not claim these clips are gameplay.

- [ ] **Step 6: Commit the updated log only**

```bash
git add pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md
git commit -m "Log VR puzzle promo source capture"
```

### Task 4: Generate and evaluate four bounded drafts

**Files:**
- Create ignored media under: `output/vr-game-things-puzzle-promo/drafts/`
- Modify: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`

**Interfaces:**
- Produces four task IDs and up to four 720p draft MP4s.
- Consumes the approved prompts, pack, and normalized source keyframes.

- [ ] **Step 1: Re-run all four dry-runs immediately before spending**

Confirm model, asset roles, five-second duration, 720p resolution, silent output, no watermark, and no seed.

- [ ] **Step 2: Submit the four draft tasks with unique names**

Use these names and commands. The executable promo guard derives its reserved
request from the exact Seedance arguments, records the estimated cost, and only
then delegates to the general CLI:

```bash
python3 pipeline/promos/vr_game_things_puzzle/guard.py generate --stage draft --estimated-cost-usd 0.61 -- generate --prompt-file pipeline/prompts/vr-game-things-puzzle/01-cockpit-approach.md --pack vehicles/apache-v1-promo --fast --resolution 720p --duration 5 --ratio 16:9 --no-audio --name vrgtp-d01-cockpit-approach
python3 pipeline/promos/vr_game_things_puzzle/guard.py generate --stage draft --estimated-cost-usd 0.61 -- generate --prompt-file pipeline/prompts/vr-game-things-puzzle/02-magnetic-connection.md --pack vehicles/apache-v1-promo --fast --resolution 720p --duration 5 --ratio 16:9 --no-audio --name vrgtp-d02-magnetic-connection
python3 pipeline/promos/vr_game_things_puzzle/guard.py generate --stage draft --estimated-cost-usd 0.61 -- generate --prompt-file pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md --pack vehicles/apache-v1-promo --fast --resolution 720p --duration 5 --ratio 16:9 --no-audio --name vrgtp-d03-three-piece-assembly
python3 pipeline/promos/vr_game_things_puzzle/guard.py generate --stage draft --estimated-cost-usd 0.61 -- generate --prompt-file pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md --pack vehicles/apache-v1-promo --fast --resolution 720p --duration 5 --ratio 16:9 --no-audio --name vrgtp-d04-hero-reveal
```

Move downloaded outputs to the `drafts/` directory without deleting the client state record.

- [ ] **Step 3: Record usage and cost**

Retrieve each task after success and record its task ID, model, resolution, duration, completion tokens, and estimated cost. Require the four-draft subtotal to remain at or below USD 2.50 before continuing.

- [ ] **Step 4: Build a review contact sheet**

Extract frames at 1, 3, and 4.5 seconds from each draft and arrange them into a labeled 4x3 contact sheet. Keep labels outside the generated imagery.

- [ ] **Step 5: Score every draft**

Score 0-2 on each criterion: Apache identity, exactly three-piece truth boundary, mechanical readability, studio tone, temporal stability, and edit usefulness. Reject any clip with extra rotors/pieces, malformed hands, combat/flight, generated text, or a score below 8/12. Select no more than two concepts for final generation.

- [ ] **Step 6: Stop condition**

If no draft passes, commit the completed failure log and stop without submitting full-model tasks. If one passes, generate one final. If two or more pass, generate only the two highest-scoring distinct concepts.

- [ ] **Step 7: Commit the draft log**

```bash
git add pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md
git commit -m "Evaluate VR puzzle Seedance promo drafts"
```

### Task 5: Generate and verify at most two 1080p finals

**Files:**
- Create ignored media under: `output/vr-game-things-puzzle-promo/finals/`
- Modify: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`

**Interfaces:**
- Produces `final-assembly.mp4` and `final-hero.mp4` when the matching concepts pass.
- Consumes only the accepted prompt concepts and the same Apache reference pack.

- [ ] **Step 1: Calculate the pre-submit spend ceiling**

Use recorded draft token usage and the official 1080p no-video estimate of approximately USD 1.87 per five-second full-model output. Do not submit a final if its expected cost could make the cumulative run exceed USD 12.

- [ ] **Step 2: Dry-run accepted final concepts**

Use the explicit Seedance 2.0 model flag; removing `--fast` alone is no longer
safe because `full` now resolves to Seedance 2.5. Retain 1080p, five seconds,
16:9, silent output, no watermark, and no seed. Confirm each body uses
`dreamina-seedance-2-0-260128`.

```bash
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f01-assembly --dry-run
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f02-hero --dry-run
```

- [ ] **Step 3: Submit at most two finals**

Use stable names `vrgtp-f01-assembly` and `vrgtp-f02-hero`. Reuse the exact accepted prompts and the Apache pack. Do not add a video reference unless an accepted draft contains essential motion that cannot be described; if video input becomes necessary, recalculate against the USD 12 cap before submission. Route every paid submission through the executable `guard.py` path; it reserves the name and request fingerprint in the promo ledger before it delegates to the general CLI.

```bash
python3 pipeline/promos/vr_game_things_puzzle/guard.py generate --stage final --estimated-cost-usd 1.89 -- generate --prompt-file pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f01-assembly
python3 pipeline/promos/vr_game_things_puzzle/guard.py generate --stage final --estimated-cost-usd 1.89 -- generate --prompt-file pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f02-hero
```

- [ ] **Step 4: Verify final media**

Require 1920x1080, 24 fps, five-second duration, silent audio state, no watermark, and the same truth-boundary review used for drafts. Reject a final that is less faithful than its draft concept.

- [ ] **Step 5: Normalize stable final filenames**

Copy accepted outputs to `final-assembly.mp4` and `final-hero.mp4`. If only one final exists, replace the other manifest slot with an authentic Unity clip and re-run the manifest duration test; do not fabricate a second AI clip.

- [ ] **Step 6: Commit the final-generation log**

```bash
git add pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md
git commit -m "Log accepted VR puzzle Seedance finals"
```

### Task 6: Assemble, inspect, and deliver the promo

**Files:**
- Modify when fallback selection changes: `pipeline/promos/vr_game_things_puzzle/manifest.json`
- Modify: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`
- Create ignored final: `output/vr-game-things-puzzle-promo/vr-game-things-puzzle-promo-v1.mp4`

**Interfaces:**
- Produces the final 1080p promo and complete audit log.
- Consumes the stable source/final filenames from Tasks 3 and 5.

- [ ] **Step 1: Validate the complete manifest**

Run the builder in validation mode. Require every referenced file to exist, the computed duration to remain 25-30 seconds, disclosure to be present, and no forbidden claims.

- [ ] **Step 2: Build the final export**

Run `build.py` with the approved manifest and final output path. Capture the exact ffmpeg command in the generation log. Fail on any ffmpeg non-zero exit status.

- [ ] **Step 3: Verify technical delivery**

Use ffprobe to require:

- 1920x1080;
- H.264 video;
- 24 fps;
- 25-30 seconds;
- AAC stereo audio;
- 48 kHz sample rate;
- `yuv420p` pixel format;
- fast-start metadata.

- [ ] **Step 4: Perform visual and audio QA**

Watch the complete export with audio. Confirm exact Apache identity, exactly three playable pieces, readable connection actions, no invented features, correct title/tagline, visible disclosure, no black frames, no malformed hands, no AI text, no extra rotors, no watermark, no clipping, and no abrupt audio cuts.

- [ ] **Step 5: Run repository verification**

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile pipeline/seedance.py pipeline/promos/vr_game_things_puzzle/build.py
git diff --check
git status --short --branch
```

Require all tests to pass and confirm only intended promo files are staged/committed.

- [ ] **Step 6: Commit the delivery record**

```bash
git add pipeline/promos/vr_game_things_puzzle/manifest.json \
  pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md
git commit -m "Complete VR Game Things Puzzle promo"
```

- [ ] **Step 7: Hand off artifacts**

Provide clickable paths to the final MP4, contact sheet, generation log, and accepted source clips. Report the final cumulative cost, task IDs, authentic-versus-cinematic disclosure, and any remaining device-validation limitation.

## Plan Self-Review

- Spec coverage: creative direction, exact storyboard, truth boundary, authentic capture, four drafts, two finals, USD 12 cap, conventional typography, sound continuity, failure paths, technical verification, disclosure, and delivery logging each map to a task.
- Isolation: the plan begins execution in a dedicated worktree and never stages the main checkout's MTL files or the Unity worktree's local changes.
- Determinism: stable prompt, media, manifest, and output names allow interrupted tasks to resume without creating duplicate paid jobs.
- Budget: four expected USD 0.60 drafts plus two expected USD 1.87 finals totals approximately USD 6.14; the hard cap remains USD 12.
- Truthfulness: every generation and edit gate rejects extra pieces, flight, combat, native hand tracking, and unimplemented product claims.
- No placeholders: runtime task IDs, token counts, costs, and QA decisions are explicitly treated as observed log values rather than invented plan data.
