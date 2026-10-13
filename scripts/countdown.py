#!/usr/bin/env python3
"""Render a countdown graphic ("47 DAYS until the lifts turn") over a photo.

Days are computed from --date (the day the post will publish) to OPENING,
so the number is right for the queue slot, not for the day you render it.

Usage:
    python3 scripts/countdown.py assets/DSCF3223.jpg --date 2026-10-12 \
        --out assets/countdown/2026-10-12.jpg
    python3 scripts/countdown.py assets/story/LM_06183.jpg --date 2026-10-13 --story \
        --out assets/countdown/story-2026-10-13.jpg
"""
import argparse
import datetime as dt
import pathlib

from PIL import Image, ImageDraw, ImageFont, ImageOps

# Furano + Niseko Grand Hirafu, both tentative (resort sites, checked 10 Oct 2026)
OPENING = dt.date(2026, 11, 28)
FONT = "/System/Library/Fonts/Supplemental/Futura.ttc"  # macOS only


def render(photo, date, out, story=False, line="UNTIL THE LIFTS TURN IN HOKKAIDO"):
    days = (OPENING - date).days
    size = (1080, 1920) if story else (1080, 1350)
    im = ImageOps.fit(Image.open(photo).convert("RGB"), size)

    # dark gradient over the lower half so white text reads on snow
    shade = Image.new("L", (1, size[1]))
    for y in range(size[1]):
        shade.putpixel((0, y), int(170 * max(0, (y / size[1] - 0.4) / 0.6)))
    im.paste(Image.new("RGB", size, "black"), mask=shade.resize(size))

    d = ImageDraw.Draw(im)
    big = ImageFont.truetype(FONT, 330 if story else 300, index=4)
    mid = ImageFont.truetype(FONT, 64, index=2)
    small = ImageFont.truetype(FONT, 36, index=0)
    w, h = size
    base = h - (560 if story else 470)
    d.text((w // 2, base), str(days), font=big, fill="white", anchor="ms")
    d.text((w // 2, base + 80), "DAYS", font=mid, fill="white", anchor="ms")
    d.text((w // 2, base + 150), line, font=small, fill="white", anchor="ms")
    d.text((w // 2, h - (220 if story else 60)), "WILDR  ·  KAMIFURANO", font=small,
           fill=(255, 255, 255, 200), anchor="ms")

    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "JPEG", quality=90)
    return days


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("photo")
    p.add_argument("--date", required=True, type=dt.date.fromisoformat,
                   help="publish date (YYYY-MM-DD)")
    p.add_argument("--out", required=True)
    p.add_argument("--story", action="store_true", help="9:16 instead of 4:5")
    p.add_argument("--line", default="UNTIL THE LIFTS TURN IN HOKKAIDO")
    a = p.parse_args()
    assert (OPENING - dt.date(2026, 10, 12)).days == 47  # self-check on the date math
    print(render(a.photo, a.date, a.out, a.story, a.line), "days")
