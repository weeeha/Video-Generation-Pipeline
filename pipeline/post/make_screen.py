"""Build the phone-screen asset composited onto the dark screen in the hero take.

Deliberately unbranded: it shows the product's *output* (a render of the finished room)
with neutral chrome, rather than inventing another company's UI.

Legibility drives every choice here. On a 1080p frame the screen is roughly 200x420px, so
fine detail is invisible: the render gets most of the height, and the only text is one
bold pill that still reads when it is ~14px tall.
"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1170, 2532                      # iPhone-ish portrait
BG = (12, 15, 20)
CARD_R = 56
ACCENT = (255, 214, 92)                # warm brass, picks up the faucet
INK = (255, 255, 255)
MUTED = (150, 158, 170)

FONTS = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttc",
    "/Library/Fonts/Arial Bold.ttf",
]


def font(size):
    for path in FONTS:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(img, radius):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, img.size[0] - 1, img.size[1] - 1],
                                           radius=radius, fill=255)
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    return out


screen = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(screen)

# --- the render card: the finished kitchen, cropped to a tall 4:5 -------------------
src = Image.open("library/places/reno-kitchen/refs/02-after-wide.png").convert("RGB")
margin = 64
card_w = W - margin * 2
card_h = int(card_w * 1.25)
sw, sh = src.size
target_ratio = card_w / card_h
crop_h = sh
crop_w = int(sh * target_ratio)
if crop_w > sw:
    crop_w = sw
    crop_h = int(sw / target_ratio)
left = (sw - crop_w) // 2
top = (sh - crop_h) // 2
card = src.crop((left, top, left + crop_w, top + crop_h)).resize(
    (card_w, card_h), Image.LANCZOS)
card_y = 300
screen.paste(rounded(card, CARD_R), (margin, card_y), rounded(card, CARD_R))

# --- header ------------------------------------------------------------------------
d.text((margin, 150), "PROJECT RENDER", font=font(58), fill=MUTED)
d.text((margin, 218), "Kitchen — full remodel", font=font(64), fill=INK)

# --- before / after toggle: the one element that must read at thumbnail size --------
pill_y = card_y + card_h + 70
pill_h = 150
pill_w = (card_w - 28) // 2
d.rounded_rectangle([margin, pill_y, margin + pill_w, pill_y + pill_h],
                    radius=pill_h // 2, fill=(30, 35, 44))
d.rounded_rectangle([margin + pill_w + 28, pill_y, margin + card_w, pill_y + pill_h],
                    radius=pill_h // 2, fill=ACCENT)


def centred(text, box, fnt, fill):
    x0, y0, x1, y1 = box
    tw = d.textbbox((0, 0), text, font=fnt)
    d.text((x0 + (x1 - x0 - (tw[2] - tw[0])) / 2 - tw[0],
            y0 + (y1 - y0 - (tw[3] - tw[1])) / 2 - tw[1]), text, font=fnt, fill=fill)


centred("BEFORE", (margin, pill_y, margin + pill_w, pill_y + pill_h), font(62), MUTED)
centred("AFTER", (margin + pill_w + 28, pill_y, margin + card_w, pill_y + pill_h),
        font(62), (18, 20, 26))

# --- estimate strip ----------------------------------------------------------------
strip_y = pill_y + pill_h + 80
d.rounded_rectangle([margin, strip_y, margin + card_w, strip_y + 210],
                    radius=44, fill=(24, 28, 36))
d.text((margin + 56, strip_y + 46), "ESTIMATED", font=font(46), fill=MUTED)
d.text((margin + 56, strip_y + 104), "$24,800", font=font(88), fill=INK)

screen.save("pipeline/post/phone_screen.png")
print("wrote pipeline/post/phone_screen.png", screen.size)
