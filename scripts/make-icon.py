#!/usr/bin/env python3
"""Generate site/apple-touch-icon.png (180x180): night-navy rounded square with a gold pin dot.
Run: python3 scripts/make-icon.py   (requires pillow)"""
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "site", "apple-touch-icon.png")

S = 180
img = Image.new("RGB", (S, S), (5, 12, 22))
dr = ImageDraw.Draw(img, "RGBA")
# subtle radial lift
dr.ellipse([-S * 0.3, -S * 0.5, S * 1.3, S * 0.9], fill=(15, 44, 78, 255))
dr.rounded_rectangle([0, 0, S - 1, S - 1], radius=40, outline=(29, 44, 71, 255), width=2)
# gold pin: glow + core + ring
cx = cy = S // 2
dr.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=(216, 162, 74, 46))
dr.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(216, 162, 74, 28))
dr.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(216, 162, 74, 255))
img.save(OUT, "PNG", optimize=True)
print("wrote", OUT, os.path.getsize(OUT), "bytes")
