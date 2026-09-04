# Current Handoff

Work-Unit-ID: FontSubsetterFoundation/v1
Repository: <legacy-repo>
Product-Or-Route: WC4FontBuilder / standalone-tool
State: Completed

## Goal

Deliver a first usable CLI that scans text, augments a small WC4-safe character set, subsets an OpenType font with layout closure, validates output coverage and key metrics, and emits a JSON report.

## Completion conditions

- CLI implementation present.
- Missing required text glyphs fail closed by default.
- OpenType subsetting uses fontTools closure.
- Synthetic-font tests pass.
- Local commit created and final Git status clean.

## Prohibited

No WC4 repository modification, no font binary commit, no remote write, no release publication, no game/device installation.

## Validation result

- pytest: 6 passed.
- compileall: passed.
- CLI entrypoint `--help`: passed.
- Real WC4 OTF/game-renderer acceptance: NotRun.

## Next work unit

WC4FontBuilderRealCorpusCompatibility/v1 — run against the actual WC4 text corpus and a user-provided full OTF, then perform renderer acceptance and tune safety/compatibility options from evidence.
