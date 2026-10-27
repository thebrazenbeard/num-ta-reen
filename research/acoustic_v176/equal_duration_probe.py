"""V176 frozen synthetic 480 ms V138 repetition vs V158 comparison.

This module measures public artificial integer detectors. Not native speech,
semantic communication, sender authentication, or a physical-channel model.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from math import pi
from pathlib import Path
from random import Random
import sys


FROZEN_FILES = {
    "geometric_pilot_code.py": "d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d",
    "redundant_geometric_code.py": "b2cdc57514ea41675f5a50c3cd9ccf4734ac54cf65fa6b612721daa8d9e8267f",
    "test_v158_hostile.py": "0edabc467b7f0e74a8167a27189f4eb81814bea8b17605bc64fdaf1f97d839e8",
}
NEGATIVE_SEED = 0x176A501
POSITIVE_SEED = 0x176B502
NEGATIVE_COUNT = 128
POSITIVE_COUNT = 96


def load_frozen(source_dir: Path):
    for name, expected in FROZEN_FILES.items():
        actual = hashlib.sha256((source_dir / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"frozen {name} checksum mismatch: {actual}")
    source = str(source_dir.resolve())
    if source not in sys.path:
        sys.path.insert(0, source)
    import geometric_pilot_code as old
    import redundant_geometric_code as proposed
    from test_v158_hostile import independent_shaped
    if old.FRAME_SAMPLES != 3840 or proposed.FRAME_SAMPLES != 7680:
        raise AssertionError("frozen 240/480 ms budget changed")
    return old, proposed, independent_shaped


def decode_two_v138(samples: tuple[float, ...], sample_rate: int, old) -> int | None:
    """Conservative two-message, 480 ms repetition consensus, no adaptive tuning."""
    if sample_rate != old.SAMPLE_RATE or len(samples) != 2*old.FRAME_SAMPLES:
        raise ValueError("expected two complete 240 ms frames")
    left = old.decode(old.Frame(sample_rate, samples[:old.FRAME_SAMPLES]))
    right = old.decode(old.Frame(sample_rate, samples[old.FRAME_SAMPLES:]))
    return left if left is not None and left == right else None


def nuisance(rng: Random) -> dict:
    return {
        "pilot_scale": rng.uniform(.80, 1.20),
        "data_scale": rng.uniform(.85, 1.15),
        "noise": rng.uniform(.0, .08),
        "gain": rng.uniform(.30, .70),
        "phase": rng.uniform(-pi, pi),
    }


def score_label(actual: int | None, expected: int) -> str:
    if actual is None:
        return "abstain"
    return "correct" if actual == expected else "wrong"


def run(source_dir: Path) -> dict:
    old, proposed, independent_shaped = load_frozen(source_dir)
    rows = []
    negative_matrix = Counter()
    for frame in independent_shaped(NEGATIVE_SEED, NEGATIVE_COUNT):
        repeat = decode_two_v138(frame.samples, frame.sample_rate, old)
        v158_result = proposed.decode(frame)
        pair = (repeat is not None, v158_result is not None)
        negative_matrix[pair] += 1
    if sum(negative_matrix.values()) != NEGATIVE_COUNT:
        raise AssertionError("negative trial count changed")

    rng = Random(POSITIVE_SEED)
    positives = {"v138_twice": Counter(), "v158": Counter()}
    for _ in range(POSITIVE_COUNT):
        state = rng.randrange(proposed.STATES)
        shared = nuisance(rng)
        first = old.render(state, seed=rng.randrange(2**32),
                           reference_drift=rng.uniform(.96, 1.04),
                           code_drift=rng.uniform(.96, 1.04), **shared)
        second = old.render(state, seed=rng.randrange(2**32),
                            reference_drift=rng.uniform(.96, 1.04),
                            code_drift=rng.uniform(.96, 1.04), **shared)
        both = first.samples + second.samples
        if len(both) != proposed.FRAME_SAMPLES:
            raise AssertionError("mismatched frame duration")
        result_old = decode_two_v138(both, old.SAMPLE_RATE, old)
        proposed_frame = proposed.render(
            state, seed=rng.randrange(2**32),
            reference_drift=rng.uniform(.96, 1.04),
            code_drift=rng.uniform(.96, 1.04),
            check_a_drift=rng.uniform(.96, 1.04),
            check_b_drift=rng.uniform(.96, 1.04), **shared)
        result_new = proposed.decode(proposed_frame)
        positives["v138_twice"][score_label(result_old, state)] += 1
        positives["v158"][score_label(result_new, state)] += 1

    public_forgery_accepted = sum(
        proposed.decode(proposed.render(state, seed=0, noise=.0)) == state
        for state in range(proposed.STATES)
    )
    result = {
        "evidence": "FROZEN_SYNTHETIC_EQUAL_DURATION_EXPERIMENT",
        "duration_ms_each": 480,
        "negative": {
            "seed": NEGATIVE_SEED,
            "count": NEGATIVE_COUNT,
            "v138_twice_accept": sum(n for (a, _), n in negative_matrix.items() if a),
            "v158_accept": sum(n for (_, b), n in negative_matrix.items() if b),
            "paired": {
                f"repeat_{int(a)}_v158_{int(b)}": negative_matrix[(a, b)]
                for a in (False, True) for b in (False, True)
            },
        },
        "positive": {
            "seed": POSITIVE_SEED,
            "count_each": POSITIVE_COUNT,
            **{key: {grade: c[grade] for grade in ("correct", "wrong", "abstain")}
               for key, c in positives.items()},
        },
        "public_forgery": {"accepted": public_forgery_accepted, "total": proposed.STATES},
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path,
                        default=Path(__file__).resolve().parent.parent /
                        "ling-acoustic-package-v168/research/acoustic_v158")
    args = parser.parse_args()
    print(json.dumps(run(args.source_dir), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
