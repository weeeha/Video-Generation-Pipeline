# VR Game Things Puzzle Promo PR Repair Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the completed VR Game Things Puzzle promo so its tracked source package, deterministic builder, paid-run safeguards, final media, and documentation are truthful and ready for a pull request.

**Architecture:** Keep deterministic assembly separate from paid Seedance submission. A corrected manifest points only to tracked accepted media, drives a locally rendered slate and matched audio/video timelines, and feeds a standalone media verifier; a separate promo-specific guard validates and atomically records any future paid task before delegating to the general Seedance client.

**Tech Stack:** Python 3.14, Pillow 12.2, pytest, ffmpeg 8.1, ffprobe, standard-library JSON/hashlib/pathlib/subprocess/tempfile/fcntl, Git, GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-08-06-vr-game-things-puzzle-promo-design.md`

## Global Constraints

- Use no new paid Seedance generation during this repair.
- Show exactly three playable pieces: cockpit, main rotor, and tail rotor.
- Remove both source videos derived from the 13-system exploded render.
- Preserve the historical record that seven drafts and two finals were submitted.
- Pin historical full-model final commands to `--model 2.0` (`dreamina-seedance-2-0-260128`).
- Keep the paid cap at USD 12, four drafts, and two finals.
- Generate title, tagline, and disclosure from `manifest.json`; do not consume `title.mp4`.
- Preserve declared source audio, substitute silence for silent shots, and mix restrained original ambience below the source timeline.
- Track only accepted media required to reproduce/review the edit; do not track rejected clips.
- Do not modify or stage the Unity repository or the unrelated untracked MTL63 files in the main checkout.
- Final output: 1920x1080, H.264, `yuv420p`, 24 fps, AAC stereo 48 kHz, 25-30 seconds, fast-start MP4.

---

## File Structure

- `deliverables/vr-game-things-puzzle-promo/source/library.mp4` — assembled-model repository render, three-second opening.
- `deliverables/vr-game-things-puzzle-promo/source/operation.mp4` — assembled-model repository render, four-second operation hold.
- `deliverables/vr-game-things-puzzle-promo/accepted/d02b-connection.mp4` — accepted 720p Seedance connection clip.
- `deliverables/vr-game-things-puzzle-promo/accepted/d03a-assembly.mp4` — accepted 720p Seedance assembly clip.
- `deliverables/vr-game-things-puzzle-promo/accepted/final-assembly.mp4` — accepted 1080p Seedance assembly final.
- `deliverables/vr-game-things-puzzle-promo/accepted/final-hero.mp4` — accepted 1080p Seedance hero final.
- `deliverables/vr-game-things-puzzle-promo/final/promo.mp4` — rebuilt final export.
- `deliverables/vr-game-things-puzzle-promo/final/contact-sheet.png` — review sheet sampled from the rebuilt export.
- `deliverables/vr-game-things-puzzle-promo/SHA256SUMS` — hashes for every tracked binary deliverable.
- `pipeline/promos/vr_game_things_puzzle/manifest.json` — single source of truth for copy, provenance, shots, audio declarations, timing, and output format.
- `pipeline/promos/vr_game_things_puzzle/slate.py` — deterministic Pillow slate renderer.
- `pipeline/promos/vr_game_things_puzzle/build.py` — manifest validator and matched ffmpeg audio/video timeline builder.
- `pipeline/promos/vr_game_things_puzzle/verify.py` — ffprobe, MP4 atom-order, and SHA-256 verification.
- `pipeline/promos/vr_game_things_puzzle/generation-policy.json` — immutable count/spend limits.
- `pipeline/promos/vr_game_things_puzzle/generation-ledger.json` — append-only historical task/reservation records.
- `pipeline/promos/vr_game_things_puzzle/guard.py` — paid-task fingerprinting, limit validation, atomic reservation, and delegated execution.
- `tests/test_vr_game_things_puzzle_promo.py` — manifest, slate, assembler, verifier, model-pin, and fresh-checkout behavior.
- `tests/test_vr_game_things_puzzle_guard.py` — offline paid-run guard behavior.
- `requirements.txt` — pinned runtime/test dependencies used by the repaired workflow.
- `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md` — corrected audit record, commands, artifact hashes, and review result.

### Task 1: Correct the manifest and create the durable accepted-media package

**Files:**
- Modify: `pipeline/promos/vr_game_things_puzzle/manifest.json`
- Modify: `tests/test_vr_game_things_puzzle_promo.py`
- Create: `deliverables/vr-game-things-puzzle-promo/source/library.mp4`
- Create: `deliverables/vr-game-things-puzzle-promo/source/operation.mp4`
- Create: `deliverables/vr-game-things-puzzle-promo/accepted/d02b-connection.mp4`
- Create: `deliverables/vr-game-things-puzzle-promo/accepted/d03a-assembly.mp4`
- Create: `deliverables/vr-game-things-puzzle-promo/accepted/final-assembly.mp4`
- Create: `deliverables/vr-game-things-puzzle-promo/accepted/final-hero.mp4`

**Interfaces:**
- Consumes: the six already accepted local media files under `output/vr-game-things-puzzle-promo/`.
- Produces: manifest shots with `path: str | null`, `duration: float`, `kind: repository | seedance | title`, `has_audio: bool`, and `source_assets: list[str]`.

- [ ] **Step 1: Write failing truth-boundary and fresh-checkout tests**

Add tests whose literal expected behavior is:

```python
def test_manifest_excludes_thirteen_system_fallbacks():
    manifest = promo.load_manifest(MANIFEST)
    paths = [str(shot.get("path", "")) for shot in manifest["shots"]]
    assert not any(path.endswith(("grab.mp4", "snap.mp4")) for path in paths)
    assert not any(
        "exploded" in asset.lower()
        for shot in manifest["shots"]
        for asset in shot.get("source_assets", [])
    )


