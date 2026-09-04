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

```powershell
.venv\Scripts\wc4-font-build.exe `
  --font C:\path\full.otf `
  --text C:\path\texts `
  --output C:\path\wc4_subset.otf `
  --report C:\path\wc4_subset.report.json
```

多个输入可以重复 `--text`：

```powershell
wc4-font-build --font full.otf --text data --text localization.json --output subset.otf
```

额外动态字符：

```powershell
wc4-font-build --font full.otf --text data --extra-chars-file extra_chars.txt --output subset.otf
```

兼容选项：

- `--safe-set wc4`：默认，小型安全集；
- `--safe-set minimal`：只补可打印 ASCII、NBSP、全角空格；
- `--safe-set none`：只保留实际文本/显式额外字符；
- `--retain-gids`：保留 glyph ID 空洞，给依赖稳定 GID 的旧渲染器做兼容试验，会牺牲一部分体积；
- `--allow-missing`：源字体缺少实际文本字符时不失败，仅用于调查；正式构建默认 fail closed。

## 文本扫描

默认递归扫描这些扩展名：

`txt, json, xml, csv, tsv, ini, cfg, yaml, yml, properties`。

文件按 UTF-8/UTF-8-SIG 读取；遇到 NUL 或解码错误会报错，不会静默跳过。目录中的 `.git`、`.venv`、`build`、`dist`、`node_modules`、`__pycache__` 默认排除。

## 报告

报告包含源/输出字节数、缩减比例、源/输出 glyph 数、扫描文件数、唯一文本字符数、安全字符数、请求字符总数、源字体缺失的必需字符/安全字符、输出覆盖校验以及关键 metrics 对比。

## 当前边界

这是独立工具仓，不是 WC4 正式四仓之一，也不建立跨仓源码依赖。实际替换进游戏后的排版、fallback、渲染器缓存/GID 假设等必须在后续真实字库验收中验证。
