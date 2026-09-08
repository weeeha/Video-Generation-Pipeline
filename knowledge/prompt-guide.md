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

### Scope every reference (2.5)

Each reference gets **one job**, and the prompt says what it must **not** contribute.
Unlabelled uploads get misassigned (the model will not guess that Image 3 is the location
and Image 4 is the jacket), and two references competing for the same detail average into
a hybrid.

> *@Image 1 defines her face, hair and coat only. Do not copy its background, lighting,
> pose or camera angle. @Image 2 defines the loft: brick wall, tall windows, morning light.
> Do not use the people in it. @Video 1 defines the camera move only.*

**Fewer references beat more.** Two matched images cut visible identity drift by roughly
60% versus six-plus in one creator test. Keep the refs you use at a similar angle and
under similar lighting; a frontal plus a profile makes the model reconcile them and invent
features. Images carry appearance; videos carry motion, camera and timing.

### The anchor block (consistent characters across clips)

Split the prompt into an **immutable anchor** you paste unchanged into every shot, and a
**variable scene block** that changes per shot. The anchor is one sentence: hair, skin,
eyes, distinctive marks, key accessories, wardrobe, one personality trait, then "Keep these
features unchanged." Negative anchors help: *"No glasses, no tied-up hair."* Our
`library/people/*/card.md` canonical description is that anchor; copy it verbatim.

When the subject passes behind something or leaves frame, **restate the anchor on
re-entry** ("the same woman, same face, same cream sweater, emerges from behind the
column"), or the model may swap identity mid-shot.

## Long takes: give the clip a timeline (2.5)

The 30-second setting adds **time, not events**. A single-idea prompt spends the first
beat well, then drifts or rushes to the end. Write the take as connected beats with
timestamps, and always describe the destination (final framing, final expression):

```
0-6s:   She notices the unopened letter beside her coffee and hesitates.
6-16s:  She picks it up and opens it; the camera pushes in slowly to a medium close-up.
16-26s: She reads. Her face moves from concern to relief.
26-30s: She sets the letter down and looks out the window. Hold on her face.
```

Rules that came up in every 2.5 guide:

- **Cause before reaction.** Name the contact, the force, and where the motion settles:
  *"the cup tips only after her sleeve catches it, hits the counter, coffee spreads and
  stops at the edge"*. Vague verbs produce floaty physics.
- **One camera move per shot.** Shot size + one movement + one focal target. Stacked
  moves read as chaos.
- **Let beats breathe.** 2.5 favours slower, less crowded beats. Rapid-cut prompt styles
  that worked on 2.0 come out glitchy on 2.5.
- **Hard locks beat soft hints.** *"No music. No dialogue. Exactly two people."*
- **Dialogue as performance.** Write lines a person can say with pauses, and block what
  they do around the line ("she stops speaking, looks down, turns the lid").
- **Fix only the broken beat.** If 24 of 30 seconds work, edit that timeline block and
  keep the seed; do not rewrite the whole prompt.

A full sectioned example (format, reference roles, starting state, timeline, camera,
continuity, audio, constraints) is in `pipeline/prompts/example-r2v-25.md`.

## Native audio — always direct it

Audio is generated **jointly with the video in the same pass** (`generate_audio: true`,
our default). Describe it explicitly every time; even ambient-only direction lifts
production value:

- **Ambient:** *"quiet kitchen room tone, the faint hum of a refrigerator, soft birdsong outside"*
- **Dialogue/VO:** put the exact line in quotes — *"A warm female voice says: 'Renovating? Just ask.'"* Multi-language works (write lines in the target script, don't romanize).
- **Voice casting is inferred from the reference images** and is word-sensitive. Name the
  accent plainly ("American", "Irish"); one tester found "American English" pushed
  delivery British because of the word "English".
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
6. For anything over ~10s, write the timeline blocks and the ending.
7. `--dry-run` to inspect the request, then iterate at 480p on `--fast`, move to 720p once
   the prompt works, and render finals on 2.5 (1080p if the delivery can play HEVC).
8. Same `--seed` + same inputs = deterministic; pin a seed once a take is close.
9. **Do not reuse 2.0 prompts on 2.5 unchanged.** Testers report visibly broken output;
   re-prompt with the timeline and scoped references above.

## Common pitfalls

| Symptom | Fix |
|---|---|
| References produce muddy/averaged result | Say what each Image N is *for* (face, costume, scene, lighting) |
| Text garbled/doubled | Common words, no symbols — or burn text in post |
| Camera ignores reference video | Describe the move in words alongside the reference |
| Clips don't chain smoothly | Start follow-up prompts "Continue from the opening frame —" and re-state palette/lighting |
| Generic output | Scene lacks concrete film vocabulary (shot, lens, light, palette) |
| VO out of sync with subtitles | Use the official subtitle template (api-reference §6.2.2) |
| Identity drifts mid-clip or across clips | Fewer, angle-matched refs; paste the anchor block unchanged; restate it after occlusion |
| Two refs blend into a hybrid person | Give each ref one job and list what it must not copy |
| Long take drifts or rushes at the end | Timeline blocks with timestamps; describe the final frame |
| Floaty or reversed physics | Write cause, contact, and where motion settles |
| Wrong accent or voice | Name the accent in one plain word; check the ref images imply the voice you want |
| Fast action morphs | Known 2.5 limit; slow the action, or cut around it in post |
| Props at wrong scale, body proportions shift | Known 2.5 limit; QA silhouette, height, wardrobe and scale, not just the face |

## Sources (community craft, Sept 2026)

Official templates: [api-reference.md §6](api-reference.md). Community guides these
sections draw on: [fal 2.5 prompting guide](https://fal.ai/learn/devs/seedance-2-5-prompting-guide),
[RunDiffusion 2.5 guide](https://www.rundiffusion.com/seedance-2-5-prompt-guide),
[Picsart 30-second takes](https://picsart.com/blog/seedance-2-5-prompting-guide/),
[CrePal character consistency](https://crepal.ai/blog/aivideo/blog-seedance-2-0-character-consistency/),
[MindStudio 2.5 review](https://www.mindstudio.ai/blog/seedance-2-5-review-guide),
[Higgsfield 2.5 guide](https://higgsfield.ai/blog/seedance-2-5-prompting-guide).
Platform-specific limits in those posts (720p cap, one reference video) do not apply to
the ModelArk API; trust api-reference.md for limits.
