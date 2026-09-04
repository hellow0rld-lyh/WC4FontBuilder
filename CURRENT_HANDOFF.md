# Current Handoff

Work-Unit-ID: WC4FontBuilderRealCorpusCompatibility/v1
Repository: <legacy-repo>
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

Qualify the font builder against real WC4 Android Chinese text and the matching-generation full Noto Sans CJK source, then encode an evidence-backed WC4 profile without creating a dependency on any WC4 product repository.

## Completion result

- Added `--profile wc4` while preserving the generic foundation profile.
- WC4 directory discovery is restricted to `stringtable_*.ini`; unrelated XML/JSON assets are not swept into the font.
- Ordinary stringtable values are required and remain fail-closed.
- `char=` dynamic characters are optional/reportable and do not block the build when the matching source font itself lacks them.
- WC4 subset options use the stock-like layout feature set `calt, ccmp, liga, vert, vrt2, kern, vpal` and drop `BASE` in addition to fontTools defaults.
- Real current-corpus build completed at 618,084 bytes / 2,496 glyphs / 2,465 cmap characters with zero missing required characters and preserved core vertical metrics.
- Compared with stock `NotoSans_cn.otf`, the output removes no cmap character and adds exactly 12 currently required Han characters.
- Rebuilding the stock cmap from the matching full 1.004 source produces 614,372 bytes / 2,484 glyphs with identical glyph order and byte-identical CFF/cmap/name/hmtx/vmtx/VORG tables. GSUB/GPOS remain structurally different, so byte-identical OTF equivalence is not claimed.
- Detailed evidence: `reports/WC4_REAL_CORPUS_COMPATIBILITY_V1.md`.

## State separation

- Research: Completed.
- Implementation: Completed.
- Static validation: Passed.
- Real-corpus build: Passed.
- Desktop renderer acceptance: NotRun.
- APK integration: NotRun.
- Device/game behavior acceptance: NotRun.

## Boundary

No WC4 repository, APK, SO, device, system font, or remote resource was modified. Full/original fonts and game assets remained external read-only inputs and are not committed.

## Remaining Unknown

Actual WC4 renderer behavior is still unverified. Static coverage, metrics, stock-shaped table output, and successful OTF generation do not prove renderer/fallback/cache/GID behavior.

## Next work unit

WC4FontBuilderRendererAcceptance/v1 — through a separately authorized disposable WC4 test-package workflow, verify representative stock text plus the 12 newly covered Han characters in the actual renderer. APK/device actions are not authorized by this handoff alone.
