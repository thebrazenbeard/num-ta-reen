"""Adversarial and measurement checks for the noncanonical held-out probe."""

import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

import research.heldout_morpheme_probe as probe

from research.heldout_morpheme_probe import (
    CORPUS_GIT_BLOB,
    LEXICON_GIT_BLOB,
    annotated_pairs,
    author_polysemy_flags,
    evaluate,
    evaluate_rows,
    learn,
    predict,
    source_rows,
)


ROOT = Path(os.environ.get("NUMTAREEN_SOURCE_ROOT", Path(__file__).resolve().parents[1]))


class HeldoutMorphemeProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = source_rows(ROOT)
        cls.score = evaluate(ROOT)

    def test_source_pin_and_protected_exclusion(self):
        self.assertEqual(len(self.rows), 27)
        self.assertEqual(self.score["source_corpus_git_blob"], CORPUS_GIT_BLOB)
        self.assertEqual(self.score["source_lexicon_git_blob"], LEXICON_GIT_BLOB)
        self.assertEqual(self.score["evidence"], "SOURCE_PINNED_TRAIN_ONLY_IGT_MORPHEME_RECOVERY")
        self.assertEqual({r["id"] for r in self.rows}.intersection({"E13", "E23", "E26"}), set())
        self.assertEqual(self.score["excluded_ids"], ["E13", "E23", "E26"])

    def test_true_leave_one_out_training_custody(self):
        self.assertEqual(self.score["eligible_heldout_folds"], 27)
        self.assertEqual(self.score["training_per_fold"], 26)
        self.assertEqual(self.score["scores"]["phrase_memorization_hits"], 0)
        self.assertEqual(self.score["scores"]["source_copy_correct_morphemes"], 0)
        # Frozen initial candidate: lossless phrase retrieval cannot learn
        # unattested grammar.  The only demonstrated improvement is partial IGT.
        self.assertEqual(self.score["scores"]["factorized_morpheme_correct"], 112)
        self.assertEqual(self.score["scores"]["factorized_morpheme_wrong"], 2)
        self.assertEqual(self.score["scores"]["whole_token_correct_morphemes"], 97)
        # This gate was selected after viewing E07/E18 source-label variation,
        # so it is NOT independently validated precision.
        self.assertEqual(self.score["scores"]["guarded_morpheme_correct"], 112)
        self.assertEqual(self.score["scores"].get("guarded_morpheme_wrong", 0), 0)
        self.assertEqual(self.score["scores"]["guarded_morpheme_abstained"], 15)

    def test_consent_clitic_transfers_but_unknown_root_abstains(self):
        heldout = next(r for r in self.rows if r["id"] == "E14")
        _whole, segments = learn(tuple(r for r in self.rows if r["id"] != "E14"))
        self.assertEqual(predict("uth’nûm=uth", segments), (None, "CONS"))
        self.assertEqual(annotated_pairs(heldout)[0][2], "SOFT-align=CONS")
        self.assertEqual(predict("novelunknown=uth", segments), (None, "CONS"))
        self.assertEqual(predict("novelunknown=novelunknown", segments), (None, None))

    def test_ambiguous_train_morpheme_abstains(self):
        examples = (
            {"id": "FA", "orthography_index": "Ta=ka.", "igt": "ta=ka X=AGT"},
            {"id": "FB", "orthography_index": "Ta=ka.", "igt": "ta=ka Y=AGT"},
        )
        _whole, segments = learn(examples)
        self.assertEqual(predict("ta=ka", segments), (None, "AGT"))

    def test_author_polysemy_gate_is_explicitly_posthoc(self):
        ambiguous = author_polysemy_flags(ROOT)
        self.assertIn("vahl", ambiguous)
        self.assertIn("nûm", ambiguous)
        bare = evaluate_rows(self.rows)["scores"]
        guarded = evaluate_rows(self.rows, polysemous_roots=ambiguous)["scores"]
        self.assertEqual(bare["factorized_morpheme_wrong"], 2)
        self.assertEqual(guarded.get("guarded_morpheme_wrong", 0), 0)
        self.assertEqual(guarded["guarded_morpheme_correct"], 112)
        self.assertEqual(guarded["guarded_morpheme_abstained"], 15)

    def test_arbitrary_in_memory_gold_forgery_never_claims_source_attestation(self):
        # The 27 eligible IDs alone do not authenticate the gold IGT. The
        # caller can forge the in-memory label with the original ID intact.
        tampered = dict(self.rows[0])
        self.assertIn("align", tampered["igt"])
        tampered["igt"] = tampered["igt"].replace("align", "FORGED", 1)
        rows = (tampered,) + self.rows[1:]
        same_flags = author_polysemy_flags(ROOT)
        baseline = evaluate_rows(self.rows, polysemous_roots=same_flags)
        forged = evaluate_rows(rows, polysemous_roots=same_flags)
        self.assertNotEqual(forged["scores"], baseline["scores"])
        for result in (baseline, forged):
            self.assertIsNone(result["source_corpus_git_blob"])
            self.assertIsNone(result["source_lexicon_git_blob"])
            self.assertEqual(result["evidence"],
                             "CALLER_SUPPLIED_UNVERIFIED_IGT_MORPHEME_RECOVERY")
        # The authenticated high-level call remains independently source-bound.
        fresh = evaluate(ROOT)
        self.assertEqual(fresh["source_corpus_git_blob"], CORPUS_GIT_BLOB)
        self.assertEqual(fresh["source_lexicon_git_blob"], LEXICON_GIT_BLOB)
        self.assertEqual(fresh["evidence"],
                         "SOURCE_PINNED_TRAIN_ONLY_IGT_MORPHEME_RECOVERY")
        self.assertEqual(fresh["scores"], baseline["scores"])

    def test_test_fold_igt_is_not_a_model_feature(self):
        # Observe the *public evaluator* for each counterfactual run, not two
        # calls to a separately constructed model (which cannot test leakage).
        # Only fabricated labels replace E18 gold; its source stays identical.
        held = next(r for r in self.rows if r["id"] == "E18")
        invented = dict(held)
        slots = invented["igt"].split()
        for index in range(1, len(slots), 2):
            slots[index] = "=".join(["SYNTHETIC"] * (1 + slots[index].count("=")))
        invented["igt"] = " ".join(slots)
        tampered_rows = tuple(invented if r["id"] == "E18" else r for r in self.rows)

        def observe_evaluation(rows):
            original_learn = probe.learn
            original_predict = probe.predict
            original_pairs = probe.annotated_pairs
            active_fold = None
            predicted = []
            gold_read = False

            def observed_learn(training):
                nonlocal active_fold
                train_ids = {r["id"] for r in training}
                self.assertEqual(len(training), 26)
                self.assertEqual(len(train_ids), 26)
                self.assertEqual(len({r["id"] for r in rows} - train_ids), 1)
                active_fold = next(iter({r["id"] for r in rows} - train_ids))
                return original_learn(training)

            def observed_predict(word, segment_map):
                result = original_predict(word, segment_map)
                if active_fold == "E18":
                    self.assertFalse(gold_read)
                    predicted.append((word, result))
                return result

            def observed_pairs(row):
                nonlocal gold_read
                if active_fold == "E18" and row["id"] == "E18":
                    # Gold custody: IGT must first be read only after every
                    # E18 source token was predicted (and never in training).
                    self.assertEqual(len(predicted), len(probe.tokens(held["orthography_index"])))
                    gold_read = True
                return original_pairs(row)

            with mock.patch.object(probe, "learn", side_effect=observed_learn), \
                 mock.patch.object(probe, "predict", side_effect=observed_predict), \
                 mock.patch.object(probe, "annotated_pairs", side_effect=observed_pairs):
                result = probe.evaluate_rows(rows)
            self.assertTrue(gold_read)
            return predicted, next(r for r in result["folds"] if r["id"] == "E18")

        baseline_predictions, baseline_gold_score = observe_evaluation(self.rows)
        changed_predictions, changed_gold_score = observe_evaluation(tampered_rows)
        self.assertEqual(baseline_predictions, changed_predictions)
        self.assertNotEqual(baseline_gold_score, changed_gold_score)

    def test_public_helpers_reject_protected_id_before_content(self):
        # Synthetic ID-only record; never load, reveal, or mock real E26 text.
        synthetic_protected = {"id": "E26"}
        with self.assertRaisesRegex(ValueError, "protected"):
            annotated_pairs(synthetic_protected)
        with self.assertRaisesRegex(ValueError, "protected"):
            learn((synthetic_protected,))
        safe_synthetic = {"id": "SYNTH", "orthography_index": "taka.",
                          "igt": "taka SAFE"}
        with mock.patch.object(probe, "annotated_pairs", wraps=annotated_pairs) as spy:
            with self.assertRaisesRegex(ValueError, "protected"):
                learn((safe_synthetic, synthetic_protected))
            # A protected ID anywhere in the training batch poisons the
            # whole transaction before even safe examples enter the learner.
            spy.assert_not_called()

    def test_duplicate_fold_and_missing_eligible_id_fail_closed(self):
        duplicate = tuple(self.rows[0] if r["id"] == self.rows[1]["id"] else r
                          for r in self.rows)
        self.assertEqual(len(duplicate), 27)
        with self.assertRaisesRegex(ValueError, "unique eligible"):
            evaluate_rows(duplicate)

    def test_noneligible_fold_id_fails_closed_even_with_27_unique_rows(self):
        changed = dict(self.rows[0], id="E31")
        substituted = (changed,) + self.rows[1:]
        self.assertEqual(len({r["id"] for r in substituted}), 27)
        with self.assertRaisesRegex(ValueError, "unique eligible"):
            evaluate_rows(substituted)

    def test_changed_corpus_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            (fake / "data").mkdir()
            shutil.copyfile(ROOT / "data" / "corpus.json", fake / "data" / "corpus.json")
            path = fake / "data" / "corpus.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "provenance mismatch"):
                source_rows(fake)

    def test_changed_dictionary_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            (fake / "data").mkdir()
            shutil.copyfile(ROOT / "data" / "lexicon.json", fake / "data" / "lexicon.json")
            path = fake / "data" / "lexicon.json"
            path.write_bytes(path.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "provenance mismatch"):
                author_polysemy_flags(fake)

    def test_authenticated_entrypoint_requires_both_exact_raw_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            (fake / "data").mkdir()
            for filename in ("corpus.json", "lexicon.json"):
                shutil.copyfile(ROOT / "data" / filename, fake / "data" / filename)
            self.assertEqual(evaluate(fake)["source_lexicon_git_blob"], LEXICON_GIT_BLOB)
            lex = fake / "data" / "lexicon.json"
            original = lex.read_bytes()
            lex.write_bytes(original + b" ")
            with self.assertRaisesRegex(ValueError, "lexicon provenance mismatch"):
                evaluate(fake)
            lex.write_bytes(original)
            corpus = fake / "data" / "corpus.json"
            corpus.write_bytes(corpus.read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "corpus provenance mismatch"):
                evaluate(fake)

    def test_str_subclass_input_is_not_executed(self):
        class Inject(str):
            def split(self, *args, **kwargs):
                return ["nûm", "ech"]

        with self.assertRaises(TypeError):
            predict(Inject("completely unrelated"), {})

    def test_unapproved_eligibility_change_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "exactly 27"):
            evaluate_rows(self.rows[:-1])


if __name__ == "__main__":
    unittest.main()
