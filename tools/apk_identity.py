#!/usr/bin/env python3
"""Print the identity of the newest APK under app/build/outputs/apk.

This is the mandatory step 0 of any release verification: prove that the file
you are about to verify is the one that was just built. Two failure modes are
both silent and both produce a cheerful "everything is fine":

  * a stale file from an earlier build with the same name is picked up
  * the script is pointed at the wrong path

So: never hard-code the artifact name. Globs it, sorts by mtime, and prints
name + bytes + mtime + sha256 together, so the numbers can be compared against
the build log and against the release asset.

Usage:
    python tools/apk_identity.py [--expect-bytes N] [--expect-sha256 HEX]
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(__file__).resolve().parent.parent
APK_DIR = REPO / "app" / "build" / "outputs" / "apk"


def human(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n:,} B  ({n / 1024 / 1024:.2f} MiB)"
    return f"{n:,} B"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--expect-bytes", type=int)
    ap.add_argument("--expect-sha256")
    args = ap.parse_args()

    if not APK_DIR.exists():
        raise SystemExit(f"no such directory: {APK_DIR}")

    apks = sorted(APK_DIR.rglob("*.apk"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not apks:
        raise SystemExit(f"no APK found under {APK_DIR}")

    print(f"{len(apks)} APK(s) under {APK_DIR.relative_to(REPO)}\n")
    ok = True
    for p in apks:
        st = p.stat()
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        print(f"  {p.name}")
        print(f"    path     : {p.relative_to(REPO)}")
        print(f"    bytes    : {human(st.st_size)}")
        print(f"    mtime    : {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))}")
        print(f"    sha256   : {digest}")
        if args.expect_bytes is not None:
            match = st.st_size == args.expect_bytes
            ok &= match
            print(f"    vs expect bytes  : {'MATCH' if match else 'MISMATCH'}")
        if args.expect_sha256:
            match = digest == args.expect_sha256
            ok &= match
            print(f"    vs expect sha256 : {'MATCH' if match else 'MISMATCH'}")
        print()

    if args.expect_bytes or args.expect_sha256:
        print("IDENTITY OK" if ok else "IDENTITY MISMATCH")
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
