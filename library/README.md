# Reference library

Reusable elements for Reference-to-Video (R2V), one **pack** per element. A pack is a
folder holding reference assets plus a `card.md` that says who/what it is and the exact
canonical wording to use in prompts. Consistency across videos comes from reusing the same
refs *and* the same wording every time.

```
library/
  people/<name>/      characters
  places/<name>/      locations & environments
  motion/<name>/      camera moves, subject motion, VFX (clips live as URLs — see below)
  <category>/_template/   copy to start a new pack
```

New categories are free: `mkdir library/products/_template` and `--pack products/<name>`
works immediately — the client doesn't hardcode category names.

## Pack anatomy

```
<name>/
  card.md      identity + canonical description + don'ts (humans read this)
  refs/        local files, attached in sorted order:
               images (jpeg/png/webp/bmp/tiff/gif) -> reference_image
               audio  (mp3/wav, 2-15s)             -> reference_audio
               (local VIDEO files are rejected — the API only takes hosted URLs
                or asset:// for video; list those in urls.txt)
  urls.txt     optional; one entry per line:  <image|video|audio> <url-or-asset://>
               '#' comments allowed. Attached after refs/ files, in file order.
```

Image specs: 300–6000px per side, aspect ratio 0.4–2.5, ≤30MB (keep refs a few MB — local
files travel as base64). Videos: ≤3 per request, ≤15s combined, 2–15s each.

## Using packs

```bash
# one pack
python3 pipeline/seedance.py generate --prompt-file scene.md --pack people/nova --name take-01

# compose: character + location + a motion clip
python3 pipeline/seedance.py generate --prompt-file scene.md \
    --pack people/nova --pack places/loft --pack motion/dolly-in --name take-02
```

Bare names work when unambiguous (`--pack nova` searches `library/*/nova`).

**Numbering:** ordinals count per asset type across the whole request, in `--pack` flag
order (each pack: `refs/` sorted first, then `urls.txt`). The client prints the map before
sending — e.g. nova's two refs are `Image 1`–`Image 2`, the loft wide shot becomes
`Image 3`, the dolly clip `Video 1`. Reference them by purpose in the prompt:

> *The woman from **Image 1** (same face and hair) stands in the loft from **Image 3**;
> reference the slow dolly-in from **Video 1** — the camera moves forward over 5 seconds.*

**One request = one scenario:** packs/references (R2V) can't be combined with
`--first-frame`/`--last-frame` (I2V chaining) — the API treats them as mutually exclusive
modes and the client blocks the combo.

## Category notes

**people/** — the real-face rule shapes everything: the API rejects uploads containing real
human faces. Cast characters as AI-generated (strongly stylized is safest; photoreal AI
faces can still trip the filter), use the console's
[digital-character library](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision?modelId=seedance-2-0-260128&tab=GenVideo)
(`asset://` IDs), or — the practical loophole — re-feed **your own generated clips** from
the last 30 days as `asset://` entries in `urls.txt`. Track those in the card's
"Trusted outputs" table (they expire!). A solid core: one clean identity shot, one
full-body/costume, one alternate angle. 3–5 good refs beat 9 redundant ones.

**places/** — a wide establishing shot locks layout + light direction; a detail shot locks
materials and dressing. Re-state the palette in the prompt anyway — refs anchor, words steer.

**motion/** — cards describe the move in words (the canonical phrase matters more here than
anywhere: "reference the slow dolly-in from Video 1 — camera moves forward over 5 seconds"),
and `urls.txt` holds the clips. Sources: clips we generated (as `asset://`, 30-day life) or
any hosted mp4/mov. Combined budget across a request: 3 clips, 15 seconds.
