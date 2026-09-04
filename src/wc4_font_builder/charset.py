from __future__ import annotations

import string
import unicodedata

MINIMAL_SAFE_CHARS = "".join(chr(codepoint) for codepoint in range(0x20, 0x7F)) + "\u00a0\u3000"
WC4_EXTRA_SAFE_CHARS = (
    "，。！？：；、（）【】《》〈〉“”‘’…—·"
    "％＋－×÷＝＜＞￥€£°℃№"
    "→←↑↓★☆◆◇●○※"
)

SAFE_SETS = {
    "none": "",
    "minimal": MINIMAL_SAFE_CHARS,
    "wc4": MINIMAL_SAFE_CHARS + WC4_EXTRA_SAFE_CHARS,
}


def glyph_relevant_characters(text: str) -> set[str]:
    """Return characters that are expected to map to visible/selectable glyphs.

    Newline/tab/control characters are formatting instructions, not glyph coverage
    requirements. Format characters are retained because shaping engines may use
    them even when they do not have an independent glyph.
    """
    result: set[str] = set()
    for char in text:
        if char in {"\r", "\n", "\t"}:
            continue
        if unicodedata.category(char) == "Cc":
            continue
        result.add(char)
    return result


def codepoints(characters: set[str] | str) -> set[int]:
    return {ord(char) for char in characters}


def describe_codepoint(codepoint: int) -> dict[str, str]:
    char = chr(codepoint)
    return {
        "codepoint": f"U+{codepoint:04X}",
        "char": char,
        "name": unicodedata.name(char, "<unnamed>"),
    }
