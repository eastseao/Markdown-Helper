<div align="center">
  <img src="https://raw.githubusercontent.com/eastseao/Markdown-Helper/main/app/src/main/ic_launcher-web.png" width="140" alt="MarkdownH">
  <h1>MarkdownH</h1>
  <p><b>A plain-text editor for notes and to-do lists on Android</b><br>
  lightweight · offline-first · what it writes is plain text</p>
  <p>
    <a href="https://github.com/eastseao/Markdown-Helper/releases/latest"><img src="https://img.shields.io/github/v/release/eastseao/Markdown-Helper?sort=semver&label=release" alt="release"></a>
    <a href="https://github.com/eastseao/Markdown-Helper/releases"><img src="https://img.shields.io/github/downloads/eastseao/Markdown-Helper/total?label=downloads" alt="downloads"></a>
    <a href="https://github.com/eastseao/Markdown-Helper/blob/main/LICENSE.txt"><img src="https://img.shields.io/github/license/eastseao/Markdown-Helper?label=license" alt="license"></a>
    <img src="https://img.shields.io/badge/Android-4.3%2B-3DDC84?logo=android&logoColor=white" alt="Android 4.3+">
  </p>
  <p><a href="https://github.com/eastseao/Markdown-Helper/blob/main/README.md">简体中文</a> ｜ <b>English</b></p>
</div>

---

## What it is

MarkdownH is a plain-text editor for Android. It aims to be versatile, flexible and
lightweight, and it works with simple markup formats such as Markdown and todo.txt.

Everything it writes is a plain file, so the documents stay interoperable with any other
text software on any platform — edit them with Notepad or Vim, filter them with grep,
convert them with Pandoc, sync them with Syncthing.

No proprietary format, no cloud account, no subscription.

| | |
|:--|:--|
| **Size** | One APK for every architecture, no NDK |
| **Network** | Works fully offline; no ads, no tracking |
| **Storage** | A local folder you choose, defaulting to internal `Documents` |
| **Minimum** | Android 4.3 (API 18) |

## Features

| Area | What you get |
|:--|:--|
| **Editing** | Syntax highlighting and a format-aware action bar — insert pictures and to-dos with one tap · auto-save with undo/redo · line numbers, in the editor and inside code blocks in view mode · custom action order, snippets and file templates · search in the document, search &amp; replace, search across all documents · folder-wide file search, favourites, dot-file support · AES-256 encryption of a document's text (Android 6+) · Notepad / QuickNote / To-Do / LinkBox shortcuts and home-screen widgets |
| **Viewing &amp; export** | Live Markdown preview in a WebView · export and share as **HTML**, **PDF** (print) and **image** · table of contents, KaTeX math, Mermaid diagrams, Jekyll front matter, footnotes |
| **Formats** | Markdown (CommonMark, via flexmark-java) · todo.txt · Zim / WikiText · AsciiDoc · Org-Mode · plain text · key-value formats such as CSV, INI, JSON, YAML and TOML<br>Any other file is opened as plain text, and binaries are previewed where possible |
| **Language &amp; appearance** | Light and dark theme, several colour schemes, custom fonts (including a dyslexia-friendly one) · in-app language selection, independent of the system language |

## Install

