"""Independent V158 hostile checks, not native-language or identity validation."""

from __future__ import annotations

from math import pi, sin
from random import Random
import unittest

import geometric_pilot_code as old
import redundant_geometric_code as proposed


def near_codebook_mismatch(count: int = 96):
    """Valid public prefix; both redundancy carriers claim *other* states."""
    rng = Random(0x163ACE)
    for i in range(count):
        state = i % proposed.STATES
        a = (state + rng.randrange(1, proposed.STATES)) % proposed.STATES
        b = (state + rng.randrange(1, proposed.STATES)) % proposed.STATES
        kwargs = dict(seed=i + 100, noise=.02, phase=.2, data_scale=1.0)
        proper = proposed.render(state, **kwargs)
        wrong_a = proposed.render(a, **kwargs)
        wrong_b = proposed.render(b, **kwargs)
        n = proposed.SLOT_SAMPLES
        samples = (
            proper.samples[:4*n]
            + wrong_a.samples[4*n:5*n]
            + proper.samples[5*n:6*n]
            + wrong_b.samples[6*n:7*n]
            + proper.samples[7*n:]
        )
        yield state, (a, b), proposed.Frame(proposed.SAMPLE_RATE, samples)


def independent_shaped(seed: int, count: int):
    """Out-of-prereg-seed broad, valid pilot and guard scaffolds."""
    rng = Random(seed)
    for _ in range(count):
        carriers = (rng.uniform(480, 730),
                    rng.uniform(680, 4400),
                    rng.uniform(680, 4400),
                    rng.uniform(680, 4400))
        phases = tuple(rng.uniform(-pi, pi) for _ in range(4))
        gains = tuple(rng.uniform(.30, .68) for _ in range(4))
        samples = []
        for n in range(proposed.FRAME_SAMPLES):
            slot, in_slot = divmod(n, proposed.SLOT_SAMPLES)
            t = n / proposed.SAMPLE_RATE
            amplitude = .28 * sin(2*pi*old.PILOT_HZ*t)
            if slot in (0, 2, 4, 6):
                k = slot//2
                amplitude += .55*sin(2*pi*carriers[k]*t+phases[k])
                gain = gains[k]
            else:
                gain = .55
            samples.append(float(gain*old._hann(in_slot)*amplitude))
        yield proposed.Frame(proposed.SAMPLE_RATE, tuple(samples))


class IndependentHostile(unittest.TestCase):
    def test_128_randomized_single_source_within_bounds(self):
        rng = Random(0x1635EED)
        correct = abstain = wrong = 0
        for _ in range(128):
            state = rng.randrange(proposed.STATES)
            frame = proposed.render(
                state,
                seed=rng.randrange(2**16),
                pilot_scale=rng.uniform(.73, 1.27),
                data_scale=rng.uniform(.81, 1.19),
                reference_drift=rng.uniform(.95, 1.05),
                code_drift=rng.uniform(.95, 1.05),
                check_a_drift=rng.uniform(.95, 1.05),
                check_b_drift=rng.uniform(.95, 1.05),
                noise=rng.uniform(.0, .15),
                gain=rng.uniform(.1, .8),
                phase=rng.uniform(-pi, pi),
            )
            result = proposed.decode(frame)
            correct += result == state
            abstain += result is None
            wrong += result is not None and result != state
        print(f"V163 randomized in-contract 128: {correct=}, {abstain=}, {wrong=}")
        self.assertEqual(wrong, 0)
        self.assertGreaterEqual(correct, 120)

    def test_frame_window_shift_probes(self):
        # Window timing shift is outside frozen V158 model: record all states
        # and require only no *wrong* confident state on the listed probes.
        results = {}
        for shift in (1, 50, 100, 240, 480, 960):
            good = abstain = wrong = 0
            for state in range(proposed.STATES):
                original = proposed.render(state, seed=3, noise=.02)
                shifted = proposed.Frame(proposed.SAMPLE_RATE,
                                         tuple(float(0.0) for _ in range(shift))
                                         + original.samples[:-shift])
                result = proposed.decode(shifted)
                good += result == state
                abstain += result is None
                wrong += result is not None and result != state
            results[shift] = (good, abstain, wrong)
        print(f"V163 timing-shift exploratory outcomes: {results}")
        self.assertTrue(all(row[2] == 0 for row in results.values()),
                        f"Timing shifts silently misdecoded: {results}")

    def test_96_known_prefix_both_mismatched_checks(self):
        accepted = []
        for state, other, frame in near_codebook_mismatch():
            recovered = proposed.decode(frame)
            if recovered is not None:
                accepted.append((state, other, recovered))
        self.assertEqual(accepted, [], f"Wrong checks accepted: {accepted[:8]}")

    def test_128_out_of_seed_shaped_noncodewords(self):
        frames = tuple(independent_shaped(0xC0DEC0DE, 128))
        baseline_accepted = sum(old.decode(proposed.project_v138(x)) is not None
                                for x in frames)
        v2_accepted = sum(proposed.decode(x) is not None for x in frames)
        print(f"V163 negative out-of-seed 128: base={baseline_accepted}, V2={v2_accepted}")
        self.assertGreater(baseline_accepted, v2_accepted)
        self.assertLessEqual(v2_accepted, 6)

    def test_bad_order_and_public_replay(self):
        for state in range(proposed.STATES):
            proper = proposed.render(state, noise=.0)
            self.assertEqual(proposed.decode(proper), state)
            n = proposed.SLOT_SAMPLES
            slots = [proper.samples[i*n:(i+1)*n] for i in range(proposed.SLOTS)]
            slots[4], slots[6] = slots[6], slots[4]
            frame = proposed.Frame(proposed.SAMPLE_RATE, tuple(x for group in slots for x in group))
            self.assertIsNone(proposed.decode(frame), f"Swapped checks accepted for {state}")

    def test_minor_mixture_is_not_unique_source_proof(self):
        # Expect apparent majority-state output for sufficiently weak minority.
        # A passing test is a *negative* source-uniqueness control.
        accepted = 0
        for a in range(proposed.STATES):
            b = (a + 1) % proposed.STATES
            x = proposed.render(a, seed=7, noise=0.0)
            y = proposed.render(b, seed=7, noise=0.0)
            mixed = proposed.Frame(proposed.SAMPLE_RATE, tuple(
                float(.9*s + .1*t) for s, t in zip(x.samples, y.samples)))
            accepted += proposed.decode(mixed) is not None
        self.assertGreater(accepted, 0, "Minor source currently seems fully detectable")


if __name__ == "__main__":
    unittest.main()
