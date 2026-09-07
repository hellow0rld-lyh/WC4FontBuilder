from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


REQUIRED_FILES = {
    "WC4FontBuilder.exe",
    "wc4-font-build.exe",
    "README.md",
    "LICENSE",
    "THIRD_PARTY_NOTICES.txt",
    "使用说明.txt",
    "manifest.json",
    "licenses/fonttools-LICENSE.txt",
    "licenses/fonttools-LICENSE.external.txt",
    "licenses/pyinstaller-COPYING.txt",
    "licenses/python-LICENSE.txt",
    "licenses/tcl-tk-license.terms",
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_archive(path: Path) -> dict[str, object]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise RuntimeError(f"release archive does not exist: {path}")

    with zipfile.ZipFile(path) as archive:
        file_names = [name for name in archive.namelist() if not name.endswith("/")]
        roots = {name.split("/", 1)[0] for name in file_names if "/" in name}
        if len(roots) != 1:
            raise RuntimeError(f"release archive must have one top-level directory, found: {sorted(roots)}")
        root = next(iter(roots))
        relative_names = {
            name[len(root) + 1 :]
            for name in file_names
            if name.startswith(root + "/")
        }
        missing = sorted(REQUIRED_FILES - relative_names)
        if missing:
            raise RuntimeError(f"release archive is missing required files: {missing}")

        manifest_name = f"{root}/manifest.json"
        manifest = json.loads(archive.read(manifest_name).decode("utf-8"))

        checked: list[str] = []
        for section in ("artifacts", "supportFiles"):
            entries = manifest.get(section)
            if not isinstance(entries, dict):
                raise RuntimeError(f"manifest section is missing or invalid: {section}")
            for relative, metadata in entries.items():
                if not isinstance(metadata, dict) or "sha256" not in metadata:
                    raise RuntimeError(f"manifest hash metadata is invalid: {section}/{relative}")
                archive_name = f"{root}/{relative}"
                try:
                    data = archive.read(archive_name)
                except KeyError as exc:
                    raise RuntimeError(f"manifested file missing from archive: {relative}") from exc
                actual = sha256_bytes(data)
                expected = str(metadata["sha256"]).lower()
                if actual != expected:
                    raise RuntimeError(
                        f"manifest hash mismatch for {relative}: expected {expected}, got {actual}"
                    )
                if "bytes" in metadata and len(data) != int(metadata["bytes"]):
                    raise RuntimeError(
                        f"manifest byte-size mismatch for {relative}: expected {metadata['bytes']}, got {len(data)}"
                    )
                checked.append(relative)

    return {
        "archive": str(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "manifestedFilesVerified": len(checked),
        "requiredFilesPresent": len(REQUIRED_FILES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a WC4 Font Builder Windows release ZIP.")
    parser.add_argument("archive", type=Path)
    parser.add_argument("--write-checksum", type=Path)
    args = parser.parse_args()

    result = verify_archive(args.archive)
    if args.write_checksum is not None:
        checksum_path = args.write_checksum.expanduser().resolve()
        checksum_path.parent.mkdir(parents=True, exist_ok=True)
        checksum_path.write_text(
            f"{result['sha256']}  {Path(str(result['archive'])).name}\n",
            encoding="utf-8",
            newline="\n",
        )
        result["checksumFile"] = str(checksum_path)

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
