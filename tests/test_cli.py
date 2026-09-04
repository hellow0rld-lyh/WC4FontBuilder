from pathlib import Path

import json
import pytest
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

from wc4_font_builder.cli import main


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


def test_analyze_does_not_require_output_and_writes_optional_report(tmp_path: Path, capsys):
    source = tmp_path / "full.otf"
    text = tmp_path / "text.txt"
    report_path = tmp_path / "analysis.json"
    make_font(source)
    text.write_text("A中国", encoding="utf-8")

    result = main([
        "--analyze",
        "--font", str(source),
        "--text", str(text),
        "--extra-chars", "B",
        "--safe-set", "none",
        "--report", str(report_path),
    ])

    captured = capsys.readouterr()
    assert result == 0
    assert "analysis=true" in captured.out
    assert "missing_required=1" in captured.out
    assert "warning: source font missing 1 required codepoints" in captured.err
    data = json.loads(report_path.read_text(encoding="utf-8"))
    assert data["analysisOnly"] is True
    assert data["explicitExtraCodepoints"] == 1
    assert data["missingRequired"][0]["char"] == "国"
    assert not list(tmp_path.glob("*subset*"))


def test_build_requires_output_unless_analyze(tmp_path: Path):
    source = tmp_path / "full.otf"
    text = tmp_path / "text.txt"
    make_font(source)
    text.write_text("A", encoding="utf-8")

    with pytest.raises(SystemExit) as exc:
        main(["--font", str(source), "--text", str(text)])

    assert exc.value.code == 2