def test_manifest_uses_only_tracked_inputs_from_fresh_checkout():
    manifest = promo.load_manifest(MANIFEST)
    errors = promo.validate_manifest(manifest, REPO, require_files=True)
    assert errors == []
    assert all(
        shot["kind"] == "title"
        or str(shot["path"]).startswith("deliverables/vr-game-things-puzzle-promo/")
        for shot in manifest["shots"]
    )
```

- [ ] **Step 2: Run the two tests and verify RED**

Run:

```bash
python3 -m pytest -q \
  tests/test_vr_game_things_puzzle_promo.py::test_manifest_excludes_thirteen_system_fallbacks \
  tests/test_vr_game_things_puzzle_promo.py::test_manifest_uses_only_tracked_inputs_from_fresh_checkout
```

Expected: both fail because the current manifest still uses ignored `grab.mp4`, `snap.mp4`, and `title.mp4` paths.

- [ ] **Step 3: Copy only accepted media into the tracked package**

Create the package directories and copy these exact files without transcoding:

```text
output/.../source/library.mp4                 -> deliverables/.../source/library.mp4
output/.../source/operation.mp4               -> deliverables/.../source/operation.mp4
output/.../drafts/d02b-connection.mp4         -> deliverables/.../accepted/d02b-connection.mp4
output/.../drafts/d03a-assembly.mp4           -> deliverables/.../accepted/d03a-assembly.mp4
output/.../finals/final-assembly.mp4           -> deliverables/.../accepted/final-assembly.mp4
output/.../finals/final-hero.mp4               -> deliverables/.../accepted/final-hero.mp4
```

Verify source/destination SHA-256 equality for all six pairs before staging.

- [ ] **Step 4: Replace the manifest with the corrected 29-second contract**

Use this shot sequence; the title shot deliberately has no media path:

```json
[
  {"path":"deliverables/vr-game-things-puzzle-promo/source/library.mp4","duration":3.0,"kind":"repository","has_audio":false,"source_assets":["library/vehicles/apache-v1-promo/refs/01-apache-studio.png"]},
  {"path":"deliverables/vr-game-things-puzzle-promo/accepted/d02b-connection.mp4","duration":5.0,"kind":"seedance","has_audio":false,"source_assets":["pipeline/prompts/vr-game-things-puzzle/02-magnetic-connection.md"]},
  {"path":"deliverables/vr-game-things-puzzle-promo/accepted/d03a-assembly.mp4","duration":5.0,"kind":"seedance","has_audio":false,"source_assets":["pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md"]},
  {"path":"deliverables/vr-game-things-puzzle-promo/accepted/final-assembly.mp4","duration":5.0,"kind":"seedance","has_audio":false,"source_assets":["pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md"]},
  {"path":"deliverables/vr-game-things-puzzle-promo/accepted/final-hero.mp4","duration":5.0,"kind":"seedance","has_audio":false,"source_assets":["pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md"]},
  {"path":"deliverables/vr-game-things-puzzle-promo/source/operation.mp4","duration":4.0,"kind":"repository","has_audio":false,"source_assets":["library/vehicles/apache-v1-promo/refs/03-apache-assembled.png"]},
  {"path":null,"duration":3.5,"kind":"title","has_audio":false,"source_assets":[]}
]
```

- [ ] **Step 5: Extend manifest validation minimally**

Require `has_audio` to be Boolean; require no path for title shots and a durable path for every other shot; reject any repository `source_assets` entry containing `exploded`.

- [ ] **Step 6: Run the full promo test file and verify GREEN**

Run `python3 -m pytest -q tests/test_vr_game_things_puzzle_promo.py` and require all tests to pass.

- [ ] **Step 7: Commit**

```bash
git add deliverables/vr-game-things-puzzle-promo/source \
  deliverables/vr-game-things-puzzle-promo/accepted \
  pipeline/promos/vr_game_things_puzzle/manifest.json \
  tests/test_vr_game_things_puzzle_promo.py
