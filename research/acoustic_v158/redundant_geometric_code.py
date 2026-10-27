"""V158 eight-slot *synthetic* public redundancy over V138's geometric codec.

This is not a Num'ta'reen sentence encoder, voice model, or source authentication
mechanism. An adversary can produce every acceptable waveform.

Requires the exact frozen research dependency geometric_pilot_code (V138).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, pi, sin
from random import Random

import geometric_pilot_code as v138


SAMPLE_RATE = v138.SAMPLE_RATE
SLOT_SAMPLES = v138.SLOT_SAMPLES
SLOTS = 8
FRAME_SAMPLES = SLOT_SAMPLES * SLOTS
STATES = v138.STATES
CHECK_A_BASE_HZ = 700.0
CHECK_B_BASE_HZ = 750.0
CHECK_RATIO = 1.30
# Frozen V158 parameter, fixed before confirmatory execution.
MAX_LOG_RESIDUAL = .112
MIN_PROMINENCE = v138.MIN_PROMINENCE
MAX_OFF_PROMINENCE = v138.MAX_OFF_PROMINENCE


@dataclass(frozen=True)
class Frame:
    sample_rate: int
    samples: tuple[float, ...]


def _check_index(state: int, check: int) -> int:
    return (3 * state + 1) % STATES if check == 0 else (5 * state + 2) % STATES


def _check_frequency(state: int, check: int, scale: float) -> float:
    base = CHECK_A_BASE_HZ if check == 0 else CHECK_B_BASE_HZ
    return base * CHECK_RATIO ** _check_index(state, check) * scale


def render(
    state: int,
    *,
    seed: int = 0,
    pilot_scale: float = 1.0,
    data_scale: float = 1.0,
    reference_drift: float = 1.0,
    code_drift: float = 1.0,
    check_a_drift: float = 1.0,
    check_b_drift: float = 1.0,
    noise: float = 0.0,
    gain: float = .7,
    phase: float = 0.0,
) -> Frame:
    """Build V138 prefix followed by two public, redundant check/guard pairs."""
    for label, value in (("check_a_drift", check_a_drift), ("check_b_drift", check_b_drift)):
        if type(value) not in (float, int) or not isfinite(value) or not .95 <= value <= 1.05:
            raise ValueError(f"{label} outside declared ±5% bound")
    prefix = v138.render(
        state, seed=seed, pilot_scale=pilot_scale, data_scale=data_scale,
        reference_drift=reference_drift, code_drift=code_drift,
        noise=noise, gain=gain, phase=phase,
    )
    # The prefix renderer validated all its parameters including integer seed.
    rng = Random(seed ^ 0xA582)
    result = list(prefix.samples)
    for absolute_n in range(v138.FRAME_SAMPLES, FRAME_SAMPLES):
        slot, in_slot = divmod(absolute_n, SLOT_SAMPLES)
        t = absolute_n / SAMPLE_RATE
        amplitude = .28 * sin(2*pi*v138.PILOT_HZ*pilot_scale*t + phase)
        if slot == 4:
            amplitude += .55*sin(2*pi*_check_frequency(
                state, 0, data_scale*check_a_drift)*t + phase/3 + .17)
        elif slot == 6:
            amplitude += .55*sin(2*pi*_check_frequency(
                state, 1, data_scale*check_b_drift)*t + phase/3 + .17)
        sample = gain*v138._hann(in_slot)*(amplitude + noise*rng.uniform(-1., 1.))
        result.append(float(sample))
    return Frame(SAMPLE_RATE, tuple(result))


def project_v138(frame: Frame) -> v138.Frame:
    """For matched negative controls, project first four slots unchanged."""
    if not isinstance(frame, Frame):
        raise ValueError("V158 Frame expected")
    return v138.Frame(frame.sample_rate, frame.samples[:v138.FRAME_SAMPLES])


def _check_slot(group: tuple[float, ...], ref_hz: float, state: int, check: int
                ) -> float | None:
    nominal = _check_frequency(state, check, ref_hz / v138.REFERENCE_HZ)
    # One fixed ±12% carrier search per check field. Adjacent supported
    # geometric states remain separated under modeled independent ±5% drift.
    low = max(1, int(nominal*.88))
    high = min(SAMPLE_RATE // 2 - 1, int(nominal*1.12))
    power, coarse_hz = v138._peak(group, low, high, 6)
    narrow_low = max(low, int(coarse_hz)-8)
    narrow_high = min(high, int(coarse_hz)+8)
    refined_power, hz = v138._peak(group, narrow_low, narrow_high)
    if refined_power > power:
        power = refined_power
    if v138._prominence(power, group) < MIN_PROMINENCE:
        return None
    if abs(log(hz / nominal)) > MAX_LOG_RESIDUAL:
        return None
    return hz


def decode(frame: Frame) -> int | None:
    """Return public artificial state or abstain, never authenticate a sender."""
    if not isinstance(frame, Frame):
        raise ValueError("V158 Frame expected")
    if frame.sample_rate != SAMPLE_RATE or len(frame.samples) != FRAME_SAMPLES:
        raise ValueError("unexpected V158 eight-slot waveform geometry")
    if not all(type(x) is float and isfinite(x) and -1 <= x <= 1 for x in frame.samples):
        raise ValueError("invalid waveform sample")
    state = v138.decode(project_v138(frame))
    if state is None:
        return None
    groups = tuple(frame.samples[i*SLOT_SAMPLES:(i+1)*SLOT_SAMPLES] for i in range(SLOTS))
    _, ref_hz = v138._peak(groups[0], 450, 770)
    _, prefix_pilot_hz = v138._peak(groups[3], 125, 235)
    for slot in (4, 5, 6, 7):
        power, hz = v138._peak(groups[slot], 125, 235)
        if v138._prominence(power, groups[slot]) < MIN_PROMINENCE:
            return None
        if abs(hz-prefix_pilot_hz) > 12:
            return None
    for check, (carrier_slot, guard_slot) in enumerate(((4, 5), (6, 7))):
        actual_hz = _check_slot(groups[carrier_slot], ref_hz, state, check)
        if actual_hz is None:
            return None
        if v138._prominence(v138._goertzel(groups[guard_slot], actual_hz),
                            groups[guard_slot]) > MAX_OFF_PROMINENCE:
            return None
    return state
