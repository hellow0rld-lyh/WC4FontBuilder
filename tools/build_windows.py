from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
import tkinter
import zipfile
from importlib.metadata import distribution, version
from pathlib import Path

import PyInstaller.__main__

from wc4_font_builder import __version__

ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = ROOT / "build" / "windows_v1"
DIST = BUILD_ROOT / "dist"
WORK = BUILD_ROOT / "work"
SPEC = BUILD_ROOT / "spec"
PACKAGE = BUILD_ROOT / f"WC4FontBuilder-v{__version__}-windows-x64"
ARCHIVE = BUILD_ROOT / f"WC4FontBuilder-v{__version__}-windows-x64.zip"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(name: str, entry: str, *, windowed: bool) -> Path:
    args = [
        str(ROOT / entry),
        "--name", name,
        "--onefile",
        "--noconfirm",
        "--paths", str(ROOT / "src"),
        "--distpath", str(DIST),
        "--workpath", str(WORK / name),
        "--specpath", str(SPEC),
        "--windowed" if windowed else "--console",
    ]
    PyInstaller.__main__.run(args)
    suffix = ".exe" if sys.platform == "win32" else ""
    result = DIST / f"{name}{suffix}"
    if not result.is_file():
        raise RuntimeError(f"PyInstaller output missing: {result}")
    return result


def write_usage(path: Path) -> None:
    path.write_text(
        "WC4 Font Builder v1\n"
        "====================\n\n"
        "推荐直接运行 WC4FontBuilder.exe。\n\n"
        "基本流程：\n"
        "1. 选择完整源 OTF/TTF。\n"
        "2. WC4 模式下添加一个或多个 stringtable_*.ini，或包含这些文件的目录。\n"
        "3. 选择输出字体与可选 JSON 报告。\n"
        "4. 可先点‘只分析覆盖’，确认必需字符缺失为 0。\n"
        "5. 点‘生成精简字体’。\n\n"
        "WC4 模式不会按‘简中/繁中’标签预设字符，而是保留文本里实际出现的 Unicode 字符。\n"
        "正式生成默认缺一项必需字符就停止，避免悄悄生成缺字字体。\n\n"
        "命令行用户可运行 wc4-font-build.exe --help。\n",
        encoding="utf-8",
        newline="\n",
    )


def find_distribution_license(distribution_name: str, suffix: str) -> Path:
    dist = distribution(distribution_name)
    normalized_suffix = suffix.replace("\\", "/")
    for item in dist.files or ():
        normalized = str(item).replace("\\", "/")
        if normalized.endswith(normalized_suffix):
            resolved = Path(dist.locate_file(item))
            if resolved.is_file():
                return resolved
    raise RuntimeError(f"license file not found for {distribution_name}: {suffix}")


def copy_support_files() -> dict[str, dict[str, object]]:
    copied: list[Path] = []
    for source, relative in (
        (ROOT / "README.md", Path("README.md")),
        (ROOT / "LICENSE", Path("LICENSE")),
        (ROOT / "THIRD_PARTY_NOTICES.txt", Path("THIRD_PARTY_NOTICES.txt")),
        (find_distribution_license("fonttools", "/licenses/LICENSE"), Path("licenses/fonttools-LICENSE.txt")),
        (
            find_distribution_license("fonttools", "/licenses/LICENSE.external"),
            Path("licenses/fonttools-LICENSE.external.txt"),
        ),
        (
            find_distribution_license("pyinstaller", "/licenses/COPYING.txt"),
            Path("licenses/pyinstaller-COPYING.txt"),
        ),
        (
            ROOT / "third_party_licenses" / "python-LICENSE.txt",
            Path("licenses/python-LICENSE.txt"),
        ),
        (
            ROOT / "third_party_licenses" / "tcl-tk-license.terms",
            Path("licenses/tcl-tk-license.terms"),
        ),
    ):
        if not source.is_file():
            raise RuntimeError(f"required release support file missing: {source}")
        destination = PACKAGE / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(destination)

    return {
        path.relative_to(PACKAGE).as_posix(): {"bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in copied
    }


def main() -> int:
    for directory in (BUILD_ROOT, DIST, WORK, SPEC, PACKAGE):
        directory.mkdir(parents=True, exist_ok=True)

    gui = build("WC4FontBuilder", "tools/windows_gui_entry.py", windowed=True)
    cli = build("wc4-font-build", "tools/windows_cli_entry.py", windowed=False)

    packaged_gui = PACKAGE / gui.name
    packaged_cli = PACKAGE / cli.name
    shutil.copy2(gui, packaged_gui)
    shutil.copy2(cli, packaged_cli)
    write_usage(PACKAGE / "使用说明.txt")
    support_files = copy_support_files()

    manifest = {
        "product": "WC4 Font Builder",
        "version": __version__,
        "platform": "windows-x64",
        "buildEnvironment": {
            "python": platform.python_version(),
            "tk": str(tkinter.TkVersion),
            "fontTools": version("fonttools"),
            "pyInstaller": version("pyinstaller"),
        },
        "artifacts": {
            packaged_gui.name: {"bytes": packaged_gui.stat().st_size, "sha256": sha256(packaged_gui)},
            packaged_cli.name: {"bytes": packaged_cli.stat().st_size, "sha256": sha256(packaged_cli)},
        },
        "supportFiles": support_files,
    }
    (PACKAGE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        package_files = sorted(
            (path for path in PACKAGE.rglob("*") if path.is_file()),
            key=lambda item: item.relative_to(PACKAGE).as_posix().casefold(),
        )
        for source in package_files:
            relative = source.relative_to(PACKAGE).as_posix()
            archive.write(source, f"{PACKAGE.name}/{relative}")

    result = {
        **manifest,
        "archive": {"path": str(ARCHIVE), "bytes": ARCHIVE.stat().st_size, "sha256": sha256(ARCHIVE)},
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
