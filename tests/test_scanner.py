from pathlib import Path

import pytest

from wc4_font_builder.scanner import TextScanError, discover_text_files, scan_text


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
