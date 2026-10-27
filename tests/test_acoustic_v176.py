"""Repository-portable custody and reproduction of frozen V176 synthetic research.

The single confirmatory run was already made and archived. Repeating its seed
tests reproducibility, not an additional independent sample.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parent.parent
RESEARCH = ROOT / "research" / "acoustic_v176"
DEPENDENCIES = ROOT / "research" / "acoustic_v158"
FROZEN_SHA256 = {
    "PROTOCOL.md": "a08bcbb0378014806b5e9b38a655aa83acb39b038a186892a87ec17c159795fc",
    "equal_duration_probe.py": "81a2e40abdc8855617e218c3c8212276c8ba7943ff5da906369b11a162838896",
    "test_equal_duration_probe.py": "5c884ff81dd7d1b4a33365b0fb1c8abb6436a8cd0673c1ad2c60a84568faf65a",
    "RESULT.json": "f7f5816eabc8914ef8107d58923cf3f4026a82cbef87c85f1a78e0f60f9ec4fe",
}


def _load_frozen_probe():
    location = RESEARCH / "equal_duration_probe.py"
    spec = importlib.util.spec_from_file_location("frozen_v176_probe", location)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load frozen V176 research")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AcousticV176PackagingTests(unittest.TestCase):
    def test_frozen_research_bytes_match_recorded_hashes(self):
        for name, expected in FROZEN_SHA256.items():
            with self.subTest(name=name):
                digest = hashlib.sha256((RESEARCH / name).read_bytes()).hexdigest()
                self.assertEqual(digest, expected)

    def test_both_codes_use_same_480ms_duration(self):
        probe = _load_frozen_probe()
        v138, v158, _ = probe.load_frozen(DEPENDENCIES)
        self.assertEqual(v138.SAMPLE_RATE, v158.SAMPLE_RATE)
        self.assertEqual(v138.FRAME_SAMPLES * 2, v158.FRAME_SAMPLES)
        self.assertEqual(v158.FRAME_SAMPLES / v158.SAMPLE_RATE, 0.48)

    def test_consensus_and_scoring_failure_cases(self):
        probe = _load_frozen_probe()
        v138, _v158, _ = probe.load_frozen(DEPENDENCIES)
        a = v138.render(3, seed=17).samples
        b = v138.render(3, seed=19).samples
        different = v138.render(4, seed=19).samples
        self.assertEqual(probe.decode_two_v138(a + b, v138.SAMPLE_RATE, v138), 3)
        self.assertIsNone(probe.decode_two_v138(a + different, v138.SAMPLE_RATE, v138))
        self.assertEqual(probe.score_label(1, 2), "wrong")
        self.assertEqual(probe.score_label(None, 2), "abstain")
        with self.assertRaises(ValueError):
            probe.decode_two_v138(a, v138.SAMPLE_RATE, v138)

    def test_single_frozen_seed_result_is_reproducible(self):
        probe = _load_frozen_probe()
        expected = json.loads((RESEARCH / "RESULT.json").read_text(encoding="utf-8"))
        observed = probe.run(DEPENDENCIES)
        self.assertEqual(observed, expected)
        self.assertEqual(observed["negative"]["v138_twice_accept"], 0)
        self.assertEqual(observed["negative"]["v158_accept"], 1)
        self.assertEqual(observed["positive"]["v138_twice"]["wrong"], 0)
        self.assertEqual(observed["positive"]["v158"]["wrong"], 0)
        self.assertEqual(observed["public_forgery"]["accepted"], 8)


if __name__ == "__main__":
    unittest.main()
