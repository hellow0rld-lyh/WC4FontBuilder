# Vendored runtime license texts

These files are license/notice texts only. They are tracked so Windows release
packaging does not depend on whether a Python installation happens to include
license files in a particular filesystem layout.

The v1.0.0 Windows release environment is pinned to Python 3.14.6.

## Python runtime

- File: `python-LICENSE.txt`
- Source: the `LICENSE.txt` shipped by the locally verified CPython 3.14.6 Windows x64 runtime.
- CPython identity: `3.14.6 (tags/v3.14.6:c63aec6)`.
- SHA-256: `935cf13e19f8c31b497d20b05d73623431a226b230c3599bc30fa3348979bc68`.
- This is the full Windows runtime license/notice file, not only the shorter top-level CPython source `LICENSE`.

## Tcl/Tk runtime

- File: `tcl-tk-license.terms`
- Source: the `license.terms` shipped by the same locally verified Python 3.14.6 Windows installation.
- Runtime identity: Tcl/Tk 8.6, Tcl patchlevel 8.6.15.
- SHA-256: `0d1e4405f6273f091732764ed89b57066be63ce64869be6c71ea337dc4f2f9b5`.

These texts are copied into the Windows release under `licenses/`. They are not
covered by the project's MIT license; their own terms apply.
