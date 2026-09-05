from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont

from wc4_font_builder.builder import BuildRequest, execute


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


def _make_font(path: Path) -> None:
    mapping = {
        0x20: "space",
        ord("A"): "A",
        ord("中"): "uni4E2D",
        ord("国"): "uni56FD",
        ord("國"): "uni570B",
        ord("與"): "uni8207",
    }
    glyph_order = [".notdef", ".null", "nonmarkingreturn", *mapping.values()]
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap(mapping)
    fb.setupGlyf({name: (_empty_glyph() if name in {".null", "nonmarkingreturn", "space"} else _box_glyph()) for name in glyph_order})
    fb.setupHorizontalMetrics({name: (600, 0) for name in glyph_order})
    fb.setupHorizontalHeader(ascent=800, descent=-200, lineGap=20)
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, sTypoLineGap=20, usWinAscent=800, usWinDescent=200)
    fb.setupNameTable({
        "familyName": "WC4 Builder Test",
        "styleName": "Regular",
        "uniqueFontIdentifier": "WC4 Builder Test Regular 1",
        "fullName": "WC4 Builder Test Regular",
        "psName": "WC4BuilderTest-Regular",
    })
    fb.setupPost()
    fb.setupMaxp()
    fb.save(path)


def test_shared_builder_workflow_builds_wc4_from_actual_tw_text(tmp_path: Path):
    source = tmp_path / "full.ttf"
    text = tmp_path / "stringtable_tw.ini"
    output = tmp_path / "subset.ttf"
    report_path = tmp_path / "subset.report.json"
    _make_font(source)
    text.write_text("label=中國與中国\nchar=₹\n", encoding="utf-8")

    report = execute(BuildRequest(
        source_font=source,
        text_inputs=[text],
        output_font=output,
        report_path=report_path,
        profile="wc4",
    ))

    assert output.is_file()
    assert report_path.is_file()
    assert report.missingRequired == []
    assert len(report.missingOptionalText) == 1
    assert report.uniqueTextCodepoints == 4
    font = TTFont(output)
    try:
        cmap = font.getBestCmap()
        assert {ord("中"), ord("国"), ord("國"), ord("與")} <= set(cmap)
    finally:
        font.close()


def test_shared_builder_analysis_does_not_write_font(tmp_path: Path):
    source = tmp_path / "full.ttf"
    text = tmp_path / "stringtable_cn.ini"
    _make_font(source)
    text.write_text("label=中国\n", encoding="utf-8")

    report = execute(BuildRequest(source_font=source, text_inputs=[text], analyze_only=True, profile="wc4"))

    assert report.analysisOnly is True
    assert report.missingRequired == []
    assert not list(tmp_path.glob("*subset*"))
