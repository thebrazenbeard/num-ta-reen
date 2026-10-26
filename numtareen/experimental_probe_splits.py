"""Evaluator-only synthetic nuisance splits; NOT Nûm’ta’reen canon.

This module deliberately keeps the answer ledger and codebook inside an
evaluator-only object. Only ``PrivateProbeSplit.observations`` may be
serialized for learners, using the separately audited four-field UNVTRSLR
acoustic transport. Python attributes are NOT a security boundary: hostile
learners must execute in an isolated process without this module or ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, pi, remainder
from random import Random

from numtareen.experimental_resonance import (
    AcousticObservation,
    DEFAULT_CODEBOOK,
    MAX_BATCH_SAMPLES,
    STATE_COUNT,
    _integer,
    _real,
    render_experimental_resonance,
)


MAX_ARMS_PER_SPLIT = 8
# Floating arithmetic around a complete 2*pi turn can leave ~1e-15 rad
# residue. This tolerance is numerical, not a perceptual similarity metric.
PHASE_PERIODIC_TOLERANCE_RAD = 1e-12
# Numerical carrier equivalence, not a psychoacoustic discrimination threshold.
# The synthetic oscillator uses floating-point pitch multiplication.
CARRIER_ROUNDOFF_REL_TOLERANCE = 1e-12


@dataclass(frozen=True)
class NuisanceArm:
    """Evaluator-private nuisance setting, unrelated to a signal's state ID."""

    gain: float = 0.65
    pitch_scale: float = 1.0
    noise_level: float = 0.0
    phase_shift_rad: float = 0.0


@dataclass(frozen=True)
class PrivateProbeSplit:
    """Only ``observations`` may cross the evaluator/learner boundary."""

    observations: tuple[AcousticObservation, ...]
    hidden_state_ids: tuple[int, ...]
    hidden_arm_ids: tuple[int, ...]


@dataclass(frozen=True)
class PrivateProbeExperiment:
    """Evaluator-only ledger containing training and frozen holdout splits."""

    train: PrivateProbeSplit
    holdout: PrivateProbeSplit


def _same_acoustic_arm(left: NuisanceArm, right: NuisanceArm) -> bool:
    """Phase rotations of whole turns are the same synthetic nuisance arm."""
    return (
        left.gain == right.gain
        and left.pitch_scale == right.pitch_scale
        and left.noise_level == right.noise_level
        and abs(remainder(left.phase_shift_rad - right.phase_shift_rad, 2 * pi))
        <= PHASE_PERIODIC_TOLERANCE_RAD
    )


def _validate_arms(name: str, arms: object) -> tuple[NuisanceArm, ...]:
    if not isinstance(arms, tuple) or not 1 <= len(arms) <= MAX_ARMS_PER_SPLIT:
        raise ValueError(f"{name} arm count must be in [1, {MAX_ARMS_PER_SPLIT}]")
    result: list[NuisanceArm] = []
    for arm in arms:
        if not isinstance(arm, NuisanceArm):
            raise ValueError(f"{name} arms must be NuisanceArm instances")
        result.append(
            NuisanceArm(
                gain=_real("gain", arm.gain, 0.01, 0.85),
                pitch_scale=_real("pitch_scale", arm.pitch_scale, 0.8, 1.2),
                noise_level=_real("noise_level", arm.noise_level, 0.0, 0.15),
                phase_shift_rad=_real("phase_shift_rad", arm.phase_shift_rad, -2 * pi, 2 * pi),
            )
        )
    if any(_same_acoustic_arm(left, right)
           for index, left in enumerate(result) for right in result[index + 1:]):
        raise ValueError(f"{name} contains duplicate nuisance arms")
    return tuple(result)


def _validate_codebook(name: str, codebook: object) -> tuple[int, ...]:
    if (
        not isinstance(codebook, tuple)
        or len(codebook) != STATE_COUNT
        or any(type(item) is not int for item in codebook)
        or set(codebook) != set(range(STATE_COUNT))
    ):
        raise ValueError(f"{name} must be an eight-state integer permutation")
    return codebook


def _carrier_rows(
    arms: tuple[NuisanceArm, ...], codebook: tuple[int, ...]
) -> tuple[tuple[int, float, float, float], ...]:
    """Private analytic carrier/gain/phase ledger; never learner-visible."""
    return tuple(
        (state, (250.0 + 92.0 * codebook[state]) * arm.pitch_scale,
         arm.gain, arm.phase_shift_rad)
        for arm in arms for state in range(STATE_COUNT)
    )


def _indistinguishable_deterministic_carriers(
    left: tuple[int, float, float, float],
    right: tuple[int, float, float, float],
) -> bool:
    """Recognize cross-label oscillator aliases despite independent noise."""
    left_state, left_hz, left_gain, left_phase = left
    right_state, right_hz, right_gain, right_phase = right
    return (
        left_state != right_state
        and left_gain == right_gain
        and isclose(left_hz, right_hz, rel_tol=CARRIER_ROUNDOFF_REL_TOLERANCE)
        and abs(remainder(left_phase - right_phase, 2 * pi))
        <= PHASE_PERIODIC_TOLERANCE_RAD
    )


