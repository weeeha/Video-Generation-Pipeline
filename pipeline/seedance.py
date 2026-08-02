#!/usr/bin/env python3
"""Seedance 2.0 CLI — BytePlus ModelArk client.

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
PEOPLE_DIR = REPO / "people"
STATE_FILE = pathlib.Path(__file__).resolve().parent / "state.json"
API = "https://ark.ap-southeast.bytepluses.com/api/v3"
MODELS = {"full": "dreamina-seedance-2-0-260128", "fast": "dreamina-seedance-2-0-fast-260128"}
TERMINAL = {"succeeded", "failed", "cancelled", "expired"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".gif"}
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


def person_refs(name):
    refs = PEOPLE_DIR / name / "refs"
    if not refs.is_dir():
        die(f"no such person: people/{name}/refs")
    files = sorted(p for p in refs.iterdir() if p.suffix.lower() in IMAGE_EXTS)
    if not files:
        die(f"people/{name}/refs has no images — add numbered refs first (see people/README.md)")
    return files


def build_content(args, prompt):
    """Assemble the content[] array; returns (content, human-readable numbering map)."""
    content = [{"type": "text", "text": prompt}]
    labels = []

    ref_images = []
    for name in args.person or []:
        ref_images += [str(p) for p in person_refs(name)]
    ref_images += list(args.image or [])

    if (args.first_frame or args.last_frame) and ref_images:
        die("first/last-frame (I2V) and reference images (R2V) are mutually exclusive API scenarios")
    if args.last_frame and not args.first_frame:
        die("--last-frame requires --first-frame")
    if len(ref_images) > 9:
        die(f"{len(ref_images)} reference images — the cap is 9")
    if len(args.video or []) > 3:
        die("max 3 reference videos (combined length <= 15s)")
    if len(args.audio or []) > 3:
        die("max 3 reference audio clips")
    if args.audio and not (ref_images or args.video or args.first_frame):
        die("audio can never be the only reference — pair it with an image or video")

    if args.first_frame:
        content.append({"type": "image_url", "image_url": {"url": to_asset_url(args.first_frame, "image")}, "role": "first_frame"})
        labels.append(f"first_frame <- {args.first_frame}")
    if args.last_frame:
        content.append({"type": "image_url", "image_url": {"url": to_asset_url(args.last_frame, "image")}, "role": "last_frame"})
        labels.append(f"last_frame  <- {args.last_frame}")
    for n, ref in enumerate(ref_images, 1):
        content.append({"type": "image_url", "image_url": {"url": to_asset_url(ref, "image")}, "role": "reference_image"})
        labels.append(f"Image {n} <- {ref}")
    for n, ref in enumerate(args.video or [], 1):
        content.append({"type": "video_url", "video_url": {"url": to_asset_url(ref, "video")}, "role": "reference_video"})
        labels.append(f"Video {n} <- {ref}")
    for n, ref in enumerate(args.audio or [], 1):
        content.append({"type": "audio_url", "audio_url": {"url": to_asset_url(ref, "audio")}, "role": "reference_audio"})
        labels.append(f"Audio {n} <- {ref}")

    if len(content) - 1 > 12:
        die("more than 12 asset files in one request")
    return content, labels


def build_body(args, content):
    resolution = args.resolution or ("720p" if args.fast else "1080p")
    if args.fast and resolution == "1080p":
        die("2.0-fast does not support 1080p — drop --fast or use --resolution 720p")
    duration = args.duration
    if duration != "auto":
        try:
            duration = int(duration)
        except ValueError:
            die("--duration must be an integer 4-15, or 'auto'")
        if not 4 <= duration <= 15:
            die("--duration must be 4-15, or 'auto'")
    body = {
        "model": MODELS["fast" if args.fast else "full"],
        "content": content,
        "generate_audio": not args.no_audio,
        "ratio": args.ratio,
        "duration": duration,
        "resolution": resolution,
        "watermark": args.watermark,
        "return_last_frame": not args.no_last_frame,
    }
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


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="create a task, poll, download to output/")
    g.add_argument("--prompt", help="prompt text inline")
    g.add_argument("--prompt-file", help="file whose entire content is the prompt")
    g.add_argument("--name", help="label used for state + output filename (default: prompt file stem)")
    g.add_argument("--person", action="append", metavar="NAME", help="attach people/NAME/refs/* as Image 1..N (repeatable)")
    g.add_argument("--image", action="append", metavar="REF", help="reference image: local path, URL, or asset:// (repeatable, max 9 total)")
    g.add_argument("--video", action="append", metavar="URL", help="reference video URL or asset:// (repeatable, max 3)")
    g.add_argument("--audio", action="append", metavar="REF", help="reference audio: local path, URL, or asset:// (repeatable, max 3)")
    g.add_argument("--first-frame", metavar="IMG", help="I2V: opening frame (e.g. a previous clip's output/<name>.last.png)")
    g.add_argument("--last-frame", metavar="IMG", help="I2V: closing frame (requires --first-frame)")
    g.add_argument("--ratio", default="16:9", choices=["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "adaptive"])
    g.add_argument("--duration", default="5", help="seconds 4-15, or 'auto' (default 5)")
    g.add_argument("--resolution", choices=["480p", "720p", "1080p"], help="default 1080p (720p with --fast)")
    g.add_argument("--fast", action="store_true", help="use the cheaper 2.0-fast model (no 1080p)")
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

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
