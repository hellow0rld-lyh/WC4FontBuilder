# AGENTS.md — WC4 Font Builder

## Repository role

This is a standalone local tooling repository for building text-driven subset OpenType fonts. It is intentionally outside the formal WC4 four-repository product graph and must not become a source/package dependency of `reconstruction`, `game`, `scenario-editor`, or `so` without a separate WC4 portfolio governance work unit.

## Start of every work unit

1. Read `PROJECT_IDENTITY.md`, `REPOSITORY_POLICY.md`, `VALIDATION.md`, and `CURRENT_HANDOFF.md`.
2. Check branch, full HEAD, Git status, and repository boundary.
3. Keep original/full fonts as external read-only inputs; never commit proprietary font binaries.
4. Separate implementation, static validation, build/package, and manual acceptance states.

## Git and risk

- Local source edits, tests, disposable build outputs, and unsigned local commits are allowed for an explicitly authorized work unit.
- No push, release publication, signing, system-wide installation, history rewrite, destructive cleanup, or credential handling without separate authorization.
- Finish with `python -m pytest`, `python -m compileall -q src tests`, `git diff --check`, and a clean Git status after the local commit.
