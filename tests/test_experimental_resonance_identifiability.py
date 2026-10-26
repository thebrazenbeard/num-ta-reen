"""Negative controls for NONCANONICAL acoustic test fixtures.

These tests evaluate a synthetic signal transport, not Nûm’ta’reen speech,
English translation, or independently learned semantic grounding. Generator
state IDs and nuisance controls stay on the evaluator side of the boundary.
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
import unittest


ROOT = Path(os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT))

from numtareen.experimental_resonance import (  # noqa: E402
    AcousticObservation,
    SCHEMA,
    render_experimental_resonance,
)


def pitch_collision() -> tuple[AcousticObservation, AcousticObservation]:
    """Different opaque states with the same observable 300 Hz carrier."""
    first = render_experimental_resonance(
        (0,), seed=7, pitch_scale=1.2, noise_level=0.0,
    )
    second = render_experimental_resonance(
        (1,), seed=7, pitch_scale=300.0 / 342.0, noise_level=0.0,
    )
    return first, second


class ExperimentalResonanceIdentifiabilityTests(unittest.TestCase):
    def test_allowed_pitch_nuisance_collides_for_two_distinct_states(self):
        self.assertEqual((250.0 + 92.0 * 0) * 1.2, 300.0)
        self.assertEqual((250.0 + 92.0 * 1) * (300.0 / 342.0), 300.0)

        first, second = pitch_collision()
        self.assertEqual(first.sample_rate_hz, 16_000)
        self.assertEqual(second.sample_rate_hz, 16_000)
        self.assertEqual(len(first.samples), 960)
        self.assertEqual(first.samples, second.samples)
        self.assertGreater(max(map(abs, first.samples)), 0.1)
        self.assertLessEqual(max(map(abs, first.samples)), 0.65)

    def test_observation_has_no_state_or_semantic_labels(self):
        first, _ = pitch_collision()
        self.assertEqual(SCHEMA, "NUMTAREEN_NONCANONICAL_SYNTHETIC_RESONANCE_V0")
        self.assertEqual(set(vars(first)), {"sample_rate_hz", "samples"})
        self.assertFalse(any(key in vars(first) for key in (
            "state", "seed", "english", "meaning", "gloss", "qualification_eligible"
        )))


@unittest.skipUnless(os.environ.get("UNVTRSLR_ROOT"),
                     "Set UNVTRSLR_ROOT for actual blind acoustic wire qualification")
class CrossRepositoryBlindAcousticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        public_root = Path(os.environ["UNVTRSLR_ROOT"]).resolve()
        sys.path.insert(0, str(public_root / "src"))
        from unvtrslr.blind_audio_observation import (  # noqa: E402
            decode_audio_observation,
            project_audio_observation,
        )
        cls.project = staticmethod(project_audio_observation)
        cls.decode = staticmethod(decode_audio_observation)

    def test_two_hidden_states_have_identical_four_field_wire(self):
        import numpy as np

        first, second = pitch_collision()
        left = self.project(first.samples, first.sample_rate_hz)
        right = self.project(second.samples, second.sample_rate_hz)

        self.assertEqual(left, right)
        self.assertEqual(set(left), {
            "schema", "sample_rate_hz", "shape", "float64_le_b64",
        })
        self.assertEqual(left["shape"], [960, 1])
        self.assertEqual(left["sample_rate_hz"], 16_000)

        reconstructed, rate = self.decode(left)
        self.assertEqual(rate, 16_000)
        self.assertEqual(reconstructed.shape, (960, 1))
        np.testing.assert_array_equal(reconstructed[:, 0], np.asarray(first.samples))

        with self.assertRaises(ValueError):
            self.decode({**left, "state": 0})


if __name__ == "__main__":
    unittest.main()
