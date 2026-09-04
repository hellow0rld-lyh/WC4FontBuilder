# Validation

Canonical local validation for `FontSubsetterFoundation/v1`:

```text
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m compileall -q src tests
git diff --check
git status --short --branch
```

The test suite must synthesize its own font inputs. Passing tests do not constitute acceptance inside the actual game renderer; real WC4 font replacement remains a separate manual acceptance work unit.
