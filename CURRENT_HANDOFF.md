# Current Handoff

Work-Unit-ID: WC4FontBuilderWindowsV1Package/v1
Repository: <repo>
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

将已通过 WC4 实际渲染验收的文本驱动 subset 核心收口为可直接使用的 Windows v1 工具：保留 CLI，新增中文 GUI，共用同一核心工作流，并生成本地单文件 EXE 工具包。

## Completion result

- 版本提升为 `1.0.0`。
- 新增共享 `BuildRequest -> execute()` 工作流；CLI 与 GUI 不再重复实现扫描、extra/safe 字符、coverage、subset 与报告逻辑。
- 新增中文 Tk GUI：源字体选择、多文本文件/目录输入、WC4/generic profile、输出字体、JSON 报告、额外字符/文件、安全字符集、retain-GID、allow-missing、覆盖分析和正式生成。
- GUI 的耗时 subset 在工作线程运行；工作线程只写线程安全队列，由 Tk 主线程轮询并更新界面，避免跨线程调用 Tk。
- 新增 Windows PyInstaller 打包入口，同时生成 `WC4FontBuilder.exe` 图形版和 `wc4-font-build.exe` 命令行版，并写入 `使用说明.txt` 与哈希 manifest。
- 新增共享工作流回归测试，覆盖 `stringtable_tw.ini` 中简繁混用按实际 Unicode 保留，以及 analysis-only 不写字体。
- README/VALIDATION 已更新 Windows v1 和实际游戏渲染验收边界。

## Windows package

Local ignored package:

```text
build/windows_v1/WC4FontBuilder-v1.0.0-windows-x64.zip
SHA-256: a13d507844b9ae38ed382bae021eb23168bc691a8f63ee22dfa2419fe7d25ebd
Bytes: 27380388

WC4FontBuilder.exe
SHA-256: 3e3b4fbdd50a7e211eb246cd485bdadef95b69e6c2bd3f31b5c57cd3128254b3
Bytes: 15488130

wc4-font-build.exe
SHA-256: 4d61f9af87d87826863d056a24d844accda43637551430cdc478fa4ab9afcd7d
Bytes: 12373912
```

No signing or remote publication was performed.

## Validation

- Core pytest after shared-workflow refactor: 17 passed.
- Python GUI self-test: passed.
- PyInstaller 6.22.2 / Python 3.14.6 Windows x64 build: passed for GUI and CLI one-file executables.
- Packaged GUI `--self-test`: passed; it constructs the complete hidden Tk widget tree, runs idle layout, and destroys cleanly.
- Packaged CLI `--help`: passed.
- Packaged CLI synthetic WC4-profile build: passed; 1 stringtable, 4 required codepoints, glyphs 8 -> 5, bytes 1032 -> 808, metrics preserved.
- Reopen of packaged-CLI output: `中/国/國/與` all present in cmap; missingRequired=0.
- Final canonical pytest/compileall/diff/status checks are required immediately before the local commit.

## Manual renderer/device acceptance

Android 1.29 WC4 manual behavior acceptance: Passed for the tested generated font. The generated subset font was placed into both `NotoSans_cn.otf` and `NotoSans_tw.otf` on the correct plaintext baseline so the visible Traditional Chinese entry necessarily exercised it; operator confirmed displayed characters were all normal.

This proves the tested v1 subset is accepted by the target renderer for that corpus. It does not claim exhaustive coverage of every source font, language, screen layout, fallback path or GID-sensitive boundary.

## State separation

- Research: Completed for v1 scope.
- Implementation: Completed.
- Synthetic/static validation: Passed.
- Windows package build: Passed.
- Packaged executable smoke/functional validation: Passed.
- Android game renderer acceptance: Passed for tested corpus/font path.
- Windows GUI manual click-through acceptance: NotRun; automated packaged-widget construction passed.
- Remote publication/release: NotRun / unauthorized.

## Failure pre-mortem / remaining risk

- A different full source font can still lack required characters; fail-closed coverage remains mandatory.
- A future stringtable may introduce characters not present in the previous generated font; rebuild from current text rather than reusing an old subset blindly.
- Renderer acceptance is scoped to the tested Android 1.29 path; unusual fallback, long-layout, vertical text or stable-GID assumptions can still require focused acceptance.
- PyInstaller bundles are unsigned; Windows may display reputation/SmartScreen warnings. Signing was intentionally not performed.
- GUI has automated construction/self-test but no human desktop click-through in this work unit.

## Next work unit

`WC4FontBuilderWindowsGuiManualAcceptance/v1` — optional manual desktop click-through and field-feedback fixes. Core v1 functionality and local Windows package are already complete.
