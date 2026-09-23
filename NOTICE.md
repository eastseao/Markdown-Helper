# NOTICE

## Origin of this work

**Markdown Helper** is a derivative work of **Markor** — <https://github.com/gsantner/markor> —
based on the **Markor 2.16.1** source release.

Markor is Copyright 2017–2025 Gregor Santner and the Markor contributors, and is
licensed under the Apache License, Version 2.0 (`LICENSE.txt`).

This project is **not** affiliated with, endorsed by, or sponsored by the Markor
project. It is an independent fork maintained by
[eastseao](https://github.com/eastseao), focused on document export quality and a
reduced user interface.

## Statement of changes

Per Apache License 2.0 section 4(b) — prominent notices stating that files were
changed — the following modifications were applied on top of Markor 2.16.1.
Every file listed below has been modified.

### 1. Application identity

| | |
|---|---|
| `applicationId` / AGP `namespace` | `net.gsantner.markor` → `io.github.eastseao.markdownhelper` |
| Java package | `net.gsantner.markor.*` → `io.github.eastseao.markdownhelper.*` |
| Java classes | `Markor*` → `MarkdownHelper*` (BaseActivity, BaseFragment, DialogFactory, FileBrowserFactory, ContextUtils, WebViewClient, SettingsFragment, WrMarkorSingleton, WrMarkorWidgetProvider) |
| App display name | `Markdown Helper` |
| Version | reset to `1.0.0` (versionCode `1`) |
| Resource names | `*markor*` → `*markdownhelper*` (incl. `@xml/markor_widget`, `prism-markor.*`, `editor_basic_color_scheme_markor`) |

Note: the vendored `net.gsantner.opoc.*` utility library and the `other.writeily.*`
legacy package keep their original namespace, as they carry no upstream branding.

### 2. Document export

- New setting **“Image export resolution”** — `1×` / `2×` / `3×`, default `2×`.
  Exporting as image now resizes the WebView viewport (plus `textZoom`) and waits
  for the renderer to re-flow, so the line breaks of the `1×` export are preserved
  while the bitmap receives proportionally more pixels. Before this change the
  image was merely upscaled/clipped.
- Export width ceiling raised `4096` → `8192` px.
- JPEG quality raised `70` → `95`.
- Setting key `share_image_export_scale`, added to `preferences_master.xml`.

### 3. User interface

- The version-update / changelog dialog shown when the app starts has been removed.
- The “rate this app” pop-up has been disabled.
- The **More** page was reduced to app information: licenses section, help/FAQ,
  “rate app” entry and the nested settings sub-page are gone; the settings that
  used to live inside that sub-page are now shown inline on the More page.
- An **About the author** card was added to the settings page.

### 4. Removed upstream-only content

`NEWS.md`, `doc/`, `experiments/`, `metadata/`, `.github/`, `crowdin.yml`, and the
upstream F-Droid / Crowdin / GitHub-shield links were removed or redirected, as
they describe infrastructure that belongs to the original project.

## Third party components

The complete list of bundled third party components and their licenses is shown
inside the application (More → Third party licenses) and stored in
`app/src/main/res/raw/licenses_3rd_party.md`.

## License

Apache License 2.0 — see [`LICENSE.txt`](LICENSE.txt).
