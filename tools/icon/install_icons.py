"""Install the generated launcher-icon set into the Markdown Helper project.

Run gen_icons.py first; this script only copies/deletes, so it can be re-run safely
(it is idempotent and always reports what it changed).

What it touches:
  app/src/main/res/drawable-{m,h,xh,xxh,xxx}dpi/ic_launcher.png            legacy icon
  app/src/main/res/drawable-{...}dpi/ic_launcher_{todo,quicknote,linkbox,share_into}.png
  app/src/main/res/drawable-{...}dpi/ic_launcher_{background,foreground,monochrome}.png
  app/src/main/res/drawable-anydpi-v26/ic_launcher_{todo,quicknote,linkbox,share_into}.xml
  app/src/main/ic_launcher-web.png
  app/src/flavorAtest/res/drawable-{...}dpi/ic_launcher.png
and DELETES the superseded VectorDrawables (replaced by the PNG layers):
  app/src/main/res/drawable/ic_launcher_{background,foreground,monochrome}.xml
  app/src/main/res/drawable/ic_launcher_{todo,quicknote,linkbox,share_into}_{background,foreground}.xml
  app/src/flavorAtest/res/drawable/ic_launcher_foreground.xml
"""
import pathlib, shutil, sys, filecmp

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TOOLS = pathlib.Path(r"I:\mar\markdown-helper-tools\icon")
STAGE = TOOLS / "stage"
REPO = pathlib.Path(r"I:\mar\markdown-helper")
MAIN = REPO / "app" / "src" / "main"
DENSITIES = ["mdpi", "hdpi", "xhdpi", "xxhdpi", "xxxhdpi"]
LAYERS = ["ic_launcher_background", "ic_launcher_foreground", "ic_launcher_monochrome"]
LEGACY = ["ic_launcher", "ic_launcher_todo", "ic_launcher_quicknote",
          "ic_launcher_linkbox", "ic_launcher_share_into"]
VARIANTS = ["todo", "quicknote", "linkbox", "share_into"]

ADAPTIVE_XML = """<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@drawable/ic_launcher_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>
</adaptive-icon>
"""

copied, written, deleted = [], [], []


def copy(src: pathlib.Path, dst: pathlib.Path, tag: str):
    if not src.exists():
        raise SystemExit(f"MISSING in stage: {src}")
    dst.parent.mkdir(parents=True, exist_ok=True)
    same = dst.exists() and filecmp.cmp(src, dst, shallow=False)
    shutil.copy2(src, dst)
    copied.append((tag, dst, same))


def rm(path: pathlib.Path):
    if path.exists():
        path.unlink()
        deleted.append(path)


def main():
    print("=== install icon set ===")

    # 1. adaptive layers + legacy icons, all densities (main)
    for d in DENSITIES:
        sdir, tdir = STAGE / "res" / f"drawable-{d}", MAIN / "res" / f"drawable-{d}"
        for name in LAYERS:
            copy(sdir / f"{name}.png", tdir / f"{name}.png", f"main/{d}/{name}")
        for name in LEGACY:
            copy(sdir / f"{name}.png", tdir / f"{name}.png", f"main/{d}/{name}")

    # 2. the four variant adaptive icons now reuse the main layers
    for v in VARIANTS:
        p = MAIN / "res" / "drawable-anydpi-v26" / f"ic_launcher_{v}.xml"
        old = p.read_text(encoding="utf-8") if p.exists() else ""
        if old.replace("\r\n", "\n") != ADAPTIVE_XML:
            p.write_text(ADAPTIVE_XML, encoding="utf-8", newline="\n")
            written.append(p)

    # 3. the store / web icon
    copy(STAGE / "ic_launcher-web.png", MAIN / "ic_launcher-web.png", "main/ic_launcher-web")

    # 4. superseded vector drawables
    for name in LAYERS:
        rm(MAIN / "res" / "drawable" / f"{name}.xml")
    for v in VARIANTS:
        rm(MAIN / "res" / "drawable" / f"ic_launcher_{v}_background.xml")
        rm(MAIN / "res" / "drawable" / f"ic_launcher_{v}_foreground.xml")

    # 5. the test flavour ships its own legacy icons + a foreground vector override
    for d in DENSITIES:
        copy(STAGE / "res" / f"drawable-{d}" / "ic_launcher.png",
             REPO / "app" / "src" / "flavorAtest" / "res" / f"drawable-{d}" / "ic_launcher.png",
             f"test/{d}/ic_launcher")
    rm(REPO / "app" / "src" / "flavorAtest" / "res" / "drawable" / "ic_launcher_foreground.xml")

    # report
    print(f"\n[files copied]  {len(copied)}")
    fresh = [c for c in copied if not c[2]]
    print(f"  changed        {len(fresh)}")
    for tag, dst, same in copied[:3]:
        print(f"    e.g. {tag:34s} {'unchanged' if same else 'UPDATED'}"
              f"  {dst.stat().st_size:>10,} B")
    print(f"[xml rewritten] {len(written)}")
    for p in written:
        print(f"    {p.relative_to(REPO)}")
    print(f"[deleted]       {len(deleted)}")
    for p in deleted:
        print(f"    {p.relative_to(REPO)}")

    # sanity: nothing left behind that still names the old vectors
    leftovers = sorted(p.relative_to(REPO) for p in MAIN.rglob("res/drawable/ic_launcher*.xml"))
    print(f"\n[check] remaining ic_launcher*.xml under res/drawable/ (header/other) = {leftovers}")


if __name__ == "__main__":
    main()
