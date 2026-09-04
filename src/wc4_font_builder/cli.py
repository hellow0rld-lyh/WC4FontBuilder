from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .charset import SAFE_SETS, codepoints, glyph_relevant_characters
from .scanner import DEFAULT_EXTENSIONS, TextScanError, scan_extra_character_files, scan_text
from .subset import FontBuildError, build_subset, write_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="wc4-font-build",
        description="Build a compact OpenType font from the text actually used by a game/mod.",
    )
    parser.add_argument("--font", required=True, type=Path, help="full source OTF/TTF")
    parser.add_argument("--text", required=True, action="append", type=Path, help="text file or directory; repeatable")
    parser.add_argument("--output", required=True, type=Path, help="output subset font")
    parser.add_argument("--report", type=Path, help="optional JSON report path")
    parser.add_argument("--extra-chars-file", action="append", default=[], type=Path, help="file containing runtime/dynamic characters")
    parser.add_argument("--extra-char", action="append", default=[], help="literal extra characters; repeatable")
    parser.add_argument("--safe-set", choices=sorted(SAFE_SETS), default="wc4")
    parser.add_argument("--retain-gids", action="store_true", help="retain glyph ID holes for compatibility experiments")
    parser.add_argument("--allow-missing", action="store_true", help="do not fail if the source font lacks required text characters")
    parser.add_argument(
        "--extensions",
        default=",".join(sorted(ext.lstrip(".") for ext in DEFAULT_EXTENSIONS)),
        help="comma-separated extensions used when scanning directories",
    )
    return parser


def _format_summary(report) -> str:
    return (
        f"files={report.scannedFileCount} "
        f"text_codepoints={report.uniqueTextCodepoints} "
        f"glyphs={report.sourceGlyphs}->{report.outputGlyphs} "
        f"bytes={report.sourceBytes}->{report.outputBytes} "
        f"reduction={report.reductionPercent:.3f}% "
        f"metrics_preserved={str(report.metricsPreserved).lower()}"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    extensions = {item.strip() for item in args.extensions.split(",") if item.strip()}
    try:
        scan = scan_text(args.text, extensions)
        extra_from_files = scan_extra_character_files(args.extra_chars_file)
        literal_extra = glyph_relevant_characters("".join(args.extra_char))
        extra_chars = set(extra_from_files) | set(literal_extra)
        report = build_subset(
            source_font=args.font,
            output_font=args.output,
            text_codepoints=codepoints(set(scan.characters)),
            explicit_extra_codepoints=codepoints(extra_chars),
            safe_codepoints=codepoints(SAFE_SETS[args.safe_set]),
            scanned_file_count=len(scan.files),
            scanned_text_characters=scan.total_text_characters,
            retain_gids=args.retain_gids,
            allow_missing=args.allow_missing,
        )
        if args.report:
            write_report(report, args.report)
        print(_format_summary(report))
        if report.missingRequired:
            print(f"warning: source font missing {len(report.missingRequired)} required codepoints", file=sys.stderr)
        if report.missingSafe:
            print(f"note: source font lacks {len(report.missingSafe)} optional safe-set codepoints", file=sys.stderr)
        return 0
    except (TextScanError, FontBuildError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
