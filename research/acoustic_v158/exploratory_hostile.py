"""Exploratory X1: mixtures and temporal corruption beyond frozen controls.

Never count these post-confirmatory probes as preregistered C-series evidence.
"""

from __future__ import annotations

from redundant_geometric_code import Frame, SAMPLE_RATE, SLOT_SAMPLES, STATES, decode, render
from v158_benchmark import PAIRS


def weighted_mixtures() -> dict:
    results = {}
    for minority_fraction in (.01, .05, .10, .15, .25, .35, .45, .50):
        accepted = abstained = 0
        wrong_majority = 0
        for a, b in PAIRS:
            left = render(a, seed=7, noise=0.0)
            right = render(b, seed=7, noise=0.0)
            w = minority_fraction
            mixed = Frame(SAMPLE_RATE, tuple(
                float((1-w)*x + w*y) for x, y in zip(left.samples, right.samples)))
            got = decode(mixed)
            accepted += got is not None
            abstained += got is None
            wrong_majority += got is not None and got != a
        results[str(minority_fraction)] = {
            "accepted": accepted, "abstained": abstained, "nonmajority": wrong_majority
        }
    return results


def truncated_or_repeated_slots() -> dict:
    frame = render(3)
    width = len(frame.samples)//8
    results = {}
    for mode in ("swap-checks", "repeat-check-a", "erase-check-b", "reverse-guards"):
        groups = [frame.samples[i*width:(i+1)*width] for i in range(8)]
        if mode == "swap-checks":
            groups[4], groups[6] = groups[6], groups[4]
        elif mode == "repeat-check-a":
            groups[6] = groups[4]
        elif mode == "erase-check-b":
            groups[6] = groups[7]
        else:
            groups[5], groups[7] = groups[7], groups[5]
        changed = Frame(SAMPLE_RATE, tuple(x for g in groups for x in g))
        results[mode] = decode(changed)
    return results


def cross_state_checksum_splices() -> dict:
    """X3: valid prefix for one state with valid checks copied from another."""
    examined = accepted = abstained = 0
    unexpected = []
    for prefix_state in range(STATES):
        first = render(prefix_state)
        for check_state in range(STATES):
            if check_state == prefix_state:
                continue
            second = render(check_state)
            mixed = Frame(SAMPLE_RATE, first.samples[:4*SLOT_SAMPLES] +
                          second.samples[4*SLOT_SAMPLES:])
            got = decode(mixed)
            examined += 1
            if got is None:
                abstained += 1
            else:
                accepted += 1
                unexpected.append((prefix_state, check_state, got))
    return {"examined": examined, "abstained": abstained,
            "accepted": accepted, "unexpected": unexpected}


def temporal_offsets() -> dict:
    """X4: fixed-length silence padding shifts complete frames in time."""
    report = {}
    for shift in (1, 8, 32, 100, 240, 480):
        correct = abstained = wrong = 0
        for state in range(STATES):
            source = render(state)
            shifted = Frame(SAMPLE_RATE, tuple(float(0) for _ in range(shift)) +
                            source.samples[:-shift])
            got = decode(shifted)
            correct += got == state
            abstained += got is None
            wrong += got is not None and got != state
        report[shift] = {"correct": correct, "abstained": abstained, "wrong": wrong}
    return report


if __name__ == "__main__":
    print("X1 weak mixtures:", weighted_mixtures())
    print("X2 malformed temporal slots:", truncated_or_repeated_slots())
    print("X3 conflicting valid check fields:", cross_state_checksum_splices())
    print("X4 time offsets:", temporal_offsets())
