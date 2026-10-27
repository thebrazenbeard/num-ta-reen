# Investigation: intermittent Linux PowerShell native-test timeout

**Scope:** Public `thebrazenbeard/num-ta-reen` PR #21 head `79e743eb0bd213983f3bb60b7eea475bc018f018`; no canonical source or production script changes.

## Symptom and evidence

- `40407715987` / offline Ubuntu Python 3.11 job `121869674178`: the first `test_native_ps7_attested` entered an external `pwsh -NoProfile -NonInteractive -File` process at approximately `2026-10-26T21:51:12Z`, then raised `subprocess.TimeoutExpired` at its exactly 20-second cap.
- The next PS7 test (`test_native_ps7_unknown_and_protected`) succeeded in about 3.6 seconds, using the same script and process model with multiple independent inputs.
- Same commit, second workflow `40407757384` succeeded in all six jobs, including Ubuntu Python 3.11; first PS7 test completed in ~2.1 seconds there. The three Windows matrix jobs passed in the initial and subsequent workflow runs, but this does not prove Linux cannot stall.
- The local execution host has no `pwsh` binary; native failure cannot be reproduced directly here. Seven Python transport tests, the additional finite-timeout regression, and expected local shell skips all pass.

## Hypotheses, falsifiers, verdict

- Cold-start `.NET`/pwsh launch under CI contention is *plausible*, predicting only the first invocation stalls and subsequent invocations recover. Observed order fits but is not uniquely diagnostic. Cannot establish root cause without process/timing telemetry on the failed runner.
- Quoting, UTF-8 or protected-token handling as a deterministic bug predicts same input also fails in the later identical run; falsified for ordinary repeatability, but intermittent subprocess transport cannot be ruled out.
- An infinite application-level deadlock predicts continued failure on the next call; this did not occur. A one-shot transient deadlock remains possible.

**Verdict:** VERIFIED intermittent first-native-invocation delay exceeding 20 seconds. Internal cause UNKNOWN; a green rerun alone is not proof of repair.

## Bounded mitigation

- Raise only the native-PowerShell subprocess bound from an arbitrary 20 seconds to 45 seconds. Leave Python transport's 10-second bound unchanged. Both native command forms continue to surface `TimeoutExpired` as test failures, with no retry, skip or success fallback.
- Add an executable Python regression that forces `subprocess.TimeoutExpired` and verifies that the native timeout remains finite and propagates, even without a PowerShell executable on the local host.

This is a tolerance adjustment for rare CI startup outliers, **not a demonstrated fix of the unknown intermittent cause**. The revised head must pass both PS5.1/PS7 Windows qualification and repeated Linux CI before being regarded as stable. The 45-second threshold is still a policy choice, not a measured upper bound.
