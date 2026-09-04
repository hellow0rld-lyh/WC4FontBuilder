from pathlib import Path

import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from wc4_font_builder.subset import FontBuildError, build_subset, write_report


def _empty_glyph():
    pen = TTGlyphPen(None)
    return pen.glyph()


def _box_glyph():
    pen = TTGlyphPen(None)
    pen.moveTo((50, 0))
    pen.lineTo((550, 0))
    pen.lineTo((550, 700))
    pen.lineTo((50, 700))
    pen.closePath()
    return pen.glyph()


def make_font(path: Path) -> None:
    glyph_order = [".notdef", ".null", "nonmarkingreturn", "space", "A", "B", "uni4E2D"]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({0x20: "space", 0x41: "A", 0x42: "B", 0x4E2D: "uni4E2D"})
    fb.setupGlyf({
        ".notdef": _box_glyph(),
        ".null": _empty_glyph(),
        "nonmarkingreturn": _empty_glyph(),
        "space": _empty_glyph(),
        "A": _box_glyph(),
        "B": _box_glyph(),
        "uni4E2D": _box_glyph(),
    })
    fb.setupHorizontalMetrics({name: (600, 0) for name in glyph_order})
    fb.setupHorizontalHeader(ascent=800, descent=-200, lineGap=20)
    fb.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        sTypoLineGap=20,
        usWinAscent=800,
        usWinDescent=200,
    )
    fb.setupNameTable({
        "familyName": "WC4 Test Font",
        "styleName": "Regular",
        "uniqueFontIdentifier": "WC4 Test Font Regular 1",
        "fullName": "WC4 Test Font Regular",
        "psName": "WC4TestFont-Regular",
    })
    fb.setupPost()
    fb.setupMaxp()
    fb.save(path)


def test_subset_keeps_requested_characters_and_metrics(tmp_path: Path):
    source = tmp_path / "full.otf"
    output = tmp_path / "subset.otf"
    report_path = tmp_path / "report.json"
    make_font(source)

    report = build_subset(
        source_font=source,
        output_font=output,
        text_codepoints={0x41, 0x4E2D},
        explicit_extra_codepoints=set(),
        safe_codepoints={0x20},
        scanned_file_count=1,
        scanned_text_characters=2,
    )
    write_report(report, report_path)

    subset = TTFont(output)
    cmap = subset.getBestCmap()
    subset.close()
    assert set(cmap) == {0x20, 0x41, 0x4E2D}
    assert report.outputGlyphs < report.sourceGlyphs
    assert report.metricsPreserved is True
    assert report.outputMissingExpected == []
    assert report_path.read_text(encoding="utf-8").endswith("\n")


def test_missing_required_codepoint_fails_closed(tmp_path: Path):
    source = tmp_path / "full.otf"
    make_font(source)
    with pytest.raises(FontBuildError, match="missing 1 required codepoints"):
        build_subset(
            source_font=source,
            output_font=tmp_path / "subset.otf",
            text_codepoints={0x41, 0x56FD},
            explicit_extra_codepoints=set(),
            safe_codepoints=set(),
            scanned_file_count=1,
            scanned_text_characters=2,
        )
