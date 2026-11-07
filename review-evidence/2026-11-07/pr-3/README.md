# Sonarr fork PR #3: reproducible test evidence

The upstream ImportFixture and ProcessFixture are run in Debug. Eight tests fail during teardown because SetStateToImportBlocked writes one warning that the tests do not expect. The proposed patch adds ExpectedWarns(1) to exactly those tests; all 28 tests pass. There is no production-code change.

Baseline implementation: `c018578e4b79ee048575c02d7a8aa2b929e4b837`

Reviewed fix head: `4c2d872db1018cedb6431217ae3e3bcf53612db4`

Before: **8 failed, 20 passed, 28 total**.

After: **0 failed, 28 passed, 28 total**.

## Raw evidence

- [Failing test run](before/console.log) and [TRX](before/tests.trx)
- [Passing test run](after/console.log) and [TRX](after/tests.trx)
- [Before metadata and failure details](before/result.json)
- [After metadata](after/result.json)

## Reproduce

Install the SDK pinned in global.json (10.0.403). In a clean clone of ecatuogno1/Sonarr, fetch the review branch and run the sibling reproduction script:

```sh
git fetch origin review/20261107-import-blocked-warning-tests
python3 /path/to/reproduce.py --repo "$PWD" --output ../sonarr-evidence --pr 3
```

The script checks out the exact reviewed commit. For the before run it replaces only the listed files with their baseline versions, retaining the proposed regression fixture. It restores the reviewed files and reruns the same fixture for the after run, then restores the original checkout. For PR #3, only the two test files are replaced: production is already identical to baseline. The exact swapped paths and executed command are recorded in each result.json. The expected failing run must fail; an unexpected pass, wrong case count, or after-run failure causes the script to stop with an assertion.

These are deterministic unit reproductions using mocked downloads, not production server traces or proof of a live download. Run locally on macOS arm64, Debug/Posix, SDK 10.0.403, with analyzers enabled. Machine-specific paths/host names in the uploaded logs are normalized; outcomes and assertion details are preserved.

Supporting source: [production warning](https://github.com/ecatuogno1/Sonarr/blob/c018578e4b79ee048575c02d7a8aa2b929e4b837/src/NzbDrone.Core/Download/CompletedDownloadService.cs#L339-L354), [Debug-only unexpected-log assertion](https://github.com/ecatuogno1/Sonarr/blob/c018578e4b79ee048575c02d7a8aa2b929e4b837/src/NzbDrone.Test.Common/LoggingTest.cs#L96-L102), and [CI Release build configuration](https://github.com/ecatuogno1/Sonarr/blob/c018578e4b79ee048575c02d7a8aa2b929e4b837/.github/actions/build/action.yml#L99).
