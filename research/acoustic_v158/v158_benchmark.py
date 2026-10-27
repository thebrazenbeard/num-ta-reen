"""Frozen V158 C2-C5 synthetic benchmark, never a natural-language metric."""

from __future__ import annotations

from dataclasses import dataclass
from math import pi, sin
from random import Random

import geometric_pilot_code as v138
from redundant_geometric_code import (
    Frame, SAMPLE_RATE, SLOT_SAMPLES, SLOTS, STATES, decode, project_v138,
    render,
)


PAIRS = ((0, 1), (0, 7), (1, 6), (2, 5), (3, 4), (2, 7), (4, 6), (5, 7))


def shaped_noncodebook_frames(count: int = 50) -> tuple[Frame, ...]:
    """Deterministic seeded public-pilot frames with independent random carriers.

    The frequencies are drawn *independently*, without using the state-to-check
    permutations, though chance can produce a valid codeword by coincidence.
    """
    if type(count) is not int or not 0 <= count <= 50:
        raise ValueError("V158 preregistered negative count must be 0..50")
    rng = Random(0xA582)
    frames = []
    for _ in range(count):
        carriers = (rng.uniform(480, 730), rng.uniform(680, 4400),
                    rng.uniform(680, 4400), rng.uniform(680, 4400))
        phases = tuple(rng.uniform(-pi, pi) for _ in range(4))
        gains = tuple(rng.uniform(.30, .68) for _ in range(4))
        samples = []
        for n in range(SLOTS * SLOT_SAMPLES):
            slot, in_slot = divmod(n, SLOT_SAMPLES)
            t = n/SAMPLE_RATE
            amplitude = .28*sin(2*pi*v138.PILOT_HZ*t)
            if slot in (0, 2, 4, 6):
                index = slot//2
                amplitude += .55*sin(2*pi*carriers[index]*t+phases[index])
                gain = gains[index]
            else:
                gain = .55
            samples.append(float(gain*v138._hann(in_slot)*amplitude))
        frames.append(Frame(SAMPLE_RATE, tuple(samples)))
    return tuple(frames)


def mixture(a: int, b: int) -> Frame:
    left = render(a, seed=7, noise=0.0)
    right = render(b, seed=7, noise=0.0)
    return Frame(SAMPLE_RATE, tuple(float(.5*x+.5*y)
                                    for x, y in zip(left.samples, right.samples)))


@dataclass(frozen=True)
class Results:
    positives_correct: int
    positives_abstain: int
    positives_wrong: int
    extreme_correct: int
    extreme_abstain: int
    extreme_wrong: int
    negatives_accepted_baseline: int
    negatives_accepted_v2: int
    equal_mix_accepted: int
    forgeries_accepted: int


def run() -> Results:
    correct = abstain = wrong = 0
    for state in range(STATES):
        for scale in (.8, 1.0, 1.2):
            for seed, skew, check_a, check_b in (
                (1, .95, .95, 1.05),
                (9, 1.05, 1.05, .95),
            ):
                received = decode(render(
                    state, seed=seed, data_scale=scale,
                    pilot_scale=scale*skew, check_a_drift=check_a,
                    check_b_drift=check_b, noise=.08, phase=(seed % 3)*.8))
                correct += received == state
                abstain += received is None
                wrong += received is not None and received != state
    extreme_correct = extreme_abstain = extreme_wrong = 0
    for state in range(STATES):
        for ref_drift, other_drift in ((1.05, .95), (.95, 1.05)):
            received = decode(render(
                state, reference_drift=ref_drift, code_drift=other_drift,
                check_a_drift=other_drift, check_b_drift=other_drift,
                noise=.04))
            extreme_correct += received == state
            extreme_abstain += received is None
            extreme_wrong += received is not None and received != state
    negatives = shaped_noncodebook_frames()
    baseline_accept = sum(v138.decode(project_v138(x)) is not None for x in negatives)
    v2_accept = sum(decode(x) is not None for x in negatives)
    mixed_accept = sum(decode(mixture(a, b)) is not None for a, b in PAIRS)
    forge_accept = sum(decode(render(s)) == s for s in range(STATES))
    return Results(correct, abstain, wrong, extreme_correct, extreme_abstain,
                   extreme_wrong, baseline_accept, v2_accept, mixed_accept,
                   forge_accept)


if __name__ == "__main__":
    print(run())
