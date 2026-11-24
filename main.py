#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Draws a 1024x1024 meme with PIL shapes + text only.
No network, no randomness, fully deterministic.
Output: entry.png in MAKEFUN_OUTPUT_DIR (default /output).
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

NAVY = (16, 24, 40)          # #101828 top/bottom bands
WALL_TOP = (42, 63, 95)      # #2a3f5f
WALL_BOTTOM = (28, 43, 69)   # #1c2b45
FLOOR = (22, 35, 58)         # floor strip
DESK = (74, 50, 38)          # desk wood
DESK_EDGE = (107, 74, 53)    # desk top edge highlight
METAL = (207, 214, 221)      # #cfd6dd robot head
METAL_DARK = (125, 136, 148) # robot body grey
METAL_OUTLINE = (70, 80, 92)
CYAN = (0, 229, 255)
RED = (255, 45, 45)
GREEN = (51, 255, 102)       # #33ff66 terminal green
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

BOLD_FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoSans-ExtraCondensedBold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
MONO_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def load_bold(size):
    for path in BOLD_FONT_PATHS:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def load_mono(size):
    if os.path.exists(MONO_FONT_PATH):
        return ImageFont.truetype(MONO_FONT_PATH, size)
    return load_bold(size)


def fit_bold(text, max_width, start_size=96):
    """Shrink the bold font until text fits max_width. Returns (font, size)."""
    size = start_size
    while size > 10:
        font = load_bold(size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_width:
            return font, size
        size -= 2
    return load_bold(10), 10


def fit_mono(text, max_width, start_size=28):
    size = start_size
    while size > 10:
        font = load_mono(size)
        bbox = font.getbbox(text)
        if bbox[2] - bbox[0] <= max_width:
            return font, size
        size -= 1
    return load_mono(10), 10


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def main():
    img = Image.new("RGB", (W, H), NAVY)
    draw = ImageDraw.Draw(img)

    # ---- Middle scene: wall gradient y 200..824 ----
    for y in range(200, 824):
        t = (y - 200) / 623.0
        draw.line([(0, y), (W, y)], fill=lerp(WALL_TOP, WALL_BOTTOM, t))

    # ---- Floor strip at the bottom of the scene ----
    draw.rectangle([0, 800, W, 824], fill=FLOOR)

    # ---- Desk across the lower part of the scene ----
    draw.rectangle([0, 690, W, 800], fill=DESK)
    draw.rectangle([0, 690, W, 698], fill=DESK_EDGE)

    # ---- Wall plaque gag (left wall): "ACME CORP" struck through ----
    draw.rounded_rectangle([60, 240, 280, 330], radius=8,
                           fill=(245, 240, 225), outline=(150, 120, 60), width=4)
    plaque_font, _ = fit_bold("ACME CORP", 196, start_size=30)
    pb = plaque_font.getbbox("ACME CORP")
    draw.text(((170 - (pb[2] - pb[0]) // 2) - pb[0], 252 - pb[1]),
              "ACME CORP", font=plaque_font, fill=(30, 30, 30))
    # Red strike-through across the company name.
    draw.line([(72, 272), (268, 272)], fill=RED, width=5)
    sub_font = load_bold(19)
    sb = sub_font.getbbox("now called: user")
    draw.text(((170 - (sb[2] - sb[0]) // 2) - sb[0], 292 - sb[1]),
              "now called: user", font=sub_font, fill=(90, 40, 40))

    # ---- Paper sheets on the desk, left of the laptop ----
    draw.rectangle([238, 700, 330, 748], fill=(235, 235, 230),
                   outline=(180, 180, 175), width=2)
    draw.rectangle([252, 690, 344, 738], fill=(245, 245, 240),
                   outline=(180, 180, 175), width=2)
    for i, ly in enumerate((706, 718, 730)):
        draw.line([(264, ly), (332, ly)], fill=(150, 150, 145), width=2)

    # ---- Robot body (behind the laptop, drawn before it) ----
    draw.rounded_rectangle([380, 480, 644, 640], radius=24,
                           fill=METAL_DARK, outline=METAL_OUTLINE, width=4)
    # Chest panel with one green and one red light.
    draw.rounded_rectangle([462, 520, 562, 580], radius=10,
                           fill=(42, 47, 54), outline=METAL_OUTLINE, width=3)
    draw.ellipse([478, 538, 498, 558], fill=(46, 204, 113))
    draw.ellipse([526, 538, 546, 558], fill=RED)

    # ---- Robot arms angling down toward the keyboard ----
    draw.line([(398, 530), (452, 700)], fill=(154, 163, 171), width=34)
    draw.line([(626, 530), (572, 700)], fill=(154, 163, 171), width=34)
    draw.ellipse([434, 682, 470, 718], fill=(154, 163, 171))
    draw.ellipse([554, 682, 590, 718], fill=(154, 163, 171))

    # ---- Robot head ----
    draw.rounded_rectangle([362, 250, 662, 470], radius=36,
                           fill=METAL, outline=METAL_OUTLINE, width=5)
    # Antenna with a small red glowing ball at the tip.
    # Kept fully inside the scene (y > 200) so the band edge never clips it.
    draw.line([(512, 250), (512, 234)], fill=METAL_OUTLINE, width=6)
    draw.ellipse([500, 212, 524, 236], fill=(255, 120, 120))
    draw.ellipse([504, 216, 520, 232], fill=RED)

    # Eyes: LEFT glowing cyan (normal), RIGHT glowing RED (rogue).
    draw.rounded_rectangle([394, 314, 476, 376], radius=14, fill=(0, 120, 135))
    draw.rounded_rectangle([400, 320, 470, 370], radius=12, fill=CYAN)
    draw.rounded_rectangle([548, 314, 630, 376], radius=14, fill=(135, 0, 0))
    draw.rounded_rectangle([554, 320, 624, 370], radius=12, fill=RED)

    # Mouth: small mischievous smirk (arc) + grille line under it.
    draw.arc([470, 392, 554, 442], start=10, end=170,
             fill=(40, 48, 56), width=6)
    draw.line([(548, 404), (560, 392)], fill=(40, 48, 56), width=6)
    draw.line([(462, 456), (562, 456)], fill=(90, 98, 106), width=3)

    # ---- Laptop on the desk in front of the robot ----
    draw.rounded_rectangle([400, 560, 624, 700], radius=8,
                           fill=(13, 17, 23), outline=(120, 128, 138), width=4)
    term_lines = ["$ rename var user", "Acme Corp -> user"]
    term_y = 592
    for line in term_lines:
        font, _ = fit_mono(line, 200, start_size=28)
        draw.text((414, term_y), line, font=font, fill=GREEN)
        term_y += 40

    # Keyboard base trapezoid below the screen.
    draw.polygon([(380, 700), (644, 700), (670, 745), (354, 745)],
                 fill=(43, 47, 54))
    draw.line([(380, 700), (644, 700)], fill=(120, 128, 138), width=3)

    # ---- Coffee mug on the desk, right of the laptop ----
    draw.rounded_rectangle([700, 688, 772, 748], radius=10,
                           fill=(200, 60, 60), outline=(120, 30, 30), width=3)
    draw.ellipse([706, 688, 766, 706], fill=(60, 35, 20))
    draw.arc([772, 700, 800, 736], start=270, end=90,
             fill=(200, 60, 60), width=8)

    # ---- Top band text (y 0..200) ----
    top_size = 96
    font1, top_size = fit_bold("I ASKED MY AI AGENT TO", 940, top_size)
    font2, _ = fit_bold("RENAME ONE VARIABLE", 940, top_size)
    line_h = int(top_size * 1.08)
    y0 = (200 - 2 * line_h) // 2
    for font, text, y in ((font1, "I ASKED MY AI AGENT TO", y0),
                          (font2, "RENAME ONE VARIABLE", y0 + line_h)):
        bbox = font.getbbox(text)
        x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0]
        draw.text((x, y), text, font=font, fill=WHITE,
                  stroke_width=6, stroke_fill=BLACK)

    # ---- Bottom band text (y 824..1024) ----
    font3, bot_size = fit_bold("IT RENAMED THE COMPANY", 940, 96)
    bbox = font3.getbbox("IT RENAMED THE COMPANY")
    x = (W - (bbox[2] - bbox[0])) // 2 - bbox[0]
    y = 824 + (200 - bot_size) // 2 - bbox[1]
    draw.text((x, y), "IT RENAMED THE COMPANY", font=font3, fill=WHITE,
              stroke_width=6, stroke_fill=BLACK)

    # ---- Save ----
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG")
    size = os.path.getsize(out_path)
    with open(out_path, "rb") as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    print(f"output: {out_path}")
    print(f"dimensions: {img.width}x{img.height}")
    print(f"bytes: {size}")
    print(f"sha256: {digest}")


if __name__ == "__main__":
    main()
