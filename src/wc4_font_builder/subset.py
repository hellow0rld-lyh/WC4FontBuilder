from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import fontTools
from fontTools import subset
from fontTools.ttLib import TTFont

from .charset import describe_codepoint


class FontBuildError(RuntimeError):
    pass


SUBSET_PROFILES = ("generic", "wc4")
WC4_LAYOUT_FEATURES = ("calt", "ccmp", "liga", "vert", "vrt2", "kern", "vpal")
WC4_EXTRA_DROP_TABLES = ("BASE",)


@dataclass(frozen=True)
class MetricSnapshot:
    unitsPerEm: int | None
    hheaAscent: int | None
    hheaDescent: int | None
    hheaLineGap: int | None
    typoAscender: int | None
    typoDescender: int | None
    typoLineGap: int | None
    winAscent: int | None
    winDescent: int | None


@dataclass(frozen=True)
class BuildReport:
    sourceFont: str
    outputFont: str
    sourceBytes: int
    outputBytes: int
    reductionPercent: float
    sourceGlyphs: int
    outputGlyphs: int
    scannedFileCount: int
    scannedTextCharacters: int
    uniqueTextCodepoints: int
    optionalTextCodepoints: int
    explicitExtraCodepoints: int
    safeCodepoints: int
    requestedCodepoints: int
    retainedRequestedCodepoints: int
    missingRequired: list[dict[str, str]]
    missingOptionalText: list[dict[str, str]]
    missingSafe: list[dict[str, str]]
    outputMissingExpected: list[dict[str, str]]
    subsetProfile: str
    layoutFeatures: list[str]
    dropTables: list[str]
    fontToolsVersion: str
    retainGids: bool
    sourceMetrics: MetricSnapshot
    outputMetrics: MetricSnapshot
    metricsPreserved: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def best_cmap(font: TTFont) -> dict[int, str]:
    cmap = font.getBestCmap()
    return cmap or {}


def snapshot_metrics(font: TTFont) -> MetricSnapshot:
    head = font.get("head")
    hhea = font.get("hhea")
    os2 = font.get("OS/2")
    return MetricSnapshot(
        unitsPerEm=getattr(head, "unitsPerEm", None),
        hheaAscent=getattr(hhea, "ascent", None),
        hheaDescent=getattr(hhea, "descent", None),
        hheaLineGap=getattr(hhea, "lineGap", None),
        typoAscender=getattr(os2, "sTypoAscender", None),
        typoDescender=getattr(os2, "sTypoDescender", None),
        typoLineGap=getattr(os2, "sTypoLineGap", None),
        winAscent=getattr(os2, "usWinAscent", None),
        winDescent=getattr(os2, "usWinDescent", None),
    )


def _descriptions(values: set[int]) -> list[dict[str, str]]:
    return [describe_codepoint(value) for value in sorted(values)]


def make_subset_options(profile: str, *, retain_gids: bool) -> subset.Options:
    if profile not in SUBSET_PROFILES:
        raise FontBuildError(f"unknown subset profile: {profile}")

    options = subset.Options()
    if profile == "generic":
        # Preserve the v1 compatibility-first behavior for non-WC4 callers.
        options.layout_features = ["*"]
        options.name_IDs = ["*"]
        options.name_languages = ["*"]
        options.name_legacy = True
        options.notdef_glyph = True
        options.notdef_outline = True
        options.recommended_glyphs = True
        options.recalc_bounds = True
    else:
        # This option set reproduces the stock Android NotoSans_cn.otf subset
        # shape from the matching Noto Sans CJK 1.004 source.
        options.layout_features = list(WC4_LAYOUT_FEATURES)
        options.drop_tables = list(
            dict.fromkeys([*options.drop_tables, *WC4_EXTRA_DROP_TABLES])
        )

    options.retain_gids = retain_gids
    options.recalc_timestamp = False
    return options


