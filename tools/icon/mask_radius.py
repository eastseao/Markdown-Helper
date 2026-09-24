"""Measure the max ink radius of the launcher layers against the real mask geometry.

Key numbers, taken from AOSP AdaptiveIconDrawable (not guessed):
    DEFAULT_VIEW_PORT_SCALE = 1/(1+2*EXTRA_INSET_PERCENTAGE) = 1/1.5 = 2/3
    -> the mask viewport covers 108 * 2/3 = 72 dp of the layer
    -> a circular mask therefore exposes a 72 dp DIAMETER circle, radius 36 dp
    SAFEZONE_SCALE = 66/72
    -> the region every legal (convex) mask must show is 66 dp diameter, radius 33 dp

So the bbox test used earlier is NOT sufficient: the bbox corners of a square-ish
glyph sit well outside both circles. What matters is the distance from the canvas
centre to the FURTHEST inked pixel.
"""
import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from PIL import Image

REPO = pathlib.Path(r"I:/mar/markdown-helper")
CANVAS_DP = 108.0
R_CIRCLE_MASK = 36.0      # what the stock circular mask actually shows
R_GUARANTEE = 33.0        # what every legal convex mask must show

print(f"{'file':46s} {'size':>9s} {'maxR dp':>8s} {'>36dp':>7s} {'>33dp':>7s}")
print("-" * 84)
worst = 0.0
for dens, fp in (("xxxhdpi", 432), ("xxhdpi", 324), ("xhdpi", 216), ("hdpi", 162), ("mdpi", 108)):
    for kind in ("foreground", "monochrome"):
        p = REPO / f"app/src/main/res/drawable-{dens}/ic_launcher_{kind}.png"
        if not p.exists():
            continue
        a = np.asarray(Image.open(p).convert("RGBA"))[:, :, 3].astype(np.float32) / 255.0
        h, w = a.shape
        yy, xx = np.mgrid[0:h, 0:w]
        cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
        rad = np.sqrt((yy - cy) ** 2 + (xx - cx) ** 2)
        ink = a > 0.03
        dp = CANVAS_DP / w
        maxr = float(rad[ink].max()) * dp
        over36 = float((rad[ink] * dp > R_CIRCLE_MASK).mean()) * 100
        over33 = float((rad[ink] * dp > R_GUARANTEE).mean()) * 100
        if dens == "xxxhdpi":
            worst = max(worst, maxr)
        print(f"{dens}/ic_launcher_{kind}.png{'':<12s} {w}x{h:<4d} {maxr:8.1f} "
              f"{over36:6.2f}% {over33:6.2f}%")

print()
print(f"worst-case max ink radius @xxxhdpi = {worst:.1f} dp")
print(f"  real circular mask radius = {R_CIRCLE_MASK:.0f} dp  -> "
      f"{'OK' if worst <= R_CIRCLE_MASK else 'CLIPPED at the corners'}")
print(f"  guaranteed safe radius    = {R_GUARANTEE:.0f} dp  -> "
      f"{'OK' if worst <= R_GUARANTEE else 'outside the guarantee'}")
if worst > R_GUARANTEE:
    print(f"  scale that would bring ALL ink inside the {R_GUARANTEE:.0f}dp circle = "
          f"{R_GUARANTEE / worst:.3f}")
if worst > R_CIRCLE_MASK:
    print(f"  scale that would bring ALL ink inside the {R_CIRCLE_MASK:.0f}dp circle = "
          f"{R_CIRCLE_MASK / worst:.3f}")
