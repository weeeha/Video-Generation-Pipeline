# VR Game Things Puzzle Seedance Promo Design

**Date:** 2026-08-06
**PR repair revision:** 2026-09-07
**Status:** Approved
**Primary deliverable:** One 25-30 second, 16:9, 1080p promotional video
**Creative line:** Build it. Then operate it.

## Purpose

Create a concise hybrid promo for the working VR Game Things Puzzle Quest 3
prototype. The video should communicate the product fantasy of assembling a
recognizable machine and then operating it, while remaining honest about the
implemented three-piece AH-64 Apache vertical slice.

The intended uses are portfolio presentation, early product pitching, and
social sharing. The video must feel cinematic without presenting unimplemented
features as working gameplay.

## PR Repair Contract

The pre-PR review found that the first completed edit was technically valid but
not safe to publish. Two repository-render fallback shots exposed the source
project's 13-system exploded view, the post-merge CLI default changed from
Seedance 2.0 to 2.5, manifest copy did not drive the rendered slate, source
audio could not survive assembly, paid-run limits were procedural rather than
enforced, and the ignored delivery media could not be reproduced from a fresh
checkout.

The repair keeps the established creative direction and uses no new paid
generation. It makes these changes before a pull request is opened:

- replace the two 13-system fallback shots with the already accepted
  `d02b-connection` and `d03a-assembly` Seedance clips;
- retain only assembled-model repository renders where repository footage is
  used, and classify every generated shot as `seedance` in the manifest;
- pin historical final-generation instructions to `--model 2.0`; removing
  `--fast` alone is no longer sufficient because the repository default is
  Seedance 2.5;
- render the title, tagline, and disclosure from manifest values using a
  deterministic local slate generator rather than a pre-rendered `title.mp4`;
- declare source-audio availability per shot, preserve and crossfade declared
  source audio, substitute silence for shots without audio, and mix restrained
  original mechanical ambience below the source timeline;
- add a promo-specific paid-run guard that reserves stable task names before
  submission, rejects duplicate prompt/configuration hashes, and blocks draft,
  final, or projected-spend limits before it invokes the general Seedance CLI;
- place the accepted inputs, final export, contact sheet, and hashes in a
  tracked `deliverables/vr-game-things-puzzle-promo/` package so a fresh clone
  can validate the manifest without relying on an ignored worktree; and
- preserve the full incident record: seven drafts were actually submitted due
  to the documented retry race, even though the designed maximum was four.

The tracked delivery package contains only the media required to reproduce and
review the accepted edit. Rejected clips remain excluded; their task IDs,
decisions, and usage stay in the generation log.

### Repair architecture

`manifest.json` remains the single assembly contract. Each shot declares its
durable path, duration, provenance kind, and whether source audio exists. The
builder validates those declarations, generates a slate image from the three
manifest copy fields with pinned Pillow and its bundled default font, builds
matched video and audio timelines, mixes the mechanical bed, and emits the
final MP4. A separate verifier checks the export's duration, dimensions, frame
rate, codecs, pixel format, audio layout, fast-start placement, and SHA-256.

The paid-run guard is separate from the deterministic assembler. It reads a
small policy file and append-only ledger, performs all count, duplicate, and
projected-cost checks, writes a reservation atomically, then delegates a single
generation to `pipeline/seedance.py`. Existing completed task records seed the
ledger, so the historical overrun is visible rather than erased. The repair
does not call the guard or generation API because no new generation is needed.

### Repair verification

Tests must first demonstrate the current failures, then cover:

- rejection of repository shots that use the known 13-system exploded assets;
- manifest-driven slate pixels changing when title, tagline, or disclosure
  changes;
- preservation of declared source audio and silence substitution for silent
  shots;
- exact `--model 2.0` dry-run bodies for the historical final commands;
- refusal of a fifth draft, third final, duplicate prompt/configuration, or a
  task that could exceed the USD 12 cap;
- fresh-checkout manifest validation using only tracked deliverables; and
- automated media assertions for the rebuilt final, followed by a complete
  human visual and audio review of the actual 29-second export.

## Sources of Truth

- Unity project:
  `/Users/nickv/VR-Game-Things-Puzzle/VR Game Things Puzzle`
- Unity scene:
  `Assets/Game/Scenes/ApachePrototype.unity`
- Current product specification:
  `Documentation/Product/V1_PRODUCT_SPEC.md`
- Existing Apache references:
  `Documentation/Apache/apache-quest-studio.png`,
  `Documentation/Apache/apache-quest-exploded.png`, and
  `Documentation/Apache/apache-quest-assembled.png`
- Video workflow repository:
  `/Users/nickv/Documents/ChatGPT/Video Generation Pipeline`

The Unity worktree contains user-owned uncommitted changes. Promo production
must not modify, stage, discard, or commit those changes.

## Truth Boundary

The promo may show only these implemented product capabilities:

- selecting the installed Apache from the Library;
- entering the engineering workspace;
- using controller-driven virtual hands;
- grabbing and positioning a loose part;
- a three-piece authored assembly sequence consisting of cockpit, main rotor,
  and tail rotor;
- magnetic socket guidance and connection feedback;
- gray loose material revealing the finished material after connection;
- completion unlocking Play;
- rotors spinning and a restrained non-damaging weapon-effect demonstration.

The promo must not imply controller-free hand tracking, combat, enemies,
flight, a complete 13-piece playable assembly, multiplayer, painting, a
production store, or additional playable vehicles.

Seedance footage is cinematic visualization of these implemented interactions,
not evidence of additional functionality. If authentic Unity capture cannot be
obtained, the final deliverable must identify itself as concept footage.

