### Recent changes
- Reports, requests and questions: <https://github.com/eastseao/Markdown-Helper/issues>
- Downloads and release notes: <https://github.com/eastseao/Markdown-Helper/releases>

### v1.0.0

First release of MarkdownH. Based on the 2.16.1 codebase of the upstream project it was
forked from; see `NOTICE.md` in the repository for the origin and the statement of changes.

**New app icon**
- The whole icon set was rebuilt from a new design, inside and out: the adaptive icon's
  background / foreground / monochrome layers, the five legacy density bitmaps, the store
  listing image, and the four alternate-launcher icons (to-do / quick note / link box /
  share into), which now reuse the shared main layers
- Sized against the real mask geometry rather than only fitting the 72 × 72 dp square.
  The stock circular mask exposes a 72 dp diameter circle, and every legal mask must
  expose the inner 66 dp diameter circle, so the artwork is bounded by a 33 dp radius —
  measured at 32 dp. Bounding-box-only checks pass while the corners are still clipped,
  which is what the first build of this release did
- A monochrome layer was added for Android 13+ themed icons
- 12 superseded vector drawables were deleted

**New "Image export resolution" setting**
- Setting **Image export resolution** (More → View & export → Image export resolution):
  `1x (screen resolution)`, `2x (recommended)` and `3x`
- Exporting a document as an image now scales the WebView viewport and lets the renderer
  re-flow before capturing. The result keeps the same line breaks as the `1x` export, with
  proportionally more pixels instead of a clipped or blank half.
- Export width ceiling raised 4096 → 8192 px
- JPEG quality raised 70 → 95 (fewer compression artifacts on text)

**Start-up**
- The first-start walkthrough (`IntroActivity`) and its four screenshots were removed
- The version-update / changelog dialog shown when the app starts was removed
- The "rate this app" pop-up was disabled
- The AppIntro dependency was dropped; the app now opens straight into the file browser
- Storage permission is still requested on start, which is a no-op once granted
- Note: the More page previously described here as "app information only" no longer
  applies — see the next section

**"More" page regrouped**
- The bottom-navigation tab and the page header icon now use the settings gear
- The 80+ settings are grouped by function into five categories, each collapsed by
  default: General · Files &amp; storage · Editor · View &amp; export · Formats
- Folding is done by a small `ExpandablePreferenceCategory` that toggles `setVisible()`
  on its own children, so the fragment needs no per-group code
- The app-information card stays at the top, outside the groups

**Renamed**
- The app display name is now MarkdownH, in every locale; `versionName` 1.0.0
- The application id is unchanged, so this installs as an upgrade rather than side by side
  with a 2.x build
- Upstream project infrastructure (F-Droid, CI, Crowdin metadata, NEWS, doc pages) was
  removed earlier in the fork
