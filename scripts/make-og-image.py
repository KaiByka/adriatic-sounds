#!/usr/bin/env python3
"""Generate site/og-image.png (1200x630) from the committed map data.

Dark night-chart rendering of the Adriatic: clipped Natural Earth coastline,
gold pins, serif title. Run: python3 scripts/make-og-image.py
Requires: pillow (pip install pillow). Fonts: Liberation (system).
"""
import json
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(HERE, "..", "site")

W, H = 1200, 630
LON0, LON1, LAT0, LAT1 = 12, 20, 41.5, 46.5  # same viewBox as site/index.html
MW, MH = 1000, 862
PX = lambda lon: (lon - LON0) / (LON1 - LON0) * MW
PY = lambda lat: (LAT1 - lat) / (LAT1 - LAT0) * MH

FONT_DIR = "/usr/share/fonts/liberation"
F_SERIF_IT = os.path.join(FONT_DIR, "LiberationSerif-Italic.ttf")
F_SANS = os.path.join(FONT_DIR, "LiberationSans-Regular.ttf")
F_SANS_B = os.path.join(FONT_DIR, "LiberationSans-Bold.ttf")

GOLD = (216, 162, 74)
MUTED = (143, 160, 184)
TEXT = (232, 237, 245)


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    coast = json.load(open(os.path.join(SITE, "data", "coastline.json")))
    pins = json.load(open(os.path.join(SITE, "data", "pins.json")))

    # cover-fit the map viewBox into the OG canvas, crop vertically centered
    scale = max(W / MW, H / MH)
    dw, dh = MW * scale, MH * scale
    # center the crop, biased slightly down (more sea)
    ox, oy = (W - dw) / 2, (H - dh) / 2 + 40

    def tx(lon):
        return PX(lon) * scale + ox

    def ty(lat):
        return PY(lat) * scale + oy

    # background: vertical night gradient
    img = Image.new("RGB", (W, H))
    top, bot = (12, 28, 51), (5, 12, 22)
    px = img.load()
    for y in range(H):
        c = lerp(top, bot, y / H)
        for x in range(W):
            px[x, y] = c
    # sea radial lift (like seaGrad)
    sea = Image.new("L", (W, H), 0)
    sd = ImageDraw.Draw(sea)
    sd.ellipse([W * 0.15, -H * 0.55, W * 0.95, H * 0.85], fill=46)
    sea = sea.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(180))
    lift = Image.new("RGB", (W, H), (15, 44, 78))
    img = Image.composite(lift, img, sea.point(lambda v: v))

    dr = ImageDraw.Draw(img, "RGBA")

    # land: glow pass then fill
    for f in coast["features"]:
        g = f["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        for rings in polys:
            pts = [(tx(x), ty(y)) for x, y in rings[0]]
            dr.polygon(pts, fill=None, outline=(216, 162, 74, 60), width=int(7 * scale))
            dr.polygon(pts, fill=(23, 45, 76, 255), outline=(43, 65, 102, 255))

    # pins: glow + core
    for p in pins:
        x, y = tx(p["lon"]), ty(p["lat"])
        if p.get("audio"):
            dr.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(216, 162, 74, 60))
            dr.ellipse([x - 6, y - 6, x + 6, y + 6], fill=GOLD)
        else:
            dr.ellipse([x - 5, y - 5, x + 5, y + 5], outline=MUTED, width=2)

    # legibility scrim on the left
    scrim = Image.new("L", (W, H), 0)
    sdr = ImageDraw.Draw(scrim)
    for x in range(W):
        a = int(190 * max(0.0, 1.0 - x / (W * 0.62)))
        sdr.line([(x, 0), (x, H)], fill=a)
    scrim = scrim.filter(__import__("PIL.ImageFilter", fromlist=["GaussianBlur"]).GaussianBlur(60))
    dark = Image.new("RGB", (W, H), (4, 9, 17))
    img = Image.composite(dark, img, scrim.point(lambda v: v))

    dr = ImageDraw.Draw(img, "RGBA")
    f_kick = ImageFont.truetype(F_SANS_B, 21)
    f_title = ImageFont.truetype(F_SERIF_IT, 78)
    f_sub = ImageFont.truetype(F_SANS, 27)

    x0, y0 = 64, 150
    dr.text((x0, y0), "A  S O U N D  M A P  O F  T H E  C R O A T I A N  C O A S T", font=f_kick, fill=GOLD)
    dr.text((x0 - 3, y0 + 48), "Sounds of the Adriatic", font=f_title, fill=TEXT)
    dr.text((x0, y0 + 160), "Tap a pin, hear the place.", font=f_sub, fill=MUTED)
    dr.text((x0, y0 + 205), "sound.marespot.com", font=f_sub, fill=GOLD)

    out = os.path.join(SITE, "og-image.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", out, os.path.getsize(out), "bytes")


if __name__ == "__main__":
    main()
