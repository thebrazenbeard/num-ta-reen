"""Executable, source-bound negative controls; no novel-language scoring."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from research.semantic_generalization_benchmark import (
    CONTRASTS, PACKET_CAPACITY, SCHEMA, UNSCORED_PROBES,
    benchmark, eligible_observations, semantic_signature,
)
from research.semantic_ir_proposal import analyze_corpus_id, load_verified_corpus


class SourceBoundGeneralizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = benchmark()

    def test_source_pinned_abstentions_not_silent_canon(self):
        rows = load_verified_corpus()
        self.assertEqual(len(rows), 30)
        self.assertEqual(self.report["authored_rows"], 30)
        self.assertEqual(self.report["eligible_rows"], 27)
        self.assertEqual(self.report["refused_ids"], ["E13", "E23", "E26"])
        self.assertEqual(self.report["schema"], SCHEMA)

    def test_feature_tagged_leave_one_out_has_no_exact_source_leak(self):
        result = self.report["holdout"]
        self.assertEqual(result["folds"], 27)
        self.assertEqual(result["train_rows_per_fold"], 26)
        self.assertEqual(result["nt_en_exact_hits"], 0)
        self.assertEqual(result["en_nt_exact_hits"], 0)
        self.assertEqual(result["abstaining_folds_both_directions"], 27)
        self.assertEqual(result["feature_tagged_folds"]["question"], 3)
        self.assertEqual(result["feature_tagged_folds"]["consent"], 3)

    def test_measured_synthetic_loss_is_not_identity_lookup(self):
        report = self.report
        self.assertEqual(report["semantic_fingerprint_unique"], 27)
        self.assertEqual(report["old_synthetic_packet_unique"], 16)
        self.assertEqual(len(report["old_synthetic_collision_groups"]), 5)
        self.assertEqual(report["old_synthetic_colliding_pairs"], 21)
        self.assertTrue(all(len(g) > 1 for g in report["old_synthetic_collision_groups"]))

    def test_attested_near_contrasts_preserved_by_igt_not_original_packet(self):
        cases = {c["contrast"]: c for c in self.report["known_source_contrasts"]}
        self.assertEqual(len(cases), len(CONTRASTS))
        self.assertTrue(all(c["source_fingerprints_differ"] for c in cases.values()))
        for tag in ("predicate_focus", "question", "argument_order"):
            self.assertTrue(cases[tag]["synthetic_acoustic_packets_equal"])
        for tag in ("echo_loop", "predicate_and_argument_consent"):
            self.assertFalse(cases[tag]["synthetic_acoustic_packets_equal"])

    def test_random_labels_fit_training_ids_but_prove_no_transfer(self):
        control = self.report["opaque_random_label_control"]
        self.assertEqual(control["slots"], PACKET_CAPACITY)
        self.assertEqual(control["unique_labels_assigned_in_sample"], 27)
        self.assertEqual(control["held_out_semantic_generalization_credit"], 0)
        self.assertEqual(len(control["mapping_sha256"]), 64)
        self.assertEqual(benchmark()["opaque_random_label_control"], control)

    def test_operational_unknowns_abstain_both_directions(self):
        self.assertEqual(self.report["unknown_input_policy"], {
            "nt_en": "incomplete", "en_nt": "incomplete"
        })

    def test_author_only_novel_probes_do_not_gain_fake_scores(self):
        probes = self.report["unscored_author_probes"]
        self.assertEqual(len(probes), len(UNSCORED_PROBES))
        self.assertEqual({p["id"] for p in probes}, {f"P{i:02d}" for i in range(1, 9)})
        self.assertTrue(all(p["status"].startswith("UNSCORED_NEEDS_AUTHOR") for p in probes))
        self.assertTrue(all("translation" not in p and "accuracy" not in p for p in probes))

    def test_protected_source_not_reproduced_in_report(self):
        source = load_verified_corpus()
        output = json.dumps(self.report, ensure_ascii=False)
        self.assertNotIn(source["E26"]["igt"], output)
        self.assertNotIn(source["E26"]["orthography"], output)
        self.assertNotIn("⟦", output)

    def test_attested_fingerprint_rejects_forged_and_unverified_packet(self):
        ir = analyze_corpus_id("E01")
        authentic = semantic_signature(ir)
        self.assertTrue(authentic)
        self.assertNotIn("E01", authentic)  # ID cannot manufacture separability.
        with self.assertRaises(ValueError):
            semantic_signature(replace(ir, corpus_id="E26"))
        with self.assertRaises(ValueError):
            semantic_signature(replace(ir, evidence="UNVERIFIED_SYNTHETIC_GLOSS"))
        with self.assertRaises(ValueError):
            semantic_signature(analyze_corpus_id("E26"))
        class FakePacket:
            def to_dict(self):
                return {"evidence": "SOURCE_VERIFIED_AUTHOR_INTERLINEAR_GLOSS"}

        with self.assertRaises(ValueError):
            semantic_signature(FakePacket())

    def test_modified_corpus_is_rejected_even_when_json_parseable(self):
        root = Path(os.environ.get("NUMTAREEN_REPO_ROOT", Path(__file__).resolve().parents[1]))
        original = root / "data" / "corpus.json"
        with tempfile.TemporaryDirectory(prefix="nt-generalization-source-test-") as folder:
            location = Path(folder) / "data"
            location.mkdir()
            fake = location / "corpus.json"
            content = original.read_bytes()
            self.assertIn(b'"schema_version": 1', content)
            fake.write_bytes(content.replace(b'"schema_version": 1', b'"schema_version": 9', 1))
            with patch.dict(os.environ, {"NUMTAREEN_REPO_ROOT": folder}):
                with self.assertRaisesRegex(ValueError, "digest mismatch"):
                    eligible_observations()


if __name__ == "__main__":
    unittest.main()
