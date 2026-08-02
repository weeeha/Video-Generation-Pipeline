# T1.5 — Style lock

**Setup:** one style block ("hand-painted watercolor storybook: translucent washes,
paper grain, brush-textured edges, rose-and-slate + faded gold") across different
content: (a) harbor at dawn, no character; (b) alley walk with Nova's standard 3D pack;
(c) alley retake with a **repainted casting pack** (`people/nova-watercolor`, sheet
restyled via Nano Banana edit). Fast @720p, 5s, seed 42.

**Takes:**

| take | tokens | verdict | note |
|---|---|---|---|
| harbor | 108,900 | **KEEP** | true watercolor, style delivered from words alone |
| alley t1 (3D refs) | 108,900 | REJECT* | world went watercolor, **Nova stayed 3D** — refs pin render style; explicit "replace the 3D look" lost |
| alley t2 (watercolor refs) | 108,900 | **KEEP** | Nova painted AND recognizable; alley matches harbor style |

*take 1 is a keeper as evidence — and the 3D-character-in-painted-world mismatch is a
usable aesthetic if ever chosen deliberately.

**Verdict: PASS via the cast-per-film-style recipe.** Environments follow the prompt's
style block reliably (harbor ↔ alley read as one film). Characters follow their **refs'**
style, not the prompt's — so a film's look must be baked in at casting: repaint the
casting sheet once (free image edit), crop a style-variant pack, done. Identity carries
in the shared canonical description; look carries in the refs. One cast, N film looks.

**Feeds:**
- library convention: style variants as sibling packs (`people/nova-watercolor`).
- gotchas: refs pin style as strongly as identity.
- The three films can each have a distinct visual identity with a shared cast.
