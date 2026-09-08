# VR Game Things Puzzle promo generation log

## Environment preflight

| Check | Observed value |
| --- | --- |
| Execution date | 2026-08-06 |
| Pipeline worktree | `/Users/nickv/Documents/ChatGPT/Video Generation Pipeline/.worktrees/vr-game-things-puzzle-promo` |
| Unity source project | `/Users/nickv/VR-Game-Things-Puzzle/VR Game Things Puzzle` |
| Spend cap | USD 12 |
| Seedance draft limit | Four 5-second 720p Fast tasks |
| Seedance final limit | Two 5-second 1080p full-model tasks |
| API-key presence | Configured; value not printed |
| ffmpeg version | 8.1 |
| Unity capture status | Repository-render fallback. Open-source MCP reported zero instances; official MCP targeted `/Users/nickv/VR-Creative-Hub/VR-Creative-Hub`, so that unrelated project was left untouched. |

## Authentic capture

| Clip | Source type | Resolution | Duration | QA result |
| --- | --- | --- | --- | --- |
| `library.mp4` | Repository hero render with restrained push-in | 1920x1080 | 3.0s | Pass; concept footage |
| `operation.mp4` | Repository hero render with restrained push-in | 1920x1080 | 4.0s | Pass; concept footage |

The earlier `grab.mp4` and `snap.mp4` repository-render fallbacks used the
13-system exploded asset. PR review required their removal. They are not in the
corrected manifest, tracked delivery package, final edit, or artifact hashes;
the corrected sequence uses the already accepted `d02b-connection.mp4` and
`d03a-assembly.mp4` Seedance clips instead.

## Draft tasks

| Name | Prompt | Task ID | Model | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `vrgtp-d01-cockpit-approach` | `01-cockpit-approach.md` | `cgt-20260806145059-rj5cc` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Reject: malformed glove/cockpit interaction |
| `vrgtp-d02-magnetic-connection` | `02-magnetic-connection.md` | `cgt-20260806145151-7dsxq` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Pass; not promoted |
| `vrgtp-d03-three-piece-assembly` | `03-three-piece-assembly.md` | `cgt-20260806145221-c5vxs` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Selected assembly concept |
| `vrgtp-d04-hero-reveal` | `04-hero-reveal.md` | `cgt-20260806145308-2rx9p` | `dreamina-seedance-2-0-fast-260128` | Succeeded | 108,900 | USD 0.61 | Reject: geometry and weapon-pod drift |

### Draft submission incident

The first multi-command submission continued after its tool cell appeared to
finish. Retrying the apparently missing names created three additional Fast
tasks before the local state was reconciled. Running Seedance tasks could not
be cancelled. All seven promo tasks were identified by prompt, inspected, and
reconciled before final generation. A simultaneous MTL task was identified by
its 21:9 output and restaurant-robot content, excluded from this promo, and not
counted in this ledger.

| Variant | Prompt | Task ID | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | ---: | ---: | --- |
| `connection-a` | `02-magnetic-connection.md` | `cgt-20260806145130-tt5b2` | Succeeded | 108,900 | USD 0.61 | Pass; not promoted |
| `assembly-b` | `03-three-piece-assembly.md` | `cgt-20260806145228-mxfgq` | Succeeded | 108,900 | USD 0.61 | Pass; not promoted |
| `hero-a` | `04-hero-reveal.md` | `cgt-20260806145241-vxlch` | Succeeded | 108,900 | USD 0.61 | Selected hero concept |

## Draft QA matrix

Score each category from 0-2. A draft must score at least 8/12 and pass every automatic rejection rule.

| Draft | Apache identity | Three-piece truth | Mechanical readability | Studio tone | Temporal stability | Edit usefulness | Total | Automatic rejection | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `d01` | 2 | 2 | 1 | 2 | 1 | 1 | 9 | Malformed glove/cockpit interaction | Reject |
| `d02a` | 2 | 2 | 0 | 2 | 2 | 1 | 9 | Connection action is not readable | Reject |
| `d02b` | 2 | 2 | 1 | 2 | 2 | 2 | 11 | None | Pass; not promoted |
| `d03a` | 2 | 2 | 2 | 2 | 2 | 2 | 12 | None | Select for final assembly |
| `d03b` | 2 | 1 | 2 | 2 | 2 | 2 | 11 | None | Pass; not promoted |
| `d04a` | 2 | 2 | 2 | 2 | 1 | 2 | 11 | None | Select for final hero |
| `d04b` | 1 | 2 | 1 | 2 | 1 | 1 | 8 | Added weapon geometry and shape drift | Reject |