## Creative Direction

The working concept is **From Pieces to Power**.

The promo takes place in a quiet, dark engineering studio. The environment uses
low-contrast cool blue-gray tones, while the model and active socket guidance
carry the strongest contrast. Cyan guidance light is restrained and functional.
Materials remain grounded and mechanical. There is no battlefield, enemy,
destruction, aggressive camera shake, or exaggerated science-fiction interface.

The rhythm moves from calm inspection to tactile connection and finally to
controlled mechanical operation. The Apache is presented as a model and
engineering object, not as a combat fantasy.

## Storyboard

| Time | Beat | Source |
| --- | --- | --- |
| 0-3s | Library card shows `AH-64 Apache` and `Start Assembly`. | Authentic Unity capture |
| 3-8s | A virtual hand grabs the gray cockpit and guides it toward a thin illuminated socket. | Unity anchor with optional Seedance polish |
| 8-13s | The part connects with magnetic alignment, pulse, mechanical sound, and gray-to-finished material reveal. | Authentic Unity capture |
| 13-18s | Main rotor and tail rotor complete a concise three-piece assembly montage. | Seedance cinematic visualization based on project references |
| 18-24s | Completion unlocks operation; the finished model receives a hero reveal, rotors accelerate, and the restrained weapon effect fires once. | Unity operation capture plus one Seedance hero shot |
| 24-30s | Finished Apache holds on the platform. Edited title: `VR Game Things Puzzle`. Closing line: `Build it. Then operate it.` | Conventional edit and typography |

All title text is created during editing. Seedance is not responsible for
rendering product copy.

## Production Workflow

### 1. Authentic capture

Capture the Library, first grab, connection event, material reveal, completion,
and Play/Stop operation from the existing Unity project. Prefer 1920x1080
capture at a stable frame rate. Do not change the Unity project merely to stage
promo footage unless separately authorized.

### 2. Seedance draft pass

Generate at most four five-second Seedance 2.0 Fast drafts at 720p:

1. cockpit approaching the socket;
2. cinematic magnetic connection;
3. three-piece assembly montage;
4. finished-model hero reveal.

Each draft uses the actual Apache renders as references. The prompts must bind
the cockpit, main rotor, and tail rotor as the only assembly pieces and preserve
the dark engineering-studio setting.

### 3. Draft evaluation

Reject a draft if it:

- changes the Apache into a different helicopter;
- creates extra rotors, weapons, limbs, hands, or assembly pieces;
- shows more than three playable parts;
- introduces a battlefield, enemies, explosions, flight, or destruction;
- makes the connection mechanically unreadable;
- generates text, logos, watermarks, or malformed interface elements;
- contradicts the calm engineering tone.

### 4. Final Seedance pass

Promote no more than two successful draft concepts to five-second, 1080p,
full-model Seedance 2.0 outputs. Use image references when sufficient. Use a
short video reference only when its motion is necessary and the increased cost
is justified.

### 5. Edit and sound

Assemble authentic Unity clips and accepted Seedance clips into one 25-30
second timeline. Use conventional edited typography. Build the soundtrack from
captured project sounds and restrained original mechanical ambience. Seedance
native audio is not the continuity source.

Final target:

- 1920x1080;
- 16:9;
- H.264 video;
- 24 or 30 frames per second, chosen to match the dominant authentic capture;
- AAC stereo audio at 48 kHz;
- no generative watermark;
- duration between 25 and 30 seconds.

## Spend Limit

The paid generation cap is **USD 12**.

- Four 720p Fast drafts are expected to cost approximately USD 2.40 total.
- Up to two 1080p finals are expected to keep the complete generation pass
  within approximately USD 6.50-11.50, depending on whether video references
  are used.
- Do not submit another paid generation if it could push the run above USD 12.
- Record task IDs, returned token usage, output specifications, and estimated
  cost for every successful generation.

Failed moderated generations are not assumed billable, but they still count as
workflow failures and must be recorded.

## Failure Handling

- If the Unity editor is connected to another project, stop before capture and
  resolve the exact project identity.
- If the Unity scene cannot be captured without changing user-owned work, use
  existing repository renders and label the result as concept footage.
- If all four Seedance drafts fail identity or truth-boundary review, stop and
  report the results rather than expanding the paid run.
- If a final Seedance output is worse than its draft, retain the draft only for
  internal review; do not upscale or present it as a 1080p final.
- If the total sequence is shorter than 25 seconds, extend authentic holds and
  transitions rather than inventing another feature.
- If sound capture is unavailable, use original non-licensed mechanical sound
  design and disclose that the audio is promotional, not recorded gameplay.

## Verification

Before delivery:

1. Watch the complete export with audio from start to finish.
2. Confirm the Apache identity and the exact three-piece sequence remain clear.
3. Confirm every depicted capability exists in the V1 product specification.
4. Confirm no shot implies combat, flight, native hand tracking, or additional
   playable models.
5. Confirm title spelling, safe margins, contrast, and legibility.
6. Inspect the export metadata for resolution, frame rate, codec, audio format,
   and duration.
7. Confirm there are no black frames, broken transitions, malformed hands,
   extra rotors, AI text, visible watermarks, or audio clipping.
8. Save the final prompt and generation parameters beside each accepted clip.
9. Provide the final promo, generation log, cost summary, and any rejected-take
   notes to the user.

## Deliverables

- One 25-30 second 1080p promotional video.
- Accepted Seedance source clips.
- Authentic Unity source captures used in the edit.
- A generation log containing prompts, task IDs, usage, costs, and decisions.
- A brief disclosure distinguishing authentic prototype footage from cinematic
  visualization.
