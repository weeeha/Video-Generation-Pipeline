# MTL63 Silo No. 5 Pipeline Test Design

**Date:** 2026-10-20
**Status:** Approved
**Deliverable:** one ~14 s, 720p, 21:9 assembly of three five-second Seedance 2.0-fast shots, plus a results note
**Scene:** Silo No. 5 data centre (MTL63 board section 05, canon status candidate)

## Purpose

MTL63's production concept is "real Montreal photography → transformation → moving shots → edit". The August 2026 slates proved the video stage (character, robot and location consistency from reference images) but every shot started from a generated still. This test runs the whole chain on one scene for the first time, starting from a photograph Nick shot himself, so it answers the board's open question of whether a real plate survives transformation and a camera move while staying recognisably Montreal.

It is the "10-to-20-second end-to-end pipeline test" that `My-Films/films/mtl63/production.md` lists as planning artefact 5. It does not choose the production stack, resolve lore, or produce final-quality footage.

## Inputs

- `library/places/mtl63-silo5-datacenter/plates/01-real-dji-0498.png` — Nick's DJI_0498 drone photograph of the Lachine Canal basin, Silo No. 5, the quays, the river and downtown (clear summer dusk).
- `library/places/mtl63-silo5-datacenter/plates/02-transformed-city-establishing.png` — the generated twenty-five-years-later version of the same view (Mtl Generations board, section 05, candidate-02).
- `library/places/mtl63-silo5-datacenter/refs/01-control-room.png` — the generated abandoned control room (section 05, control-room v2).

The committed copies are Figma exports (1379×1034 and 621×466). The full-resolution originals live on the Mac and should replace them under the same filenames before the run; the slate README says so. The API accepts 300–6000 px per side, so the exports work for a dry run and a first pass.

## Shots

All shots: `dreamina-seedance-2-0-fast-260128`, 720p, 21:9, 5 s, native audio, seed 6301 — the settings of the 2026-08-06 slates, so the results are comparable.

1. **S01 bridge** — I2V first + last frame, real plate → transformed plate. One held camera, the scene ages in place. Proves location transformation on a real plate.
2. **S02 drone push** — I2V first frame = S01's `.last.png`. One slow push toward the silo roof. Proves camera control and spatial consistency over the transformed city.
3. **S03 control room** — R2V with the pack (Image 1 = control room). One ten-centimetre dolly toward the window. Proves interior, vegetation and decay, dormant machines.

S01 and S02 are I2V and therefore cannot carry pack references (the API treats I2V and R2V as exclusive scenarios); the pack's `plates/` folder holds the frames the client is given explicitly, and only `refs/` is attached by `--pack`.

## Pass criteria

Per shot, in `pipeline/prompts/mtl63/silo5/README.md`. The test as a whole passes when the geography (canal, silo footprint, quays, river line, towers) never moves in S01 and S02, and S03 holds the room with no people, faces or lit monitors.

## Assembly

`pipeline/post/assemble_silo5.sh`: ffmpeg `xfade` + `acrossfade`, 0.5 s dissolves, offsets from the measured clip durations, H.264 CRF 18 with the native audio kept. Output `output/silo5-assembly.mp4` (gitignored like all generated media; the results note records task ids and tokens).

## Cost and run

≈109k completion tokens per clip → ≈330k tokens, ≈USD 1.85 at list. Generation runs on the Mac, where `ARK_API_KEY` resolves from `~/Documents/Claude/Projects/SeedDance/.env`; this branch carries everything else. Dry-runs of all three requests pass on the Windows PC without a key.

## Verification

- `python3 pipeline/seedance.py generate ... --dry-run` for each shot prints a well-formed body (done on the PC).
- `bash -n pipeline/post/assemble_silo5.sh` passes; the script refuses to run on missing clips.
- After the run: the three mp4s and `.last.png` files exist in `output/`, `seedance.py report` shows three succeeded tasks, the assembly plays at ≈14 s, and `RESULTS-<date>.md` is filled in.

## Out of scope

Seedance 2.5, local video models, a separate sound stage (native ambient audio only), 3D reconstruction, the Rooftop Reveal and restaurant scenes, and any change to `seedance.py`.
