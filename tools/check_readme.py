#!/usr/bin/env python3
"""Lint README.md / README.en.md / CHANGELOG.md for defects that only show up
once *both* consumers have parsed them.

Why a special check is needed at all:

    README.md and README.en.md are consumed twice.

      1. as the GitHub landing page  (GFM)
      2. as the in-app "project page"  (flexmark-java -> WebView)

    build.gradle copies them into the APK resources:

        copyReadmeDefault : README.en.md -> res/raw/readme.md
        copyReadmeChinese : README.md    -> res/raw-zh-rCN/readme.md

    So a file that renders correctly in a browser can still look wrong inside
    the app.  Every rule below encodes one such divergence.

The checks:

  R1  Soft line break between two full-width characters.
      CommonMark renders a soft break as a newline in the HTML, and the browser
      collapses it to a SPACE.  For Latin scripts that is what you want ("foo
      bar" may wrap anywhere); for Chinese it is wrong: a line wrapped after
      "，" or "。" produces a visible half-width space after the punctuation.
      Fix: join the two lines with nothing between them.

  R2  Table integrity.  A table row must be a single physical line - a blank
      line or a non-pipe line inside a table ends the table, and the rest is
      rendered as ordinary paragraph text.  Cell content that must break has
      to use <br>, never a literal newline.

  R3  HTML block integrity.  The centred header/footer is a raw <div> block.
      A CommonMark HTML block ends at the first blank line, so a blank line
      inside <div align="center"> would terminate the block and silently drop
      the centring for everything after it.  Also checks tag balance, since an
      unclosed <div> swallows the rest of the document into one HTML block.

  R4  In-repo relative links must resolve to files that really exist.

  R5  Every raw.githubusercontent.com URL must map onto a file in this repo -
      a root-relative /path/to/img.png is NOT valid on GitHub (it resolves
      against github.com, not the repository), and that mistake is invisible
      until someone opens the page.

Exit code 0 = clean, 1 = findings.  --fix repairs R1 in place.
"""

from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
RAW = "https://raw.githubusercontent.com/eastseao/Markdown-Helper/main/"

FILES = ["README.md", "README.en.md", "CHANGELOG.md"]


def is_wide(ch: str) -> bool:
    """True for characters that occupy a full em in East Asian typography.

    east_asian_width 'W' (wide) and 'F' (fullwidth) cover the CJK ideographs,
    the fullwidth punctuation block and fullwidth forms such as '｜'.  The
    'A' (ambiguous) class - middot, em dash, degree sign - is deliberately
    excluded: those are already surrounded by explicit spaces here.
    """
    return unicodedata.east_asian_width(ch) in ("W", "F")


def strip_prefix(line: str) -> str:
    """Drop blockquote / list markers so R1 can look at the real last char."""
    return re.sub(r"^[ \t]*(?:>[ \t]?|[-*+][ \t])*", "", line).rstrip()


def check_r1(text: str) -> list[tuple[int, int, str]]:
    """Return (line_no, next_line_no, text) for stray-space soft breaks."""
    lines = text.split("\n")
    hits = []
    for i in range(len(lines) - 1):
        a, b = strip_prefix(lines[i]), lines[i + 1].lstrip()
        if not a or not b:
            continue
        if lines[i].lstrip().startswith(("|", "#", "```")):
            continue
        if lines[i + 1].lstrip().startswith(("|", "#", "```")):
            continue
        # A file-embedded HTML block: line structure is authored on purpose.
        if a.endswith((">", "&")) or b.startswith("<"):
            continue
        if is_wide(a[-1]) and is_wide(b[0]):
            hits.append((i + 1, i + 2, f"...{a[-14:]}  /  {b[:14]}..."))
    return hits


def check_r2(text: str) -> list[str]:
    lines = text.split("\n")
    problems = []
    in_table = False
    for n, line in enumerate(lines, 1):
        s = line.rstrip()
        if s.lstrip().startswith("|"):
            if not s.endswith("|"):
                problems.append(f"line {n}: table row does not end with '|' -> {s[-30:]}")
            in_table = True
        elif in_table and s.strip():
            problems.append(
                f"line {n}: non-pipe line inside a table (the table ends here) -> {s[:40]}"
            )
            in_table = False
        else:
            in_table = False
    return problems


