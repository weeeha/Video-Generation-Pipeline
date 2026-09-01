#!/usr/bin/env python3
"""Seedance 2.5 / 2.0 CLI — BytePlus ModelArk client.

Generalized from the proven PermitNav pipeline (permit-nav-team/video-generation).
API contract: knowledge/api-reference.md · operational lessons: knowledge/gotchas.md

Key resolution: $ARK_API_KEY -> <repo>/.env -> ~/Documents/Claude/Projects/SeedDance/.env

Commands:
  generate   create a task (default: poll until done, download to output/)
  status     check once; downloads artifacts if succeeded
  wait       poll until terminal; downloads on success
  list       recent tasks (the API keeps 7 days)
  cancel     cancel a queued task / delete a finished record

Worked examples live in the repo README. Outputs land in output/<name>.mp4 plus
output/<name>.last.png (the chaining frame) unless --no-last-frame.
"""
import argparse, base64, json, os, pathlib, sys, time

try:
    import requests
except ImportError:
    sys.exit("needs the 'requests' package: python3 -m pip install requests")

REPO = pathlib.Path(__file__).resolve().parent.parent
OUTPUT_DIR = REPO / "output"
LIBRARY_DIR = REPO / "library"
STATE_FILE = pathlib.Path(__file__).resolve().parent / "state.json"
API = "https://ark.ap-southeast.bytepluses.com/api/v3"
MODELS = {
    "full": "dreamina-seedance-2-5-260628",       # Seedance 2.5 (the default)
    "2.0":  "dreamina-seedance-2-0-260128",       # Seedance 2.0 (adds 4k)
    "fast": "dreamina-seedance-2-0-fast-260128",  # 2.0 fast — cheaper, 720p max
    "mini": "dreamina-seedance-2-0-mini-260615",  # 2.0 mini — cheapest, 720p max
}
# per-model input/output envelopes (knowledge/api-reference.md §1, §4.2)
LIMITS = {
    "full": {"images": 30, "videos": 10, "audios": 10, "files": 50, "ref_secs": 30,
             "dur": (4, 30), "res": {"480p", "720p", "1080p"}, "audio_alone": True},
    "2.0":  {"images": 9, "videos": 3, "audios": 3, "files": 12, "ref_secs": 15,
             "dur": (4, 15), "res": {"480p", "720p", "1080p", "4k"}, "audio_alone": False},
    "fast": {"images": 9, "videos": 3, "audios": 3, "files": 12, "ref_secs": 15,
             "dur": (4, 15), "res": {"480p", "720p"}, "audio_alone": False},
    "mini": {"images": 9, "videos": 3, "audios": 3, "files": 12, "ref_secs": 15,
             "dur": (4, 15), "res": {"480p", "720p"}, "audio_alone": False},
}
TERMINAL = {"succeeded", "failed", "cancelled", "expired"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}
AUDIO_EXTS = {".mp3", ".wav"}
VIDEO_EXTS = {".mp4", ".mov"}
FORMATS = {"image": {"jpeg", "png", "webp", "bmp", "tiff", "gif"}, "audio": {"mp3", "wav"}}
SIZE_CAP_MB = {"image": 30, "audio": 15}


def die(msg):
    sys.exit(f"error: {msg}")


def load_key():
    if os.environ.get("ARK_API_KEY"):
        return os.environ["ARK_API_KEY"].strip()
    for envf in (REPO / ".env", pathlib.Path.home() / "Documents/Claude/Projects/SeedDance/.env"):
        if envf.exists():
            for line in envf.read_text().splitlines():
                line = line.strip()
                if line.startswith("ARK_API_KEY") and "=" in line:
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if val:
                        return val
    die("ARK_API_KEY not found in env, ./.env, or ~/Documents/Claude/Projects/SeedDance/.env")


def headers():
    return {"Content-Type": "application/json", "Authorization": f"Bearer {load_key()}"}


