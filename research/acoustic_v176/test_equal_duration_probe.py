"""Post-result regression checks; rerun of frozen seeds is NOT fresh evidence."""

from pathlib import Path
import unittest

import equal_duration_probe as probe


SOURCE = Path(__file__).resolve().parent.parent / "ling-acoustic-package-v168/research/acoustic_v158"


class EqualDurationProbeTests(unittest.TestCase):
    def test_both_schemes_have_480ms_budget(self):
        old, proposed, _ = probe.load_frozen(SOURCE)
        self.assertEqual(old.FRAME_SAMPLES * 2, proposed.FRAME_SAMPLES)
        self.assertEqual(proposed.FRAME_SAMPLES / old.SAMPLE_RATE, .48)

    def test_two_v138_consensus_rejects_mismatch_and_accepts_repeated_state(self):
        old, proposed, _ = probe.load_frozen(SOURCE)
        a = old.render(3, seed=17).samples
        b = old.render(3, seed=19).samples
        c = old.render(4, seed=19).samples
        self.assertEqual(probe.decode_two_v138(a + b, old.SAMPLE_RATE, old), 3)
        self.assertIsNone(probe.decode_two_v138(a + c, old.SAMPLE_RATE, old))
        with self.assertRaises(ValueError):
            probe.decode_two_v138(a, old.SAMPLE_RATE, old)
        self.assertEqual(proposed.FRAME_SAMPLES, len(a + b))

    def test_label_logic_explicitly_covers_wrong_and_abstain(self):
        self.assertEqual(probe.score_label(2, 2), "correct")
        self.assertEqual(probe.score_label(1, 2), "wrong")
        self.assertEqual(probe.score_label(None, 2), "abstain")

    def test_frozen_same_seed_outcomes_reproducible_not_independent(self):
        outcome = probe.run(SOURCE)
        self.assertEqual(outcome["negative"]["count"], 128)
        self.assertEqual(outcome["negative"]["v138_twice_accept"], 0)
        self.assertEqual(outcome["negative"]["v158_accept"], 1)
        self.assertEqual(outcome["negative"]["paired"], {
            "repeat_0_v158_0": 127,
            "repeat_0_v158_1": 1,
            "repeat_1_v158_0": 0,
            "repeat_1_v158_1": 0,
        })
        for name in ("v138_twice", "v158"):
            self.assertEqual(outcome["positive"][name], {
                "correct": 96, "wrong": 0, "abstain": 0,
            })
        self.assertEqual(outcome["public_forgery"], {"accepted": 8, "total": 8})


if __name__ == "__main__":
    unittest.main()
