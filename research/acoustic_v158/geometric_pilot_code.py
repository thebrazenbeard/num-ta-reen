"""NONCANONICAL, UNKEYED synthetic geometric-ratio acoustic experiment.

The eight integers are arbitrary machine states, not Num'ta'reen meanings.
The public waveform is forgeable. Never interpret decoding as provenance.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, log, pi, sin
from random import Random

SAMPLE_RATE = 16_000
SLOT_SAMPLES = 960
SLOTS = 4
FRAME_SAMPLES = SLOTS * SLOT_SAMPLES
STATES = 8
PILOT_HZ = 180.0
REFERENCE_HZ = 600.0
CODE_BASE_HZ = 650.0
RATIO = 1.30
MIN_PROMINENCE = .02
MAX_OFF_PROMINENCE = .009
# Across independent ±5% data slot scales, worst log skew is .100084.
# This acceptance margin is less than half the .262364 gap between states.
MAX_LOG_RESIDUAL = .112
# Exploratory X4 ambiguity gate, added AFTER the initial confirmatory run.
# Reject a second discrete state carrier with >=8% of the winner's power.
# This cannot detect arbitrarily faint second sources in finite noise.
MAX_SECONDARY_POWER_RATIO = .08


@dataclass(frozen=True)
class Frame:
    sample_rate: int
    samples: tuple[float, ...]


def _hann(index: int) -> float:
    return .5 - .5*cos(2*pi*index/(SLOT_SAMPLES-1))


def render(state: int, *, seed: int = 0, pilot_scale: float = 1.0,
           data_scale: float = 1.0, reference_drift: float = 1.0,
           code_drift: float = 1.0, noise: float = .0,
           gain: float = .7, phase: float = .0) -> Frame:
    """Four 60ms slots: pilot always; ref only in 0, state tone only in 2."""
    if type(state) is not int or not 0 <= state < STATES:
        raise ValueError("artificial state 0..7 required")
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("32-bit seed required")
    for key, value, low, high in (
        ("pilot_scale", pilot_scale, .72, 1.28),
        ("data_scale", data_scale, .8, 1.2),
        ("reference_drift", reference_drift, .95, 1.05),
        ("code_drift", code_drift, .95, 1.05),
        ("noise", noise, 0., .15),
        ("gain", gain, .01, .85),
        ("phase", phase, -2*pi, 2*pi),
    ):
        if type(value) not in (int, float) or not isfinite(value) or not low <= value <= high:
            raise ValueError(f"{key} outside experimental range")
    rng = Random(seed)
    result = []
    for n in range(FRAME_SAMPLES):
        slot, index = divmod(n, SLOT_SAMPLES)
        t = n/SAMPLE_RATE
        sample = .28*sin(2*pi*PILOT_HZ*pilot_scale*t + phase)
        if slot == 0:
            sample += .55*sin(2*pi*REFERENCE_HZ*data_scale*reference_drift*t
                              + phase/3 + .17)
        elif slot == 2:
            sample += .55*sin(2*pi*CODE_BASE_HZ*RATIO**state*data_scale
                              *code_drift*t + phase/3 + .17)
        result.append(float(gain * _hann(index) *
                            (sample + noise * rng.uniform(-1., 1.))))
    return Frame(SAMPLE_RATE, tuple(result))


def _goertzel(samples: tuple[float, ...], frequency: float) -> float:
    coefficient = 2*cos(2*pi*frequency/SAMPLE_RATE)
    one = two = 0.0
    for x in samples:
        current = x + coefficient*one - two
        two, one = one, current
    return one*one + two*two - coefficient*one*two


def _prominence(power: float, group: tuple[float, ...]) -> float:
    denominator = SLOT_SAMPLES * sum(x*x for x in group)
    return power/denominator if denominator > 0 else 0.


def _peak(group: tuple[float, ...], low: int, high: int, step: int = 2
          ) -> tuple[float, float]:
    power, hz = max((_goertzel(group, float(f)), float(f))
                    for f in range(low, high+1, step))
    return power, hz


def decode(frame: Frame) -> int | None:
    """Return artificial state or abstain. No claim of speaker authentication."""
    if not isinstance(frame, Frame):
        raise ValueError("Frame expected")
    if frame.sample_rate != SAMPLE_RATE or len(frame.samples) != FRAME_SAMPLES:
        raise ValueError("unexpected four-slot waveform geometry")
    if not all(type(x) is float and isfinite(x) and -1 <= x <= 1
               for x in frame.samples):
        raise ValueError("invalid waveform sample")
    if max(abs(x) for x in frame.samples) < 1e-5:
        return None
    groups = tuple(frame.samples[i*SLOT_SAMPLES:(i+1)*SLOT_SAMPLES]
                   for i in range(SLOTS))
    pilots = []
    for group in groups:
        power, hz = _peak(group, 125, 235)
        if _prominence(power, group) < MIN_PROMINENCE:
            return None
        pilots.append(hz)
    # Pilot frequency is an independent presence check. It MUST NOT be used
    # to infer data frequencies, because channel warping may be unequal.
    if max(pilots)-min(pilots) > 12.:
        return None
    ref_power, ref_hz = _peak(groups[0], 450, 770)
    if _prominence(ref_power, groups[0]) < MIN_PROMINENCE:
        return None

    candidates = []
    for state in range(STATES):
        expected = ref_hz*(CODE_BASE_HZ*RATIO**state/REFERENCE_HZ)
        # ±12% carrier search admits ±5% independent slot skew, without
        # allowing adjacent candidate search bands to overlap.
        lo = max(1, int(expected*.88))
        hi = min(SAMPLE_RATE//2 - 1, int(expected*1.12))
        power, coarse_hz = _peak(groups[2], lo, hi, 6)
        refine_lo = max(lo, int(coarse_hz)-8)
        refine_hi = min(hi, int(coarse_hz)+8)
        refined_power, actual_hz = _peak(groups[2], refine_lo, refine_hi)
        if refined_power > power:
            power = refined_power
        # Evaluate each candidate with the same source-independent scale.
        residual = abs(log(actual_hz/ref_hz) -
                       log(CODE_BASE_HZ/REFERENCE_HZ) - state*log(RATIO))
        candidates.append((power, state, actual_hz, residual))
    ranked = sorted(candidates, reverse=True)
    peak_power, state, code_hz, residual = ranked[0]
    if _prominence(peak_power, groups[2]) < MIN_PROMINENCE:
        return None
    if residual > MAX_LOG_RESIDUAL:
        return None
    if ranked[1][0] >= MAX_SECONDARY_POWER_RATIO*peak_power:
        return None

    # A stationary pilot/data mixture is not the designed temporal code.
    for slot in (1, 3):
        if _prominence(_goertzel(groups[slot], ref_hz), groups[slot]) > MAX_OFF_PROMINENCE:
            return None
        if _prominence(_goertzel(groups[slot], code_hz), groups[slot]) > MAX_OFF_PROMINENCE:
            return None
    return state


def make_noise_only(seed: int, amplitude: float) -> Frame:
    if type(seed) is not int or type(amplitude) is not float:
        raise ValueError("deterministic noise parameters required")
    rng = Random(seed)
    return Frame(SAMPLE_RATE, tuple(
        float(amplitude*_hann(n % SLOT_SAMPLES)*rng.uniform(-1., 1.))
        for n in range(FRAME_SAMPLES)
    ))


def make_stationary_harmonic(fundamental_hz: float) -> Frame:
    return Frame(SAMPLE_RATE, tuple(
        float(.3*_hann(n % SLOT_SAMPLES)*
              (.28*sin(2*pi*fundamental_hz*n/SAMPLE_RATE) +
               .55*sin(2*pi*3*fundamental_hz*n/SAMPLE_RATE)))
        for n in range(FRAME_SAMPLES)
    ))


def make_stationary_two_tone(state: int) -> Frame:
    return Frame(SAMPLE_RATE, tuple(
        float(.7*_hann(n % SLOT_SAMPLES)*
              (.28*sin(2*pi*PILOT_HZ*n/SAMPLE_RATE) +
               .55*sin(2*pi*CODE_BASE_HZ*RATIO**state*n/SAMPLE_RATE+.17)))
        for n in range(FRAME_SAMPLES)
    ))