## Final tasks

| Name | Source concept | Task ID | Model | Status | Completion tokens | Estimated cost | Decision |
| --- | --- | --- | --- | --- | ---: | ---: | --- |
| `vrgtp-f01-assembly` | `d03a` | `cgt-20260806150045-tkh2g` | `dreamina-seedance-2-0-260128` | Succeeded | 245,025 | USD 1.89 | Accept: readable three-piece assembly with stable Apache identity |
| `vrgtp-f02-hero` | `d04a` | `cgt-20260806150110-zqxnc` | `dreamina-seedance-2-0-260128` | Succeeded | 245,025 | USD 1.89 | Accept: clean assembled-model reveal without battlefield action |

### Historical Seedance 2.0 command pin

The recorded final tasks used `dreamina-seedance-2-0-260128`. Any future
dry-run or replay must explicitly pass `--model 2.0 --resolution 1080p
--duration 5 --ratio 16:9 --no-audio`, because the current `full` alias now
resolves to Seedance 2.5. This is a forward-looking instruction correction;
it does not rewrite the seven-draft retry incident as a compliant planned run.

```bash
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/vr-game-things-puzzle/03-three-piece-assembly.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f01-assembly --dry-run
python3 pipeline/seedance.py generate --prompt-file pipeline/prompts/vr-game-things-puzzle/04-hero-reveal.md --pack vehicles/apache-v1-promo --model 2.0 --resolution 1080p --duration 5 --ratio 16:9 --no-audio --name vrgtp-f02-hero --dry-run
```

## Cost ledger

| Stage | Successful tasks | Estimated subtotal |
| --- | ---: | ---: |
| Drafts | 7 | USD 4.27 |
| Finals | 2 | USD 3.77 |
| Total | 9 | USD 8.04 |

The historical USD 8.04 summary is preserved. The displayed per-task values
are rounded to cents, so seven entries at USD 0.61 plus two at USD 1.89 add to
USD 8.05 when the displayed values are summed; this one-cent presentation
difference does not change the recorded nine-task historical total.

## Corrected delivery assembly (2026-09-08)

No Seedance or other paid generation was called during the repair. The tracked
manifest assembled these shots in order, with 0.25-second crossfades:

| Order | Manifest source | Kind | Edit duration | Source audio |
| ---: | --- | --- | ---: | --- |
| 1 | `source/library.mp4` | Repository render | 3.0s | Unavailable; declared `false` |
| 2 | `accepted/d02b-connection.mp4` | Seedance cinematic visualization | 5.0s | Unavailable; declared `false` |
| 3 | `accepted/d03a-assembly.mp4` | Seedance cinematic visualization | 5.0s | Unavailable; declared `false` |
| 4 | `accepted/final-assembly.mp4` | Seedance cinematic visualization | 5.0s | Unavailable; declared `false` |
| 5 | `accepted/final-hero.mp4` | Seedance cinematic visualization | 5.0s | Unavailable; declared `false` |
| 6 | `source/operation.mp4` | Repository render | 4.0s | Unavailable; declared `false` |
| 7 | Manifest-generated closing slate | Edited typography | 3.5s | Unavailable; declared `false` |

The title, tagline, and disclosure were rendered locally from the manifest by
the pinned Pillow slate generator. The source-audio timeline therefore consists
of explicit stereo silence. The builder mixed restrained original mechanical
ambience beneath it: seeded pink noise, a 55 Hz hum, and seeded filtered
connection impulses at 3.000 and 7.750 seconds. Fixed seeds `6401`, `6402`, and
`6403` make the generated audio and final MP4 byte-reproducible; two independent
builds produced the same SHA-256 and byte count.

Builder invocation:

```bash
python3 pipeline/promos/vr_game_things_puzzle/build.py --manifest pipeline/promos/vr_game_things_puzzle/manifest.json --output deliverables/vr-game-things-puzzle-promo/final/promo.mp4 --print-command
```

