"""V158 exact preregistered C0-C5 controls; no source-authentication claims."""

from __future__ import annotations

import hashlib
import unittest
from pathlib import Path

from v158_benchmark import run
from redundant_geometric_code import (
    FRAME_SAMPLES, Frame, SAMPLE_RATE, STATES, decode, render,
)


V138_SHA256 = "d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d"


class RedundantGeometricCodeTests(unittest.TestCase):
    def test_C0_pinned_v138_dependency(self):
        import geometric_pilot_code as v138
        self.assertEqual(hashlib.sha256(Path(v138.__file__).read_bytes()).hexdigest(), V138_SHA256)

    def test_C1_geometry(self):
        self.assertEqual(FRAME_SAMPLES, 8*960)
        with self.assertRaises(ValueError):
            decode(Frame(SAMPLE_RATE, tuple(0.0 for _ in range(FRAME_SAMPLES-1))))
        self.assertIsNone(decode(Frame(SAMPLE_RATE, tuple(0.0 for _ in range(FRAME_SAMPLES)))))

    def test_C2_C5_full_preregistered_benchmark(self):
        report = run()
        self.assertGreaterEqual(report.positives_correct, 45)
        self.assertEqual(report.positives_wrong, 0)
        self.assertGreaterEqual(report.extreme_correct, 15)
        self.assertEqual(report.extreme_wrong, 0)
        self.assertLessEqual(report.negatives_accepted_v2, 5)
        self.assertLess(report.negatives_accepted_v2, report.negatives_accepted_baseline)
        self.assertEqual(report.equal_mix_accepted, 0)
        # Public forgeries MUST be accepted: evidence AGAINST authentication.
        self.assertEqual(report.forgeries_accepted, STATES)

    def test_invalid_public_states(self):
        for invalid in (-1, 8, 1.0, True):
            with self.assertRaises(ValueError):
                render(invalid)


if __name__ == "__main__":
    unittest.main()
