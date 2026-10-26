"""Evaluator-only nuisance stratification for noncanonical acoustic probes."""

from collections import Counter
from dataclasses import fields
from math import pi
import unittest

from numtareen.experimental_probe_splits import (
    NuisanceArm,
    render_private_balanced_probe_splits,
)


TRAIN = (
    NuisanceArm(gain=0.40, pitch_scale=0.92, noise_level=0.04),
    NuisanceArm(gain=0.65, pitch_scale=1.04, noise_level=0.09),
)
HOLDOUT = (
    NuisanceArm(gain=0.48, pitch_scale=1.12, noise_level=0.07),
    NuisanceArm(gain=0.75, pitch_scale=0.85, noise_level=0.12),
)


class ProbeSplitTests(unittest.TestCase):
    def build(self, **kwargs):
        options = dict(batch_seed=17, train_arms=TRAIN, holdout_arms=HOLDOUT)
        options.update(kwargs)
        return render_private_balanced_probe_splits(**options)

    def test_balanced_states_and_nuisance_per_split(self):
        experiment = self.build()
        self.assertEqual(len(experiment.train.observations), 16)
        self.assertEqual(len(experiment.holdout.observations), 16)
        for split in (experiment.train, experiment.holdout):
            self.assertEqual(Counter(split.hidden_state_ids), dict.fromkeys(range(8), 2))
            self.assertEqual(
                Counter(zip(split.hidden_state_ids, split.hidden_arm_ids)),
                {(state, arm): 1 for state in range(8) for arm in range(2)},
            )
            self.assertEqual(
                {(obs.sample_rate_hz, len(obs.samples)) for obs in split.observations},
                {(16000, 960)},
            )

    def test_public_observation_has_only_audio_and_rate(self):
        experiment = self.build()
        self.assertEqual(
            {f.name for f in fields(experiment.train.observations[0])},
            {"samples", "sample_rate_hz"},
        )
        self.assertEqual(
            {f.name for f in fields(experiment.holdout.observations[0])},
            {"samples", "sample_rate_hz"},
        )
        self.assertEqual(
            {f.name for f in fields(experiment.train)},
            {"observations", "hidden_state_ids", "hidden_arm_ids"},
        )

    def test_identical_seed_repeats_and_different_seed_changes_waveforms(self):
        first = self.build()
        second = self.build()
        third = self.build(batch_seed=18)
        self.assertEqual(first, second)
        self.assertNotEqual(first.train.observations, third.train.observations)
        self.assertNotEqual(first.holdout.observations, third.holdout.observations)

    def test_holdout_codebook_permutation_is_private_ablation(self):
        baseline = self.build()
        ablated = self.build(holdout_codebook=(1, 0, 2, 3, 4, 5, 6, 7))
        self.assertEqual(baseline.train, ablated.train)
        self.assertNotEqual(baseline.holdout.observations, ablated.holdout.observations)
        self.assertEqual(baseline.holdout.hidden_state_ids, ablated.holdout.hidden_state_ids)

    def test_training_and_holdout_arms_must_be_disjoint(self):
        with self.assertRaisesRegex(ValueError, "disjoint"):
            self.build(holdout_arms=(TRAIN[0],))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.build(train_arms=(TRAIN[0], TRAIN[0]))

    def test_periodic_phase_aliases_cannot_fake_nuisance_holdout(self):
        # The phase of a sinusoid is circular: 0 and +/-2*pi are the same
        # acoustic condition, although their dataclass floats differ.
        for alias in (-2 * pi, 2 * pi):
            with self.subTest(alias=alias), self.assertRaisesRegex(ValueError, "disjoint"):
                self.build(
                    train_arms=(NuisanceArm(phase_shift_rad=0.0),),
                    holdout_arms=(NuisanceArm(phase_shift_rad=alias),),
                )
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.build(train_arms=(NuisanceArm(phase_shift_rad=0.0),
                                  NuisanceArm(phase_shift_rad=2 * pi)))
        with self.assertRaisesRegex(ValueError, "disjoint"):
            self.build(train_arms=(NuisanceArm(phase_shift_rad=0.7),),
                       holdout_arms=(NuisanceArm(phase_shift_rad=0.7 - 2 * pi),))
        with self.assertRaisesRegex(ValueError, "disjoint"):
            self.build(train_arms=(NuisanceArm(phase_shift_rad=pi),),
                       holdout_arms=(NuisanceArm(phase_shift_rad=-pi),))
        # A genuinely nonperiodic phase difference remains a valid (albeit
        # scientifically tiny) separate arm; this patch is not a JND policy.
        valid = self.build(train_arms=(NuisanceArm(phase_shift_rad=0.0),),
                           holdout_arms=(NuisanceArm(phase_shift_rad=1e-8),))
        self.assertEqual(len(valid.train.observations), 8)

    def test_input_bounds_and_aggregate_cap(self):
        for invalid in (True, -1, 2**32):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "batch_seed"):
                self.build(batch_seed=invalid)
        with self.assertRaisesRegex(ValueError, "arm count"):
            self.build(train_arms=())
        with self.assertRaisesRegex(ValueError, "aggregate sample cap"):
            many_train = tuple(NuisanceArm(gain=0.1 + index * 0.08) for index in range(8))
            many_holdout = tuple(NuisanceArm(gain=0.1 + index * 0.08, pitch_scale=1.1) for index in range(8))
            self.build(samples_per_state=12_000, train_arms=many_train, holdout_arms=many_holdout)
        with self.assertRaisesRegex(ValueError, "pitch_scale"):
            self.build(train_arms=(NuisanceArm(pitch_scale=float("nan")),))
        with self.assertRaisesRegex(ValueError, "holdout_codebook"):
            self.build(holdout_codebook=tuple([0] * 8))

    def test_no_exact_public_waveform_replay_across_splits(self):
        split = self.build()
        self.assertFalse(
            {x.samples for x in split.train.observations}
            & {x.samples for x in split.holdout.observations}
        )

    def test_cross_class_alias_inside_training_is_rejected(self):
        # Synthetic states 2 and 3 use carriers 434 and 526 Hz respectively.
        # The two nuisance arms below align the carriers exactly. Distinct
        # hidden labels therefore have bit-identical public waveforms.
        colliding = (
            NuisanceArm(gain=0.4, pitch_scale=1.0, noise_level=0.0),
            NuisanceArm(gain=0.4, pitch_scale=434 / 526, noise_level=0.0),
        )
        with self.assertRaisesRegex(ValueError, "within training"):
            self.build(train_arms=colliding, holdout_arms=(NuisanceArm(gain=0.4, pitch_scale=1.1),))

    def test_noncolliding_training_arms_remain_valid(self):
        split = self.build(train_arms=(NuisanceArm(gain=0.4, pitch_scale=0.95),
                                       NuisanceArm(gain=0.4, pitch_scale=1.05)),
                           holdout_arms=(NuisanceArm(gain=0.4, pitch_scale=1.1),))
        self.assertEqual(len(split.train.observations), 16)
        self.assertEqual(len({obs.samples for obs in split.train.observations}), 16)

    def test_cross_class_alias_inside_holdout_is_rejected(self):
        colliding = (
            NuisanceArm(gain=0.4, pitch_scale=1.0, noise_level=0.0),
            NuisanceArm(gain=0.4, pitch_scale=434 / 526, noise_level=0.0),
        )
        with self.assertRaisesRegex(ValueError, "within holdout"):
            self.build(train_arms=(NuisanceArm(gain=0.4, pitch_scale=1.1),), holdout_arms=colliding)


if __name__ == "__main__":
    unittest.main()
