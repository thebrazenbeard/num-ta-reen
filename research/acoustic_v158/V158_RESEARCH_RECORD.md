# V158 preregistered synthetic redundancy experiment

**Status:** Frozen hypotheses/methods before any V158 result execution. Research-only; the eight integer labels are arbitrary synthetic states, not authored Num’ta’reen semantics, frequencies, biological resonances, sender identity or native acoustic observations.

## Research question

Can two *public* redundant state-dependent verification tones added to V138's four-slot geometric frame reduce acceptance of arbitrary correctly scaffolded (but non-codebook) tones, without losing bounded single-source ±5% channel-drift behavior? Can it reject equal-strength simultaneous-source mixtures? A receiver without a secret **cannot authenticate a speaker/source**, regardless of success on these tasks.

## Frozen hypotheses and falsifiers

- **H1 — detect randomized malformed codewords:** Two independently positioned permutation-check tones substantially lower false acceptance of public-pilot frames with randomly selected state/data/check frequencies. **Prediction:** among 50 deterministic shape-matched random controls, V2 accepts no more than 5, while V138's first-four-slot projection accepts more. **Falsifier:** V2 accepts >5 or does not improve on projected V138.
- **H2 — retain stated channel robustness:** For 48 preregistered generated positives and 16 maximally skewed ±5% independently drifting slot pairs, at least 45/48 and 15/16 respectively decode correctly, **zero** wrong-state decodes. **Falsifier:** lower accuracy or any confidently wrong state.
- **H3 — strong-source collision abstention:** For eight fixed equal-amplitude mixtures of two valid distinct state waveforms, all eight abstain. **Falsifier:** any one accepted as a unique state.
- **H4 — impossible authentication:** An adversary knowing the public waveform generator can synthesize any of the eight accepted states. **Prediction:** 8/8 direct forgeries decode correctly. This is an expected **negative security result**, not a success at authentication.

## Confirmatory methods (fixed pre-result)

- **C0:** Pin baseline source ling-acoustic-v138/geometric_pilot_code.py to SHA-256 d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d. Reproduce fixed baseline tests separately; inspect no new upstream edits.
- **C1:** Use an eight-slot synthetic frame: V138 slots 0–3 unchanged; add pilot+checkA in slot 4, pilot-only guard in slot 5, pilot+checkB in slot 6, pilot-only guard in slot 7. Check permutation indices A(s)=(3s+1)%8, B(s)=(5s+2)%8, with geometric carrier ratio 1.30; both checks compare to received slot-0 reference (not pilot) with fixed log residual bound 0.112. Unkeyed and publicly computable.
- **C2:** Positive states s=0..7, each for data-scale 0.8/1.0/1.2, seed 1/9, noise 0.08, pilot distortion 0.95/1.05, and check drift 0.95/1.05 (48 trials); plus for each state both differential reference/check extremes (16).
- **C3:** Shape-matched negative controls: 50 fixed-seed (0xA582) synthetic eight-slot frames with valid pilot/guard sequence and four independently selected off-codebook carrier frequencies (reference/data/checkA/checkB), drawn uniformly from broad bands [480,730], [680,4400], [680,4400], [680,4400] Hz, with continuous random phases/gains. Compare projected slots 0–3 using V138 baseline and full slots using V2. Noise/harmonic negatives may be exploratory follow-ups, not part of H1.
- **C4:** Eight fixed equal-strength mixtures of two different valid state waveforms at identical noise=0/seed=7, pairs (0,1),(0,7),(1,6),(2,5),(3,4),(2,7),(4,6),(5,7); all must abstain to satisfy H3.
- **C5:** Public direct forge each state using exported renderer and decode, record 8/8 expected acceptance (H4).
- **C6:** Report exact correct/abstain/wrong and false accept counts and all test command exit codes. Freeze first implementation and then independently hostile review.

## Stopping rules

Stop once C0–C6 run and report even if hypotheses fail, or an exact mathematical/implementation collision proves a criterion impossible under stated assumptions. Changes to tests, parameters, validation after seeing results are **exploratory X-series**, never retroactively confirmed. No production/canonical integration without independent review; this study alone never supports authentication or natural speech recognition.

## Evidence log (append-only after experiments)

_No experiments executed at freeze time._

### E0 — dependency pin (C0), 2026-10-27 UTC

- Command: sha256sum ling-acoustic-v138/geometric_pilot_code.py
- Exit: 0.
- Result: d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d; matches preregistered V138 candidate. This pins the imported four-slot decoder, not an authenticated source.

### E1 — test discovery name collision (dead end)

- Command: PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m unittest -v test_redundant_geometric_code
- Exit: 1 (4 tests, one ERROR); exact decisive line: AttributeError: 'dict' object has no attribute 'positives_correct'.
- Root cause: generic module basename benchmark.py loaded V138's earlier benchmark.py from the first PYTHONPATH directory. No V158 hypothesis had been tested by that erroneously imported module. Fix was mechanical module rename to v158_benchmark.py and corresponding test import; no waveform algorithm, experimental parameters or frozen tests changed.

### E2 — preregistered executable test results (C1-C5)

- Command: PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m unittest -v test_redundant_geometric_code
- Exit: 0. Four tests, 10.282s, OK. Baseline hash, frame geometry, declarative C2-C5 acceptance criteria and invalid input checks passed.
- Immutable code fingerprints at result time: redundant_geometric_code.py SHA256 b2cdc57514ea41675f5a50c3cd9ccf4734ac54cf65fa6b612721daa8d9e8267f; v158_benchmark.py 7356042db8be6c35b88813433d3bd592362a4b5bb62ca3d8fb76a543f6aff74b; test_redundant_geometric_code.py 08e403710c48780a55dbff218e104265e7b7394d6ecba8beb622005c6130542a.