git commit -m "Replace unsafe promo fallback footage"
```

### Task 2: Make slate, audio, and output verification deterministic

**Files:**
- Create: `pipeline/promos/vr_game_things_puzzle/slate.py`
- Modify: `pipeline/promos/vr_game_things_puzzle/build.py`
- Create: `pipeline/promos/vr_game_things_puzzle/verify.py`
- Modify: `tests/test_vr_game_things_puzzle_promo.py`
- Create: `requirements.txt`

**Interfaces:**
- Produces: `render_slate(manifest: dict, path: pathlib.Path) -> pathlib.Path`.
- Produces: `build_ffmpeg_command(manifest: dict, repo: pathlib.Path, output: pathlib.Path, slate_path: pathlib.Path) -> list[str]`.
- Produces: `probe_media(path: pathlib.Path) -> dict`, `verify_media(path: pathlib.Path, expected: dict) -> list[str]`, and `sha256_file(path: pathlib.Path) -> str`.
- Consumes: manifest copy fields and per-shot `has_audio` declarations from Task 1.

- [ ] **Step 1: Write a failing manifest-driven slate test**

Render two slates that differ only in `tagline`, then assert the PNG byte hashes differ. Also assert the original manifest produces a 1920x1080 RGB image.

```python
first = slate.render_slate(manifest, tmp_path / "first.png")
changed = copy.deepcopy(manifest)
changed["tagline"] = "A different approved line"
second = slate.render_slate(changed, tmp_path / "second.png")
assert Image.open(first).size == (1920, 1080)
assert hashlib.sha256(first.read_bytes()).digest() != hashlib.sha256(second.read_bytes()).digest()
```

- [ ] **Step 2: Run the slate test and verify RED**

Expected: import failure because `slate.py` does not exist.

- [ ] **Step 3: Implement the minimal slate renderer**

Use `PIL.Image.new("RGB", (width, height), "#0b1119")`, `ImageFont.load_default(size=...)`, and centered `multiline_text` calls. Render title, tagline, and disclosure in distinct vertical bands with at least 96, 54, and 28 pixel font sizes and 10% horizontal safe margins.

- [ ] **Step 4: Write failing matched-audio command tests**

Create a two-shot manifest with one `has_audio: true` shot and one silent shot. Require the filter graph to contain:

```text
[0:a]aresample=48000
anullsrc=channel_layout=stereo:sample_rate=48000
acrossfade=d=0.250
[source_audio][ambience]amix=inputs=2
```

Also require the title input path to be the generated slate path, not `title.mp4`.

- [ ] **Step 5: Run the audio tests and verify RED**

Expected: failure because the current builder never consumes shot audio and assumes every shot has a file path.

- [ ] **Step 6: Implement matched video/audio assembly**

Generate the slate before command construction. Add the slate as a looped image input for the title shot. For each shot:

```python
if shot["has_audio"]:
    filters.append(f"[{input_index}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=duration={duration:.3f},asetpts=PTS-STARTPTS[a{index}]")
else:
    filters.append(f"anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration={duration:.3f},asetpts=PTS-STARTPTS[a{index}]")
```

Join shot audio with the same 0.25-second overlaps as video using `acrossfade`. Mix the result with the restrained pink-noise/55-Hz ambience and add two short filtered mechanical impulses at the connection beats. Keep the limiter and AAC stereo output contract.

- [ ] **Step 7: Write failing verifier tests**

Create one tiny valid MP4 with ffmpeg and assert `verify_media` returns `[]`. Create an invalid 640x360 file and assert the literal error `"dimensions must be 1920x1080, got 640x360"`. Test `sha256_file` against the literal SHA-256 of `b"abc"`.

- [ ] **Step 8: Implement the verifier and verify GREEN**

Call ffprobe with JSON output and inspect the first video/audio streams. Check the `moov` atom occurs before `mdat` in the MP4 bytes. Return deterministic errors rather than raising for media mismatches.

- [ ] **Step 9: Pin dependencies and run Task 2 verification**

Create:

```text
Pillow==12.2.0
pytest==9.0.3
requests==2.33.1
```

Run the promo tests, `py_compile` on `build.py`, `slate.py`, and `verify.py`, and `git diff --check`.

- [ ] **Step 10: Commit**

```bash
git add requirements.txt pipeline/promos/vr_game_things_puzzle \
  tests/test_vr_game_things_puzzle_promo.py
