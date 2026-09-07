# GitHub / Release Checklist

This repository is prepared for a public GitHub publication, but remote writes,
history rewriting, signing, tagging and Release publication remain separate
operations.

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
7. Create an annotated or lightweight `v1.0.0` tag only after the release
   commit is fixed.
8. Publish a GitHub Release from that tag and attach the exact Windows ZIP.
9. Put the ZIP SHA-256 in the Release notes.

## Never publish

- original/full font binaries;
- WC4 APKs, game assets or extracted proprietary resources;
- local `.venv`, `build/` work directories or test device artifacts;
- credentials, tokens, signing keys or private configuration.

The Windows v1 executables are currently unsigned. Signing is not required for
the source release and must not be added casually because it introduces a
separate key-management boundary.