### E3 — exact confirmatory counts (C2-C5)

- Command: PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m v158_benchmark
- Exit: 0, 9.626s.
- Exact output: Results(positives_correct=48, positives_abstain=0, positives_wrong=0, extreme_correct=16, extreme_abstain=0, extreme_wrong=0, negatives_accepted_baseline=47, negatives_accepted_v2=0, equal_mix_accepted=0, forgeries_accepted=8)
- **C2:** 48/48 single-source positives and 16/16 extreme drift recovered, 0 wrong/abstain, exceeding H2. **C3:** 47/50 V138 projected false accepts versus 0/50 V2 on frozen random shaped controls, meeting H1. **C4:** 0/8 equal-power two-source mixtures accepted, meeting H3 on selected pairs only. **C5:** 8/8 public forgeries accepted, meeting the expected *negative authentication control*, never evidence of identity.

### E4 — confirmatory interpretation boundaries

- The V2 frame is 8 × 60ms = 480ms, twice V138's 240ms frame. Its extra redundancy increases transmitted symbols and latency; false-accept reduction is not a same-bandwidth comparison.
- Random-shaped negatives used only 50 deterministic samples; 0/50 is an empirical bound for this declared population and seed, not zero universal false accepts.
- C4 only covers eight equal-strength mixtures. Arbitrarily weak second sources can be indistinguishable in finite noise; no universal uniqueness guarantee follows.
- The public verification permutations are forgeable; no cryptographic MAC, secret key, sender identification or native Num’ta’reen frequency claims are present.

### E5 — independent verification pending

- Exact current V158 code SHA and the frozen C0-C6 protocol are ready for fresh hostile review. Until that review completes the methodological verdict is **provisional**, not independently confirmed.

### E6 — post-confirmatory exploratory hostile X1/X2

- Exploratory implementation: exploratory_hostile.py (separate from frozen waveform/benchmark code).
- Command: PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m exploratory_hostile
- Exit: 0, 3.714s.
- X1 eight fixed state-pair mixtures at each listed minority amplitude: at 1%, 5%, 10%, 15% all **8/8 accepted** as the majority state; at 25%, 35%, 45%, 50% all **8/8 abstained**. This explicitly falsifies any claim V2 detects *arbitrarily weak* simultaneous sources or always returns a unique physical source. The code is a detector under an assumed single-source model, not an acoustic scene separator.
- X2 temporal alteration: swapping check slots, duplicating check A, or erasing check B each abstained; exchanging two pilot-only guard slots still returned state 3, as expected because guard slot labels carry no data. Do not claim comprehensive anti-replay/tamper evidence.
- These post-result probes are **exploratory only** and do not change H1-H4's declared C-series scores.

### E7 — exact pinned V138 baseline standalone test (C0)

- Command: PYTHONPATH=ling-acoustic-v138 python -m unittest -v test_geometric_pilot_code
- Exit: 0. Five existing V138 checks passed, 5.861s, including its bounded pilot/data-scale positives, stationary/noise negatives, independent channel drift and public forgery control.
- Baseline module SHA remains d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d. This is a source-version matched local TEST, not external source authenticity.

### E8 — post-result exploratory X3 conflicting valid-check splice

- Added only exploratory_hostile.py X3 function; frozen C-series renderer/decoder/benchmark/test modules unchanged.
- Command: PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m exploratory_hostile
- Exit: 0, 7.474s. Decisive X3 line: {'examined': 56, 'abstained': 56, 'accepted': 0, 'unexpected': []}.
- All 56 ordered prefix-state/check-state mismatches were rejected. The V2 check fields detect *inconsistent public codeword components* under this exact test; they remain forgeable when all components are generated consistently for any chosen state.

### E9 — post-result exploratory X4 finite timing offsets

- Added only the X4 helper in exploratory_hostile.py; frozen C-series code and data unchanged.
- Command: PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m exploratory_hostile
- Exit: 0, 11.386s.
- For all eight synthetic states, shifts of 1, 8, 32, 100 samples yielded 8 correct/0 wrong/0 abstain each; shifts of 240 and 480 samples each yielded 0 correct/0 wrong/8 abstentions.
- This fixed-length zero-padding probe suggests limited timing tolerance, not voice/channel robustness, real synchronization, noise resilience, or arbitrary-offset support.

### E10 — fresh independent V163 hostile review

- Independent native reviewer: /root/ling_acoustic_v2_hostile_v163 (not the producing V158 lane). Review inputs: frozen V158 renderer/decoder/benchmark/test fingerprints E2 plus E0 pinned V138 source. Reviewer test: ling-acoustic-v2-hostile-v163/test_v158_hostile.py (reported SHA256 prefix 0edabc46); report: ling-acoustic-v2-hostile-v163/REVIEW.md.
- Reviewer reproduced preregistered C results exactly and issued **conditional PASS for the narrow bounded synthetic single-source error-detection claim**, while rejecting all origin authentication and zero-universal-false-accept claims.
- New independent exploratory negatives with a different seed/distribution: 100/128 accepted by V138 versus **4/128** accepted by V158. This is strong evidence of improvement, and direct evidence the V158 false-accept rate is **not universally zero**.
- Additional independent exploratory controls: 96 wrong-check splices accepted 0; 128 in-contract single-source positives 128/128 decoded correctly; offsets 1/50/100 samples correct for all eight states, 240/480/960 abstained for all eight; 10%-amplitude secondary-source mixtures still accepted. No source identity proof.
- The reviewer did not change V158 implementation. Exact artifact fingerprints and review distinction preserved.