Exact ffmpeg command printed by the builder, with only the absolute worktree
prefix redacted to `<repo>`:

```bash
ffmpeg -y -i '<repo>/deliverables/vr-game-things-puzzle-promo/source/library.mp4' -i '<repo>/deliverables/vr-game-things-puzzle-promo/accepted/d02b-connection.mp4' -i '<repo>/deliverables/vr-game-things-puzzle-promo/accepted/d03a-assembly.mp4' -i '<repo>/deliverables/vr-game-things-puzzle-promo/accepted/final-assembly.mp4' -i '<repo>/deliverables/vr-game-things-puzzle-promo/accepted/final-hero.mp4' -i '<repo>/deliverables/vr-game-things-puzzle-promo/source/operation.mp4' -loop 1 -framerate 24 -t 3.500 -i deliverables/vr-game-things-puzzle-promo/final/promo.slate.png -f lavfi -t 29.000 -i anoisesrc=color=pink:amplitude=0.04:sample_rate=48000:seed=6401 -f lavfi -t 29.000 -i sine=frequency=55:sample_rate=48000 -f lavfi -t 0.16 -i anoisesrc=color=white:amplitude=0.35:sample_rate=48000:seed=6402 -f lavfi -t 0.16 -i anoisesrc=color=white:amplitude=0.35:sample_rate=48000:seed=6403 -filter_complex '[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=3.000,setpts=PTS-STARTPTS[v0];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=3.000,asetpts=PTS-STARTPTS[a0];[1:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=5.000,setpts=PTS-STARTPTS[v1];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=5.000,asetpts=PTS-STARTPTS[a1];[2:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=5.000,setpts=PTS-STARTPTS[v2];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=5.000,asetpts=PTS-STARTPTS[a2];[3:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=5.000,setpts=PTS-STARTPTS[v3];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=5.000,asetpts=PTS-STARTPTS[a3];[4:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=5.000,setpts=PTS-STARTPTS[v4];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=5.000,asetpts=PTS-STARTPTS[a4];[5:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=4.000,setpts=PTS-STARTPTS[v5];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=4.000,asetpts=PTS-STARTPTS[a5];[6:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=24,format=yuv420p,trim=duration=3.500,setpts=PTS-STARTPTS[v6];anullsrc=channel_layout=stereo:sample_rate=48000,atrim=duration=3.500,asetpts=PTS-STARTPTS[a6];[v0][v1]xfade=transition=fade:duration=0.250:offset=2.750[vx1];[vx1][v2]xfade=transition=fade:duration=0.250:offset=7.500[vx2];[vx2][v3]xfade=transition=fade:duration=0.250:offset=12.250[vx3];[vx3][v4]xfade=transition=fade:duration=0.250:offset=17.000[vx4];[vx4][v5]xfade=transition=fade:duration=0.250:offset=21.750[vx5];[vx5][v6]xfade=transition=fade:duration=0.250:offset=25.500[vx6];[a0][a1]acrossfade=d=0.250:c1=tri:c2=tri[ax1];[ax1][a2]acrossfade=d=0.250:c1=tri:c2=tri[ax2];[ax2][a3]acrossfade=d=0.250:c1=tri:c2=tri[ax3];[ax3][a4]acrossfade=d=0.250:c1=tri:c2=tri[ax4];[ax4][a5]acrossfade=d=0.250:c1=tri:c2=tri[ax5];[ax5][a6]acrossfade=d=0.250:c1=tri:c2=tri[ax6];[ax6]anull[source_audio];[7:a]highpass=f=35,lowpass=f=1800,volume=0.40[noise];[8:a]volume=0.12[hum];[9:a]highpass=f=700,lowpass=f=3600,adelay=3000|3000,volume=0.24[impulse1];[10:a]highpass=f=700,lowpass=f=3600,adelay=7750|7750,volume=0.20[impulse2];[noise][hum][impulse1][impulse2]amix=inputs=4:normalize=0[ambience];[source_audio][ambience]amix=inputs=2:normalize=0,alimiter=limit=0.7,atrim=duration=29.000,asetpts=PTS-STARTPTS[aout]' -map '[vx6]' -map '[aout]' -c:v libx264 -pix_fmt yuv420p -c:a aac -ar 48000 -ac 2 -movflags +faststart deliverables/vr-game-things-puzzle-promo/final/promo.mp4
```

