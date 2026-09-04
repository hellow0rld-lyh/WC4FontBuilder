from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .charset import glyph_relevant_characters

DEFAULT_EXTENSIONS = {
    ".txt", ".json", ".xml", ".csv", ".tsv", ".ini", ".cfg",
    ".yaml", ".yml", ".properties",
}
DEFAULT_EXCLUDED_DIRS = {
    ".git", ".venv", "build", "dist", "node_modules", "__pycache__",
}


class TextScanError(RuntimeError):
    pass


@dataclass(frozen=True)
class ScanResult:
    files: tuple[Path, ...]
    characters: frozenset[str]
    total_text_characters: int


def _normalize_extensions(extensions: set[str] | None) -> set[str]:
    values = extensions or DEFAULT_EXTENSIONS
    return {value.lower() if value.startswith(".") else f".{value.lower()}" for value in values}


def discover_text_files(inputs: list[Path], extensions: set[str] | None = None) -> list[Path]:
    allowed = _normalize_extensions(extensions)
    discovered: set[Path] = set()
    for raw in inputs:
        path = raw.expanduser().resolve()
        if not path.exists():
            raise TextScanError(f"text input does not exist: {path}")
        if path.is_file():
            discovered.add(path)
            continue
        for candidate in path.rglob("*"):
            if not candidate.is_file():
                continue
            relative_parts = candidate.relative_to(path).parts[:-1]
            if any(part in DEFAULT_EXCLUDED_DIRS for part in relative_parts):
                continue
            if candidate.suffix.lower() in allowed:
                discovered.add(candidate.resolve())
    return sorted(discovered, key=lambda item: str(item).casefold())


def read_text_strict(path: Path) -> str:
    data = path.read_bytes()
    if b"\x00" in data:
        raise TextScanError(f"NUL byte found; refusing probable binary file: {path}")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise TextScanError(f"UTF-8 decode failed for {path}: {exc}") from exc


def scan_text(inputs: list[Path], extensions: set[str] | None = None) -> ScanResult:
    files = discover_text_files(inputs, extensions)
    if not files:
        raise TextScanError("no text files discovered")
    chars: set[str] = set()
    total = 0
    for path in files:
        text = read_text_strict(path)
        total += len(text)
        chars.update(glyph_relevant_characters(text))
    return ScanResult(tuple(files), frozenset(chars), total)

def scan_extra_character_files(paths: list[Path]) -> frozenset[str]:
    chars: set[str] = set()
    for path in paths:
        resolved = path.expanduser().resolve()
        if not resolved.is_file():
            raise TextScanError(f"extra character file does not exist: {resolved}")
        chars.update(glyph_relevant_characters(read_text_strict(resolved)))
    return frozenset(chars)
