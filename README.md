<div align="center">
  <img src="https://raw.githubusercontent.com/eastseao/Markdown-Helper/main/app/src/main/ic_launcher-web.png" width="140" alt="MarkdownH">
  <h1>MarkdownH</h1>
  <p><b>Android 平台的笔记与待办清单文本编辑器</b><br>
  轻量 · 离线优先 · 写出来就是纯文本</p>
  <p>
    <a href="https://github.com/eastseao/Markdown-Helper/releases/latest"><img src="https://img.shields.io/github/v/release/eastseao/Markdown-Helper?sort=semver&label=release" alt="release"></a>
    <a href="https://github.com/eastseao/Markdown-Helper/releases"><img src="https://img.shields.io/github/downloads/eastseao/Markdown-Helper/total?label=downloads" alt="downloads"></a>
    <a href="https://github.com/eastseao/Markdown-Helper/blob/main/LICENSE.txt"><img src="https://img.shields.io/github/license/eastseao/Markdown-Helper?label=license" alt="license"></a>
    <img src="https://img.shields.io/badge/Android-4.3%2B-3DDC84?logo=android&logoColor=white" alt="Android 4.3+">
  </p>
  <p><b>简体中文</b> ｜ <a href="https://github.com/eastseao/Markdown-Helper/blob/main/README.en.md">English</a></p>
</div>

---

## 这是什么

MarkdownH 是一款 Android 纯文本编辑器，目标是通用、灵活、轻量，使用 Markdown、todo.txt
这类简单标记格式做笔记和清单。

它写出来的东西就是普通文本文件，因此和其他平台的任何文本软件都能互通 —— 可以用记事本或
Vim 编辑、用 grep 过滤、用 Pandoc 转换、用 Syncthing 同步。

没有专有格式，没有云端账户，没有订阅。

| | |
|:--|:--|
| **体积** | 单个 APK，覆盖全部架构，不依赖 NDK |
| **网络** | 完全离线工作，无广告、无追踪 |
| **存放位置** | 你自己选的本地文件夹，默认内部存储的 `Documents` |
| **最低版本** | Android 4.3（API 18） |

## 功能

| 功能域 | 说明 |
|:--|:--|
| **编辑** | 语法高亮与随格式变化的操作栏，图片、待办一点即插 · 自动保存、撤销 / 重做 · 行号（编辑器内与阅读模式的代码块里） · 自定义按钮顺序、片段、文件模板 · 文档内搜索、查找替换、跨全部文档搜索 · 全目录文件搜索、收藏夹、点文件支持 · AES-256 加密文档正文（Android 6+） · 记事本 / 快速记录 / 待办 / 链接盒的快捷方式与桌面小部件 |
| **阅读与导出** | WebView 实时 Markdown 预览 · 导出并分享为 **HTML**、**PDF**（打印）和**图片** · 目录、KaTeX 数学公式、Mermaid 图表、Jekyll front matter、脚注 |
| **支持格式** | Markdown（CommonMark，解析器 flexmark-java）· todo.txt · Zim / WikiText · AsciiDoc · Org-Mode · 纯文本 · CSV、INI、JSON、YAML、TOML 等键值格式<br>其他文件一律按纯文本打开，二进制文件在可能的情况下提供预览 |
| **语言与外观** | 明暗主题、多种配色方案、自定义字体（含阅读障碍友好字体） · 应用内可单独切换语言，与系统语言解耦 |

## 安装

