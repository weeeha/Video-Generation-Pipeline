Post-Collapse Montreal: previs pass, scenes 1 to 22

TL;DR: prompts for one 5 s, 720p, 16:9 text-to-video clip per scene from
`My Films/montreal-film-scenes.md`, meant for Seedance 2.5 (`dreamina-seedance-2-5-260628`) to spend
the 2.5 resource pack before it expires on 2026-11-10 23:59 UTC+8. Previs, not finals. Run with
`scripts/run-montreal-previs.sh [files...]`; clips land in `output/mtl-scNN.mp4`.

## Status (2026-11-07)

- Rendered: sc01, sc02 (checked: 1280x720, 5 s, audio, frames match the prompt) and sc04 (could not
  be cancelled once running, so downloaded; not reviewed). 108,900 tokens each.
- sc03 was cancelled or deleted by the cancel call; the API does not say which, so it may have cost
  108,900 tokens with no output.
- sc05 to sc22 not rendered. Nick stopped the batch after scenes 1 and 2.
- **Known bug:** the runner starts up to 3 clips at once, and parallel `seedance.py` runs race on
  `state.json` (KeyError in the poller). The task still finishes on BytePlus; recover it with
  `seedance.py wait <task-id>`. Until that is fixed, pass one file at a time.

This README is notes only. The `sc*.md` files are sent verbatim, whole file, so they carry no
headings or comments.

## Sources

- Scenes and citations: `~/ClaudeCode Projects/My Films/montreal-film-scenes.md`.
- Canon wording, look, audio and spoiler rules: `~/ClaudeCode Projects/My Films/film-tokens.md`.
  Entity paragraphs for bot/restaurant, bot/spider, bot/construction, bot/mad, bot/centaur,
  prop/battery, prop/carafe, loc/rooftop, loc/home-workshop and loc/central-street are pasted
  close to verbatim.
- Scene 15 is a 5 s cut-down of `My Films/prompts/scene-15-restaurant-robot-v1.md` (the pour beat).

## Left out

- **Scene 21, Volcano.** Canon is the name only, and film-tokens.md says not to extrapolate it.
- The spoiler primitives (two moons, the food producer). No sky treatment hints at either.

## Proposed, not canon

Everything below is a previs gap-fill and needs Nick's call before it becomes canon.

- **The hero's look.** Pre-collapse: "a young man in his twenties in plain office clothes".
  Post-collapse: "a lone man in a worn dark field jacket with a backpack", kept from behind,
  over the shoulder or at the hands, because his identity is still open.
- **Dialogue not on record:** the manager's line in scene 2, the phone assistant in scene 3,
  "Hey! You okay?" in scene 18, and all of the spider's lines in scene 20. Canon lines used
  verbatim: "You're the young generation. Try to find a job." (sc01), "It's a miracle." (sc05).
  The French "Voulez-vous encore de l'eau?" (sc15) is the existing proposed wording.
- **Designs:** the manager, the office robot in sc01, the construction robot's hi-vis harness,
  the spider's police markings, the centaur's plates, the boat and science vessels.
- **Scene 13** keeps the shooting off-screen and out of focus; **scene 6** uses the A01 version
  (pool of blood), thinned by rain.
- Every post-collapse clip has no music, per audio/score-sparse (the hero alone stays dry).
