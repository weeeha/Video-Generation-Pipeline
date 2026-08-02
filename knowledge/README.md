# Knowledge

Everything we know about Seedance 2.0, consolidated. Read order for newcomers:
**prompt-guide.md → gotchas.md → api-reference.md** (the last one as lookup, not reading).

| File | What it is |
|------|------------|
| [api-reference.md](api-reference.md) | Full BytePlus ModelArk API contract — endpoints, every parameter, asset rules, official prompt templates (§6), code samples. Source of truth. |
| [prompt-guide.md](prompt-guide.md) | How to write prompts that work: the Subject+Scene+Audio formula, the four modes, reference syntax, audio direction, on-screen text. |
| [gotchas.md](gotchas.md) | Operational lessons (API quirks + what the PermitNav production run taught us). Read before burning credits. |

## Fast facts

- **Models:** `dreamina-seedance-2-0-260128` (480/720/1080p) · `dreamina-seedance-2-0-fast-260128` (no 1080p, cheaper)
- **Base URL:** `https://ark.ap-southeast.bytepluses.com/api/v3` (region ap-southeast-1, Bearer `ARK_API_KEY`)
- **Flow:** async — `POST /contents/generations/tasks` → poll `GET .../{id}` → download `content.video_url` **within 24h**
- **Key on Nick's Mac:** `~/Documents/Claude/Projects/SeedDance/.env` (not in shell profiles)
- **Consoles:** [API keys](https://console.byteplus.com/ark) · [balance](https://console.byteplus.com/finance) · [digital-character library](https://console.byteplus.com/ark/region:ark+ap-southeast-1/experience/vision?modelId=seedance-2-0-260128&tab=GenVideo)
- **Input budget per request:** ≤9 images, ≤3 videos (≤15s combined), ≤3 audio, ≤12 files, body ≤64MB
- **Durations:** 4–15s (or `auto`) · **Ratios:** 16:9, 4:3, 1:1, 3:4, 9:16, 21:9, adaptive