# ---- API ---------------------------------------------------------------------

def api_create(body):
    r = requests.post(f"{API}/contents/generations/tasks", json=body, headers=headers(), timeout=60)
    if r.status_code >= 400:
        die(f"create failed HTTP {r.status_code}: {r.text[:500]}")
    return r.json()["id"]


def api_retrieve(tid):
    r = requests.get(f"{API}/contents/generations/tasks/{tid}", headers=headers(), timeout=60)
    if r.status_code >= 400:
        die(f"retrieve failed HTTP {r.status_code}: {r.text[:500]}")
    return r.json()


def download(url, path):
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(path, "wb") as f:
            for chunk in r.iter_content(1 << 16):
                f.write(chunk)


# ---- assets ------------------------------------------------------------------

def to_asset_url(ref, kind):
    """Pass URLs/asset IDs through; encode local image/audio files as data URIs."""
    if ref.startswith(("http://", "https://", "asset://", "data:")):
        return ref
    p = pathlib.Path(ref).expanduser()
    if not p.exists():
        die(f"file not found: {ref}")
    if kind == "video":
        die(f"videos must be public URLs or asset:// IDs — base64 is unsupported: {ref}")
    fmt = {"jpg": "jpeg"}.get(p.suffix.lower().lstrip("."), p.suffix.lower().lstrip("."))
    if fmt not in FORMATS[kind]:
        die(f"unsupported {kind} format .{fmt}: {ref}")
    mb = p.stat().st_size / 1e6
    if mb > SIZE_CAP_MB[kind]:
        die(f"{ref} is {mb:.0f}MB — over the {SIZE_CAP_MB[kind]}MB per-{kind} cap")
    return f"data:{kind}/{fmt};base64,{base64.b64encode(p.read_bytes()).decode()}"


def resolve_pack(arg):
    """Accept 'people/nova', 'library/people/nova', or a bare name searched across library/*/."""
    cands = {}
    for p in (LIBRARY_DIR / arg, REPO / arg):
        if p.is_dir():
            cands[p.resolve()] = p
    if not cands and "/" not in arg:
        for p in sorted(LIBRARY_DIR.glob(f"*/{arg}")):
            if p.is_dir():
                cands[p.resolve()] = p
    packs = list(cands.values())
    if not packs:
        die(f"no pack '{arg}' under library/ (expected e.g. --pack people/nova; see library/README.md)")
    if len(packs) > 1:
        die(f"'{arg}' is ambiguous: " + ", ".join(str(p.relative_to(REPO)) for p in packs))
    if packs[0].name == "_template":
        die(f"{packs[0].relative_to(REPO)} is a template — copy it to a named pack first")
    return packs[0]


def pack_items(pack):
    """A pack's references in attach order: refs/ files (sorted; images + audio — local
    video is impossible, the API wants URLs), then urls.txt lines of
    '<image|video|audio> <url-or-asset://>'."""
    items = []
    refs = pack / "refs"
    if refs.is_dir():
        for p in sorted(refs.iterdir()):
            ext = p.suffix.lower()
            if ext in IMAGE_EXTS:
                items.append(("image", str(p)))
            elif ext in AUDIO_EXTS:
                items.append(("audio", str(p)))
            elif ext in VIDEO_EXTS:
                die(f"{p.name} in {pack.relative_to(REPO)}/refs: local video can't be sent "
                    f"(API takes hosted URLs or asset:// only) — list it in urls.txt instead")
    urls = pack / "urls.txt"
    if urls.exists():
        for i, raw in enumerate(urls.read_text().splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) != 2 or parts[0] not in ("image", "video", "audio"):
                die(f"{urls.relative_to(REPO)} line {i}: expected '<image|video|audio> <url-or-asset://>'")
            items.append((parts[0], parts[1].strip()))
    if not items:
        die(f"pack {pack.relative_to(REPO)} is empty — add refs/ files or urls.txt entries")
    return items


