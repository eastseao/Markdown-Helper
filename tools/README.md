# tools/ — 一次性改版与校验脚本

这里放的是**生成仓库里已提交产物**的脚本，不是构建链路的一部分（`./gradlew` 不会调用它们）。
它们的价值是**可追溯、可复现**：没有它们，`app/src/main/res/drawable-*/ic_launcher*.png`
和 `res/xml/prefactions__more_information.xml` 就成了无法重新推导的二进制/结构。

## 前提

- Windows + Python 3.12，需要 `Pillow`、`numpy`
- Android SDK build-tools **35.0.0**（`verify_apk.py` 会去 `I:\应用开发\Android\Sdk\build-tools\35.0.0` 找 `aapt` / `aapt2`）
- ⚠️ **脚本里写的是本机绝对路径**（`I:\mar\...`、`C:\Users\Administrator\...`）。
  换机器请先改文件顶部的常量，或给支持的命令行参数传值。

## 脚本

| 脚本 | 作用 |
|---|---|
| `icon/gen_icons.py` | 从设计稿 JPEG 生成全套**图标资源**：自适应 bg/fg/mono 三层 + 5 档 legacy 位图 + 4 个变体图标（共用同一组图层），以及参考线预览图；`ic_launcher-web.png`（商店用图）**只产出一张**，变体的 `-web.png` 不在生成范围内 |
| `icon/install_icons.py` | 把 `stage/` 的产物装进工程，并删除被取代的 vector drawable |
| `icon/verify_install.py` | 逐文件 md5 比对 `stage/` 与工程，确认安装无遗漏、无残留旧资源 |
| `icon/mask_radius.py` | ★ 量各图层**墨迹到画布中心的最大距离**，对照 36dp / 33dp 判定是否会被遮罩裁切 |
| `icon/mask_preview.py` | ★ 把成品图标套上真实遮罩几何（圆 / 超椭圆 / 圆角方形）× 真实启动器尺寸渲染，叠 66dp 与 72dp 参考圆 |
| `icon/inspect_mono.py` | 单色层可读性检查：深色底合成、着色、24dp 降采样 |
| `icon/check_mono_num.py` | 单色层 alpha 分布审计（确认没有异常半透明像素） |
| `icon/thresh_probe.py` | 提高 alpha 阈值重测最大半径，用来区分**实心墨迹**与**抗锯齿边缘** |
| `regroup_more_page.py` | 把「更多」页 84 项设置重排进 5 个可折叠分组（迁移脚本，已在输出上加了幂等守卫） |
| `rename_app.py` | 品牌改名（应用名 / 散文 / 注释），范围限定在用户可见文案 |
| `verify_apk.py` | ★ 发布前验收（42 项）：产物身份、zip 对齐、图标逐密度、安全区、品牌残留、清单检查、元素零丢失、**包内文档与仓库源文件同源** |
| `apk_identity.py` | 打印最新 APK 的「文件名 / 字节数 / mtime / sha256」，可选 `--expect-bytes` / `--expect-sha256` 断言。验收的第 0 步：先证明你验的是刚构建出来的产物 |
| `check_readme.py` | ★ README / CHANGELOG 排版检查：同一份文本要同时被 GitHub GFM 和 App 内 flexmark 解析，`--fix` 可自动合并中文软换行 |
| `move_tag.py` | ★ 把已发布的标签重指到更新的提交。**当二进制被 `--clobber` 覆盖而标签留在原处时，Release 的自动源码归档就和它的安装包对不上了**，只有移动标签才能让归档重新生成 |
| `push.py` | 推送辅助（运行时从 `gh auth token` 取凭据，不落盘、不硬编码） |

## 图标工作流

```bash
# 1) 生成到 stage/（--src 可省略，默认指向设计稿的绝对路径）
python tools/icon/gen_icons.py \
    --res <stage>/res --preview <stage>/preview \
    --src "<设计稿>.jpeg"

# 2) 装进工程
python tools/icon/install_icons.py

# 3) 校验安装结果 + 安全区
python tools/icon/verify_install.py
python tools/icon/mask_radius.py
python tools/icon/mask_preview.py
```

> 设计稿（`.jpeg`）**不在本仓库内**，见 `--src`。生成器是确定性的：同样的输入产出逐字节相同的 PNG。

## 必须守住的不变量

### 1. 自适应图标的安全区是一个 **66dp 圆**，不是 72×72dp 方形

```
108dp 画布
├── 遮罩视口        72dp   → 系统圆形遮罩实际露出的直径（半径 36dp）
├── 保证可见       66dp   → 半径 33dp，任何合法凸遮罩都必须露出
└── 外层 18dp/边          被裁掉，只用于视差/动效
```

依据（非推测）：