git commit -m "Make promo assembly deterministic"
```

### Task 3: Guard future paid runs and pin the historical Seedance model

**Files:**
- Create: `pipeline/promos/vr_game_things_puzzle/generation-policy.json`
- Create: `pipeline/promos/vr_game_things_puzzle/generation-ledger.json`
- Create: `pipeline/promos/vr_game_things_puzzle/guard.py`
- Create: `tests/test_vr_game_things_puzzle_guard.py`
- Modify: `docs/superpowers/plans/2026-08-06-vr-game-things-puzzle-promo.md`
- Modify: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`

**Interfaces:**
- Produces: `fingerprint_request(request: dict) -> str`, `validate_request(policy: dict, ledger: list[dict], request: dict) -> list[str]`, `reserve_request(ledger_path: pathlib.Path, request: dict) -> dict`, and `guarded_generate(request: dict, argv: list[str], runner=subprocess.run) -> int`.
- Consumes: policy keys `max_drafts: 4`, `max_finals: 2`, `max_usd: 12.0` and historical ledger entries for seven drafts/two finals.

- [ ] **Step 1: Write failing offline guard tests**

Cover these independent behaviors with literal expectations:

```python
assert guard.validate_request(policy, four_drafts, fifth_draft) == ["draft limit reached: 4/4"]
assert guard.validate_request(policy, two_finals, third_final) == ["final limit reached: 2/2"]
assert guard.validate_request(policy, existing, duplicate) == ["duplicate request fingerprint"]
assert guard.validate_request(policy, spent_11_60, costs_0_61) == ["spend cap exceeded: USD 12.21 > USD 12.00"]
```

Also verify a valid request is appended exactly once before an injected local runner is called, and a blocked request never calls the runner.

- [ ] **Step 2: Run the guard tests and verify RED**

Expected: import failure because `guard.py` does not exist.

- [ ] **Step 3: Implement fingerprinting and validation**

Hash canonical JSON containing only `stage`, `prompt_sha256`, `model`, `resolution`, `duration`, `ratio`, `generate_audio`, and `watermark`. Reject duplicate names and fingerprints, stage count overflow, and projected spend overflow.

- [ ] **Step 4: Implement atomic reservation and delegation**

Lock `generation-ledger.json` with `fcntl.flock`, reread it under the lock, validate, append a `reserved` record, write JSON to a sibling temporary file, `os.replace` it, then call the injected runner with `check=False`. Update the reservation to `delegated` or `failed_to_start` in a second atomic append-only event.

- [ ] **Step 5: Seed policy and historical ledger**

Record the seven draft and two final task IDs, model IDs, completion token counts, estimated costs, and decisions already present in the generation log. Mark the three duplicate/retry drafts as historical incident entries; do not rewrite them as compliant planned submissions.

- [ ] **Step 6: Pin Seedance 2.0 in historical final commands**

Change both final command templates and dry-run instructions to include:

```text
--model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio
```

Record that the explicit flag is required because `full` now resolves to Seedance 2.5.

- [ ] **Step 7: Run guard and model-pin verification**

Run both test files and two `pipeline/seedance.py generate ... --model 2.0 --dry-run` commands. Require `"model": "dreamina-seedance-2-0-260128"` and confirm no network task is created.

- [ ] **Step 8: Commit**

```bash
git add pipeline/promos/vr_game_things_puzzle/generation-policy.json \
  pipeline/promos/vr_game_things_puzzle/generation-ledger.json \
  pipeline/promos/vr_game_things_puzzle/guard.py \
  tests/test_vr_game_things_puzzle_guard.py \
  docs/superpowers/plans/2026-08-06-vr-game-things-puzzle-promo.md \
  pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md
git commit -m "Guard VR promo generation budget"
```

### Task 4: Rebuild, inspect, and commit the corrected delivery