def pretty(ref):
    if ref.startswith(("http://", "https://", "asset://", "data:")):
        return ref
    try:
        return str(pathlib.Path(ref).resolve().relative_to(REPO))
    except (ValueError, OSError):
        return ref


def model_key(args):
    """Resolve --model/--fast to a MODELS key (default: 2.5 'full')."""
    if args.fast:
        if args.model not in (None, "fast"):
            die(f"--fast conflicts with --model {args.model}")
        return "fast"
    return args.model or "full"


def build_content(args, prompt):
    """Assemble the content[] array; returns (content, human-readable numbering map)."""
    content = [{"type": "text", "text": prompt}]
    labels = []

    ref_images, ref_videos, ref_audios = [], [], []
    buckets = {"image": ref_images, "video": ref_videos, "audio": ref_audios}
    for arg in args.pack or []:
        for kind, ref in pack_items(resolve_pack(arg)):
            buckets[kind].append(ref)
    ref_images += list(args.image or [])
    ref_videos += list(args.video or [])
    ref_audios += list(args.audio or [])

    if (args.first_frame or args.last_frame) and (ref_images or ref_videos or ref_audios):
        die("first/last-frame (I2V) and references (R2V) are mutually exclusive API scenarios")
    if args.last_frame and not args.first_frame:
        die("--last-frame requires --first-frame")
    lim = LIMITS[model_key(args)]
    if len(ref_images) > lim["images"]:
        die(f"{len(ref_images)} reference images — the {model_key(args)} cap is {lim['images']}")
    if len(ref_videos) > lim["videos"]:
        die(f"max {lim['videos']} reference videos (combined length <= {lim['ref_secs']}s)")
    if len(ref_audios) > lim["audios"]:
        die(f"max {lim['audios']} reference audio clips")
    if ref_audios and not (ref_images or ref_videos) and not lim["audio_alone"]:
        die("audio can't be the only reference on 2.0-series models — pair it with an image/video, or use the 2.5 default model")

    if args.first_frame:
        content.append({"type": "image_url", "image_url": {"url": to_asset_url(args.first_frame, "image")}, "role": "first_frame"})
        labels.append(f"first_frame <- {args.first_frame}")
    if args.last_frame:
        content.append({"type": "image_url", "image_url": {"url": to_asset_url(args.last_frame, "image")}, "role": "last_frame"})
        labels.append(f"last_frame  <- {args.last_frame}")
    for n, ref in enumerate(ref_images, 1):
        content.append({"type": "image_url", "image_url": {"url": to_asset_url(ref, "image")}, "role": "reference_image"})
        labels.append(f"Image {n} <- {pretty(ref)}")
    for n, ref in enumerate(ref_videos, 1):
        content.append({"type": "video_url", "video_url": {"url": to_asset_url(ref, "video")}, "role": "reference_video"})
        labels.append(f"Video {n} <- {ref}")
    for n, ref in enumerate(ref_audios, 1):
        content.append({"type": "audio_url", "audio_url": {"url": to_asset_url(ref, "audio")}, "role": "reference_audio"})
        labels.append(f"Audio {n} <- {pretty(ref)}")

    if len(content) - 1 > lim["files"]:
        die(f"more than {lim['files']} asset files in one request")
    return content, labels


