"""Generate the full launcher-icon set for MarkdownH from the design JPEG.

Mapping rule (this is what keeps the artwork inside the adaptive-icon safe zone):
the design's beige rounded square  ==  the full 108x108dp adaptive canvas.

Sizing is NOT derived from the "72x72dp safe zone" alone - that is only the bounding
box of the mask, and its four corners lie outside a circular mask. The binding
constraint is the CIRCLE. Per the official design guidance any legal mask is convex
with at least 33dp from centre to edge, so the region guaranteed to survive every
mask is a 66dp-diameter circle (33dp radius). AOSP agrees:
AdaptiveIconDrawable.SAFEZONE_SCALE = 66f/72f.

The document glyph has square corners, so its MAX INK RADIUS is what must stay under
33dp - the bounding box diagonal is the real limit, i.e. bbox <= 66/sqrt(2) = 46.7dp.
Measured before the fix: 56dp bbox -> 39.1dp max radius (foreground) and 62dp bbox ->
43.3dp max radius (monochrome), both of which a circular-mask launcher really clips
(the overflow is solid ink, it does not move when the alpha threshold is raised).
Hence DOC_DP = 46dp, which measures ~32.3dp.

Outputs per density (drawable-{mdpi,hdpi,xhdpi,xxhdpi,xxxhdpi}/):
  ic_launcher_background.png   108dp, full bleed, the design's own vertical gradient
  ic_launcher_foreground.png   108dp, document on transparent, bbox = 46dp
  ic_launcher_monochrome.png   108dp, silhouette with the MD glyphs knocked out at 46dp
  ic_launcher.png              legacy icon (48dp x scale), beige rounded square
  ic_launcher_{todo,quicknote,linkbox,share_into}.png   copies of the legacy icon
And res/ic_launcher-web.png at 512x512 for the store listing.
"""
import argparse, sys, shutil, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = r"I:\mar\安卓Markdown编辑器APP图标设计方案.jpeg"
DENSITIES = {"mdpi": 1.0, "hdpi": 1.5, "xhdpi": 2.0, "xxhdpi": 3.0, "xxxhdpi": 4.0}
VARIANTS = ["todo", "quicknote", "linkbox", "share_into"]
WEB_ICON = 512
# The design places the document at 63% of the square (= 68dp of the 108dp canvas), which
# every launcher mask clips badly. 46dp keeps the whole glyph - corners included - inside
# the 66dp circle that any convex mask is required to show.
FG_DOC_DP = 46.0
# The monochrome layer is the same size as the foreground. It used to be rendered larger
# (62dp) for 24dp themed-icon legibility, but that pushed its corners to a 43.3dp radius,
# i.e. straight through the 33dp guarantee. Compliance wins over the extra few dp.
MONO_DOC_DP = 46.0
CANVAS_DP = 108.0


# ---------------------------------------------------------------- source

def load_source():
    im = Image.open(SRC).convert("RGB")
    a = np.asarray(im).astype(np.float32)
    beige = beige_mask(a)
    ys, xs = np.where(beige)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = max(x1 - x0, y1 - y0) + 1
    h = side // 2
    box = (int(round(cx - h)), int(round(cy - h)), int(round(cx + h)), int(round(cy + h)))
    sq = np.asarray(im.crop(box)).astype(np.float32)
    print(f"  source {im.size}   square {side}px  box={box}")
    # watermark must stay outside this box
    out = np.ones(a.shape[:2], bool)
    out[box[1]:box[3] + 1, box[0]:box[2] + 1] = False
    stray = int(((a.mean(axis=2) < 240) & out).sum())
    print(f"  pixels outside the square (watermark etc.) = {stray}  -> excluded by the crop")
    return im, sq, beige_mask(sq)


def beige_mask(a):
    R, G, B = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    return (R > G) & (G > B) & ((R - B) > 30) & (a.mean(axis=2) < 245)