def build_subset(
    *,
    source_font: Path,
    output_font: Path,
    text_codepoints: set[int],
    optional_text_codepoints: set[int] | None = None,
    explicit_extra_codepoints: set[int],
    safe_codepoints: set[int],
    scanned_file_count: int,
    scanned_text_characters: int,
    subset_profile: str = "generic",
    retain_gids: bool = False,
    allow_missing: bool = False,
) -> BuildReport:
    source_font = source_font.expanduser().resolve()
    output_font = output_font.expanduser().resolve()
    if not source_font.is_file():
        raise FontBuildError(f"source font does not exist: {source_font}")
    if source_font == output_font:
        raise FontBuildError("output font must not overwrite the source font")

    try:
        font = TTFont(source_font, recalcTimestamp=False)
    except Exception as exc:
        raise FontBuildError(f"failed to open source font: {exc}") from exc

    source_cmap = best_cmap(font)
    source_metrics = snapshot_metrics(font)
    source_glyphs = len(font.getGlyphOrder())
    required = set(text_codepoints) | set(explicit_extra_codepoints)
    optional_text = set(optional_text_codepoints or ()) - required
    requested = required | optional_text | set(safe_codepoints)
    source_available = set(source_cmap)
    missing_required = required - source_available
    missing_optional_text = optional_text - source_available
    missing_safe = set(safe_codepoints) - source_available
    if missing_required and not allow_missing:
        font.close()
        details = ", ".join(item["codepoint"] for item in _descriptions(missing_required)[:20])
        suffix = " ..." if len(missing_required) > 20 else ""
        raise FontBuildError(f"source font is missing {len(missing_required)} required codepoints: {details}{suffix}")

    keep = requested & source_available
    options = make_subset_options(subset_profile, retain_gids=retain_gids)

    subsetter = subset.Subsetter(options=options)
    subsetter.populate(unicodes=sorted(keep))
    try:
        subsetter.subset(font)
        output_font.parent.mkdir(parents=True, exist_ok=True)
        font.save(output_font)
    except Exception as exc:
        raise FontBuildError(f"font subsetting failed: {exc}") from exc
    finally:
        font.close()

    try:
        output = TTFont(output_font, recalcTimestamp=False)
    except Exception as exc:
        raise FontBuildError(f"output font failed to reopen: {exc}") from exc
    output_cmap = best_cmap(output)
    output_metrics = snapshot_metrics(output)
    output_glyphs = len(output.getGlyphOrder())
    output.close()

    missing_output = keep - set(output_cmap)
    if missing_output:
        raise FontBuildError(
            "subset output lost expected codepoints: "
            + ", ".join(item["codepoint"] for item in _descriptions(missing_output)[:20])
        )

    source_bytes = source_font.stat().st_size
    output_bytes = output_font.stat().st_size
    reduction = 0.0 if source_bytes == 0 else (1.0 - output_bytes / source_bytes) * 100.0
    return BuildReport(
        sourceFont=str(source_font),
        outputFont=str(output_font),
        sourceBytes=source_bytes,
        outputBytes=output_bytes,
        reductionPercent=round(reduction, 3),
        sourceGlyphs=source_glyphs,
        outputGlyphs=output_glyphs,
        scannedFileCount=scanned_file_count,
        scannedTextCharacters=scanned_text_characters,
        uniqueTextCodepoints=len(text_codepoints),
        optionalTextCodepoints=len(optional_text),
        explicitExtraCodepoints=len(explicit_extra_codepoints),
        safeCodepoints=len(safe_codepoints),
        requestedCodepoints=len(requested),
        retainedRequestedCodepoints=len(keep),
        missingRequired=_descriptions(missing_required),
        missingOptionalText=_descriptions(missing_optional_text),
        missingSafe=_descriptions(missing_safe),
        outputMissingExpected=_descriptions(missing_output),
        subsetProfile=subset_profile,
        layoutFeatures=list(options.layout_features),
        dropTables=list(options.drop_tables),
        fontToolsVersion=fontTools.__version__,
        retainGids=retain_gids,
        sourceMetrics=source_metrics,
        outputMetrics=output_metrics,
        metricsPreserved=source_metrics == output_metrics,
    )


def write_report(report: BuildReport, path: Path) -> None:
    resolved = path.expanduser().resolve()
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
