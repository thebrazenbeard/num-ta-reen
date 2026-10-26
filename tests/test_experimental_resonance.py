"""Executable controls for a strictly noncanonical experimental generator."""

import math
from itertools import repeat
import unittest
from dataclasses import asdict, fields

from numtareen.experimental_resonance import (
    AcousticObservation,
    MAX_BATCH_SAMPLES,
    MAX_SAMPLES,
    render_experimental_resonance,
    render_matched_batch,
)


class SyntheticResonanceTests(unittest.TestCase):
    def test_same_evaluator_seed_and_settings_are_repeatable(self):
        first = render_experimental_resonance((0, 3, 7), seed=17, noise_level=0.08)
        second = render_experimental_resonance((0, 3, 7), seed=17, noise_level=0.08)
        self.assertEqual(first, second)
        self.assertEqual(len(first.samples), 3 * 960)
        self.assertEqual(first.sample_rate_hz, 16_000)

    def test_output_has_no_truth_or_label_metadata(self):
        public = render_experimental_resonance((2, 5), seed=3)
        self.assertIsInstance(public, AcousticObservation)
        self.assertEqual({f.name for f in fields(public)}, {"samples", "sample_rate_hz"})
        self.assertEqual(set(asdict(public)), {"samples", "sample_rate_hz"})
        self.assertTrue(all(isinstance(x, float) and math.isfinite(x) for x in public.samples))
        self.assertTrue(all(-1.0 <= x <= 1.0 for x in public.samples))

    def test_noncanonical_state_contrasts_and_same_length_controls(self):
        a = render_experimental_resonance((0, 1), seed=3)
        b = render_experimental_resonance((0, 2), seed=3)
        self.assertEqual(len(a.samples), len(b.samples))
        self.assertNotEqual(a.samples, b.samples)
        self.assertEqual(a.samples[:960], b.samples[:960])

    def test_nuisance_gain_changes_amplitude_not_state_length(self):
        a = render_experimental_resonance((1,), seed=9, gain=0.2)
        b = render_experimental_resonance((1,), seed=9, gain=0.4)
        self.assertEqual(len(a.samples), len(b.samples))
        for low, high in zip(a.samples, b.samples):
            self.assertAlmostEqual(high, 2 * low, places=12)

    def test_seed_changes_noise_not_silence_control(self):
        a = render_experimental_resonance((4,), seed=1, noise_level=0.1)
        b = render_experimental_resonance((4,), seed=2, noise_level=0.1)
        self.assertNotEqual(a.samples, b.samples)
        z1 = render_experimental_resonance((4,), seed=1, noise_level=0.1, silence_control=True)
        z2 = render_experimental_resonance((4,), seed=2, noise_level=0.1, silence_control=True)
        self.assertEqual(z1.samples, z2.samples)
        self.assertEqual(z1.samples, (0.0,) * 960)

    def test_private_codebook_permutation_reassigns_carriers(self):
        normal = render_experimental_resonance((0,), seed=8)
        swapped = render_experimental_resonance(
            (0,), seed=8, evaluator_codebook=(1, 0, 2, 3, 4, 5, 6, 7)
        )
        self.assertNotEqual(normal.samples, swapped.samples)
        self.assertEqual(normal.sample_rate_hz, swapped.sample_rate_hz)

    def test_nuisance_pitch_phase_and_noise_keep_bounds(self):
        raw = render_experimental_resonance(
            (0, 4, 7), seed=123, pitch_scale=1.2,
            phase_shift_rad=math.pi, noise_level=0.15, gain=0.85,
        )
        self.assertEqual(len(raw.samples), 2880)
        self.assertLessEqual(max(abs(s) for s in raw.samples), 1.0)

    def test_matched_batch_freezes_public_geometry_across_hidden_classes(self):
        batch = render_matched_batch(((0, 4), (2, 7), (6, 1)), batch_seed=42, noise_level=0.12)
        self.assertEqual(len(batch), 3)
        self.assertEqual({(x.sample_rate_hz, len(x.samples)) for x in batch}, {(16_000, 1920)})
        self.assertNotEqual(batch[0].samples, batch[1].samples)
        self.assertEqual(batch, render_matched_batch(((0, 4), (2, 7), (6, 1)), batch_seed=42, noise_level=0.12))
        self.assertNotEqual(batch, render_matched_batch(((0, 4), (2, 7), (6, 1)), batch_seed=43, noise_level=0.12))
        self.assertTrue(all(set(asdict(x)) == {"sample_rate_hz", "samples"} for x in batch))

    def test_matched_batch_blocks_length_as_class_label(self):
        with self.assertRaisesRegex(ValueError, "identical state counts"):
            render_matched_batch(((0,), (1, 2)), batch_seed=0)
        with self.assertRaisesRegex(ValueError, "matched batch count"):
            render_matched_batch(((0,),), batch_seed=0)
        with self.assertRaisesRegex(ValueError, "matched batch count"):
            render_matched_batch(repeat((0,)), batch_seed=0)
        with self.assertRaisesRegex(ValueError, "batch_seed"):
            render_matched_batch(((0,), (1,)), batch_seed=True)
        for invalid_geometry in ("960", 960.5, True):
            with self.subTest(invalid_geometry=invalid_geometry), self.assertRaisesRegex(ValueError, "samples_per_state"):
                render_matched_batch(((0,), (1,)), batch_seed=0,
                                     samples_per_state=invalid_geometry)
        with self.assertRaisesRegex(ValueError, "aggregate sample cap"):
            render_matched_batch((tuple(range(8)) * 8 for _ in range(16)),
                                 batch_seed=0, samples_per_state=2_000)
        self.assertEqual(MAX_BATCH_SAMPLES, 1_048_576)

    def test_unicode_language_or_true_name_not_accepted_as_state_id(self):
        for values in (("nûm",), ("num",), ("ech", "reen"), ("=uth",), ("E26",)):
            with self.subTest(values=values), self.assertRaisesRegex(ValueError, "opaque integers"):
                render_experimental_resonance(values, seed=0)

    def test_invalid_parameters_fail_closed(self):
        cases = [
            ({"seed": True}, "seed"),
            ({"seed": -1}, "seed"),
            ({"seed": 2**32}, "seed"),
            ({"seed": 0, "sample_rate_hz": 0}, "sample_rate_hz"),
            ({"seed": 0, "sample_rate_hz": 16_000.5}, "sample_rate_hz"),
            ({"seed": 0, "samples_per_state": 127}, "samples_per_state"),
            ({"seed": 0, "gain": float("nan")}, "gain"),
            ({"seed": 0, "gain": float("inf")}, "gain"),
            ({"seed": 0, "noise_level": -0.1}, "noise_level"),
            ({"seed": 0, "pitch_scale": float("inf")}, "pitch_scale"),
            ({"seed": 0, "phase_shift_rad": float("nan")}, "phase_shift_rad"),
            ({"seed": 0, "silence_control": 1}, "silence_control"),
            ({"seed": 0, "evaluator_codebook": tuple([0] * 8)}, "evaluator_codebook"),
        ]
        for kwargs, expected in cases:
            with self.subTest(kwargs=kwargs), self.assertRaisesRegex(ValueError, expected):
                render_experimental_resonance((2,), **kwargs)

    def test_invalid_state_sequences_and_size_cap(self):
        for seq in ((), (True,), (-1,), (8,), (3.0,), range(65), repeat(0)):
            with self.subTest(seq=str(seq)[:25]), self.assertRaises(ValueError):
                render_experimental_resonance(seq, seed=1)
        with self.assertRaisesRegex(ValueError, "sample cap"):
            render_experimental_resonance(tuple(range(8)) * 8, seed=0, samples_per_state=12_000)
        self.assertLessEqual(32 * 960, MAX_SAMPLES)


if __name__ == "__main__":
    unittest.main()
