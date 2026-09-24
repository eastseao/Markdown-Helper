#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render the finished adaptive icon under the real launcher mask shapes.

Why this exists: the user cannot install the APK on a device, and "is it inside the
safe zone" is not something a bounding-box number settles - the box corners of a
square glyph sit outside a circular mask even when the box itself fits the 72dp
square. So this draws the composited icon through actual mask geometry.

Mask geometry, all in the 108dp layer coordinate system (AOSP AdaptiveIconDrawable):
    mask viewport  = 108 * DEFAULT_VIEW_PORT_SCALE = 108 * 2/3 = 72dp
    circle mask    = 72dp diameter (radius 36dp)          <- stock circular launcher mask
    squircle       = superellipse, half-extent 36dp, n=4  <- Pixel / most OEM defaults
    rounded square = 72 x 72, corner radius 20dp and 12dp <- several Chinese OEM ROMs
    guarantee      = 66dp diameter circle (radius 33dp)   <- what EVERY legal convex
                     mask must show, i.e. the true acceptance criterion

Usage: python mask_preview.py
"""
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = pathlib.Path(r"I:\mar\markdown-helper-tools\icon\stage\preview")
OUT = HERE / "mask_preview.png"

CANVAS_DP = 108.0
SS = 4                      # supersample factor
N = int(CANVAS_DP * SS)     # canvas pixels per panel
VISIBLE_DP = 72.0
GUARANTEE_DP = 66.0


def load_composited():
    """bg + fg, at the full 108dp canvas."""
    bg = Image.open(HERE / "bg.png").convert("RGBA")
    fg = Image.open(HERE / "fg.png").convert("RGBA")
    if bg.size != (N, N):
        bg = bg.resize((N, N), Image.LANCZOS)
    if fg.size != (N, N):
        fg = fg.resize((N, N), Image.LANCZOS)
    return Image.alpha_composite(bg, fg)


def mask_layer(kind):
    """Build an L-mode mask of the visible region, antialiased by drawing at SS scale."""
    m = Image.new("L", (N, N), 0)
    d = ImageDraw.Draw(m)
    c = N / 2.0
    r_vis = (VISIBLE_DP / 2.0) * SS          # 36dp -> the mask viewport radius
    box = [c - r_vis, c - r_vis, c + r_vis, c + r_vis]

    if kind == "circle":
        d.ellipse(box, fill=255)
    elif kind == "squircle":
        # superellipse |x/a|^n + |y/a|^n = 1, n=4, a = 36dp
        a = r_vis
        n = 4.0
        t = np.linspace(0, 2 * np.pi, 4096, endpoint=False)
        ct, st = np.cos(t), np.sin(t)
        x = a * np.sign(ct) * np.abs(ct) ** (2.0 / n)
        y = a * np.sign(st) * np.abs(st) ** (2.0 / n)
        d.polygon(list(zip((x + c).tolist(), (y + c).tolist())), fill=255)
    elif kind.startswith("rsquare"):
        rad = float(kind.split(":")[1]) * SS
        d.rounded_rectangle(box, radius=rad, fill=255)
    else:
        raise ValueError(kind)
    return m


MASKS = [
    ("circle  r=36dp", "circle"),
    ("squircle  n=4", "squircle"),
    ("round-sq  r=20dp", "rsquare:20"),
    ("round-sq  r=12dp", "rsquare:12"),
]


def tint(img, rgb):
    """Recolour a silhouette to `rgb`, keeping its alpha - how themed icons render."""
    a = img.convert("RGBA")
    arr = np.asarray(a).copy()
    arr[:, :, 0], arr[:, :, 1], arr[:, :, 2] = rgb
    return Image.fromarray(arr, "RGBA")


def main():
    comp = load_composited()
    mono = Image.open(HERE.parent / "res" / "drawable-xxxhdpi" / "ic_launcher_monochrome.png")
    mono = mono.convert("RGBA").resize((N, N), Image.LANCZOS)
    mono = tint(mono, (168, 199, 250))          # #A8C7FA, the usual Material You tint

    pad = 24
    label_h = 26
    footer_h = 30
    sizes = [48, 72, 96]                        # typical launcher icon sizes, in px
    cell = N // SS * 2                          # panel shown at 216px, readable
    rows = len(MASKS) + 1

    W = pad + len(sizes) * (cell + pad)
    H = pad + rows * (label_h + cell + pad) + footer_h
    sheet = Image.new("RGB", (W, H), (245, 246, 248))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("segoeui.ttf", 15)
        font_s = ImageFont.truetype("segoeui.ttf", 13)
    except Exception:
        font = font_s = ImageFont.load_default()

    # header
    for j, sz in enumerate(sizes):
        x = pad + j * (cell + pad)
        d.text((x + 4, 6), f"rendered at {sz}px", fill=(60, 64, 72), font=font)

    def draw_guides(panel):
        """66dp guarantee circle, drawn 1px so the user can see the acceptance line."""
        g = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        rc = (GUARANTEE_DP / 2.0) * SS
        c = N / 2.0
        gd.ellipse([c - rc, c - rc, c + rc, c + rc], outline=(0, 200, 210, 210), width=max(2, SS))
        # 72dp mask viewport outline
        rv = (VISIBLE_DP / 2.0) * SS
        gd.ellipse([c - rv, c - rv, c + rv, c + rv], outline=(255, 60, 60, 130), width=max(1, SS // 2))
        return Image.alpha_composite(panel, g)

    def emit_row(i, label, content, mask_kind):
        """Row i: label on top, then the same content under each render size."""
        m = mask_layer(mask_kind)
        panel = Image.new("RGBA", (N, N), (40, 42, 46, 255))
        masked = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        masked.paste(content, (0, 0), m)
        panel = Image.alpha_composite(panel, masked)
        panel = draw_guides(panel)
        y0 = pad + label_h + i * (label_h + cell + pad)
        d.text((pad + 4, y0 - label_h + 3), label, fill=(50, 54, 62), font=font_s)
        for j, sz in enumerate(sizes):
            x = pad + j * (cell + pad)
            sheet.paste(panel.resize((sz, sz), Image.LANCZOS),
                        (x + (cell - sz) // 2, y0 + (cell - sz) // 2))

    for i, (label, kind) in enumerate(MASKS):
        emit_row(i, label, comp, kind)

    # last row: themed (monochrome) under the circle mask
    emit_row(len(MASKS), "themed / monochrome under the circle mask", mono, "circle")

    d.text((pad + 4, H - footer_h + 6),
           "cyan circle = 66dp guarantee (every legal mask must show it)   "
           "red circle = 72dp mask viewport (the stock circular mask)",
           fill=(120, 126, 136), font=font_s)

    sheet.save(OUT)
    print(f"wrote {OUT}  ({sheet.size[0]}x{sheet.size[1]})")


if __name__ == "__main__":
    main()
