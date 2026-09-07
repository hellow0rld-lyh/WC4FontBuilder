# Current Handoff

Work-Unit-ID: WC4FontBuilderGitHubFirstPublish/v1
Repository: WC4FontBuilder repository root
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

Complete the first public v1.0.0 publication from the sanitized public repository,
without moving or rewriting the already-public release tag. Product behavior is
fixed; the remaining work is the hosted Windows package/release path.

## Fixed public release identity

- Remote: `https://github.com/hellow0rld-lyh/WC4FontBuilder.git`.
- Release commit: `9da99c3b807c30262f93af5ec2f880934e46e803`.
- Public annotated tag: `v1.0.0` -> release commit above.
- `main` was pushed to that release commit and the hosted `CI` workflow passed.
- Machine-path/privacy sanitization was completed before publication; the existing
  author email remains intentionally public by user decision.
- The tag is public and must not be moved/recreated as part of this recovery.

## First tag-workflow result

The first tag-triggered `Windows package` run did not complete publication:

- Workflow run: `34111876059`.
- Job: `101709749280` (`package`).
- `actions/checkout`, `actions/setup-python`, dependency installation and
  `Canonical tests` all Passed.
- `Build Windows package` Failed with exit code 1.
- Packaged GUI/CLI checks, release-ZIP verification, artifact upload and the
  GitHub Release publication step were therefore Skipped.
- The tag page existed, but there were no v1.0.0 Windows ZIP/checksum assets; it
  was not treated as a completed Release.

## Hosted-build root cause / forward fix

The package script incorrectly assumed that runtime license files existed under
fixed `sys.base_prefix` Python/Tk paths. That is true for the locally installed
CPython 3.14.6 used during preflight but is not a valid `setup-python` contract.
GitHub's current Windows Python tool-cache package selected by the floating `3.14`
request was inspected and contains no license files in the downloaded package.

Forward fix:

- Windows release Python is pinned to `3.14.6` instead of floating `3.14`.
- Full Python 3.14.6 Windows runtime `LICENSE.txt` and the paired Tcl/Tk 8.6.15
  `license.terms` are tracked under `third_party_licenses/` with provenance and
  SHA-256 records.
- `tools/build_windows.py` now copies those tracked license inputs instead of
  assuming they exist in `sys.base_prefix`.
- fontTools/PyInstaller license discovery remains package-metadata based and
  fail-closed.
- The workflow has a one-time forward-recovery path: only a `main` commit whose
  message is exactly `release: recover v1.0.0 package` can publish/update the
  existing `v1.0.0` Release from `main`. Normal future `main` pushes do not
  republish v1.0.0; tag and manual package behavior remain available.
- Recovery publication uses GitHub's ephemeral repository token; no local
  credential is read or exported.

## Product identity across the recovery

`git diff v1.0.0 -- src` is empty. The recovery tree does not change any runtime
font-scanning/subsetting/GUI/CLI source under `src/`; it changes only packaging,
license/provenance and publication workflow material. Therefore a recovery-built
v1.0.0 executable embeds the same product source as the public tag.

## Recovery-candidate local validation

- Canonical pytest: 17 passed.
- `compileall` over `src tests tools`: Passed.
- Windows package rebuild on the pinned local Python 3.14.6 environment: Passed.
- Packaged GUI `--self-test`: Passed.
- Packaged CLI `--help`: Passed.
- Exact release ZIP verification: Passed; 12 required files present and 10
  manifested executable/support files matched byte sizes and SHA-256 values.
- `git diff --check`: Passed.
- Current local recovery ZIP:
  `build/windows_v1/WC4FontBuilder-v1.0.0-windows-x64.zip`.
- Current local recovery ZIP SHA-256:
  `5b1fde54cb5f9ff971f0ac3e47e8078334f0d704befbf6afcde2858d2f38f226`.
- GUI EXE SHA-256 remains:
  `3e3b4fbdd50a7e211eb246cd485bdadef95b69e6c2bd3f31b5c57cd3128254b3`.
- CLI EXE SHA-256 remains:
  `6f9466bb5707b06825b8d1fe82ae9a01c330aacd8c5de9a17dfcd001f23fd7b4`.

The hosted recovery ZIP/checksum produced by GitHub Actions will be authoritative
for the public Release even if ZIP metadata causes its archive SHA-256 to differ
from this local preflight archive.

## Publication authorization / risk boundary

The user explicitly authorized completing this publication work unit, including
remote writes and GitHub Release publication. The public tag already exists, so
this recovery is strictly forward-only. No tag movement/deletion, history rewrite,
signing, destructive cleanup, unrelated credential handling, APK/device action,
or WC4 product-repository modification is authorized or needed.

## Hosted recovery / publication result

The forward recovery completed successfully without moving or rewriting the
public tag:

- Recovery commit: `e8efcc7b9fed073e34091dedca551de4cd870d68`.
- Recovery workflow run: `34112985954` (`Windows package`).
- Hosted job: `101713236366` (`package`).
- Hosted workflow conclusion: **success**.
- `Install build dependencies`: Passed.
- `Canonical tests`: Passed.
- `Build Windows package`: Passed.
- `Packaged GUI self-test`: Passed.
- `Packaged CLI smoke test`: Passed.
- `Verify release archive`: Passed.
- `Upload Windows package`: Passed.
- `Publish GitHub Release`: Passed.
- Release publication timestamp: `2026-09-07T10:46:57Z`.
- Public Release: `WC4 Font Builder v1.0.0`, non-draft and non-prerelease.
- Published Windows ZIP:
  `WC4FontBuilder-v1.0.0-windows-x64.zip` (29,385,229 bytes).
- Hosted ZIP SHA-256:
  `c65f5b07e3ca2452f9704b6383ba68e3413f82a553655447de88021815da8710`.
- Published checksum file:
  `WC4FontBuilder-v1.0.0-windows-x64.zip.sha256.txt`.
- The checksum file records the exact same hosted ZIP SHA-256 above.

The public `v1.0.0` annotated tag remains fixed at
`9da99c3b807c30262f93af5ec2f880934e46e803`; the recovery commit is a
forward-only packaging/license/workflow fix and `git diff v1.0.0 -- src` remains
empty.

## State separation

- Product implementation: Completed for v1.0.0.
- Git-history privacy sanitization: Completed.
- Local release/recovery validation: Passed.
- Public source repository / release commit: Published.
- Final-main CI for release commit: Passed.
- `v1.0.0` public tag: Published/fixed.
- First hosted Windows tag workflow: Failed at package build; retained as failure
  evidence and superseded by the successful forward recovery run.
- Forward recovery Windows workflow: Passed.
- GitHub Release Windows ZIP/checksum assets: Published and checksum-verified.
- Signing: NotRun / unsigned by design.
- Existing Android 1.29 renderer acceptance: Passed for the previously tested
  corpus/path; not repeated by this publication-only work unit.

## Next boundary

`WC4FontBuilderGitHubFirstPublish/v1` is complete. No publication blocker remains.
Any further feature work, packaging change, signing, new release, or formal WC4
portfolio integration is a separate work unit and requires its own applicable
authority/risk decision.
