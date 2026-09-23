# Markdown Helper

<img src="/app/src/main/ic_launcher-web.png" align="left" width="120" hspace="12" vspace="8">
**Text editor for notes and to-do lists (Android).**
Lightweight and offline-first, with Markdown, todo.txt, Zim/WikiText and more.

<br clear="left"/>

**Download:** [`MarkdownHelper-v1.0.0.apk`](MarkdownHelper-v1.0.0.apk) (this repository root)

---

## What it is

Markdown Helper is a plain-text editor for Android. It aims to be versatile, flexible
and lightweight, and it works with simple markup formats such as Markdown and todo.txt.

Everything it writes is a plain file, so the documents stay interoperable with any other
text software on any platform — edit them with Notepad or Vim, filter them with grep,
convert them with Pandoc, sync them with Syncthing.

## Features

**Editing**

- Syntax highlighting and a format-aware action bar — insert pictures and to-dos with one tap
- Auto-save, with undo/redo
- Line numbers, in the editor and inside code blocks in view mode
- Custom action order, snippets, custom file templates
- Search in the current document, search &amp; replace, search across all documents
- Folder-wide file search, favourites, dot-file support
- Encryption of the text of a document with AES-256 (Android 6 and newer)
- Notepad / QuickNote / To-Do / LinkBox shortcuts and home-screen widgets

**Viewing &amp; exporting**

- Live Markdown preview rendered in a WebView
- Export and share documents as **HTML**, **PDF** (print) and **image**
- Table of contents, KaTeX math, Mermaid diagrams, Jekyll front matter, footnotes

**Formats**

- Markdown (CommonMark, via flexmark-java), todo.txt, Zim / WikiText, AsciiDoc,
  Org-Mode, plain text, and key-value formats such as CSV, INI, JSON, YAML and TOML
- Any other file is opened as plain text, and binaries are previewed where possible

**Language &amp; appearance**

- Light and dark theme, several colour schemes, custom fonts (including a dyslexia-friendly one)
- In-app language selection, independent of the system language

No ads, no tracking, no unnecessary permissions.

## What this fork changes (v1.0.0)

Compared to the upstream codebase this release was derived from:

1. **Image export resolution setting.** “More → Image export resolution” offers `1×`
   (screen resolution), `2×` (default) and `3×`. Exporting a document as an image scales
   the WebView viewport and lets it re-flow, so the export keeps exactly the same line
   breaks as `1×` while getting proportionally more pixels. The export width ceiling was
   raised to 8192 px and JPEG quality to 95.
2. **The startup dialog is gone.** The changelog/update dialog shown when the app opens
   was removed, as was the “rate this app” pop-up.
3. **The More page was trimmed** to app information. The licenses category, help/FAQ,
   “rate app” entry and the nested settings sub-page were removed, and the settings that
   lived inside that sub-page are now shown inline.
4. **Rebranded and renamed.** New application id, package, class names and app name; all
   upstream project infrastructure (F-Droid/CI/Crowdin metadata) was dropped.

See [`CHANGELOG.md`](CHANGELOG.md) for details and [`NOTICE.md`](NOTICE.md) for the full
statement of changes.

## Build

Requires a JDK and the Android SDK (see `local.properties` for `sdk.dir`).

```bash
./gradlew assembleFlavorDefaultDebug     # -> app/build/outputs/apk/flavorDefault/debug/
./gradlew assembleFlavorDefaultRelease   # unsigned release build
```

On Linux/macOS there is also a `Makefile` for convenience: `make build`, `make install`,
`make lint`, `make test`.

`minSdkVersion` 18, `compileSdkVersion` / `targetSdkVersion` 35, Java 8 source/target
level, no NDK — a single APK covers all supported architectures.

### Main technologies

| Concern | Used |
|---|---|
| Language / UI | Java, Android SDK, AndroidX, Material Components |
| Editor | Custom component built on Android `EditText` |
| Preview | Android `WebView` |
| Syntax highlighting | Own implementation per format |
| Markdown parser | [flexmark-java](https://github.com/vsch/flexmark-java) |
| Zim / WikiText parser | Own implementation, transpiled to Markdown |
| todo.txt parser | Own implementation |
| Build | Gradle, AGP |

## Privacy

Markdown Helper does not use your internet connection unless your own document content
references external resources — for example an image referenced by URL. The app works
completely offline. No personal data is sent to the author or to any third party.
Documents are stored locally in a folder you choose, defaulting to the internal
`Documents` directory.

### Android permissions

| Permission | Why |
|---|---|
| `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `MANAGE_EXTERNAL_STORAGE` | read and write your documents |
| `INTERNET` | load resources referenced by your own content |
| `INSTALL_SHORTCUT` | place a shortcut to a file or folder on the launcher |
| `REQUEST_INSTALL_PACKAGES` | required by the in-app file/APK handling |

## License

The application code is licensed **Apache License 2.0** — see [`LICENSE.txt`](LICENSE.txt).
Localization and translation files (`string*.xml`) as well as the samples are licensed
**CC0 1.0** (public domain).

This project is an independent fork of an earlier open-source Android editor, and in turn
descends from the unmaintained *writeily* and *writeily-pro* projects.
[`NOTICE.md`](NOTICE.md) records the exact origin of the code, the copyright holders and
the complete list of modifications made for this fork. Third-party components bundled in
the APK are credited in More → Third party licenses inside the app.

---

## 中文说明

**Markdown Helper** 是一款 Android 纯文本笔记 / 待办编辑器，支持 Markdown、todo.txt、
Zim/WikiText、AsciiDoc、Org-Mode、CSV、JSON/YAML 等格式，全程离线，无广告、无追踪。

安装包就在本仓库根目录：`MarkdownHelper-v1.0.0.apk`。

本版在原上游 2.16.1 代码基础上做了四件事：

1. **新增「导出图片分辨率」设置**（1 倍 / 2 倍 / 3 倍，默认 2 倍）。导出为图片时会
   同步放大 WebView 视口并等待重排，因此 2 倍导出与 1 倍导出的**换行位置完全一致**，
   只是像素翻倍；导出宽度上限提到 8192 px，JPEG 质量从 70 提到 95。
2. **去掉启动弹窗**（版本更新/更新日志对话框），同时关闭了「给应用评分」的弹窗。
3. **精简「更多」页面**：协议、帮助/FAQ、评分入口、设置子页面全部移除，原先在子页面
   里的设置项改为直接平铺在「更多」页。
4. **改名换包**：应用名、包名、类名全部改为 Markdown Helper 系列，并清掉上游专属的
   F-Droid / CI / Crowdin 配置。

详细的改动清单见 [`NOTICE.md`](NOTICE.md)，版本记录见 [`CHANGELOG.md`](CHANGELOG.md)。