def build_body(args, content):
    mk = model_key(args)
    lim = LIMITS[mk]
    roles = [item.get("role") for item in content[1:]]
    has_refs = any(r and r.startswith("reference_") for r in roles)

    task_type = args.task_type
    if task_type and mk != "full":
        die("--task-type is Seedance 2.5 only — drop it, or drop --model/--fast")
    if task_type in ("edit", "extend") and "reference_video" not in roles:
        die(f"--task-type {task_type} needs at least one reference video (--video or a motion pack)")
    if mk == "full" and has_refs and not task_type:
        task_type = "auto"

    # 2.5 hard constraints: edit/extend and first-frame tasks lock the aspect
    # ratio (and edit also the duration) to the source asset — the API rejects
    # anything else, asynchronously. Fail here instead, before spending.
    forced_adaptive = task_type in ("edit", "extend") or (mk == "full" and "first_frame" in roles)
    ratio = args.ratio
    if forced_adaptive:
        if ratio not in (None, "adaptive"):
            die(f"this task locks the ratio to the source asset on 2.5 — it must be 'adaptive', not {ratio}")
        ratio = "adaptive"
    else:
        ratio = ratio or "16:9"

    resolution = args.resolution or ("1080p" if "1080p" in lim["res"] else "720p")
    if resolution not in lim["res"]:
        hint = "4k needs --model 2.0" if resolution == "4k" else "the max is 720p"
        die(f"--resolution {resolution} is unsupported on the {mk} model — {hint}")

    duration = args.duration
    lo, hi = lim["dur"]
    if task_type == "edit":
        if duration not in (None, "auto", "-1"):
            die("video editing keeps the source duration — it must be -1/'auto', so drop --duration")
        duration = -1
    elif duration is None:
        duration = 5
    elif duration == "auto":
        duration = -1
    else:
        try:
            duration = int(duration)
        except ValueError:
            die(f"--duration must be an integer {lo}-{hi}, 'auto', or -1")
        if duration != -1 and not lo <= duration <= hi:
            die(f"--duration must be {lo}-{hi}, 'auto', or -1")

    body = {
        "model": MODELS[mk],
        "content": content,
        "generate_audio": not args.no_audio,
        "ratio": ratio,
        "duration": duration,
        "resolution": resolution,
        "watermark": args.watermark,
        "return_last_frame": not args.no_last_frame,
    }
    if mk == "full" and has_refs:
        body["omni_reference_task_type"] = task_type
    if args.format:
        if mk != "full":
            die("--format is Seedance 2.5 only — 2.0-series models always output mp4")
        body["output_format"] = args.format
    if args.seed is not None:
        body["seed"] = args.seed
    return body


def redacted(body):
    """Copy of the request body with base64 payloads collapsed (for --dry-run)."""
    b = json.loads(json.dumps(body))
    for item in b["content"]:
        for k in ("image_url", "video_url", "audio_url"):
            if k in item and item[k]["url"].startswith("data:"):
                head = item[k]["url"].split(",", 1)[0]
                item[k]["url"] = f"{head},<{len(item[k]['url']):,} chars base64>"
    return b


# ---- state & lifecycle ---------------------------------------------------------

def load_state():
    return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}


def save_state(s):
    STATE_FILE.write_text(json.dumps(s, indent=2))


def resolve_task(ref):
    """Accept a task id or a --name label; returns (task_id, name-or-None)."""
    for name, rec in load_state().items():
        if ref in (name, rec.get("id")):
            return rec["id"], name
    return ref, None


def wait_task(tid, name, interval, timeout_s):
    start = time.time()
    while True:
        info = api_retrieve(tid)
        if info.get("status") in TERMINAL:
            return info
        if time.time() - start > timeout_s:
            die(f"[{name}] still {info.get('status')} after {int(timeout_s)}s — resume with: seedance.py wait {name}")
        print(f"[{name}] {info.get('status')} … {int(time.time() - start)}s", flush=True)
        time.sleep(interval)


def finish(info, name):
    """Report a terminal task; download video + chaining frame on success."""
    status = info.get("status")
    if status != "succeeded":
        err = info.get("error") or {}
        detail = f" — {err.get('code')}: {err.get('message')}" if err else ""
        print(f"[{name}] {status}{detail}")
        return status
    OUTPUT_DIR.mkdir(exist_ok=True)
    c = info.get("content") or {}
    video = OUTPUT_DIR / f"{name}.mp4"
    if video.exists():
        line = f"[{name}] succeeded — already downloaded: {video.relative_to(REPO)}"
    else:
        download(c["video_url"], video)
        line = f"[{name}] succeeded -> {video.relative_to(REPO)}"
        if c.get("last_frame_url"):
            download(c["last_frame_url"], OUTPUT_DIR / f"{name}.last.png")
            line += f" (+ {name}.last.png for chaining)"
    usage = info.get("usage") or {}
    if usage.get("completion_tokens"):
        line += f" · {usage['completion_tokens']:,} tokens"
    print(line)
    return status


