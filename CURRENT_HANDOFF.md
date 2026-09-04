# Current Handoff

Work-Unit-ID: WC4FontBuilderInitialUsability/v1
Repository: <repo>
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

收口第一版 Mod 字库工作流：不依赖语言标签，接受一个完整源字体和任意多个文本文件/目录，保留现有 WC4 stringtable 有效内容识别，并增加只分析不生成字体的覆盖检查。

## Completion result

- 仓库已迁移到 `<repo>`，仍保持独立 Git 仓，不成为 WC4 主仓源码依赖。
- `--text` 继续支持重复传入，并明确允许文件与目录混合。
- 字符提取仍只依据文本实际 Unicode 内容，不根据简中/繁中槽位、文件名做转换或过滤。
- WC4 profile 继续只扫描 `stringtable_*.ini`；普通 value 为 required，`char=` 为 dynamic/optional，key 与整行注释不进入字体。
- 已增加 `--extra-chars` 作为现有 `--extra-char` 的直观别名；`--extra-chars-file` 保持可用。
- 已增加 `--analyze`：不要求 `--output`，只读取源字体并报告字符覆盖、缺失和请求规模，不生成 subset OTF。
- 正常构建模式仍要求 `--output`，原有 fail-closed 缺字策略和 WC4 subset profile 保持不变。
- 覆盖计算抽成共享逻辑，分析和实际构建使用同一套 required/optional/extra/safe 集合计算，降低两条路径漂移风险。
- 新增回归覆盖：分析模式、正常模式 output 必填、文件+目录混合输入、繁中槽名中简繁字符混用、分析覆盖统计。

## Validation

- `.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider`: 15 passed.
- `.venv\Scripts\python.exe -m compileall -q src tests`: passed.
- `git diff --check`: passed.
- 迁移后 Python import 已确认来自新仓 `<repo>\src`。
- WC4 真实语料回归已用报告中 SHA-256 完全匹配的 Android 1.28 `stringtable_cn.ini` 与 Noto Sans CJK SC Black 1.004 母库复跑：618,084 B / 2,496 glyphs / 2,465 cmap / required missing 0 / optional missing 9。
- 本轮回归 OTF SHA-256 为 `93390a8832f974f3391f0d47123a5b1c21c61731ab06a7980b1a38922c2c7783`，与迁移前基线 OTF 完全一致，证明本轮 coverage 重构未改变 WC4 正常构建字节输出。

## State separation

- Repository relocation: Completed. 旧路径内容已清空；Windows 仍有进程占用旧空目录句柄，空目录本身暂未能删除。
- Implementation: Completed.
- Synthetic/static validation: Passed.
- Real-corpus regression after this refactor: Passed；输出与上一基线逐字节同 SHA-256。
- Desktop renderer acceptance: NotRun.
- APK integration: NotRun.
- Device/game behavior acceptance: NotRun.

## Failure pre-mortem / remaining risk

- 最大剩余风险仍是游戏实际渲染器行为；静态 cmap/metrics 与生成成功不能证明 fallback/cache/GID 行为。
- `--analyze` 只报告源字体覆盖，不预测 subset 后字节大小；实际大小仍以正式构建结果为准。
- 对未知普通文本格式，generic profile 仍按文本内容扫描；WC4 INI 应使用 `--profile wc4` 才能排除 key/comment 等无关内容。
- 原 `.venv\pyvenv.cfg` 的创建命令可能保留旧路径历史字符串，但 editable import 已重新绑定并实测从新仓加载，不影响当前运行。

## Next work unit

`WC4FontBuilderRendererAcceptance/v1` — 使用生成的精简 OTF 进入实际 WC4 字体替换/渲染验收，重点验证 fallback、缓存/GID 假设、长文本和新增汉字显示。
