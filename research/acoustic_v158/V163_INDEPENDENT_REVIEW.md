# V163 independent hostile review — V158 synthetic redundant acoustic code

**Verdict:** PASS only for the preregistered, synthetic, single-source
error-detection experiment. FAIL for any general unique-source, authenticity,
native speech, physical resonance, or unrestricted acoustic-recognition claim.

**Exact frozen targets**

- V158 `redundant_geometric_code.py` SHA-256:
  `b2cdc57514ea41675f5a50c3cd9ccf4734ac54cf65fa6b612721daa8d9e8267f`.
- V158 `v158_benchmark.py` SHA-256:
  `7356042db8be6c35b88813433d3bd592362a4b5bb62ca3d8fb76a543f6aff74b`.
- V138 dependency SHA-256:
  `d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d`.
- This independent adversarial test SHA-256:
  `0edabc467b7f0e74a8167a27189f4eb81814bea8b17605bc64fdaf1f97d839e8`.

## Fresh executed evidence

From scratch repository root, Python 3.12:

1. `PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m unittest -v test_redundant_geometric_code`
   → exit **0**, four tests PASS, ~10.5s.
2. `PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m v158_benchmark`
   → exit **0**, exact `Results(positives_correct=48, positives_abstain=0,
   positives_wrong=0, extreme_correct=16, extreme_abstain=0, extreme_wrong=0,
   negatives_accepted_baseline=47, negatives_accepted_v2=0,
   equal_mix_accepted=0, forgeries_accepted=8)`.
3. `PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m unittest -v ling-acoustic-v2-hostile-v163/test_v158_hostile.py`
   → exit **0**, four adversarial tests PASS, ~26.3s. Out-of-preregister-seed
   128 independent random public-pilot frames: old V138 **100/128** accepted,
   V158 **4/128** accepted. Thus `0/50` is not a universal zero-false-accept
   guarantee; the ~96% reduction in this *different synthetic sample* is real
   but distribution-bound.
   Also 96 valid V138 prefixes combined with two incorrect V158 check fields
   yielded **0** accepted; swapping the check slots of eight genuine public
   frames yielded **0** accepted; publicly generated true frames remained
   accepted.
4. Independent positive/timing extension:
   `PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m unittest -v ling-acoustic-v2-hostile-v163.test_v158_hostile.IndependentHostile.test_128_randomized_single_source_within_bounds ling-acoustic-v2-hostile-v163.test_v158_hostile.IndependentHostile.test_frame_window_shift_probes`
   → exit **0**, two tests PASS, ~11.2s. Across 128 sampled in-contract
   single-source signals with independently randomized pilot/data/reference/
   code/check ±5% scales, phase, gain and noise, decoded **128 correct,
   0 abstain, 0 wrong**. Shift 1/50/100 samples: each eight correct; shift
   240/480/960: each eight abstained, none wrong. Timing shifts are exploratory,
   not part of C-series preregistration.

## Material hostile conclusions

> **No origin verification.** The codec has no secret and public `render(s)`
> passes `decode` for each state. It is a consistency check on known synthetic
> structure, not speaker authentication or a Num’ta’reen acoustic detector.

> **No unique-source guarantee.** A weaker concurrent waveform can be
> accepted as the stronger one; V158's own independent X1 reports all eight
> mixtures at 1%, 5%, 10%, and 15% minority accepted. The separate V163 test
> confirms acceptance with a 10% minority. Strong equal mixtures are rejected,
> but arbitrary faint mixtures cannot be ruled out in finite noise.

> **Sampling changes the false-accept rate.** Frozen broad-carrier negative
> `0/50` was reproduced. A different seeded sample with the same broad
> carrier ranges produced **4/128** V158 false accepts. No zero-FAR,
> distribution-free, or physical-world claim is justified.

The V158 frame is eight 60ms slots (480ms) versus V138's four slots (240ms).
The improvement is **not** same-bandwidth or same-latency; public check
permutations add redundancy that an adversary can replicate.

**Classification:** Confirmed synthetic bounded improvement, with explicit
falsifiers for authenticity, unique-state interpretation, and zero error.

**Authority/canon:** Read-only review; no implementation, GitHub, branch,
protected manuscript, or canonical-language changes.
