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
    optional_characters: frozenset[str] = frozenset()
    profile: str = "generic"


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


def discover_wc4_stringtable_files(inputs: list[Path]) -> list[Path]:
    """Discover WC4 stringtable INI files without sweeping unrelated assets.

    An explicitly named file may have any basename but must be an INI. Directory
    inputs are intentionally restricted to ``stringtable_*.ini`` so XML comments,
    resource labels and other non-rendered strings cannot accidentally enlarge the
    generated game font.
    """

    discovered: set[Path] = set()
    for raw in inputs:
        path = raw.expanduser().resolve()
        if not path.exists():
            raise TextScanError(f"text input does not exist: {path}")
        if path.is_file():
            if path.suffix.casefold() != ".ini":
                raise TextScanError(f"WC4 profile requires an INI stringtable file: {path}")
            discovered.add(path)
            continue
        for candidate in path.rglob("*"):
            if not candidate.is_file():
                continue
            relative_parts = candidate.relative_to(path).parts[:-1]
            if any(part in DEFAULT_EXCLUDED_DIRS for part in relative_parts):
                continue
            name = candidate.name.casefold()
            if name.startswith("stringtable_") and candidate.suffix.casefold() == ".ini":
                discovered.add(candidate.resolve())
    return sorted(discovered, key=lambda item: str(item).casefold())


def scan_wc4_stringtables(inputs: list[Path]) -> ScanResult:
    """Parse WC4 stringtables by display semantics.

    Ordinary ``key=value`` values are required renderer text. The special ``char``
    directive declares runtime/dynamic characters and is optional: if the source
    font lacks one of those characters, the build reports it but does not fail.
    Full-line ``;``/``#`` comments and keys are never treated as display text.
    """

    files = discover_wc4_stringtable_files(inputs)
    if not files:
        raise TextScanError("no WC4 stringtable INI files discovered")

    required: set[str] = set()
    optional: set[str] = set()
    total = 0
    for path in files:
        text = read_text_strict(path)
        for line_number, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith((";", "#")):
                continue
            if "=" not in line:
                raise TextScanError(
                    f"malformed WC4 stringtable line without '=': {path}:{line_number}"
                )
            raw_key, value = line.split("=", 1)
            key = raw_key.strip()
            if not key:
                raise TextScanError(f"empty WC4 stringtable key: {path}:{line_number}")
            chars = glyph_relevant_characters(value)
            total += len(value)
            if key.casefold() == "char":
                optional.update(chars)
            else:
                required.update(chars)

    optional.difference_update(required)
    return ScanResult(
        tuple(files),
        frozenset(required),
        total,
        frozenset(optional),
        "wc4",
    )


def scan_extra_character_files(paths: list[Path]) -> frozenset[str]:
    chars: set[str] = set()
    for path in paths:
        resolved = path.expanduser().resolve()
        if not resolved.is_file():
            raise TextScanError(f"extra character file does not exist: {resolved}")
        chars.update(glyph_relevant_characters(read_text_strict(resolved)))
    return frozenset(chars)
