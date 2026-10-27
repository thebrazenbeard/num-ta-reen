"""Discover frozen noncanonical V158 and independently authored V163 checks.

The original files are byte-for-byte copies of their reviewed research heads.
Only this small root-suite adapter adjusts the import path; none of the frozen
algorithms, preregistered samples, or hostile negative distributions changes.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import unittest


RESEARCH = Path(__file__).resolve().parents[1] / "research" / "acoustic_v158"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

from test_redundant_geometric_code import RedundantGeometricCodeTests  # noqa: E402,F401
from test_v158_hostile import IndependentHostile  # noqa: E402,F401


class AcousticResearchPackagingTests(unittest.TestCase):
    """Pinned custody prevents a later edit silently inheriting prior review."""

    FROZEN = {
        "geometric_pilot_code.py": "d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d",
        "redundant_geometric_code.py": "b2cdc57514ea41675f5a50c3cd9ccf4734ac54cf65fa6b612721daa8d9e8267f",
        "v158_benchmark.py": "7356042db8be6c35b88813433d3bd592362a4b5bb62ca3d8fb76a543f6aff74b",
        "test_redundant_geometric_code.py": "08e403710c48780a55dbff218e104265e7b7394d6ecba8beb622005c6130542a",
        "test_v158_hostile.py": "0edabc467b7f0e74a8167a27189f4eb81814bea8b17605bc64fdaf1f97d839e8",
    }

    def test_exact_frozen_reviewed_sources(self):
        for name, expected in self.FROZEN.items():
            with self.subTest(file=name):
                self.assertEqual(
                    hashlib.sha256((RESEARCH / name).read_bytes()).hexdigest(), expected
                )

    def test_eight_slot_duration_is_twice_v138(self):
        import geometric_pilot_code as old
        import redundant_geometric_code as new

        self.assertEqual(old.FRAME_SAMPLES, 3840)
        self.assertEqual(new.FRAME_SAMPLES, 7680)
        self.assertEqual(old.SAMPLE_RATE, new.SAMPLE_RATE)
        self.assertEqual(1000 * old.FRAME_SAMPLES / old.SAMPLE_RATE, 240)
        self.assertEqual(1000 * new.FRAME_SAMPLES / new.SAMPLE_RATE, 480)


if __name__ == "__main__":
    unittest.main()
