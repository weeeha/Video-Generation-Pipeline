# Sweeper Squad

**One-line:** the containment troopers — anthropomorphic feline soldiers in sealed armour,
sent in to sterilise bio-weapon sites and, this time, sent back out without finishing.

## Canonical description

Anthropomorphic feline soldiers: lean athletic build, digitigrade legs ending in paw feet,
long tail with a curled tip. A full-face armoured cat helmet in smooth grey plate —
upright pointed ears, large black lens eyes, a short muzzle respirator with vent slots —
worn sealed at all times. Dark charcoal armoured bodysuit with a sculpted chest plate
carrying an engraved feather-like unit insignia, sleeved arms, harness webbing and belt
pouches, thigh and shin plating, articulated gauntlets with clawed fingertips. Matte
gunmetal palette with restrained orange-tan chevron marking on one shoulder. Standard arm
is a black bullpup combat shotgun with orange stencilling.

Bearing: professional and tired. They move like people leaving somewhere, not taking it.

## Reference images (file order = Image N ordinal)

| # | File | What it locks |
|---|------|---------------|
| 1 | `refs/01-identity.png` | helmet shape, ears, respirator, armour panelling, tail |
| 2 | `refs/02-fullbody-weapon.jpg` | full silhouette + shotgun carry position |
| 3 | `refs/03-incinerator.png` | the rear guard's flamethrower — canister, twin hoses, nozzle |

## Squad composition

Default fire team of three, identical armour pattern — helmets sealed, so individuality
comes from posture and role, not faces:

- **Point** — shotgun up, walking behind the warbeast.
- **Middle** — supporting a limping teammate, or carrying salvage.
- **Rear** — **the flamethrower operator.** Canister on her back, twin hoses to the nozzle,
  walking backwards, covering the way they came. This is a fixed role, not a variant: the
  incinerator belongs to the rear guard and to nobody else.

Blocking the rear guard is the hard part. Take 03 (2026-08-05) put all three abreast facing
camera because the scale plate's composition outvoted the prompt. When she matters, spend
several sentences on her: state that her back is to the group, that she never turns to face
the direction of travel, and that she is the closest figure to the lens.

## Don'ts

- **Helmets never come off.** No exposed faces, ever — it's the look *and* it keeps the
  scene clear of the real-face reference filter entirely.
- Never heroic: no hero poses, no charging, no shouting. This squad withdraws.
- No unit patches, numbers or readable text rendered on screen.
- Don't mix in human soldiers — the whole cast is feline.

## Trusted outputs (asset:// refs)

| Date | Task | Shows | Expires |
|------|------|-------|---------|
| 2026-08-05 | `cgt-20260805103757-ws69w` | **best take** — 5 refs, 3 troopers, correct beast scale + flank cannons (720p fast, seed 42) | ~2026-09-04 |
| 2026-08-05 | `cgt-20260805103006-qg2rx` | 4 refs, no scale plate — better retreat staging, beast oversized, cannons lost | ~2026-09-04 |
| 2026-08-05 | `cgt-20260805100503-s9ttt` | T2V baseline, no refs — **off-model**, see below | ~2026-09-04 |

⚠️ The baseline take was generated from words only, with no reference packs attached. The
corridor is on-model; the *characters are not* — legs came out plantigrade with boots
instead of digitigrade paws, armour pattern and weapon are generic, and the warbeast came
out white and roughly trooper-height instead of weathered gunmetal at twice trooper height.
**Don't re-feed this task as an `asset://` character reference** — it would propagate the
wrong design. It's kept here as the control that proves what the refs are for.
