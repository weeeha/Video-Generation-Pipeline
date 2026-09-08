"""Deterministic verification for rendered promo media."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
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
    mp4_bytes = path.read_bytes()
    moov_offset = mp4_bytes.find(b"moov")
    mdat_offset = mp4_bytes.find(b"mdat")
    return {
        "width": int(video["width"]),
        "height": int(video["height"]),
        "fps": _frame_rate(video.get("avg_frame_rate", "0/0")),
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