TAGS = ("div", "p", "sub", "b", "h1")


def check_r3(text: str) -> list[str]:
    problems = []
    for tag in TAGS:
        opened = len(re.findall(rf"<{tag}[\s>]", text))
        closed = len(re.findall(rf"</{tag}>", text))
        if opened != closed:
            problems.append(f"<{tag}> unbalanced: {opened} opened, {closed} closed")

    # A blank line inside an outer <div> splits it into two HTML blocks.
    depth = 0
    for n, line in enumerate(text.split("\n"), 1):
        if not line.strip() and depth > 0:
            problems.append(f"line {n}: blank line inside an open <div> - the HTML block ends here")
        opens = len(re.findall(r"<div[\s>]", line))
        closes = len(re.findall(r"</div>", line))
        depth = max(0, depth + opens - closes)
    return problems


def check_r4(text: str) -> list[str]:
    problems = []
    for m in re.finditer(r"\]\(([^)\s]+)\)", text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = target.split("#", 1)[0].split("?", 1)[0]
        if not path:
            continue
        if not (REPO / path).exists():
            problems.append(f"relative link does not resolve: {target}")
    return problems


def check_r5(text: str) -> list[str]:
    problems = []
    for m in re.finditer(r'(?:src|href)="https://raw\.githubusercontent\.com/([^"]+)"', text):
        rest = m.group(1)
        # .../<owner>/<repo>/<branch>/<path>
        parts = rest.split("/", 4)
        if len(parts) < 5:
            problems.append(f"raw URL too short to map onto a file: {rest}")
            continue
        if parts[0] != "eastseao" or parts[1] != "Markdown-Helper":
            problems.append(f"raw URL points at another repository: {rest}")
            continue
        # split("/", 4) yields five pieces, and the fifth is everything after the
        # FOURTH slash - so the repo path is parts[3] + "/" + parts[4], not
        # parts[4] alone.  Taking parts[4] on its own silently drops the leading
        # directory and reports a false "missing file".
        relpath = parts[3] + "/" + parts[4]
        local = REPO / relpath
        if not local.exists():
            problems.append(f"raw URL references a missing file: {relpath}")

    # Root-relative paths: valid inside the app, broken on GitHub.
    for m in re.finditer(r'(?:src|href)="(/[^/"][^"]*)"', text):
        problems.append(f"root-relative path {m.group(1)} is invalid on GitHub (404)")
    return problems


def run(fname: str, fix: bool) -> int:
    path = REPO / fname
    if not path.exists():
        print(f"  SKIP  {fname} (not present)")
        return 0
    text = path.read_text(encoding="utf-8")
    original = text
    findings = 0

    r1 = check_r1(text)
    if r1 and fix:
        lines = text.split("\n")
        for _, nxt, _ in reversed(r1):
            lines[nxt - 1] = lines[nxt - 1].lstrip()
            lines[nxt - 2] = lines[nxt - 2].rstrip()
        joined = []
        for i, line in enumerate(lines):
            if joined and any(nxt == i + 1 for _, nxt, _ in r1):
                joined[-1] += line
            else:
                joined.append(line)
        text = "\n".join(joined)
        r1 = check_r1(text)

    if r1:
        findings += len(r1)
        print(f"  R1  {len(r1)} stray-space soft break(s)")
        for a, b, snip in r1:
            print(f"        lines {a}-{b}: {snip}")
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"      -> {fname} rewritten ({len(original) - len(text)} bytes shorter)")

    for label, fn in (("R2", check_r2), ("R3", check_r3), ("R4", check_r4), ("R5", check_r5)):
        probs = fn(text)
        if probs:
            findings += len(probs)
            print(f"  {label}  {len(probs)} problem(s)")
            for p in probs:
                print(f"        {p}")

    if findings == 0:
        print(f"  OK    {fname}")
    return findings


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="repair R1 in place")
    args = ap.parse_args()

    print("README lint (GFM + flexmark dual-consumer rules)")
    total = 0
    for f in FILES:
        total += run(f, args.fix)
    print()
    if total:
        print(f"{total} finding(s)")
        raise SystemExit(1)
    print("all clean")


if __name__ == "__main__":
    main()