| 方式 | 说明 |
|:--|:--|
| **Releases 页面** | 从 [最新 Release](https://github.com/eastseao/Markdown-Helper/releases/latest) 下载 APK，在手机上打开安装（首次会提示「允许来自此来源的应用」） |
| **仓库根目录** | [`MarkdownHelper-v1.0.0.apk`](https://github.com/eastseao/Markdown-Helper/blob/main/MarkdownHelper-v1.0.0.apk) 与 Releases 上的文件逐字节相同 |

要求 **Android 4.3（API 18）及以上**。单个 APK 覆盖全部架构，不必按机型挑选。

> **从早期的 `net.gsantner.markor` 版本升级**：默认笔记本目录由应用名推导，旧版留下的是
> `Documents/markor`。那个目录是纯存储、不是应用数据（应用从未写过它），改个名即可：
> `adb shell mv /sdcard/Documents/markor /sdcard/Documents/markdownh`
> 或者直接在 **更多 → 文件与存储 → 笔记本** 里重选一个目录。

## 这个版本改了什么（v1.0.0）

相对于本版所基于的上游代码：

**全新应用图标**
- 从设计稿重做了整套图标，里外都换：自适应图标的背景 / 前景 / 单色三层、5 档传统密度位图、商店用大图，以及 4 个别名启动器图标（待办 / 快速记录 / 链接盒 / Share into）——这 4 个与主图标共用同一组图层，不再各自一套画稿
- 尺寸按**真实遮罩几何**定，而不是只保证落在 72 × 72 dp 方块内：系统圆形遮罩实际露出
  72 dp 直径的圆，而任何合法遮罩都必须露出内侧 **66 dp 直径的圆**。图稿最外缘到中心的距离为
  32 dp，所以圆形、圆角方形、超椭圆遮罩都不会裁到它
- 含 Android 13+ 主题图标用的**单色层**

**新增「导出图片分辨率」设置**
- 「更多 → 阅读与导出 → 导出图片分辨率」提供 `1 倍`（屏幕分辨率）、`2 倍`（默认）、`3 倍`
- 导出为图片时会同步放大 WebView 视口并等它重排，因此 2 倍导出与 1 倍导出的**换行位置完全一致**，只是像素按比例增加。导出宽度上限提到 8192 px，JPEG 质量从 70 提到 95

**去掉全部启动弹窗**
- 首次启动的引导页及其 4 张截图已移除
- 启动时的版本更新 / 更新日志对话框已移除，「给应用评分」弹窗一并关闭
- 应用现在直接进入文件浏览器

**「更多」页面重构为可折叠分组**
- 底部标签与页首图标改为设置齿轮
- 80 多项设置按功能域归入 5 个分组，**每组默认收起**，一眼能看清全貌：
  **通用**（主题、语言、启动、导航栏）· **文件与存储**（笔记本、快速记录、待办位置、附件、搜索、备份）·
  **编辑器**（字体、缩进、配色、语法高亮）· **阅读与导出**（预览、注入、分享与图片导出）·
  **格式高级设置**（Markdown / todo.txt / WikiText / AsciiDoc / Org-Mode 等各自的高级项）

**改名**
- 应用名改为 **MarkdownH**，覆盖全部语言
- application id 保持不变，因此这是**覆盖升级**，不会和旧版并排装出两个应用

详细改动见 [`CHANGELOG.md`](https://github.com/eastseao/Markdown-Helper/blob/main/CHANGELOG.md)，完整的改动声明见 [`NOTICE.md`](https://github.com/eastseao/Markdown-Helper/blob/main/NOTICE.md)。

## 自行构建

需要 JDK 和 Android SDK（`sdk.dir` 写在 `local.properties` 里）。

```bash
./gradlew assembleFlavorDefaultDebug     # -> app/build/outputs/apk/flavorDefault/debug/
./gradlew assembleFlavorDefaultRelease   # 未签名的 release 构建
```

Linux / macOS 下还可以用 `Makefile`：`make build`、`make install`、`make lint`、`make test`。

`minSdkVersion` 18，`compileSdkVersion` / `targetSdkVersion` 35，Java 源 / 目标级别 8，不依赖 NDK —— 一个 APK 覆盖全部受支持的架构。

### 主要技术选型

| 方面 | 使用 |
|:--|:--|
| 语言 / UI | Java、Android SDK、AndroidX、Material Components |
| 编辑器 | 基于 Android `EditText` 的自研组件 |
| 预览 | Android `WebView` |
| 语法高亮 | 各格式自研实现 |
| Markdown 解析 | [flexmark-java](https://github.com/vsch/flexmark-java) |
| Zim / WikiText 解析 | 自研实现，转译为 Markdown |
| todo.txt 解析 | 自研实现 |
| 构建 | Gradle、AGP |

## 隐私

除非你自己的文档内容引用了外部资源（例如用 URL 引用的图片），否则 MarkdownH
不会使用你的网络连接。应用完全离线工作，不会把你的任何个人数据发给作者或任何第三方。

### 权限说明

| 权限 | 用途 |
|:--|:--|
| `READ_EXTERNAL_STORAGE`、`WRITE_EXTERNAL_STORAGE`、`MANAGE_EXTERNAL_STORAGE` | 读写你的文档 |
| `INTERNET` | 加载你自己内容里引用的资源 |
| `INSTALL_SHORTCUT` | 在桌面上放置文件或文件夹的快捷方式 |
| `REQUEST_INSTALL_PACKAGES` | 应用内文件 / APK 处理所需 |

## 许可与出处

应用代码采用 **Apache License 2.0** —— 见 [`LICENSE.txt`](https://github.com/eastseao/Markdown-Helper/blob/main/LICENSE.txt)。本地化与翻译文件（`string*.xml`）以及样例文件采用 **CC0 1.0**（公有领域）。

本项目是某个早期开源 Android 编辑器的独立分支，往上还可追溯到已停止维护的
*writeily* 与 *writeily-pro* 项目。[`NOTICE.md`](https://github.com/eastseao/Markdown-Helper/blob/main/NOTICE.md)
记录了代码的确切来源、版权持有人，以及本分支所做的全部修改。APK 内打包的第三方组件署名见应用内「更多 → 第三方许可」。

---

<div align="center">
<sub><a href="https://github.com/eastseao/Markdown-Helper/blob/main/README.en.md">English version</a> ｜ 本页是仓库首页默认展示的 README</sub>
</div>
