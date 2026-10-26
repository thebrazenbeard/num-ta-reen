"""Synthetic acoustic test fixture, NOT canonical Nûm’ta’reen speech.

Nûm’ta’reen source documents describe multimodal resonance state-sharing but
do not specify a native Hertz-to-meaning mapping. These arbitrary eight
synthetic states exist solely for blinded, adversarial signal-learning tests.
This module cannot synthesize words, true names, or authorial chord notation.

Import this generator only in an evaluator process. Give learners *only* the
``AcousticObservation`` samples and sample rate, packaged by an independently
audited blind transport. Never expose input states, seed, codebook or nuisance
settings to learner-side code.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
from math import cos, isfinite, pi, sin
from numbers import Integral, Real
from random import Random
from typing import Iterable


SCHEMA = "NUMTAREEN_NONCANONICAL_SYNTHETIC_RESONANCE_V0"
STATE_COUNT = 8
MAX_SAMPLES = 262_144  # Matches the UNVTRSLR blind observation scalar cap.
MAX_BATCH_SAMPLES = 1_048_576  # Bound evaluator allocation across trials.
DEFAULT_CODEBOOK = tuple(range(STATE_COUNT))


@dataclass(frozen=True)
class AcousticObservation:
    """Learner-eligible raw signal. No labels, IDs, keys, or expected actions."""

    sample_rate_hz: int
    samples: tuple[float, ...]


def _integer(name: str, value: object, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral) or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return int(value)


def _real(name: str, value: object, low: float, high: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, Real)
        or not isfinite(float(value))
        or not low <= float(value) <= high
    ):
        raise ValueError(f"{name} must be finite and within [{low}, {high}]")
    return float(value)


def render_experimental_resonance(
    states: Iterable[int],
    *,
    seed: int,
    sample_rate_hz: int = 16_000,
    samples_per_state: int = 960,
    gain: float = 0.65,
    pitch_scale: float = 1.0,
    noise_level: float = 0.0,
    phase_shift_rad: float = 0.0,
    evaluator_codebook: tuple[int, ...] = DEFAULT_CODEBOOK,
    silence_control: bool = False,
) -> AcousticObservation:
    """Render bounded, reproducible noncanonical audio from opaque state IDs.

    The input state sequence and arbitrary tone codebook are **evaluator-only**
    variables. The output carries no language/English/gloss metadata. Global
    gain, pitch scale, phase and noise support nuisance-matched adversarial
    trials. ``silence_control`` preserves duration while removing all signal.
    There is no decoder, sound-to-English contract or native phonology here.
    """

    sample_rate_hz = _integer("sample_rate_hz", sample_rate_hz, 8_000, 48_000)
    samples_per_state = _integer("samples_per_state", samples_per_state, 128, 12_000)
    seed = _integer("seed", seed, 0, (1 << 32) - 1)
    gain = _real("gain", gain, 0.01, 0.85)
    pitch_scale = _real("pitch_scale", pitch_scale, 0.8, 1.2)
    noise_level = _real("noise_level", noise_level, 0.0, 0.15)
    phase_shift_rad = _real("phase_shift_rad", phase_shift_rad, -2 * pi, 2 * pi)
    if not isinstance(silence_control, bool):
        raise ValueError("silence_control must be boolean")

    if not isinstance(evaluator_codebook, tuple) or len(evaluator_codebook) != STATE_COUNT:
        raise ValueError("evaluator_codebook must be an eight-state permutation")
    if any(isinstance(x, bool) or not isinstance(x, Integral) for x in evaluator_codebook):
        raise ValueError("evaluator_codebook must contain integer states")
    if set(evaluator_codebook) != set(range(STATE_COUNT)):
        raise ValueError("evaluator_codebook must be a one-to-one permutation")

    try:
        # Consuming an unbounded generator before checking length would hang
        # an evaluator. Materialize only one beyond the declared limit.
        sequence = tuple(islice(iter(states), 65))
    except TypeError as exc:
        raise ValueError("states must be iterable") from exc
    if not 1 <= len(sequence) <= 64:
        raise ValueError("states length must be in [1, 64]")
    if any(isinstance(x, bool) or not isinstance(x, Integral) or x < 0 or x >= STATE_COUNT for x in sequence):
        raise ValueError("states must contain only opaque integers from 0 through 7")
    total_samples = len(sequence) * samples_per_state
    if total_samples > MAX_SAMPLES:
        raise ValueError("render would exceed the blind observation sample cap")

    if silence_control:
        return AcousticObservation(sample_rate_hz, (0.0,) * total_samples)

    random = Random(seed)
    samples: list[float] = []
    for state in sequence:
        # Artificial resonant states. Fixed codebook is deliberately exposed
        # *only* to the evaluator and should be ablated/permuted in trials.
        carrier_hz = (250.0 + 92.0 * evaluator_codebook[int(state)]) * pitch_scale
        for n in range(samples_per_state):
            t = n / sample_rate_hz
            window = 0.5 - 0.5 * cos(2.0 * pi * n / (samples_per_state - 1))
            phase = 2.0 * pi * carrier_hz * t + phase_shift_rad
            tone = 0.74 * sin(phase) + 0.26 * sin(2.0 * phase + 0.21)
            noise = noise_level * random.uniform(-1.0, 1.0)
            samples.append(gain * window * (tone + noise))
    return AcousticObservation(sample_rate_hz, tuple(samples))


def render_matched_batch(
    state_sequences: Iterable[Iterable[int]],
    *,
    batch_seed: int,
    sample_rate_hz: int = 16_000,
    samples_per_state: int = 960,
    gain: float = 0.65,
    pitch_scale: float = 1.0,
    noise_level: float = 0.0,
    phase_shift_rad: float = 0.0,
    evaluator_codebook: tuple[int, ...] = DEFAULT_CODEBOOK,
) -> tuple[AcousticObservation, ...]:
    """Render a small comparison batch with label-blind public geometry.

    Every observation has identical sample rate, duration and global nuisance
    controls; stochastic noise seeds are sampled independently of state values
    from a private batch seed. The *caller* must still randomize label/order,
    counterbalance nuisance across batches, and keep its answer ledger sealed.
    This helper does not establish semantic grounding or absence of shortcuts.
    """

    batch_seed = _integer("batch_seed", batch_seed, 0, (1 << 32) - 1)
    try:
        batch = tuple(tuple(islice(iter(states), 65)) for states in islice(iter(state_sequences), 17))
    except TypeError as exc:
        raise ValueError("state_sequences must be iterable sequences") from exc
    if not 2 <= len(batch) <= 16:
        raise ValueError("matched batch count must be in [2, 16]")
    if len({len(sequence) for sequence in batch}) != 1:
        raise ValueError("all matched batch sequences must have identical state counts")
    samples_per_state = _integer("samples_per_state", samples_per_state, 128, 12_000)
    if len(batch) * len(batch[0]) * samples_per_state > MAX_BATCH_SAMPLES:
        raise ValueError("matched batch would exceed aggregate sample cap")
    rng = Random(batch_seed)
    noise_seeds = rng.sample(range(1 << 32), len(batch))
    rendered = tuple(
        render_experimental_resonance(
            sequence,
            seed=seed,
            sample_rate_hz=sample_rate_hz,
            samples_per_state=samples_per_state,
            gain=gain,
            pitch_scale=pitch_scale,
            noise_level=noise_level,
            phase_shift_rad=phase_shift_rad,
            evaluator_codebook=evaluator_codebook,
        )
        for sequence, seed in zip(batch, noise_seeds)
    )
    if len({(item.sample_rate_hz, len(item.samples)) for item in rendered}) != 1:
        raise RuntimeError("internal matched batch geometry violation")
    return rendered
