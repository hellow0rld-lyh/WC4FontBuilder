from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .charset import SAFE_SETS, codepoints, glyph_relevant_characters
from .scanner import (
    DEFAULT_EXTENSIONS,
    TextScanError,
    scan_extra_character_files,
    scan_text,
    scan_wc4_stringtables,
)
from .subset import FontBuildError, SUBSET_PROFILES, analyze_subset, build_subset, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wc4-font-build",
        description="Build a compact OpenType font from the text actually used by a game/mod.",
    )
    parser.add_argument("--font", required=True, type=Path, help="full source OTF/TTF")
    parser.add_argument(
        "--text",
        required=True,
        action="append",
        type=Path,
        help="text file or directory; repeatable and files/directories may be mixed",
    )
    parser.add_argument("--output", type=Path, help="output subset font; required unless --analyze is used")
    parser.add_argument("--report", type=Path, help="optional JSON report path")
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="analyze character coverage without writing a subset font",
    )
    parser.add_argument(
        "--profile",
        choices=SUBSET_PROFILES,
        default="generic",
        help="generic scanner/subsetter or WC4 stringtable/stock-compatible profile",
    )
    parser.add_argument("--extra-chars-file", action="append", default=[], type=Path, help="file containing runtime/dynamic characters")
    parser.add_argument(
        "--extra-char",
        "--extra-chars",
        dest="extra_char",
        action="append",
        default=[],
        help="literal extra characters; repeatable",
    )
    parser.add_argument(
        "--safe-set",
        choices=sorted(SAFE_SETS),
        default=None,
        help="optional safety set; defaults to wc4 for generic profile and none for WC4 profile",
    )
    parser.add_argument("--retain-gids", action="store_true", help="retain glyph ID holes for compatibility experiments")
    parser.add_argument("--allow-missing", action="store_true", help="do not fail if the source font lacks required text characters")
    parser.add_argument(
        "--extensions",
        default=",".join(sorted(ext.lstrip(".") for ext in DEFAULT_EXTENSIONS)),
        help="comma-separated extensions used when scanning directories",
    )
    return parser


def _format_build_summary(report) -> str:
    return (
        f"profile={report.subsetProfile} "
        f"files={report.scannedFileCount} "
        f"text_codepoints={report.uniqueTextCodepoints} "
        f"optional_text_codepoints={report.optionalTextCodepoints} "
        f"glyphs={report.sourceGlyphs}->{report.outputGlyphs} "
        f"bytes={report.sourceBytes}->{report.outputBytes} "
        f"reduction={report.reductionPercent:.3f}% "
        f"metrics_preserved={str(report.metricsPreserved).lower()}"
    )


def _format_analysis_summary(report) -> str:
    return (
        f"analysis=true "
        f"profile={report.subsetProfile} "
        f"files={report.scannedFileCount} "
        f"text_codepoints={report.uniqueTextCodepoints} "
        f"optional_text_codepoints={report.optionalTextCodepoints} "
        f"extra_codepoints={report.explicitExtraCodepoints} "
        f"safe_codepoints={report.safeCodepoints} "
        f"requested_codepoints={report.requestedCodepoints} "
        f"supported_codepoints={report.sourceSupportedRequestedCodepoints} "
        f"missing_required={len(report.missingRequired)} "
        f"missing_optional={len(report.missingOptionalText)} "
        f"missing_safe={len(report.missingSafe)} "
        f"source_glyphs={report.sourceGlyphs} "
        f"source_bytes={report.sourceBytes}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.analyze and args.output is None:
        parser.error("--output is required unless --analyze is used")
    extensions = {item.strip() for item in args.extensions.split(",") if item.strip()}
    try:
        if args.profile == "wc4":
            scan = scan_wc4_stringtables(args.text)
            default_safe_set = "none"
        else:
            scan = scan_text(args.text, extensions)
            default_safe_set = "wc4"
        safe_set_name = args.safe_set or default_safe_set
        extra_from_files = scan_extra_character_files(args.extra_chars_file)
        literal_extra = glyph_relevant_characters("".join(args.extra_char))
        extra_chars = set(extra_from_files) | set(literal_extra)
        common = dict(
            source_font=args.font,
            text_codepoints=codepoints(set(scan.characters)),
            optional_text_codepoints=codepoints(set(scan.optional_characters)),
            explicit_extra_codepoints=codepoints(extra_chars),
            safe_codepoints=codepoints(SAFE_SETS[safe_set_name]),
            scanned_file_count=len(scan.files),
            scanned_text_characters=scan.total_text_characters,
            subset_profile=args.profile,
            retain_gids=args.retain_gids,
        )
        if args.analyze:
            report = analyze_subset(**common)
            summary = _format_analysis_summary(report)
        else:
            report = build_subset(
                output_font=args.output,
                allow_missing=args.allow_missing,
                **common,
            )
            summary = _format_build_summary(report)
        if args.report:
            write_report(report, args.report)
        print(summary)
        if report.missingRequired:
            print(f"warning: source font missing {len(report.missingRequired)} required codepoints", file=sys.stderr)
        if report.missingOptionalText:
            print(
                f"note: source font lacks {len(report.missingOptionalText)} optional profile codepoints",
                file=sys.stderr,
            )
        if report.missingSafe:
            print(f"note: source font lacks {len(report.missingSafe)} optional safe-set codepoints", file=sys.stderr)
        return 0
    except (TextScanError, FontBuildError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
