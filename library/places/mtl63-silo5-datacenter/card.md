# Mtl63 Silo No. 5 Data Centre

**One-line:** the Silo No. 5 grain-elevator complex on Montreal's Lachine Canal basin, converted into a data centre before the collapse and now a dead, overgrown cable network twenty-five years later. Canon status: **candidate** (board section 05).

## Canonical description

An aerial view across the Lachine Canal basin toward the St. Lawrence under a low overcast dusk: the long concrete bulk of Silo No. 5 and its riverside quays sit between the canal and the river, downtown Montreal's towers in their real positions on the left horizon. Twenty-five years after collapse the concrete is streaked and weathered, young trees and vines have taken the canal banks, rail yards and quay edges, shallow floodwater lies on the lower quays, and the silo's roof and flanks carry an accreted network of cable trays, cooling housings and improvised structures with a scattering of dim amber service lights. Cool blue-grey light, wet surfaces, restrained amber practicals, grounded photorealistic live-action scale.

Interior (control room): a curved operations console of dead dark monitors with a few amber indicator lights, two worn empty swivel chairs, open floor panels full of bundled black cable, moss and vines along the right wall and ceiling conduits, and a tall curved window onto a multi-storey overgrown server hall where warm sunlight comes through haze in soft shafts.

## Reference images (file order = Image N ordinal)

Only `refs/` is attached by `--pack` (R2V). The two `plates/` files are I2V first/last frames and are passed explicitly with `--first-frame` / `--last-frame`; the client never attaches them as references.

| # | File | What it locks |
|---|------|---------------|
| 1 | `refs/01-control-room.png` | control-room geometry, console, chairs, cable floor, window onto the server hall, light direction (sun through the window, camera-right haze) |

| Plate | File | Role |
|---|------|------|
| real | `plates/01-real-dji-0498.png` | the actual drone photograph (Nick, DJI_0498, Aug 2026): canal, Silo No. 5, quays, river, downtown. S01 first frame. |
| transformed | `plates/02-transformed-city-establishing.png` | the generated "25 years later" version of the same view (Mtl Generations board, section 05, candidate-02). S01 last frame. |

**Resolution note.** The copies committed here are Figma exports (plate 1 at 1379×1034, plate 2 and the ref at 621×466). The originals live on the Mac: `DJI_0498.JPG` (4032×3024) and the generated PNGs from the Mtl Generations run. Drop them in under the same filenames before generating finals; 621 px is inside the API's 300–6000 px window but is a weak anchor.

## Don'ts

- Never move the canal, the silo footprint, the quays, the river line or the downtown towers; the whole point of this location is that it stays recognisably Montreal.
- No tropical jungle, desert, neon cyberpunk, or uniformly destroyed ruin — selective overgrowth and decay over intact concrete.
- Keep the cool overcast exterior light and the warm hazy window light in the interior; no golden-hour glamour on the exterior.
- No people, vehicles, robots, animals, readable signs, logos, HUD or watermark unless a prompt asks for them.
- Machines and lights are dormant: a few dim amber service lights, nothing bright, pulsing or moving.