- AOSP `AdaptiveIconDrawable`：`EXTRA_INSET_PERCENTAGE = 1/4` →
  `DEFAULT_VIEW_PORT_SCALE = 1/(1+2×1/4) = 2/3` → 视口 = 108 × 2/3 = 72dp；
  `SAFEZONE_SCALE = 66f/72f`
- 官方设计指南：任何合法遮罩都是凸多边形，中心到边缘不得小于 33dp

**验收判据是「墨迹到画布中心的最大距离 ≤ 33dp」，不是「外接矩形在 72×72 内」。**
后者是假通过——方形四角在圆外。字形有直角时，限制来自对角线：`bbox ≤ 66/√2 ≈ 46.7dp`。

当前各层实测 **31.8–32.0dp**，`0.00%` 墨迹出圈（由 `verify_apk.py` 断言）。

### 2. `android:key="@string/..."` 必须有对应的字符串定义

`android:key` 写成资源引用时，aapt2 会在 **link 期**解析它。缺定义不会在编译期报错，只在 link 期报
`resource string/xxx not found`——而且 AGP 默认把它渲染成没用的
`AAPT2 ... Unexpected error during link`，**不加 `--info` 看不到真实原因**。
分组 key 的字符串由 `regroup_more_page.py` 自动补齐。

### 3. 重排大型 preference XML 必须证明零丢失

`regroup_more_page.py` 在写盘前断言：所有原 `android:key` 出现且仅出现一次；
`verify_apk.py` 再断言打包后的 XML 元素数与源码一致（117/117）。

### 4. README 有两个消费者，排版必须同时成立

`README.md` / `README.en.md` **不只是 GitHub 首页**，`build.gradle` 还会把它们复制进 APK 资源：

```
copyReadmeDefault : README.en.md -> res/raw/readme.md        （所有语言的兜底）
copyReadmeChinese : README.md    -> res/raw-zh-rCN/readme.md （zh-rCN 自动选中）
```

也就是同一个文件要被 **两套解析器**（GitHub 的 GFM、App 内的 flexmark-java）渲染，两边都成立才算改对。
已知的两个分歧点：

- **中文软换行会渲染成多余空格。** CommonMark 把软换行输出成换行符，浏览器折叠为**一个空格**。
  英文里这是期望行为，中文里是错的：在「，」或「。」之后折行会凭空多出半个空格。
  → 中文散文段落不要在句中折行；`check_readme.py --fix` 可自动合并。
- **表格单元格不能含真实换行。** 一行必须是一个完整表格行，需要换行只能写 `<br>`。

另外首部的居中 `<div align="center">` 是**裸 HTML 块**：CommonMark 的 HTML 块到第一个空行为止，
所以块内不能出现空行，否则居中对后续内容失效。

```bash
python tools/check_readme.py          # 退出码非 0 表示有排版问题
python tools/check_readme.py --fix    # 只修 R1（合并软换行）
```

### 5. 脚本不要批量删除目录（环境护栏会拦下整个进程）

本机有安全护栏：**单轮删除文件数超过约 50 个会被拒绝**，并且拒绝发生在脚本进程内部，
表现为脚本**中途死掉**，而不是某个检查失败。典型症状：

```
[safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED] {"count":2429,"threshold":50,...}
```
紧接着脚本退出、没有任何 CHECK 输出——很容易被误读成「脚本有 bug」或「代码写错了」。
实测：`verify_apk.py` 原来用固定解包目录 + `shutil.rmtree()` 清空，删到 2400+ 个文件时整轮中止，
前 8 个 STEP 只输出到一半。

**正确做法是让脚本根本不需要删除**：`verify_apk.py` 现在每次 `tempfile.mkdtemp()` 解包到全新目录。
顺带还消除了「上一次解包残留文件污染本次结果」的隐患。不要试图绕过护栏。

### 6. 覆盖二进制资产后，标签必须跟着移动

GitHub Releases 里的 **Source code (zip/tar.gz) 是在线生成的，不是资产**，无法替换，
只能通过移动标签来刷新。所以 `gh release upload --clobber` 换掉 APK 之后，
如果标签还留在原提交，这个 Release 就变成「新安装包 + 旧源码」——而且不会报任何错。
`tools/move_tag.py` 就是干这个的，它强制要求目标是 `origin/main` 的祖先，并且只 **force-update**
引用、绝不删除标签（删掉会让 Release 与标签脱钩）。

## 发布

```bash
python tools/verify_apk.py            # 36 项检查，全绿才发
python tools/push.py                  # 推 main
gh release upload v1.0.0 ./MarkdownHelper-v1.0.0.apk --clobber
```

发布前务必 `./gradlew clean assembleFlavorDefaultDebug`：增量构建会多出约 4.6 MB 对齐填充。
