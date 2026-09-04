from wc4_font_builder.charset import SAFE_SETS, glyph_relevant_characters


def test_control_characters_are_not_glyph_requirements():
    assert glyph_relevant_characters("A\n中\tB") == {"A", "中", "B"}


def test_wc4_safe_set_extends_minimal_without_bulk_cjk():
    assert set(SAFE_SETS["minimal"]) < set(SAFE_SETS["wc4"])
    assert "A" in SAFE_SETS["wc4"]
    assert "。" in SAFE_SETS["wc4"]
    assert "中" not in SAFE_SETS["wc4"]
