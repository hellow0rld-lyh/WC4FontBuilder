# Repository Policy

Policy-ID: WC4-FONT-BUILDER-REPO-001
Status: Active

## Allowed

- Python source for text scanning and OpenType subsetting.
- Unit/integration tests that synthesize fonts at runtime.
- Documentation, schemas, examples, and local validation scripts.
- Disposable local `.venv`, reports, and generated fonts ignored by Git.

## Forbidden by default

- Committing original/full font binaries or game assets.
- Copying WC4 repository source into this repository.
- Establishing a formal source/package dependency on WC4 repositories without portfolio authority.
- Remote writes, release publication, signing, system-wide dependency installation, or Git history rewrite.

## Compatibility posture

Use `fontTools.subset` rather than implementing sfnt/CFF/TrueType rewriting manually. Preserve layout closure and core font metrics, fail closed when required text characters are absent, and make compatibility-sensitive choices such as glyph-ID retention explicit flags.
