# Sonarr fork PR #1: reproducible test evidence

The regression fixture imports download1 into series 1 and download2 into series 2, then checks the series on each DownloadCompletedEvent. With the upstream implementation, the second assertion fails: Expected value to be 2, but found 1. With the reviewed fix, it passes. The two existing upstream multi-season tests are included and remain green.

Baseline implementation: `c018578e4b79ee048575c02d7a8aa2b929e4b837`

Reviewed fix head: `94a54f372a9261d4aa5b68b883fb93f7ca1b282e`

Before: **1 failed, 2 passed, 3 total**.

After: **0 failed, 3 passed, 3 total**.

## Raw evidence

- [Failing test run](before/console.log) and [TRX](before/tests.trx)
- [Passing test run](after/console.log) and [TRX](after/tests.trx)
- [Before metadata and failure details](before/result.json)
- [After metadata](after/result.json)

## Reproduce

Install the SDK pinned in global.json (10.0.403). In a clean clone of ecatuogno1/Sonarr, fetch the review branch and run the sibling reproduction script:

```sh
git fetch origin review/20261107-manual-import-complete-series
python3 /path/to/reproduce.py --repo "$PWD" --output ../sonarr-evidence --pr 1
```

The script checks out the exact reviewed commit. For the before run it replaces only the listed files with their baseline versions, retaining the proposed regression fixture. It restores the reviewed files and reruns the same fixture for the after run, then restores the original checkout. For PR #3, only the two test files are replaced: production is already identical to baseline. The exact swapped paths and executed command are recorded in each result.json. The expected failing run must fail; an unexpected pass, wrong case count, or after-run failure causes the script to stop with an assertion.

These are deterministic unit reproductions using mocked downloads, not production server traces or proof of a live download. Run locally on macOS arm64, Debug/Posix, SDK 10.0.403, with analyzers enabled. Machine-specific paths/host names in the uploaded logs are normalized; outcomes and assertion details are preserved.

The fixture asserts completion-event series ownership. It does not exercise actual folder deletion; the corrected importedSeries variable is also passed to ShouldDeleteFolder.
