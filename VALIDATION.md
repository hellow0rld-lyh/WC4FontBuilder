# Validation

Canonical local validation for `WC4FontBuilderRealCorpusCompatibility/v1` and subsequent source changes:

```text
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m compileall -q src tests
git diff --check
git status --short --branch
```

The canonical test suite must synthesize its own font inputs and must not require proprietary/original font binaries or WC4 assets.

For `WC4FontBuilderRealCorpusCompatibility/v1`, an additional local real-corpus probe was run against external read-only inputs. Its evidence is recorded in `reports/WC4_REAL_CORPUS_COMPATIBILITY_V1.md`; generated fonts and JSON reports remain ignored local build artifacts. This probe supplements but does not replace the canonical synthetic suite.

Passing tests and real-corpus font generation alone do not constitute acceptance inside the actual game renderer. Renderer/device acceptance is a separate evidence class and, where completed, is recorded explicitly below.

For the Windows v1 package work unit, additionally run:

```text
.venv\Scripts\python.exe -c "from wc4_font_builder.gui import main; raise SystemExit(main(['--self-test']))"
.venv\Scripts\python.exe tools\build_windows.py
build\windows_v1\dist\WC4FontBuilder.exe --self-test
build\windows_v1\dist\wc4-font-build.exe --help
```

The packaged CLI must also complete one synthetic WC4-profile subset build and the resulting font must be reopened to verify every requested codepoint remains in cmap. Windows package validation supplements but does not replace the canonical pytest/compileall/diff/status checks.

Android 1.29 renderer acceptance is now recorded for the tested generated font through the visible Traditional Chinese language entry. Treat that as scoped manual behavior evidence, not proof for every language/font/layout combination.

## GitHub publication-prep validation

Before the first public push or a release-preparation commit, additionally verify:

```text
.venv\Scripts\python.exe -m pip install -e . --no-deps --no-build-isolation
.venv\Scripts\python.exe tools\build_windows.py
build\windows_v1\dist\WC4FontBuilder.exe --self-test
build\windows_v1\dist\wc4-font-build.exe --help
```

The release ZIP must contain the project MIT license, `THIRD_PARTY_NOTICES.txt`,
README, manifest, both executables, and the full license files copied from the
installed fontTools, PyInstaller, Python and Tcl/Tk distributions. Verify each
manifested support-file SHA-256 against the bytes inside the ZIP.

Before publication, scan the repository (excluding ignored build/venv/cache
outputs) for private-key/token patterns and machine-specific absolute paths, and
confirm Git tracks no font/APK/EXE binaries. Example paths such as `C:\path\...`
in README command snippets are not machine-specific evidence.

GitHub workflow files can be reviewed locally, but a hosted GitHub Actions run is
a separate validation state and remains NotRun until the repository is actually
pushed and the workflows execute on GitHub.
