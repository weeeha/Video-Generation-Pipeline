"""Render the manifest-derived closing slate for the promo."""

from __future__ import annotations

import pathlib

from PIL import Image, ImageDraw, ImageFont


def _draw_centered(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    width: int,
    y: int,
    safe_margin: int,
) -> None:
    bounds = draw.multiline_textbbox((0, 0), text, font=font, align="center")
    text_width = bounds[2] - bounds[0]
    if text_width > width - 2 * safe_margin:
        raise ValueError("slate copy exceeds the horizontal safe margin")
    draw.multiline_text(
        ((width - text_width) / 2, y), text, fill="#f4f7fb", font=font, align="center"
    )


def render_slate(manifest: dict, path: pathlib.Path) -> pathlib.Path:
    """Render a 16:9 RGB slate from the approved manifest copy."""
    width = int(manifest["width"])
    height = int(manifest["height"])
    image = Image.new("RGB", (width, height), "#0b1119")
    draw = ImageDraw.Draw(image)
    safe_margin = int(width * 0.1)

    _draw_centered(
        draw,
        str(manifest["title"]),
        ImageFont.load_default(size=96),
        width,
        int(height * 0.19),
        safe_margin,
    )
    _draw_centered(
        draw,
        str(manifest["tagline"]),
        ImageFont.load_default(size=54),
        width,
        int(height * 0.48),
        safe_margin,
    )
    _draw_centered(
        draw,
        str(manifest["disclosure"]),
        ImageFont.load_default(size=28),
        width,
        int(height * 0.78),
        safe_margin,
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
    return path
