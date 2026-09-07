# Current Handoff

Work-Unit-ID: WC4FontBuilderGitHubFirstPublish/v1
Repository: WC4FontBuilder repository root
Product-Or-Route: WC4FontBuilder / standalone-tool
State: ReadyForTag

## Goal

Complete the first public v1.0.0 publication from the already-pushed sanitized
repository: fix the exact release commit, validate and rebuild the Windows package,
push `main`, create/push `v1.0.0`, verify hosted GitHub workflows where observable,
and publish the validated Windows ZIP as the GitHub Release asset.

## Current repository / remote fact

- Repository remote: `https://github.com/hellow0rld-lyh/WC4FontBuilder.git`.
- `main` tracks `origin/main`.
- Before this release-candidate update, local `main` and `origin/main` were both at
  `b7308f695e2d52b4ec3fb752f7a90d44f0bf00f4` with ahead=0 / behind=0.
- No local or remote release tag existed at that check.
- The machine-path privacy cleanup is already complete and the existing author
  email is intentionally public.
- The GitHub owner/repository name is now authoritative, so project URLs are being
  added to `pyproject.toml` in this release candidate.

## Previously completed privacy / package evidence

- Full rewritten-history machine-path scan: 0 user-profile, temp-path, username,
  or Unix-home matches; only neutral `C:\\path\\...` README examples remain.
- Common private-key / GitHub-token / AWS-key / OpenAI-key patterns: 0 matches.
- Git-tracked proprietary font/APK/EXE/key/certificate binaries: none.
- Canonical pytest: 17 passed.
- Canonical compileall: Passed.
- Windows GUI packaged self-test: Passed.
- Windows CLI smoke test and synthetic WC4 subset build: Passed.
- Synthetic output retained `中/国/國/與` with `missingRequired=0`.
- Android 1.29 renderer behavior acceptance remains Passed for the previously
  tested corpus/path; it is not repeated by this publication-only work unit.

## Release-candidate requirements

Before fixing the tag:

1. Run canonical pytest and compileall.
2. Rebuild the Windows v1 package from the exact release-candidate tree.
3. Run packaged GUI self-test and CLI smoke test.
4. Run a packaged synthetic WC4 subset build and reopen the output cmap.
5. Verify release ZIP required files and manifest support-file hashes.
6. Run `git diff --check` and confirm the exact Git status.
7. Create a clean local release-candidate commit and push `main`.
8. Create/push `v1.0.0` only from that fixed commit.

## Publication authorization

The user explicitly authorized completing the publication work unit, including
remote writes, tag creation and GitHub Release publication for this repository.
No signing, history rewrite, destructive cleanup, or unrelated credential export
is authorized by this work unit.

## State separation

- Product implementation: Completed for v1.0.0.
- Git-history privacy sanitization: Completed.
- Current release-candidate static/build validation: Passed.
- Source repository first push: Completed before this work unit resumed.
- Hosted GitHub CI validation for the final release commit: Pending until push.
- `v1.0.0` tag: Pending.
- GitHub Release and Windows ZIP asset: Pending; tag-triggered Windows workflow now verifies the exact hosted ZIP and creates the Release using GitHub's ephemeral repository token.
- Signing: NotRun / not required.

## Current release-candidate validation result

- Editable install after final project URLs: Passed.
- Canonical pytest: 17 passed.
- Canonical compileall: Passed.
- Windows package rebuild: Passed.
- Packaged GUI `--self-test`: Passed.
- Packaged CLI `--help`: Passed.
- Packaged synthetic WC4 subset build: Passed; `中/国/國/與` retained and required missing count is 0.
- Exact ZIP verification: 12 required files present; 10 manifested executable/support files match recorded byte sizes and SHA-256 values.
- Local candidate ZIP: `build/windows_v1/WC4FontBuilder-v1.0.0-windows-x64.zip`.
- Local candidate ZIP SHA-256: `306c09f9f40a279e6f61c180b8ecd0a87f091d5e666662cd445e898f65df4809`.
- `WC4FontBuilder.exe` SHA-256: `3e3b4fbdd50a7e211eb246cd485bdadef95b69e6c2bd3f31b5c57cd3128254b3`.
- `wc4-font-build.exe` SHA-256: `6f9466bb5707b06825b8d1fe82ae9a01c330aacd8c5de9a17dfcd001f23fd7b4`.
- GitHub workflow publication path was checked against current GitHub documentation: `GITHUB_TOKEN` is job-scoped/ephemeral and the workflow grants only repository `contents: write`; no local credential is exported.

## Next boundary

Fix this tree as the release commit, push `main`, verify final-main CI, push the
`v1.0.0` tag, then verify the tag-triggered Windows package/release workflow and
the published Release asset. Stop only for a real GitHub publication blocker, a
failing release gate, or a NoGo.
