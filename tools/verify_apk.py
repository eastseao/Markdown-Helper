#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Release verification for MarkdownH v1.0.0 (Request H).

Design notes - why it is written this way:
  * The APK path is NEVER trusted from memory. AGP derives the file name from
    applicationId + versionCode + versionName + flavor + buildType, so a stale
    APK is the classic false positive. STEP 0 globs, sorts by mtime, prints
    name/size/mtime and copies the winner to the release asset name.
  * This box has a flaky console encoding (GBK default), so stdout is
    reconfigured to UTF-8 first and nothing is written to the console by a
    shell redirect.
  * `markor` is only REPORTED for binary blobs, and ASSERTED only for
    res/ + assets/, because the upstream fork legitimately keeps references
    (e.g. licence/attribution text) that are not user-visible strings.

Usage:  python verify_apk.py
"""

import datetime
import hashlib
import io
import pathlib
import re
import shutil
import subprocess
import sys
import zipfile

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(r"I:\mar\markdown-helper")
BUILD_OUT = REPO / "app" / "build" / "outputs" / "apk" / "flavorDefault" / "debug"
RELEASE_ASSET = REPO / "MarkdownHelper-v1.0.0.apk"
EXT = pathlib.Path(r"I:\mar\markdown-helper-tools\apkcheck-verify")

BUILD_TOOLS = pathlib.Path(r"I:\应用开发\Android\Sdk\build-tools\35.0.0")

EXPECT_PACKAGE = "io.github.eastseao.markdownhelper"
EXPECT_LABELS = {"MarkdownH"}          # application-label / app_name
EXPECT_VERSION_NAME = "1.0.0"

CANVAS_DP = 108.0
SAFE_DP = 72.0
R_MASK_DP = 36.0     # circle mask actually exposes 108 * 2/3 = 72dp across -> r=36dp
R_GUARANTEE_DP = 33.0  # every legal convex mask must show the 66dp circle -> r=33dp
DENSITIES = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]

CHECKS = []


def hr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


def claim(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    return ok


def tool(name):
    for ext in (".exe", ".bat", ""):
        c = BUILD_TOOLS / f"{name}{ext}"
        if c.exists():
            return str(c)
    return None


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    return (p.stdout or "") + (p.stderr or "")


# --------------------------------------------------------------------- STEP 0
hr("STEP 0 - artifact identity (glob + mtime, never a remembered path)")
cands = sorted(BUILD_OUT.glob("*.apk"), key=lambda p: p.stat().st_mtime)
if not cands:
    sys.exit(f"FATAL: no APK in {BUILD_OUT} - the build did not produce one")
for p in cands:
    s = p.stat()
    ts = datetime.datetime.fromtimestamp(s.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    print(f"  candidate : {p.name}")
    print(f"              {s.st_size:,} B   mtime={ts}")
NEW = cands[-1]
st = NEW.stat()
print(f"\n  CHOSEN    : {NEW.name}")
print(f"  size      : {st.st_size:,} bytes ({st.st_size / 1048576:.2f} MiB)")
shutil.copy2(NEW, RELEASE_ASSET)
assert RELEASE_ASSET.stat().st_size == st.st_size, "size changed during copy!"
data = RELEASE_ASSET.read_bytes()
print(f"  -> copied to release asset: {RELEASE_ASSET.name}")
print(f"  md5     = {hashlib.md5(data).hexdigest()}")
print(f"  sha256  = {hashlib.sha256(data).hexdigest()}")

# ------------------------------------------------------------ zip / padding
hr("STEP 0b - zip hygiene (a clean build has no alignment holes)")
with zipfile.ZipFile(RELEASE_ASSET) as z:
    infos = z.infolist()
    names = z.namelist()
    comp = sum(i.compress_size for i in infos)
    nlen = sum(len(i.filename.encode("utf-8")) for i in infos)
    end = max(i.header_offset + 30 + len(i.filename.encode("utf-8")) + i.compress_size
              for i in infos)
    pad = end - comp - 30 * len(infos) - nlen
    print(f"  entries = {len(infos)}")
    print(f"  padding = {pad:,} B")
    claim("no alignment padding (clean build)", pad < 20000,
          "clean" if pad < 20000 else "INCREMENTAL build suspected")

# ------------------------------------------------------------------ badging
hr("STEP 1a - aapt dump badging")
aapt = tool("aapt")
aapt2 = tool("aapt2")
print(f"  aapt  = {aapt}")
print(f"  aapt2 = {aapt2}")
dump = run([aapt, "dump", "badging", str(RELEASE_ASSET)]) if aapt else ""
if not dump and aapt2:
    dump = run([aapt2, "dump", "badging", str(RELEASE_ASSET)])
for line in dump.splitlines():
    if line.startswith(("package:", "sdkVersion", "targetSdkVersion",
                        "application-label", "application-icon",
                        "launchable-activity", "application: ")):
        print("  " + line)

hr("STEP 1b - identity assertions")
pkg = re.search(r"^package: name='([^']+)'", dump, re.M)
ver = re.search(r"^package:.*versionName='([^']*)'", dump, re.M)
vc = re.search(r"^package:.*versionCode='([^']*)'", dump, re.M)
labels = sorted({ln.split(":", 1)[1].strip().strip("'")
                 for ln in dump.splitlines() if ln.startswith("application-label")})
claim(f"package == {EXPECT_PACKAGE}", bool(pkg) and pkg.group(1) == EXPECT_PACKAGE,
      pkg.group(1) if pkg else "n/a")
claim(f"versionName == {EXPECT_VERSION_NAME}",
      bool(ver) and ver.group(1) == EXPECT_VERSION_NAME, ver.group(1) if ver else "n/a")
print(f"  versionCode = {vc.group(1) if vc else 'n/a'}")
claim(f"application-label == {sorted(EXPECT_LABELS)}", set(labels) == EXPECT_LABELS,
      f"found {labels}")
# the brand rename must not leave the old name in any locale label
claim("no 'Markdown Helper' label left", not any("Markdown Helper" in l for l in labels),
      f"{labels}")

# --------------------------------------------------------------- extraction
hr("STEP 1c - unpack for content checks")
if EXT.exists():
    shutil.rmtree(EXT, ignore_errors=True)
EXT.mkdir(parents=True)
with zipfile.ZipFile(RELEASE_ASSET) as z:
    z.extractall(EXT)
print(f"  unpacked {len(names)} entries -> {EXT}")

hr("STEP 1d - packaged icon inventory")
icons = sorted(n for n in names if "ic_launcher" in n)
for n in icons:
    print("  " + n)
print(f"  total ic_launcher* entries = {len(icons)}")
claim("adaptive icon XML present",
      any(n.startswith("res/drawable-anydpi-v26/ic_launcher") for n in icons))
for d in DENSITIES:
    # AGP rewrites `drawable-mdpi` to `drawable-mdpi-v4` inside the APK, so match the
    # version qualifier optionally. Getting this wrong makes the check silently vacuous.
    pat = re.compile(rf"^res/drawable-{d}(-v\d+)?/ic_launcher(_[a-z_]+)?\.png$")
    claim(f"legacy raster @{d}", any(pat.match(n) for n in icons))
claim("monochrome layer packaged (Android 13+ themed icons)",
      any(re.search(r"/ic_launcher_monochrome\.png$", n) for n in icons))

# --------------------------------------------------------------- safe zone
hr("STEP 1e - safe-zone audit of the packaged foreground / monochrome layers")
try:
    import numpy as np
    from PIL import Image
    HAVE_PIL = True
except Exception as exc:
    HAVE_PIL = False
    print(f"  PIL/numpy unavailable ({exc}) - skipped")


def packaged(*parts):
    """Resolve a resource name to its real in-APK path, tolerating the -vNN qualifier."""
    for n in names:
        if all(p in n for p in parts):
            return n
    return None


def geometry(apk_path, label):
    """The REAL acceptance test for a launcher layer.

    A bounding-box test against the 72dp square is not enough: the corners of a
    square-ish glyph lie outside a circular mask even when the box fits the square.
    What matters is the distance from the canvas centre to the furthest inked
    pixel, compared against
        36dp - the radius the stock circular mask actually exposes, and
        33dp - the radius every legal convex mask must expose (the 66dp circle).
    """
    im = Image.open(EXT / apk_path).convert("RGBA")
    a = np.asarray(im)[:, :, 3].astype(np.float32) / 255.0
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    rad = np.sqrt((yy - (h - 1) / 2.0) ** 2 + (xx - (w - 1) / 2.0) ** 2) * (CANVAS_DP / w)
    m = a > 0.5                       # solid ink only - ignore the AA fringe
    if not m.any():
        return claim(f"{label} non-empty", False, "alpha channel all zero")
    maxr = float(rad[m].max())
    over33 = float((rad[m] > R_GUARANTEE_DP).mean()) * 100
    print(f"    {w}x{h}px  max ink radius = {maxr:.1f} dp   "
          f"(mask r={R_MASK_DP:.0f}dp, guarantee r={R_GUARANTEE_DP:.0f}dp)   "
          f"{over33:.2f}% of ink outside the guarantee")
    claim(f"{label} inside the 72dp circle mask (r=36dp)", maxr <= R_MASK_DP)
    return claim(f"{label} inside the 66dp guarantee (r=33dp)", maxr <= R_GUARANTEE_DP)


n_geom = 0
if HAVE_PIL:
    for d in ("xxxhdpi", "xxhdpi", "xhdpi"):
        for kind in ("ic_launcher_foreground", "ic_launcher_monochrome"):
            p = packaged(f"drawable-{d}", f"{kind}.png")
            if p:
                geometry(p, f"{kind}@{d}")
                n_geom += 1
claim("safe-zone audit actually ran", n_geom >= 4,
      f"{n_geom} layers measured (0 would mean the check silently did nothing)")

# --------------------------------------------------------- residue / brand
hr("STEP 1f - brand residue")
res_hits, blob_hits = [], []
for p in EXT.rglob("*"):
    if not p.is_file():
        continue
    try:
        low = p.read_bytes().lower()
    except Exception:
        continue
    rel = str(p.relative_to(EXT)).replace("\\", "/")
    if b"markor" in low:
        (res_hits if rel.startswith(("res/", "assets/")) else blob_hits).append(
            (rel, low.count(b"markor")))
print(f"  'markor' inside res/ or assets/  = {len(res_hits)}")
for rel, c in res_hits[:15]:
    print(f"      {c:3d}x {rel}")
print(f"  'markor' in other blobs (dex/arsc/…) = {len(blob_hits)}")
for rel, c in sorted(blob_hits, key=lambda t: -t[1])[:10]:
    print(f"      {c:3d}x {rel}")
claim("no 'markor' in any compiled resource or asset", not res_hits)
print(f"  raw byte count in the APK = {data.lower().count(b'markor')}")

arsc = (EXT / "resources.arsc")
if arsc.exists():
    blob = arsc.read_bytes()
    old = blob.count(b"Markdown Helper")
    print(f"\n  'Markdown Helper' occurrences in resources.arsc = {old}")
    claim("old brand name gone from compiled strings", old == 0)

# ----------------------------------------------------------- manifest checks
hr("STEP 1g - packaged manifest: IntroActivity / walkthrough removed")
if aapt2:
    tree = run([aapt2, "dump", "xmltree", "--file", "AndroidManifest.xml",
                str(RELEASE_ASSET)])
    n_intro = tree.lower().count("introactivity")
    print(f"  'IntroActivity' occurrences in packaged manifest = {n_intro}")
    claim("IntroActivity not declared", n_intro == 0)
    for line in tree.splitlines():
        s = line.strip()
        if s.startswith("A: http://schemas.android.com/apk/res/android:name") and "activity" in s.lower():
            print("   ", s[:140])
    n_appintro = tree.lower().count("appintro")
    print(f"  'appintro' occurrences = {n_appintro}")
    claim("AppIntro library not declared", n_appintro == 0)

# intro drawables (the walkthrough screenshots) must be gone
jpgs = [n for n in names if re.search(r"screen\d", n, re.I)]
print(f"  screen*.jpg walkthrough images packaged = {len(jpgs)}  {jpgs}")
claim("walkthrough screenshots removed", not jpgs)

# ----------------------------------------------------------------- new code
hr("STEP 1h - the regrouping actually shipped")
GROUP_CLS = "io.github.eastseao.markdownhelper.activity.ExpandablePreferenceCategory"
xml_names = [n for n in names if "prefactions__more_information" in n]
print(f"  packaged path(s) = {xml_names}")
print("  note: aapt2 resource-versioning splits one source file into a base config plus a")
print("        higher-API config (here `()` and `(v22)`), so 2 entries are expected.")
print("  note: android:key is stored as a resolved @string reference, so the key text is NOT")
print("        visible in the XML dump - it is checked in resources.arsc further down.")
claim("more-information preference XML packaged", bool(xml_names))

# invariant: every element in the source must survive compilation. aapt2 xmltree indents
# element lines ("    E: Tag (line=N)"), and element names are printed as written (mixed
# unqualified Preference/CheckBoxPreference and fully-qualified androidx.* classes).
SRC_XML = REPO / "app/src/main/res/xml/prefactions__more_information.xml"
src_text = SRC_XML.read_text(encoding="utf-8")
src_elems = re.findall(r"<([A-Za-z][\w.]*)[\s/>]", src_text)
print(f"  source elements: {len(src_elems)}  "
      f"({len(set(src_elems))} distinct kinds)")
for xn in xml_names:
    dur = run([aapt2, "dump", "xmltree", "--file", xn, str(RELEASE_ASSET)]) if aapt2 else ""
    elems = re.findall(r"^ *E: (\S+)", dur, re.M)
    n_groups = elems.count(GROUP_CLS)
    print(f"  {xn}: {len(elems)} elements, {n_groups}x "
          f"{GROUP_CLS.rsplit('.', 1)[-1]}")
    claim(f"5 collapsible category elements in {xn}", n_groups == 5, f"found {n_groups}")
    claim(f"no element lost in {xn}", len(elems) == len(src_elems),
          f"shipped {len(elems)} vs source {len(src_elems)}")

# the 5 group keys are translatable=false ASCII, so they live in the string pool
# of resources.arsc - check both possible encodings rather than guess
if (EXT / "resources.arsc").exists():
    blob = (EXT / "resources.arsc").read_bytes()
    ids = ["general", "files", "editor", "view", "formats"]
    found = [i for i in ids
             if f"pref_key__more_group_{i}".encode() in blob
             or f"pref_key__more_group_{i}".encode("utf-16-le") in blob]
    print(f"  group key strings found in resources.arsc = {found}")
    claim("all 5 group key strings compiled", len(found) == 5, f"{len(found)}/5")

# ------------------------------------------------------------------ summary
hr("SUMMARY")
bad = [c for c in CHECKS if not c[1]]
print(f"  {len(CHECKS) - len(bad)}/{len(CHECKS)} checks passed")
for name, _ok, detail in bad:
    print(f"    FAIL: {name}   {detail}")
print(f"\n  release asset : {RELEASE_ASSET}")
print(f"  size          : {st.st_size:,} B ({st.st_size / 1048576:.2f} MiB)")
sys.exit(1 if bad else 0)
