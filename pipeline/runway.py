#!/usr/bin/env python3
"""Runway Dev API client for the film work: Aleph 2.0 (edit real footage) and Act-Two (performance transfer).

Sits beside seedance.py and follows its rules: --dry-run is free and prints exactly what would be sent,
the key is never printed, outputs are downloaded immediately because URLs expire (24 to 48 h here).

Key resolution: $RUNWAYML_API_SECRET, then repo .env, then ~/Documents/Claude/Projects/SeedDance/.env.

Subcommands
  upload   <file>                       ephemeral upload, prints the runway:// URI to reuse (uploads expire)
  aleph    --video PLATE [--prompt|--prompt-file] [--keyframe IMG@SECONDS ...] [--range START:END]
           [--aspect 16:9] [--format mp4|prores|png_sequence|sdr_rec709_10bit] [--seed N] [--name slug]
  act-two  --character IMG_OR_VIDEO --performance VIDEO [--body] [--expression 1..5] [--ratio 1280:720] [--name slug]
  status   <task-id>          wait <task-id>          cancel <task-id>

Local files given to --video, --keyframe, --character, --performance are uploaded automatically.
URLs and runway:// URIs are passed through. Prompt files may be markdown: a ```prompt fenced block is
sent when present, otherwise the whole file.

Costs (1 credit = $0.01): aleph2 28 credits per output second, 56 minimum; act_two 5 per second, 3 s minimum;
prores/png +5 per second; 10-bit +20 per second. The dry run prints the estimate when ffprobe can read the input.
"""
import argparse, json, mimetypes, os, pathlib, re, shutil, subprocess, sys, time

try:
    import requests
except ImportError:
    sys.exit("needs the 'requests' package: python3 -m pip install requests")

BASE = "https://api.dev.runwayml.com/v1"
VERSION = "2024-11-06"
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_OUT = REPO / "output" / "runway"
STATE = HERE / "runway-state.json"
POLL_S = 5            # the spec says not to expect updates more often than every 5 s
TERMINAL = {"SUCCEEDED", "FAILED", "CANCELLED"}
SURCHARGE = {"mp4": 0, "prores": 5, "png_sequence": 5, "sdr_rec709_10bit": 20}


def die(msg):
    sys.exit(f"error: {msg}")


