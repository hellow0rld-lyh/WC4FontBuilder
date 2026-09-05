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
