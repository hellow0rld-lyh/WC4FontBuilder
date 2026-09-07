# Current Handoff

Work-Unit-ID: WC4FontBuilderGitHistoryPrivacySanitization/v1
Repository: WC4FontBuilder repository root
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

Sanitize machine-specific local paths from the complete unpublished Git history
before the first public push, while preserving the existing commit-author email
by explicit user decision. Do not push, tag, sign, publish, or change product
behavior in this work unit.

## Completion result

- Started from clean `main` at
  `258864a42c4a8219db72ede8aba569df054d728b`, with no remote and no release tag.
- Created and verified an ignored local complete-history recovery bundle at
  `build/pre_history_sanitize_258864a.bundle` before rewriting history. It is
  local recovery evidence only and must not be published.
- Rewrote all six linear pre-publication commits, replacing machine-specific
  repository, legacy-repository, external-input, and temporary-path strings with
  semantic placeholders.
- The rewritten six-commit history ended at pre-closeout HEAD
  `d097ef5c0d82ee4ce6c83251c3b43fe839682a93` before this handoff update.
- Commit author identity was preserved on every rewritten commit. All six still
  use `helloworld-lyh <helloworld-lyh@outlook.com>`.
- `RELEASE_CHECKLIST.md` now treats author-email privacy and machine-path privacy
  as independent decisions instead of coupling path sanitization to use of a
  GitHub `noreply` address.
- No remote write, tag creation, signing, release publication, system-wide
  installation, APK/device action, or WC4 product-repository modification was
  performed.

## Full-history privacy validation

The rewritten `main` history was scanned commit-by-commit and blob-by-blob:

- Windows user-profile path pattern: 0 matches.
- Windows temporary-directory machine-path pattern: 0 matches.
- Historical local username marker: 0 matches.
- Unix/macOS user-home path pattern: 0 matches.
- Remaining Windows absolute strings are only intentional README examples using
  the neutral `C:\path\...` placeholder.
- Common private-key, GitHub-token, AWS access-key, OpenAI-key, and generic
  secret-assignment patterns: 0 matches.
- Git-tracked OTF/TTF/WOFF/EXE/APK/key/certificate binaries: none.

## Validation

- Editable install with `--no-deps --no-build-isolation`: Passed.
- Canonical pytest: 17 passed.
- Canonical compileall: Passed.
- Python GUI full-widget `--self-test`: Passed.
- Windows package rebuild: Passed.
- Packaged GUI `--self-test`: Passed.
- Packaged CLI `--help`: Passed.
- Packaged CLI synthetic WC4 subset build: Passed.
- Synthetic output reopen: `中/国/國/與` all present; `missingRequired=0`.
- Release ZIP required-file check: Passed.
- Release ZIP support-file hash verification against manifest: Passed.

Current rebuilt Windows artifacts:

```text
WC4FontBuilder.exe
SHA-256: 3e3b4fbdd50a7e211eb246cd485bdadef95b69e6c2bd3f31b5c57cd3128254b3

wc4-font-build.exe
SHA-256: 6f9466bb5707b06825b8d1fe82ae9a01c330aacd8c5de9a17dfcd001f23fd7b4

build/windows_v1/WC4FontBuilder-v1.0.0-windows-x64.zip
SHA-256: 81fbcde5e1519c81cfbcf55851c65750d8dc74af63555cce685f6c0eac78abc2
Bytes: 27417844
```

The two executable hashes are unchanged from publication prep. The rebuilt ZIP
hash changed because the archive was regenerated; required contents and manifest
hashes were revalidated.

## State separation

- Privacy/history research: Completed.
- Git-history rewrite implementation: Completed.
- Static/local validation: Passed.
- Windows build/package validation: Passed.
- Existing Android 1.29 renderer behavior acceptance: Passed for the previously
  tested corpus/path; not repeated by this privacy-only work unit.
- Windows GUI human click-through: NotRun; packaged automated widget self-test
  remains Passed.
- GitHub hosted workflows: NotRun; repository has not been pushed.
- Remote repository creation/binding/push: NotRun / unauthorized here.
- Git tag / GitHub Release publication: NotRun / unauthorized here.
- Signing: NotRun / unauthorized.

## Remaining blocker / decision

The Git-history privacy decision is resolved: machine-local paths are sanitized,
and the existing author email is intentionally retained.

The remaining publication decisions are the exact GitHub owner/repository name
and explicit authorization for remote writes/tag/release publication. Hosted CI
cannot be validated until the first push occurs.

## Next work unit

`WC4FontBuilderGitHubFirstPublish/v1` — after explicit remote-write authorization,
bind the exact GitHub repository, push `main`, verify hosted CI, create `v1.0.0`,
and publish the exact validated Windows ZIP as the Release asset.
