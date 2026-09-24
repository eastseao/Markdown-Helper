"""Rename the user-visible app name from "Markdown Helper" to "MarkdownH".

Scope (deliberately not a blind repo-wide sed):
  * res/values/string-not_translatable.xml   app_name_real + the colour-scheme label
  * res/values*/strings.xml                  the in-app prose that names the app (41 files)
  * flavorAtest/res/values/string-not_translatable.xml   the "(test)" variant
  * Java comments                            internal notes about the app itself

NOT touched on purpose:
  NOTICE.md / LICENSE.txt / CONTRIBUTORS.md   upstream attribution (legally required)
  README.md / README.en.md / CHANGELOG.md     project docs; the GitHub repo stays Markdown-Helper
  applicationId                               keeping it avoids installing a second copy

Note: app_name also feeds AppSettings.getDefaultNotebookFile(), i.e. the default notebook
folder becomes Documents/markdownh on a FRESH install. Existing installs keep the folder
path stored in pref_key__notebook_directory, so nobody's notes move.
"""
import pathlib, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(r"I:\mar\markdown-helper")
MAIN_RES = REPO / "app" / "src" / "main" / "res"
OLD, NEW = "Markdown Helper", "MarkdownH"

# longest first so "Markdown Helpers" does not become "MarkdownHs"
PATTERNS = [(re.compile(r"Markdown Helpers"), NEW), (re.compile(r"Markdown Helper"), NEW)]

report = []


def apply(path: pathlib.Path, only_names=None):
    src = path.read_text(encoding="utf-8")
    out = src
    if only_names:
        # touch only the <string name="..."> bodies listed, leave the rest byte-identical
        for name in only_names:
            m = re.search(r'(<string name="%s"[^>]*>)(.*?)(</string>)' % re.escape(name),
                          out, re.S)
            if not m:
                report.append((path, f"!! <string name={name}> NOT FOUND", 0))
                continue
            body = m.group(2)
            new_body = body
            for pat, rep in PATTERNS:
                new_body = pat.sub(rep, new_body)
            if new_body != body:
                out = out[:m.start(2)] + new_body + out[m.end(2):]
                report.append((path, name, body.count(OLD.split()[0]) or 1))
    else:
        for pat, rep in PATTERNS:
            out = pat.sub(rep, out)
        if out != src:
            report.append((path, "whole file", len(PATTERNS)))
    if out != src:
        path.write_text(out, encoding="utf-8", newline="")
        return True
    return False


def main():
    changed_files = 0

    # 1. main app_name + colour-scheme label
    p = MAIN_RES / "values" / "string-not_translatable.xml"
    if apply(p, ["app_name_real", "editor_basic_color_scheme_markdownhelper"]):
        changed_files += 1
        print(f"[1] {p.relative_to(REPO)}  app_name_real / colour-scheme label")

    # 2. test flavour label
    p = REPO / "app/src/flavorAtest/res/values/string-not_translatable.xml"
    if apply(p, ["app_name"]):
        changed_files += 1
        print(f"[2] {p.relative_to(REPO)}  app_name (test)")

    # 3. in-app prose across every locale
    hits, files = 0, []
    for p in sorted(MAIN_RES.glob("values*/strings.xml")):
        before = p.read_text(encoding="utf-8")
        n = len(re.findall(r"Markdown Helper", before))
        if apply(p):
            hits += n
            files.append(p)
            changed_files += 1
    print(f"[3] locale prose: {hits} occurrence(s) in {len(files)} strings.xml file(s)")

    # 4. Java comments that describe the app itself
    jfiles = []
    for p in sorted(REPO.glob("app/src/**/*.java")):
        before = p.read_text(encoding="utf-8")
        if "Markdown Helper" not in before:
            continue
        if apply(p):
            jfiles.append(p)
            changed_files += 1
    print(f"[4] Java comments: {len(jfiles)} file(s)")
    for p in jfiles:
        print(f"    {p.relative_to(REPO)}")

    print(f"\nchanged files: {changed_files}")
    for path, name, _ in report:
        print(f"  {path.relative_to(REPO)}  <- {name}")

    # leftover audit: only docs / licence files may still carry the old name
    print("\n=== leftover 'Markdown Helper' outside docs ===")
    import subprocess
    r = subprocess.run(["grep", "-rl", "--include=*.xml", "--include=*.java",
                        "--include=*.gradle", "Markdown Helper", "app/src"],
                       cwd=REPO, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip() or "(none)")


if __name__ == "__main__":
    main()
