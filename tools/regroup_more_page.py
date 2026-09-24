"""Regroup the "More" page into 5 collapsible, functional-domain groups.

Why a script instead of hand-editing: the file carries 77 settings with dozens of icons,
defaults, list entries and cross-references. Rewriting it by hand risks silently dropping
one. This script parses the existing XML into a node tree, moves each node into its new
group, and then ASSERTS that every original android:key appears exactly once in the output.

Grouping (by functional domain, as requested: 4~5 groups, all collapsed by default):

  1 general  通用与外观   theme, language, start-up, navigation bar, keep screen on,
                          screenshots, multi window, special documents, experimental, encryption
  2 files    文件与存储   notebook/quicknote/todo locations, attachments, snippets,
                          file browser, search, backup
  3 editor   编辑器       font, tab width, colour scheme, syntax highlighting, editor misc
  4 view     阅读与导出   preview, inject, text, share/export image, chrome custom tabs
  5 formats  格式高级设置 per-format advanced settings (markdown, todo.txt, wikitext,
                          plaintext, asciidoc, orgmode)

Physical line indentation is preserved by shifting every emitted node by a per-node delta,
so multi-line tags and comments stay internally consistent; only the leading whitespace of
each line changes.

GOTCHA (learned the hard way): the group keys are written as
`android:key="@string/pref_key__more_group_<id>"`, i.e. aapt2 RESOLVES them. A key without a
matching `<string>` definition does not fail the XML parse or the aapt2 *compile* step - it
fails the aapt2 **link** step with "resource string/... not found", which AGP renders as the
useless "AAPT2 ... Unexpected error during link" unless you build with --info. The script
therefore now keeps the key strings and the XML in sync by itself.
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(r"I:\mar\markdown-helper")
TARGET = REPO / "app/src/main/res/xml/prefactions__more_information.xml"
STRFILE = REPO / "app/src/main/res/values/string-not_translatable.xml"
STRANCHOR = '    <string name="pref_key__more_info__app"'
CLS = "io.github.eastseao.markdownhelper.activity.ExpandablePreferenceCategory"
LEAF_RE = re.compile(r'android:key="@string/([A-Za-z0-9_]+)"')
TITLE_RE = re.compile(r'android:title="@string/([A-Za-z0-9_]+)"')
INDENT = 4


# ------------------------------------------------------------------ parser
class Node:
    __slots__ = ("tag", "raw", "depth", "children", "leading", "label")

    def __init__(self, tag, raw, depth):
        self.tag = tag
        self.raw = raw              # exact source text of the element
        self.depth = depth          # original nesting depth (root element = 0)
        self.children = []
        self.leading = []           # comment/blank chunks that sit right before this element
        self.label = None


def find_tag_end(s, i):
    """i points at '<'. Return (end_index_exclusive, self_closing, is_close, name)."""
    q = None
    j = i
    while j < len(s):
        c = s[j]
        if q:
            if c == q:
                q = None
        elif c in "\"'":
            q = c
        elif c == ">":
            seg = s[i:j + 1]
            self_closing = seg.rstrip()[:-1].rstrip().endswith("/")
            is_close = seg.startswith("</")
            m = re.match(r"</?\s*([A-Za-z0-9_.:]+)", seg)
            return j + 1, self_closing, is_close, (m.group(1) if m else "")
        j += 1
    raise SystemExit("unterminated tag at %d" % i)


def parse_children(text, pos, end, depth, parent_label):
    """Parse sibling elements in text[pos:end] at the given depth.

    Each node keeps its source text VERBATIM except that the first line is prefixed with its
    original indentation (the file is uniformly 4-space indented), so that re-indenting a node
    is a single uniform per-line shift.
    """
    nodes = []
    pending = []
    pad = " " * (depth * INDENT)
    while pos < end:
        lt = text.find("<", pos)
        if lt == -1 or lt >= end:
            break
        if text.startswith("<!--", lt):
            close = text.find("-->", lt)
            if close == -1:
                break
            pending.append((lt, close + 3))
            pos = close + 3
            continue
        tag_end, self_closing, is_close, name = find_tag_end(text, lt)
        if is_close:
            break
        node = Node(name, pad + text[lt:tag_end], depth)
        node.label = node_label(node, parent_label)
        node.leading = pending
        pending = []
        if self_closing:
            nodes.append(node)
            pos = tag_end
            continue
        # find the matching close tag, skipping nested same-name elements
        k = tag_end
        level = 1
        while k < end:
            nxt = text.find("<", k)
            if nxt == -1 or nxt >= end:
                break
            if text.startswith("<!--", nxt):
                c2 = text.find("-->", nxt)
                k = (c2 + 3) if c2 != -1 else end
                continue
            e2, sc2, cl2, nm2 = find_tag_end(text, nxt)
            if nm2 == name:
                if cl2:
                    level -= 1
                    if level == 0:
                        break
                elif not sc2:
                    level += 1
            k = e2
        close_end = find_tag_end(text, k)[0]
        node.raw = pad + text[lt:close_end]
        inner_start, inner_end = tag_end, k
        node.children = parse_children(text, inner_start, inner_end, depth + 1, node.label)
        nodes.append(node)
        pos = close_end
    return nodes


def node_label(node, parent_label):
    """Stable, human readable id.

    A node carrying android:key IS a leaf preference - use the key, it is globally unique.
    Everything else (the containers, which have no key) is identified by its title path.
    """
    m = LEAF_RE.search(node.raw[:2000])
    if m:
        return m.group(1)
    m = TITLE_RE.search(node.raw[:2000])
    if m:
        return f"{parent_label}/{m.group(1)}" if parent_label else m.group(1)
    return f"{parent_label}/{node.tag}"


# ------------------------------------------------------------------ reindent & emit
def shift(raw, delta):
    if delta == 0:
        return raw
    out = []
    for line in raw.split("\n"):
        if line.strip():
            if delta > 0:
                out.append(" " * delta + line)
            else:
                drop = min(-delta, len(line) - len(line.lstrip()))
                out.append(line[drop:])
        else:
            out.append(line)
    return "\n".join(out)


DROP_COMMENTS = [
    "Settings (flattened)", "General screen", "Document browser screen",
    "Editor screen", "View screen", "Formats screen", "Most important settings",
]


def emit_leading(node, delta, lines):
    for a, b in node.leading:
        chunk = SOURCE[a:b]
        if any(t in chunk for t in DROP_COMMENTS):
            continue
        # the comment sits at the same indentation as the element that follows it; its first
        # line has to be padded the same way node.raw was, otherwise re-indenting is lopsided
        chunk = " " * (node.depth * INDENT) + chunk
        for line in shift(chunk, delta).split("\n"):
            if line.strip():
                lines.append(line)
            elif lines and lines[-1] != "":
                lines.append("")


def emit_node(node, new_depth, lines, exclude=()):
    delta = (new_depth - node.depth) * INDENT
    emit_leading(node, delta, lines)
    if node.children and exclude:
        # rebuild the container without the excluded direct children
        te = find_tag_end(node.raw, node.raw.index("<"))[0]
        lines.extend(shift(node.raw[:te], delta).split("\n"))
        for ch in node.children:
            if ch.label in exclude:
                continue
            emit_node(ch, new_depth + 1, lines)
        close = node.raw.rfind("</")
        lines.append(shift(" " * (node.depth * INDENT) + node.raw[close:], delta))
    else:
        for line in shift(node.raw, delta).split("\n"):
            lines.append(line)
    lines.append("")


def emit_leaf(node, new_depth, lines):
    emit_node(node, new_depth, lines)


# ------------------------------------------------------------------ main
SOURCE = ""
GROUPS = [
    dict(id="general", title="@string/general", icon="@drawable/ic_widgets_black_24dp",
         summary="@string/app_settings",
         items=["pref_key__app_theme", "pref_key__language",
                "pref_key__app_start_tab_v2", "pref_key__app_start_folder",
                "pref_key__exts_to_always_open_in_this_app",
                "pref_key__navigationbar_color", "pref_key__theming_hide_system_statusbar",
                "pref_key__is_keep_screen_on", "pref_key__is_disallow_screenshots",
                "C:general/features",
                "pref_key__set_encryption_password"]),
    dict(id="files", title="@string/settings_group_files", icon="@drawable/ic_folder_white_24dp",
         summary="@string/files_and_folders",
         items=["C:general/save_location",
                "pref_key__attachment_folder_name", "pref_key__snippet_directory_path",
                "C:other/file_browser", "C:general/search", "C:other/backup"]),
    dict(id="editor", title="@string/edit_mode", icon="@drawable/ic_edit_black_24dp",
         summary="@string/editor_settings",
         items=["pref_key__font_family", "pref_key__editor_font_size", "pref_key__tab_width_v2",
                "C:edit_mode/basic_color_scheme", "C:edit_mode/syntax_highlighting",
                "pref_key__is_highlighting_activated", "C:edit_mode/miscellaneous"]),
    dict(id="view", title="@string/settings_group_view_export", icon="@drawable/ic_visibility_black_24dp",
         summary="@string/display_converted_markup",
         items=["pref_key__is_preview_first", "pref_key__swipe_to_change_mode",
                "C:view_mode/inject", "C:view_mode/text",
                "pref_key__share_into_format", "pref_key__share_image_export_width",
                "pref_key__share_image_export_scale", "pref_key__share_image_export_scale_note",
                "pref_key__open_links_with_chrome_custom_tabs"]),
    dict(id="formats", title="@string/format", icon="@drawable/gs_markdown_black_24dp",
         summary=None,
         items=["C:format/markdown", "C:format/todo_txt", "C:format/wikitext",
                "C:format/plaintext", "C:format/asciidoc", "C:format/orgmode"]),
]
# containers that must lose one direct child -> label: [children to drop]
DROPS = {"C:general/features": ["pref_key__is_highlighting_activated"]}


def main():
    global SOURCE
    SOURCE = TARGET.read_text(encoding="utf-8")

    # This is a ONE-SHOT migration script: it expects the *flat* upstream layout as input.
    # Running it again on its own output would try to regroup the already-grouped tree and
    # silently mangle it, so bail out early - but still guarantee the key strings exist,
    # because that is the part it is safe (and idempotent) to re-assert.
    if "pref_key__more_group_" in SOURCE:
        print("already regrouped - refusing to run the migration again")
        ensure_group_key_strings([g["id"] for g in GROUPS])
        return

    root_start = SOURCE.find("<PreferenceScreen")
    root_open_end = find_tag_end(SOURCE, root_start)[0]
    root_close = SOURCE.rfind("</PreferenceScreen>")
    prologue = SOURCE[:root_start]
    root_open = SOURCE[root_start:root_open_end]
    epilogue = SOURCE[root_close:]
    top = parse_children(SOURCE, root_open_end, root_close, 1, "")

    # index
    by_label = {}

    def walk(nodes):
        for n in nodes:
            by_label.setdefault(n.label, n)
            walk(n.children)

    walk(top)
    print(f"parsed {len(top)} top-level blocks, {len(by_label)} labelled nodes")

    about = next(n for n in top if "pref_key__more_info__app" in (n.raw or ""))
    # 'general/features' has a title, so it is labelled 'general/features'
    print("Available containers:", sorted(k for k in by_label if "/" in k and k.count("/") == 1))

    lines = []
    lines.extend(prologue.rstrip("\n").split("\n"))
    lines.append("")
    lines.extend(root_open.split("\n"))
    lines.append("")

    # About card stays at the top, outside any group
    emit_node(about, 1, lines)

    for g in GROUPS:
        lines.append("")
        lines.append(f"    <!-- ==================== {g['id']} ==================== -->")
        lines.append(f"    <{CLS}")
        lines.append(f'        android:key="@string/pref_key__more_group_{g["id"]}"')
        lines.append(f'        android:icon="{g["icon"]}"')
        if g["summary"]:
            lines.append(f'        android:summary="{g["summary"]}"')
        lines.append(f'        android:title="{g["title"]}">')
        for item in g["items"]:
            if item.startswith("C:"):
                children = DROPS.get(item, [])
                emit_node(by_label[item[2:]], 2, lines, exclude=children)
            else:
                emit_node(by_label[item], 2, lines)
        lines.append(f"    </{CLS}>")

    lines.append("")
    lines.append(epilogue.rstrip("\n").split("\n")[-1])
    out = "\n".join(lines).rstrip("\n") + "\n"

    # ---------------- validation: nothing lost, nothing duplicated ----------------
    src_keys = re.findall(r'android:key="@string/([A-Za-z0-9_]+)"', SOURCE)
    out_keys = re.findall(r'android:key="@string/([A-Za-z0-9_]+)"', out)
    src_leaf = [k for k in src_keys if not k.startswith("pref_key__more_group_")]
    missing = [k for k in src_leaf if out_keys.count(k) == 0]
    dup = sorted({k for k in out_keys if out_keys.count(k) > 1})
    print(f"\nandroid:key in source : {len(src_keys)}")
    print(f"android:key in output : {len(out_keys)}  (5 of them are the new group keys)")
    print(f"missing               : {missing or 'NONE'}")
    print(f"duplicated            : {dup or 'NONE'}")
    if missing or dup:
        raise SystemExit("REFUSING TO WRITE - key set changed")

    ensure_group_key_strings([g["id"] for g in GROUPS])

    TARGET.write_text(out, encoding="utf-8", newline="")
    print(f"\nwrote {TARGET.relative_to(REPO)}  ({len(out.splitlines())} lines, "
          f"was {len(SOURCE.splitlines())})")


def ensure_group_key_strings(ids):
    """Idempotently declare pref_key__more_group_<id> in string-not_translatable.xml.

    android:key="@string/..." is resolved by aapt2 at LINK time, so a missing declaration
    turns into a link failure, not a parse error. Keep both sides together.
    """
    text = STRFILE.read_text(encoding="utf-8")
    missing = [i for i in ids if f'name="pref_key__more_group_{i}"' not in text]
    if not missing:
        print(f"group key strings : all {len(ids)} already declared")
        return
    lines = text.split("\n")
    at = next((k for k, line in enumerate(lines) if line.startswith(STRANCHOR)), None)
    if at is None:
        raise SystemExit(f"anchor not found in {STRFILE.name}: {STRANCHOR!r}")
    block = [f'    <string name="pref_key__more_group_{i}" translatable="false">'
             f'pref_key__more_group_{i}</string>' for i in missing]
    lines[at + 1:at + 1] = block
    STRFILE.write_text("\n".join(lines), encoding="utf-8", newline="")
    print(f"group key strings : inserted {missing} into {STRFILE.name}")


if __name__ == "__main__":
    main()