# ---- commands ------------------------------------------------------------------

def cmd_generate(args):
    if bool(args.prompt) == bool(args.prompt_file):
        die("exactly one of --prompt / --prompt-file is required")
    prompt = args.prompt or pathlib.Path(args.prompt_file).read_text().strip()
    name = args.name or (pathlib.Path(args.prompt_file).stem if args.prompt_file
                         else time.strftime("clip-%m%d-%H%M%S"))
    content, labels = build_content(args, prompt)
    body = build_body(args, content)
    for line in labels:
        print(" ", line)
    if args.dry_run:
        print(json.dumps(redacted(body), indent=2))
        return
    s = load_state()
    if name in s and s[name].get("status") not in ("failed", "cancelled", "expired"):
        die(f"name '{name}' already tracks task {s[name]['id']} — pick another, or run: seedance.py status {name}")
    tid = api_create(body)
    s[name] = {"id": tid, "model": body["model"], "created": time.strftime("%Y-%m-%d %H:%M:%S")}
    save_state(s)
    print(f"[{name}] task {tid} created")
    if args.no_wait:
        print(f"poll later with: python3 pipeline/seedance.py wait {name}")
        return
    info = wait_task(tid, name, args.interval, args.timeout)
    s = load_state()
    s[name]["status"] = info.get("status")
    save_state(s)
    if finish(info, name) != "succeeded":
        sys.exit(1)


def cmd_status(args):
    tid, name = resolve_task(args.task)
    info = api_retrieve(tid)
    st = info.get("status")
    if st in TERMINAL:
        if name:
            s = load_state()
            s[name]["status"] = st
            save_state(s)
        finish(info, name or tid)
    else:
        print(f"[{name or tid}] {st}")


def cmd_wait(args):
    tid, name = resolve_task(args.task)
    info = wait_task(tid, name or tid, args.interval, args.timeout)
    if name:
        s = load_state()
        s[name]["status"] = info.get("status")
        save_state(s)
    if finish(info, name or tid) != "succeeded":
        sys.exit(1)


def cmd_list(args):
    params = {"page_num": 1, "page_size": args.limit}
    if args.status:
        params["filter.status"] = args.status
    r = requests.get(f"{API}/contents/generations/tasks", headers=headers(), params=params, timeout=60)
    if r.status_code >= 400:
        die(f"list failed HTTP {r.status_code}: {r.text[:300]}")
    d = r.json()
    by_id = {rec.get("id"): n for n, rec in load_state().items()}
    print(f"{d.get('total', 0)} task(s) in the last 7 days")
    for t in d.get("items") or []:
        ts = time.strftime("%m-%d %H:%M", time.localtime(t.get("created_at", 0)))
        tag = by_id.get(t.get("id"), "")
        print(f"  {t.get('id')}  {t.get('status', ''):9}  {ts}  {t.get('model', '')}  {tag}")


