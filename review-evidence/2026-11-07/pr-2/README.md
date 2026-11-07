# Sonarr fork PR #2: reproducible test evidence

The series has tag ID 1 (called Anime in the PR example). Client A has tag 1; client B has no tags. Both are Torrent providers returned by the mocked client factory. The indexer explicitly selects client B (ID 2). The upstream implementation filters B out before resolving the explicit choice, throwing DownloadClientUnavailableException. The fix returns B. The suite also checks matching/mismatching tags, absent clients, blocked clients, protocol filtering and ordinary client selection.

Baseline implementation: `c018578e4b79ee048575c02d7a8aa2b929e4b837`

Reviewed fix head: `c1b69fa302c9a2f018046b33bd4bb28946c5524e`

Before: **1 failed, 16 passed, 17 total**.

After: **0 failed, 17 passed, 17 total**.

## Raw evidence

- [Failing test run](before/console.log) and [TRX](before/tests.trx)
- [Passing test run](after/console.log) and [TRX](after/tests.trx)
- [Before metadata and failure details](before/result.json)
- [After metadata](after/result.json)

## Reproduce

Install the SDK pinned in global.json (10.0.403). In a clean clone of ecatuogno1/Sonarr, fetch the review branch and run the sibling reproduction script:

```sh
git fetch origin review/20261107-indexer-download-client-tags
python3 /path/to/reproduce.py --repo "$PWD" --output ../sonarr-evidence --pr 2
```

The script checks out the exact reviewed commit. For the before run it replaces only the listed files with their baseline versions, retaining the proposed regression fixture. It restores the reviewed files and reruns the same fixture for the after run, then restores the original checkout. For PR #3, only the two test files are replaced: production is already identical to baseline. The exact swapped paths and executed command are recorded in each result.json. The expected failing run must fail; an unexpected pass, wrong case count, or after-run failure causes the script to stop with an assertion.

These are deterministic unit reproductions using mocked downloads, not production server traces or proof of a live download. Run locally on macOS arm64, Debug/Posix, SDK 10.0.403, with analyzers enabled. Machine-specific paths/host names in the uploaded logs are normalized; outcomes and assertion details are preserved.