def row_beige(sq, m):
    """Per-row background colour, median over the pure-background strips of that row.

    Two traps avoided here: sampling a band blindly picks up the white canvas in the
    rounded corners, and masking only on "beige-ish" picks up the document's drop shadow
    (which is a dark beige). The document spans 18.5%..81.5% of the square, so the outer
    15% strips are guaranteed to be pure background; rows with no data at all (inside the
    corner radius) are interpolated.
    """
    h, w = m.shape
    band = max(4, int(w * 0.15))
    sel = np.zeros_like(m)
    sel[:, :band] = True
    sel[:, w - band:] = True
    sel &= m
    prof = np.full((h, 3), np.nan, np.float32)
    for y in range(h):
        row = sq[y][sel[y]]
        if len(row) >= 5:
            prof[y] = np.median(row, axis=0)
    good = ~np.isnan(prof[:, 0])
    if good.sum() < 2:
        raise SystemExit("could not estimate the background colour")
    idx = np.arange(h)
    for c in range(3):
        prof[:, c] = np.interp(idx, idx[good], prof[good, c])
    # smooth away any residual shadow/vignette contamination so the gradient stays clean
    win = max(3, (h // 12) | 1)
    for c in range(3):
        col = Image.fromarray(prof[:, c].reshape(h, 1).astype(np.uint8), "L")
        col = col.filter(ImageFilter.MedianFilter(size=win)).filter(ImageFilter.GaussianBlur(win / 6.0))
        prof[:, c] = np.asarray(col, dtype=np.float32).reshape(h)
    return prof


def measure_radius(sq, m):
    """Corner radius of the design's rounded square, relative to the side length.

    For a rounded rect the left edge starts `r` px in from the border at y=0 and reaches
    x=0 at y=r, so both measurements estimate the same r.
    """
    h, w = m.shape
    xmin = np.array([np.where(m[y])[0].min() if m[y].any() else w for y in range(h)])
    r_top = float(xmin[0])
    hits = np.where(xmin <= 1)[0]
    r_side = float(hits[0]) if len(hits) else r_top
    return float(np.clip((r_top + r_side) / 2 / w, 0.05, 0.45))


def doc_layers(sq, m, prof, lo=14.0, hi=30.0):
    """Document RGBA + monochrome alpha, both in square-relative coordinates."""
    bg = prof[:, None, :]
    d = np.abs(sq - bg).max(axis=2)
    alpha = np.clip((d - lo) / (hi - lo), 0.0, 1.0)

    h, w = alpha.shape
    inset = max(int(w * 0.18), 8)
    keep = np.zeros_like(alpha)
    keep[inset:h - inset, inset:w - inset] = 1.0     # ignore the rounded-away white corners
    alpha *= keep

    ys, xs = np.where(alpha > 0.35)
    box = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))
    print(f"  document bbox {box[1]-box[0]+1}x{box[3]-box[2]+1}px "
          f"({(box[1]-box[0]+1)/w:.1%} of the square)")

    doc = Image.fromarray(np.dstack([np.clip(sq, 0, 255).astype(np.uint8),
                                     (alpha * 255).astype(np.uint8)]), "RGBA")

    # monochrome: a single-colour silhouette. Only genuinely dark *neutral* ink is knocked
    # out (the MD glyphs); the thin grey rules and the blue block stay filled, otherwise
    # the mark turns to noise at 24dp in the themed-icon tray. The saturation factor keeps
    # the blue block filled even though its luminance is low.
    lum = sq.mean(axis=2)
    sat = sq.max(axis=2) - sq.min(axis=2)
    ink = np.clip((140.0 - lum) / 40.0, 0.0, 1.0)
    ink *= np.clip((60.0 - sat) / 60.0, 0.0, 1.0)
    mono = np.clip(alpha * (1.0 - ink), 0.0, 1.0)
    return doc, mono, box


# ---------------------------------------------------------------- geometry

