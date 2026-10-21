# Mtl63 Silo No. 5 — end-to-end pipeline test slate

The first MTL63 test that runs the board's source-to-screen chain on one scene: a real Montreal photograph → its transformed still → moving shots → a cut. Scene: the Silo No. 5 data centre (board section 05, canon status candidate). Pack: `library/places/mtl63-silo5-datacenter/`.

All three shots use the 2.0 fast model at 720p, 21:9, five seconds, 24 fps, native ambient audio and seed `6301`, so results sit beside the 2026-08-06 slates. Spec: `docs/superpowers/specs/2026-10-20-mtl63-silo5-pipeline-test-design.md`.

| Shot | Mode | Inputs | Proves | Pass criteria |
|---|---|---|---|---|
| S01 bridge | I2V, first + last frame | real DJI_0498 → transformed candidate-02 | location transformation on a real plate | geography never moves; the ageing reads as time passing, not a dissolve; ends on the transformed still |
| S02 drone push | I2V, first frame = `output/silo5-s01.last.png` | S01 last frame | camera control + spatial consistency over the transformed city | one clean push, no orbit or reset; silo, canal, quays and towers hold their positions; detail resolves without inventing new buildings |
| S03 control room | R2V, `--pack places/mtl63-silo5-datacenter` | `refs/01-control-room.png` | interior, vegetation and decay, dormant machines | room and console geometry held; monitors stay dark; one dolly, no people or faces |

Budget: three clips at ≈109k completion tokens each ≈ 330k tokens, ≈ USD 1.85 at the 2.0-fast list rate in `pipeline/pricing.json`. `--dry-run` first; nothing is spent until the task is created.

## Run (on the Mac, where `ARK_API_KEY` resolves)

```bash
cd ~/path/to/Video-Generation-Pipeline && git pull && git switch mtl63/silo5-pipeline-test
P=pipeline/prompts/mtl63/silo5
K=library/places/mtl63-silo5-datacenter

# optional: drop the full-resolution originals in under the same names first
#   DJI_0498.JPG            -> $K/plates/01-real-dji-0498.png   (JPG is fine; keep the name or edit the command)
#   candidate-02 PNG        -> $K/plates/02-transformed-city-establishing.png
#   control-room v2 PNG     -> $K/refs/01-control-room.png

python3 pipeline/seedance.py generate --prompt-file $P/s01-bridge-real-to-transformed.md \
  --first-frame $K/plates/01-real-dji-0498.png --last-frame $K/plates/02-transformed-city-establishing.png \
  --fast --ratio 21:9 --duration 5 --seed 6301 --name silo5-s01

python3 pipeline/seedance.py generate --prompt-file $P/s02-drone-push.md \
  --first-frame output/silo5-s01.last.png \
  --fast --ratio 21:9 --duration 5 --seed 6301 --name silo5-s02

python3 pipeline/seedance.py generate --prompt-file $P/s03-control-room-dolly.md \
  --pack places/mtl63-silo5-datacenter \
  --fast --ratio 21:9 --duration 5 --seed 6301 --name silo5-s03

bash pipeline/post/assemble_silo5.sh          # -> output/silo5-assembly.mp4
python3 pipeline/seedance.py report           # spend
```

Run S01 and review `output/silo5-s01.mp4` before S02: S02 chains from S01's last frame, so a failed S01 wastes S02. S03 is independent and can run at any time.

If 21:9 crops the silo off the plates (they are 4:3), rerun with `--ratio adaptive`; note it in the results.

## Results

Copy to `RESULTS-<date>.md` and fill in, same shape as `../tests/RESULTS-2026-08-06.md`:

```markdown
# Mtl63 Silo No. 5 pipeline test — results

Model: `dreamina-seedance-2-0-fast-260128`
Format: 720p, 21:9, five seconds, 24 fps, native audio, seed `6301`
Plates: Figma exports | full-resolution originals (delete one)

| Shot | Task | Tokens | Verdict | Production note |
|---|---|---:|---|---|
| S01 bridge | `cgt-...` | | Pass / Conditional / Fail | |
| S02 drone push | `cgt-...` | | | |
| S03 control room | `cgt-...` | | | |

## Spend

- Total: `...` tokens, ≈ USD ... (from `seedance.py report`).

## Production conclusions

- Does the real → transformed bridge read as time passing on a real plate?
- Does spatial consistency survive a camera move over the transformed city?
- Which of the board's capability tests (location transformation, spatial consistency, vegetation and decay, lighting, atmosphere, edit continuity) does this scene now cover, and which remain open?
```
