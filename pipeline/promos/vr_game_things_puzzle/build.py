#!/usr/bin/env python3
"""Validate and assemble the VR Game Things Puzzle promo timeline."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shlex
import subprocess
import sys


SHOT_KINDS = {"unity", "seedance", "title"}
FORBIDDEN_CLAIMS = {
    "combat": r"\bcombat\b",
    "flight": r"\b(?:fly|flies|flying|flight)\b",
    "hand tracking": r"\bhand[ -]?tracking\b",
    "13-piece": r"\b13[ -]?piece\b",
    "multiplayer": r"\bmultiplayer\b",
    "buy": r"\bbuy\b",
    "store purchase": r"\bstore purchase\b",
}


def load_manifest(path: pathlib.Path) -> dict:
    return json.loads(path.read_text())


def timeline_duration(manifest: dict) -> float:
    shots = manifest.get("shots", [])
    if not shots:
        return 0.0
    transition = float(manifest.get("transition", 0.0))
    duration = sum(float(shot["duration"]) for shot in shots)
    return round(duration - transition * (len(shots) - 1), 3)


def validate_manifest(manifest: dict, repo: pathlib.Path, require_files: bool = True) -> list[str]:
    errors: list[str] = []
    if (manifest.get("width"), manifest.get("height")) != (1920, 1080):
        errors.append("output dimensions must be 1920x1080")
    if manifest.get("fps") not in (24, 30):
        errors.append("fps must be 24 or 30")

    duration = timeline_duration(manifest)
    if not 25.0 <= duration <= 30.0:
        errors.append(f"timeline duration must be 25-30 seconds, got {duration:.3f}")

    shots = manifest.get("shots", [])
    for index, shot in enumerate(shots, 1):
        kind = shot.get("kind")
        if kind not in SHOT_KINDS:
            errors.append(f"shot {index} has unsupported kind: {kind}")

    has_seedance = any(shot.get("kind") == "seedance" for shot in shots)
    disclosure = str(manifest.get("disclosure", ""))
    if has_seedance and "cinematic visualization" not in disclosure.lower():
        errors.append("Seedance shots require a cinematic visualization disclosure")

    searchable = " ".join(
        str(manifest.get(key, "")) for key in ("title", "tagline", "disclosure")
    ).lower()
    for label, pattern in FORBIDDEN_CLAIMS.items():
        if re.search(pattern, searchable, flags=re.IGNORECASE):
            errors.append(f"forbidden claim: {label}")

    if require_files:
        for index, shot in enumerate(shots, 1):
            relative = pathlib.Path(shot.get("path", ""))
            if not (repo / relative).is_file():
                errors.append(f"shot {index} source is missing: {relative}")
    return errors


def build_ffmpeg_command(
    manifest: dict, repo: pathlib.Path, output: pathlib.Path
) -> list[str]:
    shots = manifest["shots"]
    width = manifest["width"]
    height = manifest["height"]
    fps = manifest["fps"]
    transition = float(manifest.get("transition", 0.0))
    total = timeline_duration(manifest)

    command = ["ffmpeg", "-y"]
    for shot in shots:
        command.extend(["-i", str(repo / shot["path"])])
    command.extend(
        [
            "-f",
            "lavfi",
            "-t",
            f"{total:.3f}",
            "-i",
            "anoisesrc=color=pink:amplitude=0.012:sample_rate=48000",
            "-f",
            "lavfi",
            "-t",
            f"{total:.3f}",
            "-i",
            "sine=frequency=55:sample_rate=48000",
        ]
    )

    filters: list[str] = []
    for index, shot in enumerate(shots):
        filters.append(
            f"[{index}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},fps={fps},format=yuv420p,"
            f"trim=duration={float(shot['duration']):.3f},setpts=PTS-STARTPTS[v{index}]"
        )

    current = "v0"
    elapsed = float(shots[0]["duration"])
    for index in range(1, len(shots)):
        offset = elapsed - transition
        result = f"vx{index}"
        filters.append(
            f"[{current}][v{index}]xfade=transition=fade:duration={transition:.3f}:"
            f"offset={offset:.3f}[{result}]"
        )
        current = result
        elapsed += float(shots[index]["duration"]) - transition

    noise_index = len(shots)
    sine_index = noise_index + 1
    filters.extend(
        [
            f"[{noise_index}:a]highpass=f=35,lowpass=f=1800,volume=0.16[noise]",
            f"[{sine_index}:a]volume=0.025[hum]",
            "[noise][hum]amix=inputs=2:normalize=0,"
            f"atrim=duration={total:.3f},asetpts=PTS-STARTPTS[aout]",
        ]
    )

    command.extend(
        [
            "-filter_complex",
            ";".join(filters),
            "-map",
            f"[{current}]",
            "-map",
            "[aout]",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    return command


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=pathlib.Path, required=True)
    parser.add_argument("--output", type=pathlib.Path)
    parser.add_argument("--repo", type=pathlib.Path, default=pathlib.Path.cwd())
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--print-command", action="store_true")
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    errors = validate_manifest(manifest, args.repo, require_files=True)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
    if args.validate_only:
        print(f"valid: {timeline_duration(manifest):.3f}s")
        return
    if args.output is None:
        parser.error("--output is required unless --validate-only is set")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = build_ffmpeg_command(manifest, args.repo, args.output)
    if args.print_command:
        print(shlex.join(command))
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()