**Files:**
- Create: `deliverables/vr-game-things-puzzle-promo/final/promo.mp4`
- Create: `deliverables/vr-game-things-puzzle-promo/final/contact-sheet.png`
- Create: `deliverables/vr-game-things-puzzle-promo/SHA256SUMS`
- Modify: `pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md`

**Interfaces:**
- Consumes: corrected manifest and accepted-media package from Tasks 1-3.
- Produces: final MP4 plus reproducible hashes and a truthful audit record.

- [ ] **Step 1: Validate and rebuild**

Run the builder with the tracked manifest and write directly to `deliverables/vr-game-things-puzzle-promo/final/promo.mp4`. Capture the exact redacted ffmpeg command in the generation log.

- [ ] **Step 2: Run automated output verification**

Run `verify.py` and require no errors for 1920x1080, H.264, yuv420p, 24 fps, 29.000 seconds, AAC stereo 48 kHz, and `moov` before `mdat`.

- [ ] **Step 3: Generate the review sheet and hashes**

Extract frames at `1, 4, 7, 10, 13, 16, 19, 22, 25, 28` seconds into a labeled contact sheet. Generate sorted SHA-256 lines relative to the deliverable root for the six inputs, final MP4, and contact sheet.

- [ ] **Step 4: Perform complete visual/audio QA**

Review the contact sheet and transition-adjacent frames for extra pieces, malformed hands, added geometry, AI text, black frames, or missing disclosure. Inspect the audio waveform/spectrogram and ffmpeg `astats` for continuity, clipping, and audible connection cues. Do not describe repository renders as gameplay.

- [ ] **Step 5: Correct the generation log**

Record the new manifest sequence, deterministic slate, audio-source status, mechanical ambience, exact artifact hashes, automated verification, visual limitations, and the reviewer-driven removal of `grab.mp4`/`snap.mp4`. Keep the USD 8.04 historical spend and all nine task IDs unchanged.

- [ ] **Step 6: Run repository verification**

```bash
python3 -m pytest -q
python3 -m py_compile pipeline/seedance.py pipeline/promos/vr_game_things_puzzle/*.py
python3 pipeline/promos/vr_game_things_puzzle/build.py --manifest pipeline/promos/vr_game_things_puzzle/manifest.json --validate-only
python3 pipeline/promos/vr_game_things_puzzle/verify.py deliverables/vr-game-things-puzzle-promo/final/promo.mp4
git diff --check
git status --short --branch
```

- [ ] **Step 7: Commit**

```bash
git add deliverables/vr-game-things-puzzle-promo \
  pipeline/prompts/vr-game-things-puzzle/GENERATION-LOG.md
git commit -m "Deliver repaired VR puzzle promo"
```

### Task 5: Review and open the pull request

**Files:**
- No new product files unless review finds a defect.

**Interfaces:**
- Consumes: `origin/main..feature/vr-game-things-puzzle-promo` after Tasks 1-4.
- Produces: a pushed feature branch and GitHub pull request against `main`.

- [ ] **Step 1: Rebase-free integration check**

Fetch `origin`, confirm `origin/main` is an ancestor of HEAD, and merge current `origin/main` if needed. Never force-push.

- [ ] **Step 2: Run the full verification suite again**

Require all tests, compilation, manifest validation, media verification, hash verification, and `git diff --check` to pass on the exact commit that will be pushed.

- [ ] **Step 3: Request final read-only code/media review**

Review `origin/main..HEAD` against the approved spec, with special attention to the original Critical and Important findings. Fix every Critical or Important issue before proceeding.

- [ ] **Step 4: Push and create the PR**

Push `feature/vr-game-things-puzzle-promo` with upstream tracking and create a non-draft PR against `main`. The PR body must distinguish repository renders, Seedance cinematic visualization, automated media verification, and any remaining physical/device validation gap.

- [ ] **Step 5: Report the PR and artifact links**

Return the GitHub PR URL plus clickable local links to the final MP4, contact sheet, manifest, generation log, and SHA-256 manifest.

## Plan Self-Review

- Spec coverage: corrected footage, model pin, manifest slate, source-audio path, paid-run guard, durable package, incident preservation, final rebuild, review, and PR are each assigned to a task.
- Isolation: every write is confined to the clean feature worktree; main-checkout MTL63 files and the Unity repository are excluded.
- Type consistency: `path`, `has_audio`, `source_assets`, slate path, policy keys, ledger request fields, and verifier return types are consistent across tasks.
- No paid side effects: every Seedance invocation in this plan uses `--dry-run`; rebuilding uses only existing local media.
- No placeholders: every runtime value comes from the existing generation log, current media, or deterministic verification commands.
