### Recent changes
- Reports, requests and questions: <https://github.com/eastseao/markdown-helper/issues>
- Downloads and release notes: <https://github.com/eastseao/markdown-helper/releases>

### v1.0.0
First release of Markdown Helper. Based on the 2.16.1 codebase of the upstream
project it was forked from; see NOTICE.md in the repository for the origin and the
statement of changes.

**Image export**
- New setting **Image export resolution** (More → Image export resolution):
  `1x (screen resolution)`, `2x (recommended)` and `3x`
- Exporting a document as an image now scales the WebView viewport and lets the
  renderer re-flow before capturing. The result keeps the same line breaks as the
  `1x` export, with proportionally more pixels instead of a clipped or blank half.
- Export width ceiling raised 4096 → 8192 px
- JPEG quality raised 70 → 95 (fewer compression artifacts on text)

**Interface**
- The version-update dialog shown when the app starts has been removed
- The "rate this app" pop-up has been disabled
- The More page now only contains app information: the licenses category, help/FAQ,
  "rate app" entry and the nested settings sub-page were removed
- The settings that used to live inside that sub-page are now shown inline on the
  More page
- An "About the author" card was added to the settings

**Project**
- Renamed to Markdown Helper: new application id, package name, class names and
  app display name
- Upstream project infrastructure (F-Droid, CI, Crowdin metadata, NEWS, doc pages)
  was removed
