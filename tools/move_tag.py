#!/usr/bin/env python3
"""Re-point a published release tag at a newer commit.

Why this exists
---------------
GitHub serves "Source code (zip)" / "(tar.gz)" on every release, but those are
NOT release assets - they are generated on demand from the *tag*. So replacing
a binary with `gh release upload --clobber` leaves the release internally
inconsistent: the APK is the new build, the source archive is the old tree.
The only way to refresh the auto-generated archives is to move the tag.

Safety rules baked in, because moving a published tag is a public and
effectively irreversible act:

  * the target must already be reachable from origin/main (never tag an
    unmerged or stale commit)
  * the working tree must be clean
  * the ref is force-UPDATED, never deleted - deleting the tag would detach
    the GitHub release from it
  * it prints the old and new commit side by side and requires --yes

Usage
-----
    python tools/move_tag.py v1.0.0 --yes            # -> origin/main HEAD
    python tools/move_tag.py v1.0.0 --to <sha> --yes
"""

from __future__ import annotations

import argparse
import base64
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = r"I:\mar\markdown-helper"
GH = r"C:\Users\Administrator\.local\bin\gh.exe"
GIT = r"C:\Program Files\Git\cmd\git.exe"


def run(args, env=None):
    r = subprocess.run(args, cwd=REPO, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tag")
    ap.add_argument("--to", default="origin/main", help="commit to point the tag at")
    ap.add_argument("--yes", action="store_true", help="actually push")
    args = ap.parse_args()

    rc, out, err = run([GH, "auth", "token"])
    token = out
    if rc != 0 or not token:
        raise SystemExit(f"gh auth token failed: {err}")
    print(f"gh auth token      : OK (len={len(token)})")

    rc, out, err = run([GIT, "fetch", "origin", "main", "--tags"])
    print(f"fetch              : rc={rc} {err[:200]}")

    rc, dirty, _ = run([GIT, "status", "--porcelain"])
    if dirty:
        raise SystemExit(f"working tree is not clean:\n{dirty}")

    rc, new_sha, err = run([GIT, "rev-parse", args.to])
    if rc != 0 or not new_sha:
        raise SystemExit(f"cannot resolve {args.to}: {err}")
    new_sha = new_sha.split()[0]

    # The target must be part of main's history, otherwise the tag would point
    # at something that was never merged.
    rc, _, _ = run([GIT, "merge-base", "--is-ancestor", new_sha, "origin/main"])
    if rc != 0:
        raise SystemExit(f"{new_sha[:8]} is not an ancestor of origin/main - refusing")

    rc, old_sha, _ = run([GIT, "rev-parse", f"refs/tags/{args.tag}"])
    if rc != 0:
        rc, old_sha, _ = run(["git", "ls-remote", "--tags", "origin", args.tag])
        old_sha = old_sha.split()[0] if old_sha else "(none)"
    else:
        old_sha = old_sha.split()[0]

    print()
    print(f"tag                : {args.tag}")
    print(f"  now points at    : {old_sha[:8]}  {run([GIT, 'log', '--oneline', '-1', old_sha])[1]}")
    print(f"  will point at    : {new_sha[:8]}  {run([GIT, 'log', '--oneline', '-1', new_sha])[1]}")
    rc, ahead, _ = run([GIT, "rev-list", "--count", f"{old_sha}..{new_sha}"])
    print(f"  commits gained   : {ahead}")

    if old_sha == new_sha:
        print("\nalready up to date - nothing to do")
        return

    if not args.yes:
        print("\n--yes not given: dry run only, nothing pushed")
        return

    b64 = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"

    # Move the LOCAL ref first. `git push <ref>` pushes whatever the local ref
    # currently points at, so skipping this makes the push a no-op that still
    # exits 0 and still reports "Everything up-to-date" - the remote tag stays
    # put and the only signal is the verification at the end of this script.
    rc, out, err = run([GIT, "update-ref", f"refs/tags/{args.tag}", new_sha])
    if rc != 0:
        raise SystemExit(f"could not move the local tag: {err}")
    rc, local_now, _ = run([GIT, "rev-parse", f"refs/tags/{args.tag}"])
    print(f"\nlocal tag moved to : {local_now[:8]}")
    if local_now != new_sha:
        raise SystemExit("local tag did not move - refusing to push")

    # Force-UPDATE the ref. Never delete it: deleting would detach the GitHub
    # release, and the release is the thing we are trying to keep coherent.
    rc, out, err = run([
        GIT, "-c", "credential.helper=",
        "-c", f"http.extraHeader=Authorization: Basic {b64}",
        "push", "--force", "origin", f"refs/tags/{args.tag}:refs/tags/{args.tag}",
    ], env=env)
    print(f"\npush --force       : rc={rc}")
    if out:
        print("stdout:", out[:600])
    if err:
        print("stderr:", err[:600])

    rc, after, _ = run(["git", "ls-remote", "--tags", "origin", args.tag])
    after = after.split()[0] if after else "(none)"
    print(f"remote tag now     : {after[:8]}")
    if after == new_sha:
        print("CONSISTENT")
    else:
        # Non-zero exit on purpose: a silent failure here leaves the release
        # shipping a binary and a source tree from different commits.
        print(f"MISMATCH - remote is {after[:8]}, expected {new_sha[:8]}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
