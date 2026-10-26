"""Evaluator-only cross-repository synthetic acoustic benchmark.

No canonical Nûm’ta’reen signal or English semantics is represented here.
Opaque state/arm IDs belong to the trusted evaluator, never to a blind
observation. This in-process test is NOT learner/evaluator isolation.
"""

from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
import sys
import unittest

ROOT = Path(os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT))

from numtareen.experimental_probe_splits import (  # noqa: E402
    NuisanceArm,
    render_private_balanced_probe_splits,
)


# Separate nuisance settings from the existing private split regression so
# this test exercises a second frozen, explicitly synthetic experiment.
TRAIN = (
    NuisanceArm(gain=0.40, pitch_scale=0.92, noise_level=0.04),
    NuisanceArm(gain=0.65, pitch_scale=1.04, noise_level=0.09),
)
HOLDOUT = (
    NuisanceArm(gain=0.48, pitch_scale=1.12, noise_level=0.07),
    NuisanceArm(gain=0.75, pitch_scale=0.85, noise_level=0.12),
)


PUBLIC_ROOT = Path(os.environ.get("UNVTRSLR_ROOT", "/nonexistent")).resolve()
HAS_PUBLIC_SUPERVISED_PEER = (
    bool(os.environ.get("UNVTRSLR_ROOT"))
    and (PUBLIC_ROOT / "src/unvtrslr/empirical_signal_baselines.py").is_file()
)


@unittest.skipUnless(HAS_PUBLIC_SUPERVISED_PEER,
                     "Requires public supervised acoustic peer, not legacy reference-only pin")
class EvaluatorOnlySyntheticBenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(PUBLIC_ROOT / "src"))
        from unvtrslr.blind_audio_observation import (  # noqa: E402
            decode_audio_observation,
            project_audio_observation,
        )
        from unvtrslr.empirical_signal_baselines import (  # noqa: E402
            LabeledAcousticTrial,
            score_supervised_peak_lookup,
        )

        cls.decode = staticmethod(decode_audio_observation)
        cls.project = staticmethod(project_audio_observation)
        cls.Trial = LabeledAcousticTrial
        cls.score = staticmethod(score_supervised_peak_lookup)
        cls.experiment = render_private_balanced_probe_splits(
            batch_seed=17, train_arms=TRAIN, holdout_arms=HOLDOUT,
        )

    @classmethod
    def evaluator_trials(cls, split, prefix: str):
        # Critical boundary: hidden IDs are joined in evaluator memory only,
        # AFTER waveform projection. Never serialize a LabeledAcousticTrial to
        # a learner or permit its private fields into the four-key payload.
        rows = []
        for index, (audio, label) in enumerate(zip(
            split.observations, split.hidden_state_ids,
        )):
            wire = cls.project(audio.samples, audio.sample_rate_hz)
            rows.append(cls.Trial(
                trial_id=f"{prefix}-{index}",
                family_id=f"{prefix}-family-{index}",
                payload=wire,
                opaque_class_id=label,
            ))
        return rows

    def test_balanced_private_labels_and_unlabeled_public_wire(self):
        experiment = self.experiment
        for split in (experiment.train, experiment.holdout):
            self.assertEqual(len(split.observations), 16)
            self.assertEqual(Counter(split.hidden_state_ids),
                             dict.fromkeys(range(8), 2))
            self.assertEqual(Counter(zip(split.hidden_state_ids, split.hidden_arm_ids)),
                             {(state, arm): 1 for state in range(8) for arm in range(2)})
        train = self.evaluator_trials(experiment.train, "train")
        holdout = self.evaluator_trials(experiment.holdout, "holdout")
        self.assertEqual(len(train), len(holdout))
        for row in train + holdout:
            self.assertEqual(set(row.payload), {
                "schema", "sample_rate_hz", "shape", "float64_le_b64",
            })
            self.assertEqual(row.payload["sample_rate_hz"], 16000)
            self.assertEqual(row.payload["shape"], [960, 1])
            samples, rate = self.decode(row.payload)
            self.assertEqual(rate, 16000)
            self.assertEqual(samples.shape, (960, 1))
            self.assertFalse(any(key in row.payload for key in (
                "hidden_state_ids", "hidden_arm_ids", "seed", "label", "english",
                "meaning", "source_text", "opaque_class_id",
            )))

    def test_supervised_frequency_shortcut_vs_constant_chance(self):
        train = self.evaluator_trials(self.experiment.train, "train")
        holdout = self.evaluator_trials(self.experiment.holdout, "holdout")
        # Balanced eight-way labels make any constant predictor 2/16 = 1/8.
        for constant in range(8):
            self.assertEqual(sum(row.opaque_class_id == constant for row in holdout) / 16,
                             1 / 8)
        result = self.score(train, holdout)
        self.assertEqual((result.train_count, result.holdout_count), (16, 16))
        self.assertEqual({label for label, _ in result.class_carriers_hz}, set(range(8)))
        self.assertTrue(result.oracle_supervision_used)
        self.assertFalse(result.semantic_qualification)
        self.assertEqual(result.claim_ceiling,
                         "SUPERVISED_SPECTRAL_LOOKUP_NEGATIVE_CONTROL_ONLY")
        # Deterministic fixture fingerprint: the oracle-supervised shortcut
        # gets only 3/16 holdout trials right. This is not evidence of
        # statistically significant generalization or semantic learning.
        self.assertEqual(result.accuracy, 3 / 16)

    def test_holdout_codebook_permutation_is_negative_control(self):
        normal = self.experiment
        permuted = render_private_balanced_probe_splits(
            batch_seed=17, train_arms=TRAIN, holdout_arms=HOLDOUT,
            holdout_codebook=(1, 0, 2, 3, 4, 5, 6, 7),
        )
        self.assertEqual(permuted.train, normal.train)
        self.assertEqual(permuted.holdout.hidden_state_ids, normal.holdout.hidden_state_ids)
        self.assertNotEqual(permuted.holdout.observations, normal.holdout.observations)
        train = self.evaluator_trials(normal.train, "train")
        ordinary = self.score(train, self.evaluator_trials(normal.holdout, "holdout"))
        shifted = self.score(train, self.evaluator_trials(permuted.holdout, "holdout"))
        self.assertFalse(ordinary.semantic_qualification)
        self.assertFalse(shifted.semantic_qualification)
        self.assertTrue(ordinary.oracle_supervision_used)
        self.assertTrue(shifted.oracle_supervision_used)
        # Frozen negative-control scores guard against a no-op codebook
        # permutation. A 1/16 delta is too small for a semantic claim.
        self.assertEqual(ordinary.accuracy, 3 / 16)
        self.assertEqual(shifted.accuracy, 2 / 16)

    def test_replay_label_injection_and_metadata_confounds_rejected(self):
        train = self.evaluator_trials(self.experiment.train, "train")
        holdout = self.evaluator_trials(self.experiment.holdout, "holdout")
        replaced = list(holdout)
        replaced[0] = self.Trial("replay", "holdout-replay", train[0].payload,
                                 holdout[0].opaque_class_id)
        with self.assertRaisesRegex(ValueError, "replay"):
            self.score(train, replaced)

        injected = list(holdout)
        injected[0] = self.Trial(
            "injected", "holdout-injected",
            {**holdout[0].payload, "hidden_state_id": 0},
            holdout[0].opaque_class_id,
        )
        with self.assertRaisesRegex(ValueError, "allowlist"):
            self.score(train, injected)

        confounded = list(holdout)
        confounded[0] = self.Trial(
            "bad-rate", "holdout-rate", self.project([0.1] * 960, 8_000),
            holdout[0].opaque_class_id,
        )
        with self.assertRaisesRegex(ValueError, "metadata"):
            self.score(train, confounded)


if __name__ == "__main__":
    unittest.main()