| How | Details |
|:--|:--|
| **Releases page** | Download the APK from the [latest release](https://github.com/eastseao/Markdown-Helper/releases/latest) and open it on your phone (you will be asked to allow installs from this source the first time) |
| **Repository root** | [`MarkdownHelper-v1.0.0.apk`](https://github.com/eastseao/Markdown-Helper/blob/main/MarkdownHelper-v1.0.0.apk) — byte-for-byte identical to the file on the release |

Requires **Android 4.3 (API 18) or newer**. A single APK covers every architecture, so
there is nothing to pick by device model.

> **Upgrading from an older `net.gsantner.markor` build**: the default notebook folder is
> derived from the app name, and the older build left `Documents/markor` behind. That
> folder is plain storage, not app data — the app never wrote it — so renaming it is
> enough: `adb shell mv /sdcard/Documents/markor /sdcard/Documents/markdownh`
> Or just pick a different folder under **More → Files &amp; storage → Notebook**.

## What this release changes (v1.0.0)

Compared to the upstream codebase this release was derived from:

**A new app icon**
- The whole set was rebuilt from a new design, inside and out: the adaptive icon's
  background / foreground / monochrome layers, the five legacy density bitmaps, the store
  listing image, and the four alternate-launcher icons (to-do / quick note / link box /
  share into) — those four now share the main icon's layers instead of carrying a
  separate set of drawings each
- Sized against the **real mask geometry** rather than just fitting the 72 × 72 dp square:
  the stock circular mask exposes a 72 dp diameter circle, and every legal mask must
  expose the inner **66 dp diameter circle**. The furthest ink sits 32 dp from the centre,
  so circle, rounded-square and superellipse masks all leave it intact
- Includes a **monochrome layer** for Android 13+ themed icons

**New "Image export resolution" setting**
- "More → View &amp; export → Image export resolution" offers `1×` (screen resolution),
  `2×` (default) and `3×`
- Exporting a document as an image scales the WebView viewport and lets it re-flow, so the
  `2×` export keeps exactly the same line breaks as `1×` while getting proportionally more
  pixels. The export width ceiling was raised to 8192 px and JPEG quality to 95

**All start-up dialogs removed**
- The first-start walkthrough and its four screenshots are gone
- The version-update / changelog dialog shown at launch is gone, and the "rate this app"
  pop-up is disabled
- The app now opens straight into the file browser

**The "More" page regrouped into collapsible sections**
- The bottom-nav tab and the page header now use the settings gear
- 80+ settings are grouped by function into five sections, **each collapsed by default**,
  so the page is scannable at a glance:
  **General** (theme, language, start-up, navigation bar) · **Files &amp; storage** (notebook,
  quick note, to-do locations, attachments, search, backup) · **Editor** (font, indent,
  colour scheme, syntax highlighting) · **View &amp; export** (preview, inject, sharing and
  image export) · **Formats** (advanced options per Markdown / todo.txt / WikiText /
  AsciiDoc / Org-Mode)

**Renamed**
- The app name is now **MarkdownH**, across every locale
- The application id is unchanged, so this is an in-place **upgrade** — it will not install
  a second copy next to an older version

See [`CHANGELOG.md`](https://github.com/eastseao/Markdown-Helper/blob/main/CHANGELOG.md) for
details and [`NOTICE.md`](https://github.com/eastseao/Markdown-Helper/blob/main/NOTICE.md)
for the full statement of changes.

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
|:--|:--|
| Language / UI | Java, Android SDK, AndroidX, Material Components |
| Editor | Custom component built on Android `EditText` |
| Preview | Android `WebView` |
| Syntax highlighting | Own implementation per format |
| Markdown parser | [flexmark-java](https://github.com/vsch/flexmark-java) |
| Zim / WikiText parser | Own implementation, transpiled to Markdown |
| todo.txt parser | Own implementation |
| Build | Gradle, AGP |

## Privacy

MarkdownH does not use your internet connection unless your own document content
references external resources — for example an image referenced by URL. The app works
completely offline. No personal data is sent to the author or to any third party.

### Android permissions

| Permission | Why |
|:--|:--|
| `READ_EXTERNAL_STORAGE`, `WRITE_EXTERNAL_STORAGE`, `MANAGE_EXTERNAL_STORAGE` | read and write your documents |
| `INTERNET` | load resources referenced by your own content |
| `INSTALL_SHORTCUT` | place a shortcut to a file or folder on the launcher |
| `REQUEST_INSTALL_PACKAGES` | required by the in-app file/APK handling |

## License &amp; origin

The application code is licensed **Apache License 2.0** — see
[`LICENSE.txt`](https://github.com/eastseao/Markdown-Helper/blob/main/LICENSE.txt).
Localization and translation files (`string*.xml`) as well as the samples are licensed
**CC0 1.0** (public domain).

This project is an independent fork of an earlier open-source Android editor, and in turn
descends from the unmaintained *writeily* and *writeily-pro* projects.
[`NOTICE.md`](https://github.com/eastseao/Markdown-Helper/blob/main/NOTICE.md) records the
exact origin of the code, the copyright holders and the complete list of modifications
made for this fork. Third-party components bundled in the APK are credited in
More → Third party licenses inside the app.

---

<div align="center">
<sub><a href="https://github.com/eastseao/Markdown-Helper/blob/main/README.md">中文版</a> ｜ the repository home page shows the Chinese version by default</sub>
</div>
