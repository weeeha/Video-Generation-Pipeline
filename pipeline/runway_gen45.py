"""Runway Gen-4.5 image to video through the Runway API (model "gen4.5", 12 credits per output second).

Gen-4.5 has no video-to-video: it animates one still (used as the first frame) from a text prompt, so it invents
the motion. Reuses runway.py's key, upload, polling and download.

  python pipeline/runway_gen45.py --image FIRST.jpg --prompt-file P.md [--duration 5] [--ratio 1280:720]
                                  [--seed N] --name NAME --out DIR [--dry-run]
"""
import argparse
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location("runway", pathlib.Path(__file__).with_name("runway.py"))
rw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rw)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--image", required=True)
    p.add_argument("--prompt"); p.add_argument("--prompt-file")
    p.add_argument("--duration", type=int, default=5, help="2 to 10 s")
    p.add_argument("--ratio", default="1280:720")
    p.add_argument("--seed", type=int)
    p.add_argument("--name", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    prompt = rw.read_prompt(a)
    if not prompt:
        rw.die("Gen-4.5 needs --prompt or --prompt-file (max 1000 characters)")
    if len(prompt) > 1000:
        rw.die(f"prompt is {len(prompt)} characters; Gen-4.5 takes 1000 at most")
    body = {"model": "gen4.5", "promptImage": [{"uri": rw.resolve_media(a.image, a.dry_run), "position": "first"}],
            "promptText": prompt, "ratio": a.ratio, "duration": a.duration}
    if a.seed is not None:
        body["seed"] = a.seed
    rw.submit("/image_to_video", body, a.name, pathlib.Path(a.out), a.dry_run, a.duration * 12)


if __name__ == "__main__":
    main()
