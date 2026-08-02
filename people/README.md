# People — the character library

One folder per character. Seedance 2.0's R2V mode keeps a character consistent across
completely different scenes when you attach their reference images and say *"the woman from
Image 1"* — this library is the asset side of that.

```
people/
  _template/          copy to start a new person
  <name>/
    card.md           who they are + the canonical prompt paragraph + voice + don'ts
    refs/             01-*.png, 02-*.png … numbered reference images (upload order!)
```

## How it's used

```bash
python3 pipeline/seedance.py generate --prompt-file scene.md --person <name> --name take-01
```

`--person <name>` attaches every image in `people/<name>/refs/` (sorted) as
`reference_image` items — so `refs/01-identity.png` is **Image 1** in your prompt,
`02-…` is **Image 2**, etc. The client prints the numbering map before sending.
Multiple `--person` flags work; numbering continues across them in flag order.

In the prompt, reference them explicitly and by purpose:

> *The woman from **Image 1** (same face and hair) wearing the outfit from **Image 2**
> sits in a rain-lit café window…*

## Rules for reference images

- **1–9 images per request.** 3–5 well-chosen refs beat 9 redundant ones: one clean
  identity shot, one full-body/costume, one alternate angle is a solid core.
- **No real human faces.** Uploads containing real people are rejected by the API. Use:
  - AI-generated characters (our default — generate a "casting sheet" with an image model
    or Seedance itself; strongly stylized faces are safest, photoreal AI faces can still
    trip the filter),
  - the console's [digital-character library](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision?modelId=seedance-2-0-260128&tab=GenVideo) (`asset://<ID>`),
  - **trusted prior outputs**: any face-containing video this account generated in the last
    30 days can be re-fed as `asset://<ID>` — so a character's best generated clip becomes
    their strongest reference. Save winning clips and note their asset use in the card.
- **Specs:** jpeg/png/webp, 300–6000px per side, aspect ratio between 0.4 and 2.5, ≤30MB.
  Local files are sent as base64 — keep refs a few MB each.

## The card

`card.md` holds the **canonical description** — the exact reusable paragraph for prompts —
plus voice notes for dialogue, wardrobe variants, and don'ts. Consistency comes from using
the same wording every time, not from re-describing the character from scratch per prompt.

Copy `_template/`, fill in the card, drop numbered refs, done.
