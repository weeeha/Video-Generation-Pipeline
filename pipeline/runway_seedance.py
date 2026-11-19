"""Seedance 2 / 2.5 through the Runway API: video to video.

seedance2: 40 credits per output second at 1080p. seedance2_5 (720p): 30 per output second + 15 per input second,
80 minimum; its --mode edit changes the input in place (duration "auto", no ratio, 720p out for a 720p input).

Reuses runway.py's key, upload, polling and download. Schema confirmed against the API on 2026-11-15 with
rejected (free) requests: promptVideo, promptText, references [{uri}], ratio (e.g. "1280:720"), duration, seed, audio.

  python pipeline/runway_seedance.py --video CLIP.mp4 --prompt-file P.md [--ref IMG ...] [--duration 5]
                                     [--ratio 1280:720] [--seed N] --name NAME --out DIR [--dry-run]
"""
import argparse
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location("runway", pathlib.Path(__file__).with_name("runway.py"))
rw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rw)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--video", required=True)
    p.add_argument("--prompt"); p.add_argument("--prompt-file")
    p.add_argument("--ref", action="append", default=[], help="reference image (look, character); repeatable")
    p.add_argument("--duration", type=int, default=5)
    p.add_argument("--ratio", default="1280:720")
    p.add_argument("--seed", type=int)
    p.add_argument("--name", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--model", default="seedance2", choices=["seedance2", "seedance2_5"])
    p.add_argument("--mode", choices=["reference", "extend", "edit"], help="seedance2_5 only")
    p.add_argument("--draft", action="store_true", help="seedance2_5: cheap 480p preview")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    secs = rw.probe_seconds(a.video)
    if secs and secs > 15:
        rw.die(f"input is {secs:.1f}s; keep Seedance inputs to 15 s or less")
    body = {"model": a.model, "promptVideo": rw.resolve_media(a.video, a.dry_run)}
    if a.mode in ("edit", "extend"):
        body["mode"] = a.mode
        body["duration"] = "auto" if a.mode == "edit" else a.duration
    else:
        body.update(ratio=a.ratio, duration=a.duration)
        if a.mode:
            body["mode"] = a.mode
    if a.draft:
        body["draft"] = True
    prompt = rw.read_prompt(a)
    if prompt:
        body["promptText"] = prompt
    if a.ref:
        body["references"] = [{"uri": rw.resolve_media(r, a.dry_run)} for r in a.ref]
    if a.seed is not None:
        body["seed"] = a.seed
    if a.model == "seedance2_5":
        out_s = secs if a.mode == "edit" and secs else a.duration
        est = max(80, round(out_s * (20 if a.draft else 30) + (secs or 0) * (10 if a.draft else 15)))
    else:
        est = a.duration * 40
    rw.submit("/video_to_video", body, a.name, pathlib.Path(a.out), a.dry_run, est)


if __name__ == "__main__":
    main()
