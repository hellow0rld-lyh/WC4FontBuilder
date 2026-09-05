# Current Handoff

Work-Unit-ID: WC4FontBuilderGitHubPublicationPrep/v1
Repository: WC4FontBuilder repository root
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

Prepare the completed v1.0.0 source tree and Windows package for a future public
GitHub first push and GitHub Release without performing any remote write, history
rewrite, signing or tag creation in this work unit.

## Completion result

- Added a project MIT `LICENSE`.
- Added `THIRD_PARTY_NOTICES.txt`, including the important boundary that source
  fonts/generated font subsets and WC4 assets are not covered by the project MIT
  license.
- `pyproject.toml` now exposes MIT license metadata, contributor author metadata,
  keywords and supported-Python classifiers.
- Added `RELEASE_CHECKLIST.md` with first-push and v1.0.0 release gates.
- Added GitHub `CI` workflow for Python 3.10/3.12/3.14.
- Added Windows-package workflow for manual runs and `v*` tag pushes. The workflow
  builds and validates the ZIP and uploads a workflow artifact; it does not create
  a GitHub Release automatically.
- Current GitHub action majors were checked against upstream on 2026-09-05; the
  workflows use `actions/checkout@v7`, `actions/setup-python@v7`, and
  `actions/upload-artifact@v7`.
- Windows packaging now copies README, project license, third-party notices and
  full fontTools/PyInstaller/Python/Tcl-Tk license texts into the release ZIP.
- `manifest.json` records Python/Tk/fontTools/PyInstaller versions plus hashes for
  executables and release support files.
- Sanitized machine-specific repository/external-input paths in tracked evidence.
- Historical real-corpus report now makes clear that its old renderer NotRun state
  was superseded by the later scoped Android 1.29 renderer acceptance.
- Governance/authority documents remain tracked; they contain no detected secret
  material and remain required for future local work units.

## Windows package after publication prep

```text
build/windows_v1/WC4FontBuilder-v1.0.0-windows-x64.zip
SHA-256: cffe2ed2f7ab8c4826a03337a2dae820074d221ba86b616e813d0627b59c20ca
Bytes: 27417844

WC4FontBuilder.exe
SHA-256: 3e3b4fbdd50a7e211eb246cd485bdadef95b69e6c2bd3f31b5c57cd3128254b3
Bytes: 15488130

wc4-font-build.exe
SHA-256: 6f9466bb5707b06825b8d1fe82ae9a01c330aacd8c5de9a17dfcd001f23fd7b4
Bytes: 12373911
```

The ZIP contains all required release support/license files and their bytes match
the `manifest.json` SHA-256 records. No signing was performed.

## Validation

- Editable package metadata/install after publication metadata changes: Passed.
- Canonical pytest: 17 passed.
- Canonical compileall: Passed.
- Windows package rebuild: Passed.
- Packaged GUI full-widget `--self-test`: Passed.
- Packaged CLI `--help`: Passed.
- Packaged CLI synthetic WC4 build: Passed; `中/国/國/與` all present and
  `missingRequired=0`.
- Release ZIP required-file check: Passed.
- Release ZIP support-file hash verification against manifest: Passed.
- Secret/private-key/common-token-pattern scan over publishable worktree: no match.
- Machine-specific absolute-path scan: only intentional `C:\path\...` README
  examples remain; user/machine paths were removed from tracked evidence.
- Git-tracked font/TTF/WOFF/EXE/APK binary check: none.
- GitHub hosted CI/Windows-package execution: NotRun; requires first remote push.

## State separation

- Publication-prep research: Completed.
- Repository/documentation implementation: Completed.
- Static/local validation: Passed.
- Windows build/package validation: Passed.
- Existing Android renderer behavior acceptance: Passed for the tested corpus/path.
- GitHub hosted workflow validation: NotRun.
- Remote repository creation/binding/push: NotRun / unauthorized in this work unit.
- Git tag / GitHub Release publication: NotRun / unauthorized.
- Signing: NotRun / unauthorized.
- Windows GUI human click-through: NotRun; automated packaged widget construction
  remains Passed.

## Remaining blocker / decision

All current commits use the configured author email
`helloworld-lyh@outlook.com`. The four commits predating this publication-prep
work unit also contain 12 historical machine-path occurrences
(`<user-path>...` / `<temp-path>...`) even though the current
tree is sanitized. None are credentials, and the pre-publication history scan
found no private-key/common-token pattern and no binary blobs.

If the email or historical paths should not become public, sanitize them before
the first push. Changing existing commits requires a separately authorized local
history rewrite; it was intentionally not performed in this work unit.

There is currently no Git remote and no release tag. The final GitHub owner/repo
name is therefore intentionally not invented in `pyproject.toml` project URLs.

## Next work unit

`WC4FontBuilderGitHubFirstPublish/v1` — after explicit remote-write authorization
and the Git-history privacy decision, bind the exact GitHub repository, push
`main`, verify hosted CI, create `v1.0.0`, and publish the exact validated Windows
ZIP as the Release asset.
