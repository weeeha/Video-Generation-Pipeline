# T1.3 — Character survives a world change

**Setup:** Nova pack only (3 refs, no place pack), two hostile-palette scenarios with
wardrobe changes: night suburban street after rain (charcoal coat, cool blue + lamp
accents) and cold minimalist cafe (denim jacket, grey overcast light). Fast @720p, 5s,
seed 42, both concurrent (lock fix verified in production).

**Takes:**

| take | task id | tokens | verdict | note |
|---|---|---|---|---|
| night street | cgt-20260803065703-sclq4 | 108,900 | **KEEP** | identity + directed wardrobe exact; palette flipped as asked |
| cool cafe | cgt-20260803065703-6sbdz | 108,900 | **KEEP** | identity holds in cold light; unprompted Apple logo on the laptop |

**Verdict: PASS, both take 1.** Three casting refs are enough to carry the character
into any palette, wardrobe, or location — the "films have more than one location"
requirement is satisfied. The card's warm-palette "don'ts" are a style choice, not a
technical limit.

**Watch-out found:** unprompted real-world branding (Apple logo). For film work add
"no visible brand logos" to prompts with laptops/phones/cars, or paint out in post.

**Feeds:** gotchas (brand slip-ins); both clips logged as trusted outputs on Nova's card
(night look + cafe look now reusable as asset:// refs for 30 days).
