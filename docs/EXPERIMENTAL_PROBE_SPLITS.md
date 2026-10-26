# Experimental probe splits (noncanonical, evaluator-only)

Status: `SYNTHETIC_NUISANCE_CONTROL_ONLY / SEMANTICS_UNQUALIFIED`

`numtareen.experimental_probe_splits` creates reproducible training and frozen
holdout sets for the eight *arbitrary* states emitted by
`experimental_resonance`. These states **are not Num’ta’reen words**, a native
Hertz alphabet, true-name chords, or author-approved mappings to English.

## Boundary

Only `PrivateProbeSplit.observations` may be passed through the UNVTRSLR blind
acoustic transport. Every element is an `AcousticObservation` with precisely
`sample_rate_hz` and `samples`; UNVTRSLR serializes exactly its four allowed
waveform fields. Keep `PrivateProbeExperiment` and its
`hidden_state_ids`/`hidden_arm_ids` **inside the evaluator process**. Never
import the Num generator, this module, the lexicon/corpus, or any evaluator
codebook into sender/receiver processes.

Python attribute visibility is **not** an isolation mechanism. The UNVTRSLR
in-process causal screen includes a reproducible `inspect.stack()` answer
oracle, so these splits must not be advertised as sealed against hostile
callbacks until actual process/host controls are independently tested.

## Constructing a probe

```python
from numtareen.experimental_probe_splits import (
    NuisanceArm,
    render_private_balanced_probe_splits,
)

private = render_private_balanced_probe_splits(
    batch_seed=17,
    train_arms=(
        NuisanceArm(gain=0.4, pitch_scale=0.92, noise_level=0.04),
        NuisanceArm(gain=0.65, pitch_scale=1.04, noise_level=0.09),
    ),
    holdout_arms=(
        NuisanceArm(gain=0.48, pitch_scale=1.12, noise_level=0.07),
        NuisanceArm(gain=0.75, pitch_scale=0.85, noise_level=0.12),
    ),
)
public_train = private.train.observations
public_holdout = private.holdout.observations
# Do not deliver any other private.* fields to learners.
```

The helper checks all arm ranges, rejects duplicate phase-periodic nuisance
arms and cross-split arm overlap, bounds aggregate samples to 1,048,576, uses
independent noise seeds, and rejects exact waveform replay **within each split**
as well as across train/holdout. This matters because two arbitrary hidden
state IDs can produce identical samples under different pitch settings, making
their labels impossible to distinguish from the public signal. Each state occurs
**once per nuisance arm** in each split. Thus the finite nuisance-arm schedule
is exactly balanced by state, and sample rate/duration are uniform; different
gain/pitch/noise/phase combinations are held out.

Exact duplicate rejection is only a minimal validity guard. It does **not**
reject near-identical or statistically ambiguous signals; noisy cross-class
collisions and independent captures remain unresolved. No perfect held-out
classification result should be interpreted as semantics without checking
observability and those collision risks.

An optional evaluator-only `holdout_codebook` permutation is a negative-control
probe of frequency-codebook memorization. Even without this ablation, a trivial
FFT lookup can decode the original eight-state toy generator. Always compare
against that lookup baseline, nuisance-matched nearest-frequency classifiers,
constant-message and replay baselines, and actual intervention controls.

## Claim ceiling

This module establishes only **synthetic, reproducible nuisance stratification**.
It does not show language emergence, learned grounding, semantic transfer,
universal translation, robustness to real-world acoustic capture, or three-host
isolation. Meaningful qualification requires blinded live captures, frozen
separate learners, evaluator-only feedback, preregistered holdouts, unexpected
nuisance/partner swaps, intervention tests, and review of covert channels.

Regression command from an installation or repository root with module on
`PYTHONPATH`:

```bash
python -m unittest discover -s tests -p 'test_experimental_probe_splits.py' -v
```
