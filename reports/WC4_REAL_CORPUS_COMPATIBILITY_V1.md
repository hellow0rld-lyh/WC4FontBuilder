# WC4 Real Corpus Compatibility v1

Work-Unit-ID: `WC4FontBuilderRealCorpusCompatibility/v1`

Repository: `WC4FontBuilder` repository root

## Scope

Validate the standalone font builder against real WC4 Android Chinese text and the matching-generation full Noto Sans CJK source, then encode only the evidence-backed WC4-specific scanning and subset policy in this repository.

This work unit does **not** modify any WC4 product repository, APK, SO, game asset, device, or system font. Full/original font binaries and WC4 assets remain external read-only inputs and are not committed.

## External read-only inputs

| Input | Size | SHA-256 |
| --- | ---: | --- |
| External read-only `NotoSansCJKsc-Black-v1.004.otf` | 17,324,316 B | `4f64a0adc660f0066baf25a361cb5f2206952d3e71d05dcade25088c89857c4d` |
| WC4 Android 1.28 `assets\font\NotoSans_cn.otf` | 615,000 B | `545fa24d0794de8570a1a2fd0aabc1492eb828893bdde09ae360e5a7786b7054` |
| Current WC4 Android 1.28 `assets\stringtable_cn.ini` | 832,112 B | `526df6148cd147b3f3533b83166c55a1ed72207c1cda849e2dacafd79e663427` |

The full font and stock game font identify as `Noto Sans CJK SC Black`, version `1.004`, and share the relevant vertical metrics.

## Research result

The stock Android font contains 2,484 glyphs and 2,453 cmap characters. The matching full 1.004 source contains 65,535 glyphs and 44,683 cmap characters.

WC4 `stringtable_cn.ini` is not safely modeled as arbitrary raw text. The evidence-backed semantics are:

- ordinary non-comment `key=value` values are renderer-required text;
- the special `char=` value declares runtime/dynamic characters;
- keys and full-line `;`/`#` comments are not renderer text;
- unrelated XML/JSON assets must not be swept into the font merely because they contain Chinese comments or resource labels.

For the current real Chinese stringtable, the semantic scanner finds 2,445 unique required characters and 29 characters that occur only in `char=`. The union is 2,474 requested characters. Nine optional-only characters are absent even from the complete Noto Sans CJK SC Black 1.004 source and therefore remain reportable fallback cases rather than build failures:

`U+010D č`, `U+0142 ł`, `U+0E3F ฿`, `U+20A6 ₦`, `U+20AA ₪`, `U+20B1 ₱`, `U+20B9 ₹`, `U+20BA ₺`, `U+20BD ₽`.

Compared with the stock game font, current required text needs exactly 12 additional Han characters:

`U+5080 傀`, `U+5121 儡`, `U+5974 奴`, `U+5C3E 尾`, `U+5F08 弈`, `U+6A61 橡`, `U+755C 畜`, `U+77A9 瞩`, `U+7BEE 篮`, `U+7CB9 粹`, `U+80F6 胶`, `U+8BFB 读`.

## Stock-like subset policy

The evidence-backed WC4 profile uses fontTools subsetting with these layout features:

`calt`, `ccmp`, `liga`, `vert`, `vrt2`, `kern`, `vpal`.

It adds `BASE` to fontTools' normal drop-table list and keeps `recalc_timestamp=false`. Generic profile behavior remains unchanged and continues to use the compatibility-first full layout closure from the foundation work unit.

When the full 1.004 source is subset using the exact stock cmap, the implemented WC4 profile produces:

- 614,372 B versus stock 615,000 B;
- exactly 2,484 glyphs in both;
- identical glyph order;
- byte-identical `CFF `, `cmap`, `name`, `hmtx`, `vmtx`, and `VORG` table data;
- `GSUB` and `GPOS` are not byte-identical (`502` vs stock `952` bytes and `4,720` vs stock `4,876` bytes respectively).

Therefore the profile is stock-shaped and reproduces the core glyph/cmap/metric payload, but **byte-for-byte OTF identity is not claimed**.

## Current-corpus build result

Local ignored artifact:

`build\wc4_real_corpus\NotoSans_cn.otf`

SHA-256: `93390a8832f974f3391f0d47123a5b1c21c61731ab06a7980b1a38922c2c7783`

Result:

- output size: 618,084 B;
- output glyphs: 2,496;
- output cmap: 2,465;
- required source-font missing characters: 0;
- optional profile missing characters: 9;
- output lost expected characters: 0;
- stock cmap removed characters: 0;
- newly added cmap characters: exactly the 12 Han characters listed above;
- source/output core vertical metrics: preserved;
- reduction from full source: 96.432%.

The local JSON evidence is generated under `build\wc4_real_corpus\NotoSans_cn.report.json` and is ignored by Git together with generated font binaries.

## State separation

- Research: **Completed** — real WC4 corpus, stock font, and matching full source compared.
- Implementation: **Completed** — semantic WC4 scanner, optional dynamic character handling, and stock-like subset profile implemented while generic behavior is retained.
- Static validation: **Passed** — synthetic tests plus exact cmap/metric/table comparisons passed for the evidence described above.
- Build: **Passed** — real current-corpus OTF generated locally with zero missing required characters.
- Desktop renderer acceptance: **NotRun**.
- APK integration: **NotRun**.
- Device/game behavior acceptance: **NotRun in this historical work unit**. A later Android 1.29 renderer acceptance is recorded in `CURRENT_HANDOFF.md` and `README.md`.

## Remaining Unknown / boundary

At the time of this work unit, the generated OTF had not yet been exercised in the actual WC4 renderer. That historical boundary was later advanced by a scoped Android 1.29 renderer acceptance; see `CURRENT_HANDOFF.md`. The acceptance remains corpus/path scoped and does not prove every fallback, layout or GID-sensitive boundary.

## Next work unit

`WC4FontBuilderRendererAcceptance/v1` — consume the ignored generated OTF through a separately authorized disposable WC4 test-package workflow and verify representative old text plus all 12 newly covered Han characters in the real renderer. No APK/device action is authorized by this report itself.
