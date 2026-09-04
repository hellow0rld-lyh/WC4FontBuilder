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

Passing tests and real-corpus font generation do not constitute acceptance inside the actual game renderer. WC4 font replacement remains a separate manual renderer/device acceptance work unit.