## Export verification

| Check | Observed value | Result |
| --- | --- | --- |
| Duration 25-30 seconds | 29.000s | Pass |
| Resolution 1920x1080 | 1920x1080 | Pass |
| Frame rate 24 fps | 24/1 | Pass |
| H.264 and `yuv420p` | H.264, `yuv420p` | Pass |
| AAC stereo 48 kHz | AAC LC, 2 channels, 48,000 Hz | Pass |
| Fast start | `moov` offset 36; `mdat` offset 21,434 | Pass |
| Verifier CLI | Exact delivery contract; no errors | Pass |
| Bitwise rebuild | Two 4,703,054-byte builds; identical SHA-256 | Pass |
| Title, tagline, disclosure | Visible at 28s and throughout sampled closing slate | Pass by static frame inspection |
| Audio continuity | No `silencedetect` interval at -60 dB for 0.10s; two cue spikes visible | Pass by automated/static inspection |
| Audio level | `astats` peak -23.7792 dBFS; RMS -39.1778 dBFS; no NaN/Inf | Pass; no clipping indicated |

Visual QA used the labeled 1, 4, 7, 10, 13, 16, 19, 22, 25, and
28-second contact sheet, additional half-second samples across the full edit,
and before/during/after samples at every transition. No sampled frame showed AI
text, watermarks, malformed hands, added playable pieces, missing disclosure,
or an actually blank frame. The accepted Seedance shots contain cinematic
assembly motion and material/lighting variation; they are visualization, not
repository-render footage or recorded gameplay.

`blackdetect` classified 17.250-17.625 seconds as black. Frame-by-frame review
of all 19 frames from 17.000-17.750 seconds showed a continuous Apache
silhouette and illuminated platform rim; even the darkest frame had nonzero
content (maximum luma 129). This is an intentionally very dark transition, not
a blank frame. It also classified 25.750-28.958 seconds because the slate is
mostly near-black; title, tagline, and disclosure remain visibly present in
the sampled closing frames. These are documented threshold results, not a
claim based on literal real-time playback.

Audio QA used a waveform/spectrogram and `ffmpeg astats`. The bed is continuous
and the connection cues are visible at their designed positions. This task did
not include literal real-time human playback through speakers, so perceived
loudness, timbre, and mix quality remain a playback-review limitation.

Delivery: `deliverables/vr-game-things-puzzle-promo/final/promo.mp4`

SHA-256: `e0a5df4d591b7e586de1ab61874d18ae4c0adabdbedca327ff7d75f04d135d51`

The path-sorted `deliverables/vr-game-things-puzzle-promo/SHA256SUMS` records
the six tracked inputs, final MP4, and labeled contact sheet:

| Relative path | SHA-256 |
| --- | --- |
| `accepted/d02b-connection.mp4` | `fd8d86cc6409ad28e7334a80a093eb3271457e69c9a7de9b3f4813657659475d` |
| `accepted/d03a-assembly.mp4` | `b8a4ce4c86d23cce79ae672b820448c988ecf491abd6cddf488cb0d92ba649e9` |
| `accepted/final-assembly.mp4` | `27de739844d594dbff41da0ff4d7301dfa8fa76e166d2e8eceb586553bc3974e` |
| `accepted/final-hero.mp4` | `b6c78fe0e3eb003131e671c5e9b0c12ddb3e57771c89e2c86fbf2f6adf11ab33` |
| `final/contact-sheet.png` | `89984ac8258b579c7f418b723a471cbf60c7a26ac4bb450f862f3ae52d692bd8` |
| `final/promo.mp4` | `e0a5df4d591b7e586de1ab61874d18ae4c0adabdbedca327ff7d75f04d135d51` |
| `source/library.mp4` | `9e01411f4ad62b76aaf9fd1b5a9f77d3d2ecc3cae62cdce0d4dba1326ed03f1e` |
| `source/operation.mp4` | `366fa314e26dacc0cec7c470eb0c861ab617c51fbfb4e1e8c5649c07c20053c7` |

## Disclosure

Concept footage from repository renders with Seedance cinematic visualization.
Generated footage is used only to visualize interactions already implemented
in the three-piece Apache vertical slice. It is not evidence of flight, combat,
native hand tracking, additional playable pieces, or other playable models.
