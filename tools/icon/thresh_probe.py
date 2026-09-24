import sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import numpy as np
from PIL import Image
REPO = pathlib.Path(r"I:/mar/markdown-helper")
CANVAS_DP = 108.0
print(f"{'layer':26s} " + " ".join(f"a>{t:<5}" for t in (0.03, 0.10, 0.25, 0.50, 0.75)))
print("-" * 76)
for kind in ("foreground", "monochrome"):
    p = REPO / f"app/src/main/res/drawable-xxxhdpi/ic_launcher_{kind}.png"
    a = np.asarray(Image.open(p).convert("RGBA"))[:, :, 3].astype(np.float32) / 255.0
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rad = np.sqrt((yy - (h - 1) / 2.0) ** 2 + (xx - (w - 1) / 2.0) ** 2) * (CANVAS_DP / w)
    row = []
    for t in (0.03, 0.10, 0.25, 0.50, 0.75):
        m = a > t
        row.append(f"{rad[m].max():6.1f}" if m.any() else "   n/a")
    print(f"{kind:26s} " + " ".join(row))
print()
print("read: if the max radius barely moves as the threshold rises, the overflow is REAL ink")
print("      (a sharp corner), not a soft anti-aliased fringe.")