def place(src, canvas_px, box, size_dp):
    """Centre `src` (cropped to `box`) on a canvas_px square, scaled so its bbox is size_dp dp.

    canvas_px always represents the full 108dp canvas, so size_dp is directly comparable
    with the 72x72dp safe zone.
    """
    x0, x1, y0, y1 = box
    scale = (canvas_px * size_dp / CANVAS_DP) / max(x1 - x0 + 1, y1 - y0 + 1)
    dw = max(1, int(round((x1 - x0 + 1) * scale)))
    dh = max(1, int(round((y1 - y0 + 1) * scale)))
    layer = src.crop((x0, y0, x1 + 1, y1 + 1)).resize((dw, dh), Image.LANCZOS)
    canvas = Image.new("RGBA" if src.mode == "RGBA" else "L", (canvas_px, canvas_px),
                       (0, 0, 0, 0) if src.mode == "RGBA" else 0)
    canvas.paste(layer, ((canvas_px - dw) // 2, (canvas_px - dh) // 2))
    return canvas


def rounded_alpha(size_px, radius_frac, ss=4):
    S = size_px * ss
    m = Image.new("L", (S, S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, S - 1, S - 1],
                                        radius=int(round(S * radius_frac)), fill=255)
    return np.asarray(m.resize((size_px, size_px), Image.LANCZOS)).astype(np.float32) / 255.0


def gradient_bg(prof, canvas_px):
    """Full-bleed background: the design's own vertical colour profile, extended horizontally."""
    p = prof / 255.0
    h = p.shape[0]
    ys = np.linspace(0, h - 1, canvas_px)
    lo = np.floor(ys).astype(int)
    hi = np.minimum(lo + 1, h - 1)
    t = (ys - lo)[:, None]
    rows = p[lo] * (1 - t) + p[hi] * t                       # canvas_px x 3
    img = np.repeat(rows[:, None, :], canvas_px, axis=1)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")


def legacy_icon(sq, px, radius_frac):
    base = Image.fromarray(np.clip(sq, 0, 255).astype(np.uint8), "RGB").resize((px, px), Image.LANCZOS)
    base = base.convert("RGBA")
    base.putalpha(Image.fromarray((rounded_alpha(px, radius_frac) * 255).astype(np.uint8), "L"))
    return base


# ---------------------------------------------------------------- main

def main():
    global SRC
    ap = argparse.ArgumentParser()
    ap.add_argument("--res", required=True,
                    help="output dir for res/, e.g. <stage>/res")
    ap.add_argument("--preview", required=True,
                    help="output dir for the reference sheets, e.g. <stage>/preview")
    ap.add_argument("--src", default=SRC,
                    help=f"the design JPEG (default: {SRC})")
    args = ap.parse_args()
    SRC = args.src
    res = pathlib.Path(args.res)
    prev = pathlib.Path(args.preview)
    prev.mkdir(parents=True, exist_ok=True)
    if not pathlib.Path(SRC).exists():
        raise SystemExit(f"design file not found: {SRC}\n"
                         f"pass --src <path> to point at it")

    print("[1] source")
    _, sq, mask = load_source()
    sidelen = sq.shape[0]
    prof = row_beige(sq, mask)

    print("[2] document / monochrome")
    doc, mono, dbox = doc_layers(sq, mask, prof)

    print("[3] background profile")
    p = prof.astype(int)
    radius = measure_radius(sq, mask)
    print(f"  top={tuple(p[0])} mid={tuple(p[sidelen//2])} bottom={tuple(p[-1])}")
    print(f"  corner radius = {radius:.3f} of the side")

    print("[4] per-density output")
    for name, scale in DENSITIES.items():
        outdir = res / f"drawable-{name}"
        outdir.mkdir(parents=True, exist_ok=True)
        canvas = int(round(CANVAS_DP * scale))
        legacy_px = int(round(48 * scale))

        gradient_bg(prof, canvas).save(outdir / "ic_launcher_background.png")
        place(doc, canvas, dbox, FG_DOC_DP).save(outdir / "ic_launcher_foreground.png")

        mo = place(Image.fromarray((mono * 255).astype(np.uint8), "L"), canvas, dbox, MONO_DOC_DP)
        mon = Image.new("RGBA", (canvas, canvas), (255, 255, 255, 0))
        mon.putalpha(mo)
        mon.save(outdir / "ic_launcher_monochrome.png")

        leg = legacy_icon(sq, legacy_px, radius)
        leg.save(outdir / "ic_launcher.png")
        for v in VARIANTS:
            leg.save(outdir / f"ic_launcher_{v}.png")
        print(f"  {name:8s} canvas {canvas:3d}px  legacy {legacy_px:3d}px  "
              f"+ {len(VARIANTS)} variants")

    web = Image.new("RGB", (WEB_ICON, WEB_ICON), (255, 255, 255))
    web.paste(legacy_icon(sq, WEB_ICON, radius), (0, 0), legacy_icon(sq, WEB_ICON, radius))
    web.save(res.parent / "ic_launcher-web.png")
    print(f"[5] ic_launcher-web.png {WEB_ICON}x{WEB_ICON}")

    # ---- preview sheet: foreground / legacy / monochrome at xxxhdpi, guides = safe zone ----
    canvas = int(CANVAS_DP * DENSITIES["xxxhdpi"])
    fg = place(doc, canvas, dbox, FG_DOC_DP)
    moimg = Image.new("RGBA", (canvas, canvas), (255, 255, 255, 0))
    moimg.putalpha(place(Image.fromarray((mono * 255).astype(np.uint8), "L"), canvas, dbox, MONO_DOC_DP))
    bg = gradient_bg(prof, canvas).convert("RGBA")
    leg = legacy_icon(sq, canvas, radius)

    order = [("bg", bg), ("fg", fg), ("composited", Image.alpha_composite(bg.copy(), fg)),
             ("legacy", leg), ("mono", moimg)]
    gap = 24
    sheet = Image.new("RGBA", (len(order) * canvas + (len(order) - 1) * gap, canvas), (32, 32, 32, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (tag, img) in enumerate(order):
        ox = i * (canvas + gap)
        sheet.alpha_composite(img, (ox, 0))
        img.save(prev / f"{tag}.png")
        dr.rectangle([ox + 72, 72, ox + 360, 360], outline=(255, 0, 0, 255), width=2)     # 72dp safe square
        dr.ellipse([ox + 84, 84, ox + 348, 348], outline=(0, 200, 255, 255), width=2)     # 66dp circle
    sheet.convert("RGB").save(prev / "sheet.png")
    print(f"[6] previews -> {prev}   order: {' | '.join(t for t, _ in order)}")


if __name__ == "__main__":
    main()
