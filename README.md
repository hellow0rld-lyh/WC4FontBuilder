# WC4 Font Builder

根据游戏/Mod 实际文本，从完整 OTF/TTF 自动生成精简 OpenType 字库。

第一版目标不是“简单按 Unicode 删字形”，而是：

1. 扫描文本目录与文件；
2. 汇总真正需要显示的字符；
3. 补充一个很小的 WC4 安全字符集（ASCII、常用中西文标点等）；
4. 使用 `fontTools.subset` 做 OpenType-aware subset，让 GSUB/GPOS、复合字形等依赖由成熟库处理；
5. 重新打开输出字体，验证必需字符覆盖率；
6. 比较关键纵向 metrics，输出 JSON 报告。

## 安装（仓内隔离环境）

```powershell
py -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

## 使用

通用模式保持第一版行为：

```powershell
.venv\Scripts\wc4-font-build.exe `
  --font C:\path\full.otf `
  --text C:\path\texts `
  --output C:\path\wc4_subset.otf `
  --report C:\path\wc4_subset.report.json
```

WC4 原版兼容模式使用 `--profile wc4`：

```powershell
.venv\Scripts\wc4-font-build.exe `
  --profile wc4 `
  --font C:\path\NotoSansCJKsc-Black.otf `
  --text C:\path\stringtable_cn.ini `
  --output C:\path\NotoSans_cn.otf `
  --report C:\path\NotoSans_cn.report.json
```

WC4 profile 不会把整个 `assets` 目录中的 XML/JSON 注释和资源标记机械加入字库。显式传入文件时要求 INI；传入目录时只发现 `stringtable_*.ini`。普通 `key=value` 的 value 是必需字符，源字体缺失时 fail closed；特殊 `char=` 行是动态/可选字符，缺失只记录并提示。注释和 key 不参与字符集。WC4 profile 默认 `--safe-set none`，因为原版动态字符已经由 `char=` 声明；仍可显式覆盖 `--safe-set`。

多个输入可以重复 `--text`，文件和目录可以混合：

```powershell
wc4-font-build --font full.otf --text data --text localization.json --output subset.otf
```

字符提取不根据“简中/繁中”等语言槽位或文件名做转换或过滤，只保留输入文本实际出现的 Unicode 字符。因此即使 `stringtable_tw.ini` 实际装的是简体中文，或同一份文本简繁混用，也会按真实内容生成字库。

额外动态字符既可以直接传入，也可以从文件读取：

```powershell
wc4-font-build --font full.otf --text data --extra-chars "0123456789+-" --output subset.otf
wc4-font-build --font full.otf --text data --extra-chars-file extra_chars.txt --output subset.otf
```

只分析、不生成字体：

```powershell
wc4-font-build --analyze --profile wc4 --font full.otf --text stringtable_cn.ini --report analysis.json
```

`--analyze` 不要求 `--output`，会报告扫描文件数、Required/Dynamic/Extra/Safe 字符数量、源字体实际覆盖数量和缺失字符，但不会写出 subset OTF。正常构建模式仍必须指定 `--output`。

兼容选项：

- `--profile generic`：默认，保持第一版通用扫描与保守 OpenType layout closure；
- `--profile wc4`：按 WC4 stringtable 语义扫描，并使用从 Android 原版字库实测得到的 stock-like subset 配置；
- `--safe-set wc4`：generic profile 默认，小型安全集；
- `--safe-set minimal`：只补可打印 ASCII、NBSP、全角空格；
- `--safe-set none`：只保留实际文本/显式额外字符；
- `--retain-gids`：保留 glyph ID 空洞，给依赖稳定 GID 的旧渲染器做兼容试验，会牺牲一部分体积；
- `--allow-missing`：源字体缺少实际文本字符时不失败，仅用于调查；正式构建默认 fail closed。

## 文本扫描

默认递归扫描这些扩展名：

`txt, json, xml, csv, tsv, ini, cfg, yaml, yml, properties`。

文件按 UTF-8/UTF-8-SIG 读取；遇到 NUL 或解码错误会报错，不会静默跳过。目录中的 `.git`、`.venv`、`build`、`dist`、`node_modules`、`__pycache__` 默认排除。

## 报告

构建报告包含源/输出字节数、缩减比例、源/输出 glyph 数、扫描文件数、唯一必需文本字符数、仅动态/可选字符数、显式额外字符数、安全字符数、请求字符总数、源字体缺失的必需/可选/安全字符、输出覆盖校验、实际 subset profile、layout feature/drop-table 配置、fontTools 版本以及关键 metrics 对比。分析模式报告同样记录字符来源和缺字情况，但只读取源字体，不创建输出字体。

## WC4 真实语料验证

`WC4FontBuilderRealCorpusCompatibility/v1` 已用 Android 1.28 当前中文 `stringtable_cn.ini` 与同代 `Noto Sans CJK SC Black 1.004` 完整母库验证：当前输出为 618,084 bytes / 2,496 glyphs / 2,465 cmap 字符；原版 `NotoSans_cn.otf` 为 615,000 bytes / 2,484 glyphs / 2,453 cmap 字符。输出未移除原版 cmap 字符，只新增当前文本实际需要的 12 个汉字；必需字符缺失为 0，母库本身不覆盖的 9 个 `char=` 动态字符只作为 optional 提示。关键纵向 metrics 保持一致。

用原版 cmap 反向重建时，WC4 profile 得到 614,372 bytes / 2,484 glyphs，glyph order 与原版一致，且 CFF、cmap、name、hmtx、vmtx、VORG 表逐字节一致；GSUB/GPOS 仍有小幅结构差异，因此不能声明生成文件与原版 OTF 逐字节等价。详见 `reports/WC4_REAL_CORPUS_COMPATIBILITY_V1.md`。

## 当前边界

这是独立工具仓，不是 WC4 正式四仓之一，也不建立跨仓源码依赖。实际替换进游戏后的排版、fallback、渲染器缓存/GID 假设等必须在后续真实字库验收中验证。
