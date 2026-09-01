# Knowledge

Everything we know about Seedance 2.5 / 2.0, consolidated. Read order for newcomers:
**prompt-guide.md → gotchas.md → api-reference.md** (the last one as lookup, not reading).

| File | What it is |
|------|------------|
| [api-reference.md](api-reference.md) | Full BytePlus ModelArk API contract — endpoints, every parameter, asset rules, official prompt templates (§6), code samples. Source of truth. |
| [prompt-guide.md](prompt-guide.md) | How to write prompts that work: the Subject+Scene+Audio formula, the four modes, reference syntax, audio direction, on-screen text. |
| [gotchas.md](gotchas.md) | Operational lessons (API quirks + what the PermitNav production run taught us). Read before burning credits. |

## Fast facts

- **Models:** `dreamina-seedance-2-5-260628` (2.5 — our default: 30s, 50 refs, 1080p 10-bit HEVC, ~+50% price) · `dreamina-seedance-2-0-260128` (2.0 — adds 4k) · `dreamina-seedance-2-0-fast-260128` / `dreamina-seedance-2-0-mini-260615` (720p max, cheaper)
- **Base URL:** `https://ark.ap-southeast.bytepluses.com/api/v3` (region ap-southeast-1, Bearer `ARK_API_KEY`)
- **Flow:** async — `POST /contents/generations/tasks` → poll `GET .../{id}` → download `content.video_url` **within 24h**
- **Key on Nick's Mac:** `~/Documents/Claude/Projects/SeedDance/.env` (not in shell profiles)
- **Consoles:** [API keys](https://console.byteplus.com/ark) · [balance](https://console.byteplus.com/finance) · [digital-character library](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision?modelId=seedance-2-0-260128&tab=GenVideo)
- **Input budget per request:** 2.5 → ≤30 images, ≤10 videos, ≤10 audio (≤30s combined ref video/audio), ≤50 files; 2.0 → ≤9 images, ≤3 videos (≤15s combined), ≤3 audio, ≤12 files. Body ≤64MB either way
- **Durations:** 2.5 → 4–30s (or `-1` auto); 2.0 → 4–15s · **Ratios:** 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive (2.5 forces adaptive on edit/extend/first-frame tasks)
- **2.5 task typing:** `omni_reference_task_type: auto|edit|extend` — declare it to fail fast; errors `InvalidParameter.TaskTypeMismatch` / `.TaskTypeConstraint` (api-reference §3.1.5)
