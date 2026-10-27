"""Adversarial tests for the retrospective single-paradigm factoring probe."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parents[1]
RESEARCH = REPO_ROOT / "research"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

import factorial_scope_probe as probe


SOURCE = REPO_ROOT


class FactorialProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rows = probe.source_rows(SOURCE)

    def test_source_root_is_relative_to_published_test_file(self):
        self.assertEqual(SOURCE, Path(__file__).resolve().parents[1])
        self.assertTrue((SOURCE / "data" / "corpus.json").is_file())

    def test_source_pin_matches_current_public_bare_blob(self):
        raw = (SOURCE / "data" / "corpus.json").read_bytes()
        self.assertEqual(probe._git_blob(raw), probe.SOURCE_CORPUS_BLOB)

    def test_retrospective_heldout_pretrained_baselines(self):
        out = probe.evaluate_repo(SOURCE)
        self.assertEqual(out["train_ids"], ["E01", "E08", "E15"])
        self.assertEqual(out["heldout_id"], "E22")
        self.assertEqual(out["evidence"], probe.PINNED)
        self.assertEqual(out["outcomes"]["whole_sentence_lookup"]["state"], "abstain")
        self.assertEqual(out["outcomes"]["source_token_copy"]["state"], "wrong")
        self.assertEqual(out["outcomes"]["marker_composition"]["state"], "exact")

    def test_two_compositions_agree_with_observed_training_operators(self):
        model = probe.learn({rid: self.rows[rid] for rid in probe.TRAIN_IDS})
        via_loop_then_q = model.synthesize(loop=True, question=True)
        via_q_then_loop = model.preposed_loop + probe._uncapitalize(
            model.synthesize(loop=False, question=True))
        self.assertEqual(via_loop_then_q, via_q_then_loop)

    def test_heldout_igt_cannot_be_seen_by_predictor(self):
        class GuardRows(dict):
            permitted = False

            def __getitem__(self, key):
                if key == "E22" and not self.permitted:
                    raise AssertionError("heldout row read before prediction")
                return super().__getitem__(key)

        rows = GuardRows(self.rows)
        original_predict = probe.predict

        def inspected_predict(training):
            self.assertNotIn("E22", training)
            result = original_predict(training)
            rows.permitted = True
            return result

        with patch.object(probe, "predict", inspected_predict):
            out = probe.evaluate_rows(rows)
        self.assertEqual(out["outcomes"]["marker_composition"]["state"], "exact")
        self.assertEqual(out["evidence"], probe.UNVERIFIED)

    def test_hostile_row_mapping_cannot_switch_from_benign_to_protected(self):
        class SpoofRow(dict):
            def get(self, key, default=None):
                if key in ("orthography", "igt"):
                    return "Nûm ta=en ech."
                return super().get(key, default)

            def __getitem__(self, key):
                if key == "orthography":
                    return "⟦hidden-chord⟧"
                return super().__getitem__(key)

        rows = dict(self.rows)
        rows["E22"] = SpoofRow(self.rows["E22"])
        with self.assertRaisesRegex(ValueError, "stable dict"):
            probe.evaluate_rows(rows)

    def test_heldout_gold_counterfactual_changes_score_not_prediction(self):
        control = probe.evaluate_rows(self.rows)
        changed = copy.deepcopy(self.rows)
        changed["E22"]["orthography"] = "Invented evaluation-only gold."
        changed["E22"]["igt"] = "invented WRONG"
        counterfactual = probe.evaluate_rows(changed)
        self.assertEqual(control["outcomes"]["marker_composition"]["prediction"],
                         counterfactual["outcomes"]["marker_composition"]["prediction"])
        self.assertEqual(counterfactual["outcomes"]["marker_composition"]["state"], "wrong")
        self.assertEqual(counterfactual["evidence"], probe.UNVERIFIED)

    def test_caller_gold_forgery_never_upgrades_source_attestation(self):
        changed = copy.deepcopy(self.rows)
        changed["E22"]["orthography"] = "Invented gold."
        result = probe.evaluate_rows(changed)
        self.assertEqual(result["evidence"], probe.UNVERIFIED)
        self.assertNotIn("source_corpus_git_blob", result)

    def test_missing_duplicate_and_protected_inputs_fail_closed(self):
        for bad in ({k:v for k,v in self.rows.items() if k != "E15"},
                    dict(self.rows, E26={"id":"E26"}),
                    dict(self.rows, E99={"id":"E99"})):
            with self.subTest(ids=sorted(bad)):
                with self.assertRaises(ValueError):
                    probe.evaluate_rows(bad)
        withheld = copy.deepcopy(self.rows)
        withheld["E22"]["orthography"] = "⟦not-public⟧"
        with self.assertRaises(ValueError):
            probe.evaluate_rows(withheld)

    def test_modified_source_blob_rejected_before_analysis(self):
        with tempfile.TemporaryDirectory() as td:
            data = Path(td) / "data"
            data.mkdir()
            text = (SOURCE / "data" / "corpus.json").read_text(encoding="utf-8")
            (data / "corpus.json").write_text(text + " ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unverified corpus"):
                probe.evaluate_repo(Path(td))

    def test_unseen_lexical_context_unsupported_not_synthesized(self):
        with self.assertRaises(ValueError):
            probe.learn({"E01":self.rows["E01"], "E08":self.rows["E08"],
                         "E20":{"id":"E20"}})
        self.assertEqual(probe.REQUESTED_FACTORS, (True, True))


if __name__ == "__main__":
    unittest.main()
