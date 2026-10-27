"""Adversarial corpus controls for order-sensitive source meanings."""

from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import patch

from research.contrastive_focus_audit import audit
from research.semantic_ir_proposal import load_verified_corpus
from research.typed_semantic_channel import AbstentionError, encode_corpus_id


ROOT = Path(os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])).resolve()


class SourceBoundOrderContrastTests(unittest.TestCase):
    def test_same_token_multiset_has_distinct_authored_focus_rendering(self):
        r = audit(repo_root=ROOT)
        self.assertEqual(r, audit())
        self.assertTrue(r["same_surface_word_bag"])
        self.assertTrue(r["same_unordered_argument_roles"])
        self.assertTrue(r["different_authored_english"])
        self.assertTrue(r["e03_source_note_mentions_focus"])

    def test_typed_channel_keeps_argument_order_but_not_inferred_focus_tag(self):
        r = audit(repo_root=ROOT)
        self.assertTrue(r["typed_frames_distinct"])
        self.assertEqual(r["argument_order_e02"], (("AGT", 1), ("PAT", 2)))
        self.assertEqual(r["argument_order_e03"], (("PAT", 1), ("AGT", 2)))
        self.assertTrue(r["explicit_discourse_metadata_empty_for_both"])
        self.assertFalse(r["unseen_translation_demonstrated"])
        self.assertFalse(r["qualification_eligible"])

    def test_overt_focus_consent_and_question_have_independent_controls(self):
        r = audit(repo_root=ROOT)
        self.assertEqual(r["independent_contrast_axes"],
                         {"overt_focus": True, "consent": True, "question": True})

    def test_not_an_unseen_grammatical_generator(self):
        # The unobserved permutation is not an authorized corpus ID.
        with self.assertRaises(AbstentionError):
            encode_corpus_id("E99", repo_root=ROOT)

    def test_refuses_modified_source_before_reporting_pinned_provenance(self):
        source = ROOT / "data" / "corpus.json"
        original = source.read_bytes()
        altered = original.replace(b'"E03"', b'"E93"', 1)
        self.assertNotEqual(altered, original)
        with patch.object(Path, "read_bytes", return_value=altered):
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                audit(repo_root=ROOT)

    def test_protected_source_never_enters_contrast_report(self):
        r = audit(repo_root=ROOT)
        output = repr(r)
        self.assertNotIn("E26", output)
        self.assertNotIn("⟦", output)
        self.assertNotIn("⟧", output)
        self.assertEqual(len(load_verified_corpus(ROOT)), 30)


if __name__ == "__main__":
    unittest.main()
