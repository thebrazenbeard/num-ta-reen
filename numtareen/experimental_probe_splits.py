"""Evaluator-only synthetic nuisance splits; NOT Nûm’ta’reen canon.

This module deliberately keeps the answer ledger and codebook inside an
evaluator-only object. Only ``PrivateProbeSplit.observations`` may be
serialized for learners, using the separately audited four-field UNVTRSLR
acoustic transport. Python attributes are NOT a security boundary: hostile
learners must execute in an isolated process without this module or ledger.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
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
    if len(set(result)) != len(result):
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
    if set(train_arms) & set(holdout_arms):
        raise ValueError("training and holdout nuisance arms must be disjoint")
    evaluator_codebook = _validate_codebook("evaluator_codebook", evaluator_codebook)
    if holdout_codebook is None:
        holdout_codebook = evaluator_codebook
    else:
        holdout_codebook = _validate_codebook("holdout_codebook", holdout_codebook)

    total_trials = STATE_COUNT * (len(train_arms) + len(holdout_arms))
    if total_trials * samples_per_state > MAX_BATCH_SAMPLES:
        raise ValueError("experiment exceeds aggregate sample cap")
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
    if {obs.samples for obs in train.observations} & {obs.samples for obs in holdout.observations}:
        raise ValueError("identical public waveform replay across train and holdout")
    return PrivateProbeExperiment(train, holdout)