def load_key():
    k = os.environ.get("RUNWAYML_API_SECRET", "").strip()
    if k:
        return k
    for envf in (REPO / ".env", pathlib.Path.home() / "Documents/Claude/Projects/SeedDance/.env"):
        if envf.exists():
            for line in envf.read_text().splitlines():
                if line.strip().startswith("RUNWAYML_API_SECRET"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    die("RUNWAYML_API_SECRET not found. export it, or add RUNWAYML_API_SECRET=... to "
        "~/Documents/Claude/Projects/SeedDance/.env (never commit it)")


def headers():
    return {"Authorization": f"Bearer {load_key()}", "X-Runway-Version": VERSION, "Content-Type": "application/json"}


def api(method, path, body=None):
    r = requests.request(method, f"{BASE}{path}", headers=headers(),
                         data=json.dumps(body) if body is not None else None, timeout=60)
    try:
        payload = r.json()
    except ValueError:
        payload = {"raw": r.text[:500]}
    if r.status_code >= 400:
        die(f"HTTP {r.status_code} on {method} {path}: {json.dumps(payload)[:800]}")
    return payload


# ---------- state ----------
def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {"tasks": {}, "uploads": {}}


def save_state(s):
    STATE.write_text(json.dumps(s, indent=1))


# ---------- media helpers ----------
def is_remote(ref: str) -> bool:
    return ref.startswith(("http://", "https://", "runway://", "data:"))


def probe_seconds(path: str):
    if not shutil.which("ffprobe") or is_remote(path):
        return None
    try:
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", path], capture_output=True, text=True, timeout=20).stdout.strip()
        return float(out)
    except Exception:
        return None


def upload(path: str, dry: bool = False) -> str:
    """Two-step ephemeral upload: POST /uploads for a presigned form, then POST the file to it."""
    p = pathlib.Path(path).expanduser()
    if not p.exists():
        die(f"file not found: {p}")
    if dry:
        return f"runway://(would-upload {p.name}, {p.stat().st_size // 1024} KB)"
    st = load_state()
    cached = st["uploads"].get(str(p.resolve()))
    if cached and time.time() - cached["t"] < 6 * 3600:
        print(f"  reusing upload from this session: {cached['uri']}")
        return cached["uri"]
    grant = api("POST", "/uploads", {"filename": p.name, "type": "ephemeral"})
    mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    with p.open("rb") as fh:
        r = requests.post(grant["uploadUrl"], data=grant.get("fields", {}), files={"file": (p.name, fh, mime)}, timeout=600)
    if r.status_code >= 400:
        die(f"upload POST failed HTTP {r.status_code}: {r.text[:400]}")
    st["uploads"][str(p.resolve())] = {"uri": grant["runwayUri"], "t": time.time()}
    save_state(st)
    print(f"  uploaded {p.name} -> {grant['runwayUri']}")
    return grant["runwayUri"]


def resolve_media(ref: str, dry: bool) -> str:
    return ref if is_remote(ref) else upload(ref, dry)


def read_prompt(args) -> str | None:
    if getattr(args, "prompt", None):
        return args.prompt
    if getattr(args, "prompt_file", None):
        text = pathlib.Path(args.prompt_file).read_text()
        m = re.search(r"```prompt\s*\n(.*?)```", text, re.S)
        return (m.group(1) if m else text).strip()
    return None


# ---------- task lifecycle ----------
def download(url: str, dest: pathlib.Path) -> pathlib.Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with dest.open("wb") as fh:
            for chunk in r.iter_content(1 << 20):
                fh.write(chunk)
    return dest


def ext_for(url: str, fmt: str) -> str:
    if fmt == "png_sequence":
        return ".zip"
    if fmt == "prores":
        return ".mov"
    m = re.search(r"\.(mp4|mov|png|jpg|jpeg|webp|zip)(\?|$)", url)
    return f".{m.group(1)}" if m else ".mp4"


def finish(task: dict, name: str, out_dir: pathlib.Path, fmt: str = "mp4"):
    status = task["status"]
    if status == "SUCCEEDED":
        paths = []
        for i, url in enumerate(task["output"]):
            suffix = f"-{i}" if len(task["output"]) > 1 else ""
            paths.append(download(url, out_dir / f"{name}-{task['id'][:8]}{suffix}{ext_for(url, fmt)}"))
        print(f"  SUCCEEDED  cost={task.get('cost', {}).get('credits')} credits")
        for p in paths:
            print(f"  saved {p}  ({p.stat().st_size // 1024} KB)")
    elif status == "FAILED":
        print(f"  FAILED  code={task.get('failureCode')}  cost={task.get('cost', {}).get('credits')}\n  {task.get('failure')}")
    else:
        print(f"  {status}  cost={task.get('cost', {}).get('credits')}")


def wait_task(tid: str, timeout_s: int = 1800) -> dict:
    t0 = time.time(); last = None
    while time.time() - t0 < timeout_s:
        task = api("GET", f"/tasks/{tid}")
        sig = (task["status"], task.get("progress"))
        if sig != last:
            print(f"  {time.time() - t0:6.0f}s  {task['status']}  progress={task.get('progress')}")
            last = sig
        if task["status"] in TERMINAL:
            return task
        time.sleep(POLL_S)
    die(f"timed out after {timeout_s}s waiting on {tid}")


def submit(path: str, body: dict, name: str, out_dir: pathlib.Path, dry: bool, est_credits, fmt: str = "mp4"):
    print(f"POST {BASE}{path}")
    print(json.dumps(body, indent=2))
    if est_credits is not None:
        print(f"estimated cost: {est_credits} credits (${est_credits / 100:.2f})")
    else:
        print("estimated cost: unknown (ffprobe could not read the input duration)")
    if dry:
        print("dry run, nothing sent.")
        return
    created = api("POST", path, body)
    tid = created["id"]
    st = load_state(); st["tasks"][tid] = {"name": name, "path": path, "t": time.time(), "out": str(out_dir), "fmt": fmt}; save_state(st)
    print(f"task {tid} created; polling every {POLL_S}s")
    finish(wait_task(tid), name, out_dir, fmt)


# ---------- commands ----------
def cmd_upload(args):
    print(upload(args.file, args.dry_run))


def cmd_aleph(args):
    dry = args.dry_run
    plate_secs = probe_seconds(args.video)
    if plate_secs and plate_secs > 30:
        die(f"input is {plate_secs:.1f}s; Aleph accepts 30 s or less. Trim first (ffmpeg -ss/-t).")
    body = {"model": "aleph2", "videoUri": resolve_media(args.video, dry)}
    prompt = read_prompt(args)
    if prompt:
        if len(prompt) > 1000:
            die(f"promptText is {len(prompt)} chars; limit 1000")
        body["promptText"] = prompt
    if args.keyframe:
        kfs = []
        for spec in args.keyframe:
            if "@" not in spec:
                die(f"--keyframe needs IMG@SECONDS (or IMG@0.5f for a fraction): {spec}")
            img, at = spec.rsplit("@", 1)
            kf = {"uri": resolve_media(img, dry)}
            if at.endswith("f"):
                kf["at"] = float(at[:-1])
            else:
                kf["seconds"] = float(at)
            if args.range:
                s, e = args.range.split(":")
                kf["range"] = {"start_seconds": int(s), "end_seconds": int(e)}
            kfs.append(kf)
        body["keyframes"] = kfs
    if not prompt and not args.keyframe:
        die("Aleph needs --prompt/--prompt-file or at least one --keyframe")
    if args.aspect:
        body["targetAspectRatio"] = args.aspect
    if args.format != "mp4":
        body["outputFormat"] = args.format
        if args.format == "prores" and args.prores_profile:
            body["proresProfile"] = args.prores_profile
    if args.seed is not None:
        body["seed"] = args.seed
    est = None
    if plate_secs:
        est = max(56, round(plate_secs * (28 + SURCHARGE[args.format])))
    name = args.name or f"aleph-{pathlib.Path(args.video).stem}"
    submit("/video_to_video", body, name, pathlib.Path(args.out), dry, est, args.format)


def cmd_act_two(args):
    dry = args.dry_run
    perf_secs = probe_seconds(args.performance)
    if perf_secs and not (3 <= perf_secs <= 30):
        die(f"performance is {perf_secs:.1f}s; Act-Two needs 3 to 30 s")
    char_ref = args.character
    is_video = bool(re.search(r"\.(mp4|mov|webm|mkv)$", char_ref, re.I)) or args.character_is_video
    body = {
        "model": "act_two",
        "character": {"type": "video" if is_video else "image", "uri": resolve_media(char_ref, dry)},
        "reference": {"type": "video", "uri": resolve_media(args.performance, dry)},
        "expressionIntensity": args.expression,
        "ratio": args.ratio,
    }
    if args.body:
        if is_video:
            print("  note: bodyControl is ignored for character videos")
        body["bodyControl"] = True
    if args.seed is not None:
        body["seed"] = args.seed
    est = max(15, round(perf_secs * 5)) if perf_secs else None
    name = args.name or f"acttwo-{pathlib.Path(args.performance).stem}"
    submit("/character_performance", body, name, pathlib.Path(args.out), dry, est)


def cmd_status(args):
    task = api("GET", f"/tasks/{args.task_id}")
    print(json.dumps({k: v for k, v in task.items() if k != "output"}, indent=1))
    if task["status"] == "SUCCEEDED":
        st = load_state().get("tasks", {}).get(args.task_id, {})
        finish(task, st.get("name", "task"), pathlib.Path(st.get("out", DEFAULT_OUT)), st.get("fmt", "mp4"))


def cmd_wait(args):
    st = load_state().get("tasks", {}).get(args.task_id, {})
    finish(wait_task(args.task_id), st.get("name", "task"), pathlib.Path(st.get("out", DEFAULT_OUT)), st.get("fmt", "mp4"))


def cmd_cancel(args):
    r = requests.delete(f"{BASE}/tasks/{args.task_id}", headers=headers(), timeout=30)
    print(f"HTTP {r.status_code} {r.text[:200]}")


def build_parser():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    u = sub.add_parser("upload", help="ephemeral upload; prints the runway:// URI")
    u.add_argument("file"); u.add_argument("--dry-run", action="store_true")

    a = sub.add_parser("aleph", help="Aleph 2.0: edit a plate of 30 s or less")
    a.add_argument("--video", required=True, help="plate: local file, https URL or runway:// URI")
    a.add_argument("--prompt"); a.add_argument("--prompt-file")
    a.add_argument("--keyframe", action="append", help="IMG@SECONDS or IMG@0.5f (fraction). Up to 5")
    a.add_argument("--range", help="START:END whole seconds, applied to every keyframe (end exclusive)")
    a.add_argument("--aspect", choices=["16:9", "4:3", "3:2", "1:1", "2:3", "3:4", "9:16", "21:9"], help="targetAspectRatio (outpaint)")
    a.add_argument("--format", default="mp4", choices=list(SURCHARGE))
    a.add_argument("--prores-profile", choices=["422 Proxy", "422 LT", "422", "422 HQ", "4444", "4444 XQ"])
    a.add_argument("--seed", type=int)
    a.add_argument("--name"); a.add_argument("--out", default=str(DEFAULT_OUT))
    a.add_argument("--dry-run", action="store_true", help="print the exact request and estimate, send nothing")

    t = sub.add_parser("act-two", help="Act-Two: a performance video drives a character image or video")
    t.add_argument("--character", required=True, help="character image (or video) file / URL")
    t.add_argument("--character-is-video", action="store_true", help="force video type when the extension is ambiguous")
    t.add_argument("--performance", required=True, help="driving video, 3 to 30 s, one person, face visible, waist-up")
    t.add_argument("--body", action="store_true", help="bodyControl: transfer gestures too (character images only)")
    t.add_argument("--expression", type=int, default=3, choices=range(1, 6), metavar="1-5")
    t.add_argument("--ratio", default="1280:720", choices=["1280:720", "720:1280", "960:960", "1104:832", "832:1104", "1584:672"])
    t.add_argument("--seed", type=int)
    t.add_argument("--name"); t.add_argument("--out", default=str(DEFAULT_OUT))
    t.add_argument("--dry-run", action="store_true")

    for cmd, fn in (("status", cmd_status), ("wait", cmd_wait), ("cancel", cmd_cancel)):
        p = sub.add_parser(cmd); p.add_argument("task_id"); p.set_defaults(func=fn)
    u.set_defaults(func=cmd_upload); a.set_defaults(func=cmd_aleph); t.set_defaults(func=cmd_act_two)
    return ap


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
