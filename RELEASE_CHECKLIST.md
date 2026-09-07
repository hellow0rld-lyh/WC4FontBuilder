# GitHub / Release Checklist

The source repository is already public on GitHub. History rewriting, signing,
tagging and Release publication remain separately controlled operations.

## Before the first push

1. Decide the final GitHub owner and repository name.
2. Confirm the commit-author email is intended for public exposure and run a
   full-history privacy/path scan. Author-email privacy and machine-path privacy
   are independent decisions: use a GitHub `noreply` address only when the email
   should be hidden, and sanitize machine-local path strings separately when
   needed. Any required history rewrite must be explicitly authorized and done
   **before** the first push. Do not rewrite already-published history merely for
   cosmetic cleanup.
3. Create an empty GitHub repository without generating a README, license or
   `.gitignore` on GitHub.
4. Add the new repository as `origin` and verify the exact URL before pushing.
5. Push `main`, then confirm the `CI` workflow passes.

## v1.0.0 release gate

1. Start from a clean `main` at the intended release commit.
2. Run the canonical local validation from `VALIDATION.md`.
3. Build the Windows package with:

   ```powershell
   .venv\Scripts\python.exe tools\build_windows.py
   ```

4. Run the packaged GUI self-test and CLI smoke test.
5. Verify the SHA-256 reported for
   `build/windows_v1/WC4FontBuilder-v1.0.0-windows-x64.zip`.
6. Confirm the archive contains `LICENSE`, `THIRD_PARTY_NOTICES.txt`, README,
   full third-party license texts, the manifest, GUI executable and CLI
   executable.
7. Push the fixed release commit to `main` and confirm the `CI` workflow passes.
8. Create and push `v1.0.0` only from that fixed commit. The tag-triggered
   `Windows package` workflow rebuilds the package, verifies the exact ZIP,
   creates a SHA-256 checksum file, uploads the workflow artifact, and publishes
   the GitHub Release with the ZIP and checksum attached.
9. Confirm the tag workflow succeeds and verify the published Release/tag/assets.

## Never publish

- original/full font binaries;
- WC4 APKs, game assets or extracted proprietary resources;
- local `.venv`, `build/` work directories or test device artifacts;
- credentials, tokens, signing keys or private configuration.

The Windows v1 executables are currently unsigned. Signing is not required for
the source release and must not be added casually because it introduces a
separate key-management boundary.
