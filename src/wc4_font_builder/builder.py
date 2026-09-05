from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .charset import SAFE_SETS, codepoints, glyph_relevant_characters
from .scanner import (
    DEFAULT_EXTENSIONS,
    scan_extra_character_files,
    scan_text,
    scan_wc4_stringtables,
)
from .subset import AnalysisReport, BuildReport, analyze_subset, build_subset, write_report


@dataclass(slots=True)
class BuildRequest:
    source_font: Path
    text_inputs: list[Path]
    output_font: Path | None = None
    report_path: Path | None = None
    analyze_only: bool = False
    profile: str = "wc4"
    extra_character_files: list[Path] = field(default_factory=list)
    extra_characters: str = ""
    safe_set: str | None = None
    retain_gids: bool = False
    allow_missing: bool = False
    extensions: set[str] | None = None


def execute(request: BuildRequest) -> AnalysisReport | BuildReport:
    if not request.text_inputs:
        raise ValueError("at least one text input is required")
    if not request.analyze_only and request.output_font is None:
        raise ValueError("output font is required for a build")

    if request.profile == "wc4":
        scan = scan_wc4_stringtables(request.text_inputs)
        default_safe_set = "none"
    elif request.profile == "generic":
        scan = scan_text(request.text_inputs, request.extensions or DEFAULT_EXTENSIONS)
        default_safe_set = "wc4"
    else:
        raise ValueError(f"unknown profile: {request.profile}")

    safe_set_name = request.safe_set or default_safe_set
    if safe_set_name not in SAFE_SETS:
        raise ValueError(f"unknown safe set: {safe_set_name}")

    extra_from_files = scan_extra_character_files(request.extra_character_files)
    literal_extra = glyph_relevant_characters(request.extra_characters)
    extra_chars = set(extra_from_files) | set(literal_extra)

    common = dict(
        source_font=request.source_font,
        text_codepoints=codepoints(set(scan.characters)),
        optional_text_codepoints=codepoints(set(scan.optional_characters)),
        explicit_extra_codepoints=codepoints(extra_chars),
        safe_codepoints=codepoints(SAFE_SETS[safe_set_name]),
        scanned_file_count=len(scan.files),
        scanned_text_characters=scan.total_text_characters,
        subset_profile=request.profile,
        retain_gids=request.retain_gids,
    )

    if request.analyze_only:
        report = analyze_subset(**common)
    else:
        report = build_subset(
            output_font=request.output_font,
            allow_missing=request.allow_missing,
            **common,
        )

    if request.report_path is not None:
        write_report(report, request.report_path)
    return report