def cmd_cancel(args):
    r = requests.delete(f"{API}/contents/generations/tasks/{args.task}", headers=headers(), timeout=60)
    if r.status_code >= 400:
        die(f"cancel failed HTTP {r.status_code}: {r.text[:300]}")
    print(f"{args.task} cancelled (if queued) / record deleted (if finished)")


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="create a task, poll, download to output/")
    g.add_argument("--prompt", help="prompt text inline")
    g.add_argument("--prompt-file", help="file whose entire content is the prompt")
    g.add_argument("--name", help="label used for state + output filename (default: prompt file stem)")
    g.add_argument("--pack", action="append", metavar="PACK", help="attach a library pack (people/nova, places/loft, or a bare name searched across library/*/): refs/ images+audio and urls.txt entries become numbered references (repeatable)")
    g.add_argument("--image", action="append", metavar="REF", help="reference image: local path, URL, or asset:// (repeatable, max 30 on 2.5 / 9 on 2.0)")
    g.add_argument("--video", action="append", metavar="URL", help="reference video URL or asset:// (repeatable, max 10 on 2.5 / 3 on 2.0)")
    g.add_argument("--audio", action="append", metavar="REF", help="reference audio: local path, URL, or asset:// (repeatable, max 10 on 2.5 / 3 on 2.0; audio-only refs are 2.5 only)")
    g.add_argument("--first-frame", metavar="IMG", help="I2V: opening frame (e.g. a previous clip's output/<name>.last.png); 2.5 forces ratio adaptive")
    g.add_argument("--last-frame", metavar="IMG", help="I2V: closing frame (requires --first-frame)")
    g.add_argument("--model", choices=list(MODELS), help="full = Seedance 2.5 (default) · 2.0 / fast / mini = the 2.0 series")
    g.add_argument("--task-type", dest="task_type", choices=["auto", "edit", "extend"], help="2.5 omni-reference intent (omni_reference_task_type): auto is attached whenever references are present; edit/extend add the constraints the API enforces, validated here before spending")
    g.add_argument("--format", choices=["mp4", "mov"], help="2.5 output container — mov (H.264/yuv444p/PCM) keeps better color for edit/extend")
    g.add_argument("--ratio", choices=["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"], help="default 16:9; edit/extend/first-frame on 2.5 force adaptive")
    g.add_argument("--duration", help="seconds — 4-30 on 2.5, 4-15 on the 2.0 series, or 'auto'/-1 for model-chosen (default 5; edit forces -1)")
    g.add_argument("--resolution", choices=["480p", "720p", "1080p", "4k"], help="default 1080p (720p on fast/mini); 4k is 2.0-full only; 2.5 1080p is 10-bit HEVC")
    g.add_argument("--fast", action="store_true", help="shorthand for --model fast (2.0-fast: cheaper, 720p max)")
    g.add_argument("--seed", type=int, help="pin for reproducibility (same seed + inputs = same video)")
    g.add_argument("--no-audio", action="store_true", help="silent video (default generates native audio)")
    g.add_argument("--watermark", action="store_true")
    g.add_argument("--no-last-frame", action="store_true", help="skip last-frame capture (disables chaining)")
    g.add_argument("--no-wait", action="store_true", help="create only; poll later with 'wait'")
    g.add_argument("--dry-run", action="store_true", help="print the request body and exit — spends nothing")
    g.add_argument("--interval", type=int, default=20, help="poll interval seconds")
    g.add_argument("--timeout", type=int, default=2400, help="poll timeout seconds")
    g.set_defaults(fn=cmd_generate)

    st = sub.add_parser("status", help="check once; download artifacts if succeeded")
    st.add_argument("task", help="task id or --name label")
    st.set_defaults(fn=cmd_status)

    w = sub.add_parser("wait", help="poll until terminal; download on success")
    w.add_argument("task", help="task id or --name label")
    w.add_argument("--interval", type=int, default=20)
    w.add_argument("--timeout", type=int, default=2400)
    w.set_defaults(fn=cmd_wait)

    l = sub.add_parser("list", help="recent tasks (the API keeps 7 days)")
    l.add_argument("--status", choices=["queued", "running", "succeeded", "failed", "cancelled", "expired"])
    l.add_argument("--limit", type=int, default=20)
    l.set_defaults(fn=cmd_list)

    c = sub.add_parser("cancel", help="cancel a queued task / delete a finished record")
    c.add_argument("task", help="task id")
    c.set_defaults(fn=cmd_cancel)

    return ap


def main():
    args = build_parser().parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
