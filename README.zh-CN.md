# Markdown Helper

<img src="/app/src/main/ic_launcher-web.png" align="left" width="120" hspace="12" vspace="8">
**Android 平台的笔记与待办清单文本编辑器。**
轻量、离线优先，支持 Markdown、todo.txt、Zim/WikiText 等多种格式。

<br clear="left"/>

[English](https://github.com/eastseao/Markdown-Helper/blob/main/README.md) | **简体中文**

**下载：** [`MarkdownHelper-v1.0.0.apk`](MarkdownHelper-v1.0.0.apk)（就在本仓库根目录）

---

## 这是什么

Markdown Helper 是一款 Android 纯文本编辑器，目标是通用、灵活、轻量，使用 Markdown、
todo.txt 这类简单标记格式做笔记和清单。

它写出来的东西就是普通文本文件，因此和其他平台的任何文本软件都能互通 —— 可以用记事本或
Vim 编辑、用 grep 过滤、用 Pandoc 转换、用 Syncthing 同步。

## 功能

**编辑**

- 语法高亮 + 随格式变化的操作栏，图片和待办一点即插
- 自动保存，支持撤销 / 重做
- 行号显示，编辑器内和阅读模式的代码块里都有
- 自定义按钮顺序、片段（snippets）、自定义文件模板
- 当前文档内搜索、查找替换、跨全部文档搜索
- 全目录文件搜索、收藏夹、点文件（dotfile）支持
- 用 AES-256 加密文档正文（需 Android 6 及以上）
- 记事本 / 快速记录 / 待办 / 链接盒的快捷方式与桌面小部件

**阅读与导出**

- WebView 实时 Markdown 预览
- 导出并分享为 **HTML**、**PDF**（打印）和 **图片**
- 目录、KaTeX 数学公式、Mermaid 图表、Jekyll front matter、脚注

**支持格式**

- Markdown（CommonMark，解析器为 flexmark-java）、todo.txt、Zim / WikiText、
  AsciiDoc、Org-Mode、纯文本，以及 CSV、INI、JSON、YAML、TOML 等键值格式
- 其他文件一律按纯文本打开，二进制文件在可能的情况下提供预览

**语言与外观**

- 明暗主题、多种配色方案、自定义字体（含阅读障碍友好字体）
- 应用内可单独切换语言，与系统语言解耦

无广告、无追踪、无多余权限。

## 本版改了哪些（v1.0.0）

相对于本版所基于的上游代码：

1. **新增「导出图片分辨率」设置。** 「更多 → 导出图片分辨率」提供 `1 倍`（屏幕分辨率）、
   `2 倍`（默认）、`3 倍`。导出为图片时会同步放大 WebView 视口并等它重排，因此 2 倍导出
   与 1 倍导出的**换行位置完全一致**，只是像素按比例增加。导出宽度上限提到 8192 px，
   JPEG 质量从 70 提到 95。
2. **去掉启动弹窗。** 打开应用时弹出的版本更新 / 更新日志对话框已移除，「给应用评分」
   弹窗也一并关闭。
3. **精简「更多」页面**，只保留应用信息。协议分类、帮助 / FAQ、「给应用评分」入口、
   以及嵌套的设置子页面全部移除，原先藏在子页面里的设置项改为直接平铺在「更多」页。
4. **改名换包。** 换用新的 application id、包名、类名和应用名；上游专属的项目基础设施
   （F-Droid / CI / Crowdin 元数据）已全部删除。

详细改动见 [`CHANGELOG.md`](CHANGELOG.md)，完整的改动声明见 [`NOTICE.md`](NOTICE.md)。

## 自行构建

需要 JDK 和 Android SDK（`sdk.dir` 写在 `local.properties` 里）。

```bash
./gradlew assembleFlavorDefaultDebug     # -> app/build/outputs/apk/flavorDefault/debug/
./gradlew assembleFlavorDefaultRelease   # 未签名的 release 构建
```

Linux / macOS 下还可以用 `Makefile`：`make build`、`make install`、`make lint`、`make test`。

`minSdkVersion` 18，`compileSdkVersion` / `targetSdkVersion` 35，Java 源 / 目标级别 8，
不依赖 NDK —— 一个 APK 覆盖全部受支持的架构。

### 主要技术选型

| 方面 | 使用 |
|---|---|
| 语言 / UI | Java、Android SDK、AndroidX、Material Components |
| 编辑器 | 基于 Android `EditText` 的自研组件 |
| 预览 | Android `WebView` |
| 语法高亮 | 各格式自研实现 |
| Markdown 解析 | [flexmark-java](https://github.com/vsch/flexmark-java) |
| Zim / WikiText 解析 | 自研实现，转译为 Markdown |
| todo.txt 解析 | 自研实现 |
| 构建 | Gradle、AGP |

## 隐私

除非你自己的文档内容引用了外部资源（例如用 URL 引用的图片），否则 Markdown Helper
不会使用你的网络连接。应用完全离线工作，不会把你的任何个人数据发给作者或任何第三方。
文档保存在你自己选择的本地文件夹里，默认是内部存储的 `Documents` 目录。

### 权限说明

| 权限 | 用途 |
|---|---|
| `READ_EXTERNAL_STORAGE`、`WRITE_EXTERNAL_STORAGE`、`MANAGE_EXTERNAL_STORAGE` | 读写你的文档 |
| `INTERNET` | 加载你自己内容里引用的资源 |
| `INSTALL_SHORTCUT` | 在桌面上放置文件或文件夹的快捷方式 |
| `REQUEST_INSTALL_PACKAGES` | 应用内文件 / APK 处理所需 |

## 许可

应用代码采用 **Apache License 2.0** —— 见 [`LICENSE.txt`](LICENSE.txt)。
本地化与翻译文件（`string*.xml`）以及样例文件采用 **CC0 1.0**（公有领域）。

本项目是某个早期开源 Android 编辑器的独立分支，往上还可追溯到已停止维护的
*writeily* 与 *writeily-pro* 项目。[`NOTICE.md`](NOTICE.md) 记录了代码的确切来源、
版权持有人，以及本分支所做的全部修改。APK 内打包的第三方组件署名见应用内
「更多 → 第三方许可」。
