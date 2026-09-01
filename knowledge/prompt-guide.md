# Seedance — Prompt Guide (2.5 / 2.0)

Seedance reads prompts as **natural language**, not keyword salads. Write the way you'd
brief a director: who, what, where, how it sounds. (Official templates verbatim:
[api-reference.md §6](api-reference.md).)

## The basic formula

> **Subject** (who is doing what) + **Scene** (spatial background, lighting, visual style) + **Audio** (ambient, voiceover, dialogue, music)

One paragraph covering all three is a complete prompt:

> *A woman in a red trench coat walks briskly across a rain-slick neon-lit Tokyo crosswalk at night, low-key cyberpunk palette with magenta and cyan reflections, shallow depth of field, anamorphic lens flare. Ambient city sound with distant traffic; her heels click against wet pavement.*

Layer cinematography inside the **Scene** portion — shot type, camera move, lens, lighting,
palette. Vague mood words alone produce generic output; concrete film vocabulary doesn't.

## The four modes

| Mode | Input | Use for |
|------|-------|---------|
| **T2V** | text only | anything from scratch |
| **I2V** | text + first frame (± last frame) | animating a still; **chaining clips** (feed the previous clip's last frame — keeps person + location) |
| **R2V** | text + reference images/videos/audio | **consistent characters** (our `people/` system), products, motion/camera/VFX borrowing |
| **V2V** | text + video(s) | add/remove/modify elements, extend forward/back, stitch clips (2.0: ≤3 clips/15s · 2.5: ≤10 clips/30s) |

I2V first-frame and R2V reference images are **mutually exclusive** in one request.

## Referencing uploaded assets

Assets are referenced by **type + upload order**: `Image 1`, `Image 2`, `Video 1`, `Audio 1`.
Numbering counts only items of that type, in `content[]` order — so **upload in the order
you'll reference**. Seedance 2.5's official examples use an `@` prefix (`@Image1`,
`@Video 1`) — same ordinals, either style works, stay consistent within a prompt.

**2.5 intent keywords are load-bearing.** On 2.5, an edit task's prompt must contain an
editing phrase ("edit the video", "add", "delete/remove", "modify/replace/change") and an
extension task's prompt must contain an extension phrase ("extend forward/backward",
"continue", "continue the story") — the model classifies the task from these words, and a
mismatch with `omni_reference_task_type` fails the task (gotchas.md).

Two rules that make or break R2V:

1. **Name what each reference is for.** Not "use the references" but *"the woman from
   Image 1"*, *"the camera movement from Video 2"*, *"the composition of Image 3"*.
2. **Describe the borrowed thing in words too.** "Reference the slow dolly-in from Video 1 —
   the camera moves forward over 5 seconds" beats a bare pointer.

Template (subject consistency): `Use the [Subject] from [Image N] to generate
[Scene Description], maintaining consistent [Subject] features.`

## Native audio — always direct it

Audio is generated **jointly with the video in the same pass** (`generate_audio: true`,
our default). Describe it explicitly every time; even ambient-only direction lifts
production value:

- **Ambient:** *"quiet kitchen room tone, the faint hum of a refrigerator, soft birdsong outside"*
- **Dialogue/VO:** put the exact line in quotes — *"A warm female voice says: 'Renovating? Just ask.'"* Multi-language works (write lines in the target script, don't romanize).
- **Music:** genre + mood + dynamics — *"a single warm piano note rises softly underneath"*
- Silence is a choice too: end with *"No music."*

## On-screen text

Text rendering works but is the least reliable feature (see gotchas). If you must:
common words only, no special symbols, and specify content + timing + position + entrance +
color/font explicitly. For anything brand-critical, generate a clean plate and burn captions
in post — that's what the PermitNav pipeline did.

## Working method

1. Pick the mode (what inputs exist?).
2. Write the Subject + Scene + Audio paragraph.
3. Add concrete cinematography to the Scene.
4. Name every reference (`Image N` / `Video N`) and what it contributes.
5. Direct the audio.
6. `--dry-run` to inspect the request, then generate at 720p/`--fast` to iterate; 1080p full model for finals.
7. Same `--seed` + same inputs = deterministic — pin a seed once a take is close.

## Common pitfalls

| Symptom | Fix |
|---|---|
| References produce muddy/averaged result | Say what each Image N is *for* (face, costume, scene, lighting) |
| Text garbled/doubled | Common words, no symbols — or burn text in post |
| Camera ignores reference video | Describe the move in words alongside the reference |
| Clips don't chain smoothly | Start follow-up prompts "Continue from the opening frame —" and re-state palette/lighting |
| Generic output | Scene lacks concrete film vocabulary (shot, lens, light, palette) |
| VO out of sync with subtitles | Use the official subtitle template (api-reference §6.2.2) |
