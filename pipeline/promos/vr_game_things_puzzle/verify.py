"""Deterministic verification for rendered promo media."""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from fractions import Fraction


def sha256_file(path: pathlib.Path) -> str:
    """Return the SHA-256 digest for a media artifact."""
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _frame_rate(value: str) -> float:
    return float(Fraction(value)) if value not in {"", "0/0"} else 0.0


def _duration(value: str | None) -> float:
    return float(value) if value not in {None, "", "N/A"} else 0.0


def probe_media(path: pathlib.Path) -> dict:
    """Return normalized audio/video metadata from ffprobe."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    video = next(stream for stream in payload["streams"] if stream["codec_type"] == "video")
    audio = next(
        (stream for stream in payload["streams"] if stream["codec_type"] == "audio"),
        None,
    )
    format_duration = _duration(payload.get("format", {}).get("duration"))
    stream_duration = _duration(video.get("duration"))
    mp4_bytes = path.read_bytes()
    moov_offset = mp4_bytes.find(b"moov")
    mdat_offset = mp4_bytes.find(b"mdat")
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": _frame_rate(video.get("avg_frame_rate", "0/0")),
        "pix_fmt": video.get("pix_fmt"),
        "format_duration": format_duration,
        "stream_duration": stream_duration,
        "duration": format_duration or stream_duration,
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "sample_rate": int(audio["sample_rate"]) if audio else None,
        "channels": int(audio["channels"]) if audio else None,
        "faststart": moov_offset >= 0 and mdat_offset >= 0 and moov_offset < mdat_offset,
    }


def verify_media(path: pathlib.Path, expected: dict) -> list[str]:
    """Return stable contract errors instead of raising for media mismatches."""
    try:
        actual = probe_media(path)
    except (FileNotFoundError, subprocess.CalledProcessError, StopIteration, ValueError):
        return [f"could not probe media: {path}"]

    errors: list[str] = []
    if "width" in expected or "height" in expected:
        expected_width = expected.get("width", actual["width"])
        expected_height = expected.get("height", actual["height"])
        if (actual["width"], actual["height"]) != (expected_width, expected_height):
            errors.append(
                f"dimensions must be {expected_width}x{expected_height}, "
                f"got {actual['width']}x{actual['height']}"
            )
    if "fps" in expected and abs(actual["fps"] - float(expected["fps"])) > 0.01:
        errors.append(f"fps must be {expected['fps']}, got {actual['fps']:.3f}")
    if actual["pix_fmt"] != "yuv420p":
        errors.append(f"pixel format must be yuv420p, got {actual['pix_fmt']}")
    if not 25.0 <= actual["duration"] <= 30.0:
        errors.append(f"duration must be 25-30 seconds, got {actual['duration']:.3f}")
    for key, label in (
        ("video_codec", "video codec"),
        ("audio_codec", "audio codec"),
        ("sample_rate", "audio sample rate"),
        ("channels", "audio channels"),
    ):
        if key in expected and actual[key] != expected[key]:
            errors.append(f"{label} must be {expected[key]}, got {actual[key]}")
    if not actual["faststart"]:
        errors.append("moov atom must occur before mdat")
    return errors


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=pathlib.Path)
    args = parser.parse_args(argv)
    expected = {
        "width": 1920,
        "height": 1080,
        "fps": 24,
        "video_codec": "h264",
        "audio_codec": "aac",
        "sample_rate": 48000,
        "channels": 2,
    }
    errors = verify_media(args.media, expected)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)

    actual = probe_media(args.media)
    print(
        f"valid: {actual['width']}x{actual['height']} "
        f"{actual['video_codec']} {actual['pix_fmt']} "
        f"{actual['fps']:.3f}fps {actual['duration']:.3f}s "
        f"{actual['audio_codec']} stereo {actual['sample_rate']}Hz "
        f"faststart sha256={sha256_file(args.media)}"
    )


if __name__ == "__main__":
    main()
