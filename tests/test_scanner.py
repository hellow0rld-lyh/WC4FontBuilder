from pathlib import Path

import pytest

from wc4_font_builder.scanner import (
    TextScanError,
    discover_text_files,
    discover_wc4_stringtable_files,
    scan_text,
    scan_wc4_stringtables,
)


def test_directory_scan_is_recursive_and_extension_filtered(tmp_path: Path):
    (tmp_path / "a.txt").write_text("中国A", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "b.json").write_text('{"name":"B"}', encoding="utf-8")
    (nested / "skip.bin").write_bytes(b"ignored")
    ignored = tmp_path / ".venv"
    ignored.mkdir()
    (ignored / "hidden.txt").write_text("X", encoding="utf-8")

    files = discover_text_files([tmp_path])
    assert [path.name for path in files] == ["a.txt", "b.json"]
    result = scan_text([tmp_path])
    assert {"中", "国", "A", "B"} <= set(result.characters)
    assert "X" not in result.characters


def test_nul_input_fails_closed(tmp_path: Path):
    path = tmp_path / "bad.txt"
    path.write_bytes(b"abc\x00def")
    with pytest.raises(TextScanError):
        scan_text([path])


def test_wc4_stringtable_scan_separates_required_and_optional_text(tmp_path: Path):
    path = tmp_path / "stringtable_cn.ini"
    path.write_text(
        "\ufeff; 注释里的字不应进入字体\n"
        "country_name=中国 A\n"
        "char= A₹€\n"
        "general_intro=读取\n",
        encoding="utf-8",
    )

    result = scan_wc4_stringtables([path])

    assert result.profile == "wc4"
    assert {"中", "国", "A", "读", "取"} <= set(result.characters)
    assert "注" not in result.characters
    assert "c" not in result.characters
    assert set(result.optional_characters) == {"₹", "€"}


def test_wc4_directory_scan_ignores_unrelated_assets(tmp_path: Path):
    (tmp_path / "stringtable_cn.ini").write_text("name=中国\n", encoding="utf-8")
    (tmp_path / "layout.xml").write_text("<!-- 不应扫描 -->", encoding="utf-8")
    (tmp_path / "other.ini").write_text("name=也不扫描\n", encoding="utf-8")

    files = discover_wc4_stringtable_files([tmp_path])

    assert [path.name for path in files] == ["stringtable_cn.ini"]


def test_wc4_malformed_non_comment_line_fails_closed(tmp_path: Path):
    path = tmp_path / "stringtable_cn.ini"
    path.write_text("valid=中国\nbroken line\n", encoding="utf-8")

    with pytest.raises(TextScanError, match="without '='"):
        scan_wc4_stringtables([path])


def test_multiple_file_and_directory_inputs_are_merged(tmp_path: Path):
    direct = tmp_path / "direct.txt"
    direct.write_text("简A", encoding="utf-8")
    folder = tmp_path / "texts"
    folder.mkdir()
    (folder / "nested.txt").write_text("繁B", encoding="utf-8")

    result = scan_text([direct, folder])

    assert {"简", "A", "繁", "B"} <= set(result.characters)
    assert len(result.files) == 2


def test_wc4_profile_uses_actual_characters_not_language_slot_name(tmp_path: Path):
    path = tmp_path / "stringtable_tw.ini"
    path.write_text("name=中国與中國\n", encoding="utf-8")

    result = scan_wc4_stringtables([path])

    assert {"中", "国", "與", "國"} <= set(result.characters)