def _has_carrier_alias(
    left_rows: tuple[tuple[int, float, float, float], ...],
    right_rows: tuple[tuple[int, float, float, float], ...] | None = None,
) -> bool:
    """Bounded O((8 * arms)^2) evaluator-only structural ambiguity check."""
    if right_rows is None:
        return any(
            _indistinguishable_deterministic_carriers(left, right)
            for index, left in enumerate(left_rows)
            for right in left_rows[index + 1:]
        )
    return any(
        _indistinguishable_deterministic_carriers(left, right)
        for left in left_rows for right in right_rows
    )


def render_private_balanced_probe_splits(
    *,
    batch_seed: int,
    train_arms: tuple[NuisanceArm, ...],
    holdout_arms: tuple[NuisanceArm, ...],
    sample_rate_hz: int = 16_000,
    samples_per_state: int = 960,
    evaluator_codebook: tuple[int, ...] = DEFAULT_CODEBOOK,
    holdout_codebook: tuple[int, ...] | None = None,
) -> PrivateProbeExperiment:
    """Render label-balanced experiments with explicitly shifted nuisance arms.

    Every synthetic state appears exactly once under *every* nuisance arm in
    its split, so gain/pitch/noise/phase are not class labels. Training and
    holdout arms cannot overlap. The optional holdout-only codebook permutation
    is a negative-control ablation for rote frequency lookup, not a claim of
    learned semantics. No English or native phonology is encoded here.
    """

    batch_seed = _integer("batch_seed", batch_seed, 0, (1 << 32) - 1)
    sample_rate_hz = _integer("sample_rate_hz", sample_rate_hz, 8_000, 48_000)
    samples_per_state = _integer("samples_per_state", samples_per_state, 128, 12_000)
    train_arms = _validate_arms("train", train_arms)
    holdout_arms = _validate_arms("holdout", holdout_arms)
    if any(_same_acoustic_arm(a, b) for a in train_arms for b in holdout_arms):
        raise ValueError("training and holdout nuisance arms must be disjoint")
    evaluator_codebook = _validate_codebook("evaluator_codebook", evaluator_codebook)
    if holdout_codebook is None:
        holdout_codebook = evaluator_codebook
    else:
        holdout_codebook = _validate_codebook("holdout_codebook", holdout_codebook)

    total_trials = STATE_COUNT * (len(train_arms) + len(holdout_arms))
    if total_trials * samples_per_state > MAX_BATCH_SAMPLES:
        raise ValueError("experiment exceeds aggregate sample cap")
    train_carriers = _carrier_rows(train_arms, evaluator_codebook)
    holdout_carriers = _carrier_rows(holdout_arms, holdout_codebook)
    if _has_carrier_alias(train_carriers):
        raise ValueError("structurally ambiguous carrier labels within training split")
    if _has_carrier_alias(holdout_carriers):
        raise ValueError("structurally ambiguous carrier labels within holdout split")
    # Explicit holdout codebook permutation is an *intentional* negative
    # control, not a positive semantic evaluation. Preserve that intervention.
    # The normal same-codebook evaluation must reject cross-label physical
    # aliases across its train/frozen-holdout boundary.
    if holdout_codebook == evaluator_codebook and _has_carrier_alias(train_carriers, holdout_carriers):
        raise ValueError("structurally ambiguous carrier labels across train and holdout")
    rng = Random(batch_seed)
    all_seeds = iter(rng.sample(range(1 << 32), total_trials))

    def render_split(arms: tuple[NuisanceArm, ...], codebook: tuple[int, ...]) -> PrivateProbeSplit:
        # The cartesian product balances nuisance settings *exactly* for each
        # hidden state, rather than hoping independent random draws balance.
        jobs = [(state, arm_idx, arm) for arm_idx, arm in enumerate(arms) for state in range(STATE_COUNT)]
        rng.shuffle(jobs)
        observations: list[AcousticObservation] = []
        labels: list[int] = []
        nuisance_ids: list[int] = []
        for state, arm_idx, arm in jobs:
            observation = render_experimental_resonance(
                (state,),
                seed=next(all_seeds),
                sample_rate_hz=sample_rate_hz,
                samples_per_state=samples_per_state,
                evaluator_codebook=codebook,
                gain=arm.gain,
                pitch_scale=arm.pitch_scale,
                noise_level=arm.noise_level,
                phase_shift_rad=arm.phase_shift_rad,
            )
            observations.append(observation)
            labels.append(state)
            nuisance_ids.append(arm_idx)
        return PrivateProbeSplit(tuple(observations), tuple(labels), tuple(nuisance_ids))

    train = render_split(train_arms, evaluator_codebook)
    holdout = render_split(holdout_arms, holdout_codebook)
    # Exact public waveforms are not independent examples even if their
    # evaluator-private labels or nuisance-arm IDs differ.  Cross-class
    # carrier aliases can occur *inside* a split, not just across splits.
    # The aggregate sample cap above bounds these temporary sets.
    train_waveforms = {obs.samples for obs in train.observations}
    holdout_waveforms = {obs.samples for obs in holdout.observations}
    if len(train_waveforms) != len(train.observations):
        raise ValueError("identical public waveform replay within training split")
    if len(holdout_waveforms) != len(holdout.observations):
        raise ValueError("identical public waveform replay within holdout split")
    if train_waveforms & holdout_waveforms:
        raise ValueError("identical public waveform replay across train and holdout")
    return PrivateProbeExperiment(train, holdout)
