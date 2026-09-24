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
| `icon/gen_icons.py` | 从设计稿 JPEG 生成全套图标：自适应 bg/fg/mono 三层 + 5 档 legacy 位图 + `ic_launcher-web.png` + 4 个变体图标，并输出参考线预览图 |
| `icon/install_icons.py` | 把 `stage/` 的产物装进工程，并删除被取代的 vector drawable |
| `icon/verify_install.py` | 逐文件 md5 比对 `stage/` 与工程，确认安装无遗漏、无残留旧资源 |
| `icon/mask_radius.py` | ★ 量各图层**墨迹到画布中心的最大距离**，对照 36dp / 33dp 判定是否会被遮罩裁切 |
| `icon/mask_preview.py` | ★ 把成品图标套上真实遮罩几何（圆 / 超椭圆 / 圆角方形）× 真实启动器尺寸渲染，叠 66dp 与 72dp 参考圆 |
| `icon/inspect_mono.py` | 单色层可读性检查：深色底合成、着色、24dp 降采样 |
| `icon/check_mono_num.py` | 单色层 alpha 分布审计（确认没有异常半透明像素） |
| `icon/thresh_probe.py` | 提高 alpha 阈值重测最大半径，用来区分**实心墨迹**与**抗锯齿边缘** |
| `regroup_more_page.py` | 把「更多」页 84 项设置重排进 5 个可折叠分组（迁移脚本，已在输出上加了幂等守卫） |
| `rename_app.py` | 品牌改名（应用名 / 散文 / 注释），范围限定在用户可见文案 |
| `verify_apk.py` | ★ 发布前验收：产物身份、逐密度图标、安全区、残留扫描、清单检查、元素零丢失 |
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

## 发布

```bash
python tools/verify_apk.py            # 36 项检查，全绿才发
python tools/push.py                  # 推 main
gh release upload v1.0.0 ./MarkdownHelper-v1.0.0.apk --clobber
```

发布前务必 `./gradlew clean assembleFlavorDefaultDebug`：增量构建会多出约 4.6 MB 对齐填充。
