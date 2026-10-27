"""Author-pinned consent contrasts: strict observations and abstentions."""

from __future__ import annotations

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = Path(os.environ.get("NUMTAREEN_ROOT", HERE.parent)).resolve()
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))

from research.consent_scope_audit import audit
from numtareen.engine import Translator
from research.typed_semantic_channel import decode_frame, encode_corpus_id


class ConsentScopeSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = audit(ROOT)
        cls.by_id = {
            row["source_id"]: row for row in cls.report["observations"]
        }

    def test_exact_corpus_and_protected_conflict_abstentions(self):
        self.assertEqual(
            self.report["source_git_blob_sha1"],
            "53d9f27d03579a1a3fc700c3394b56f834da784e",
        )
        self.assertEqual(self.report["abstained_source_ids"],
                         ["E13", "E23", "E26"])
        self.assertNotIn("⟦", repr(self.report))
        self.assertNotIn("⟧", repr(self.report))

    def test_attested_minimal_consent_pair_not_conflated(self):
        # Source E07 is witness-marked stabilization with coercion-risk note.
        # Source E18 is the same base predicate with *two* CONS locations.
        plain = self.by_id["E07"]
        consented = self.by_id["E18"]
        self.assertEqual(plain["explicit_cons_indices"], [])
        self.assertEqual(consented["explicit_cons_indices"], [0, 1])
        self.assertEqual(consented["predicate_cons_indices"], [0])
        self.assertEqual(consented["participant_cons_indices"], [1])
        self.assertFalse(plain["qualifies_as_independent_consent"])
        self.assertFalse(consented["qualifies_as_independent_consent"])
        self.assertNotEqual(
            decode_frame(encode_corpus_id("E07", repo_root=ROOT), repo_root=ROOT).semantic,
            decode_frame(encode_corpus_id("E18", repo_root=ROOT), repo_root=ROOT).semantic,
        )

    def test_predicate_consent_attachment_differs_from_participant(self):
        for eid in ("E14", "E21"):
            with self.subTest(eid=eid):
                record = self.by_id[eid]
                self.assertEqual(record["predicate_cons_indices"], [0])
                self.assertEqual(record["participant_cons_indices"], [])
                self.assertTrue(record["scope_unestablished"])

    def test_grant_silence_and_prohibition_not_promoted_to_consent(self):
        grant = self.by_id["E12"]
        silence = self.by_id["E27"]
        refusal = self.by_id["E30"]
        self.assertTrue(grant["record_grant_predicate"])
        self.assertTrue(silence["respect_silence_predicate"])
        self.assertEqual(refusal["polarity"], ["PROH", "NEG"])
        for item in (grant, silence, refusal):
            self.assertEqual(item["explicit_cons_indices"], [])
            self.assertTrue(item["scope_unestablished"])
        self.assertEqual(self.report["revocation_rule"],
                         "UNESTABLISHED_BY_AUTHORED_CORPUS")
        self.assertFalse(self.report["infer_permission_from_silence"])

    def test_unattested_consent_attachment_does_not_become_attested(self):
        translator = Translator(ROOT / "data")
        for text in (
            "Vahl=uth ta=en ech.",       # E18 minus participant CONS
            "Vahl ta=en=uth ech.",       # E18 minus predicate CONS
        ):
            with self.subTest(text=text):
                result = translator.translate(text, "nt-en")
                self.assertNotEqual(result["status"], "attested")
        self.assertEqual(
            translator.translate("Vahl=uth ta=en=uth ech.", "nt-en")["status"],
            "attested",
        )

    def test_tampered_corpus_cannot_claim_source_identity(self):
        with patch.object(Path, "read_bytes", return_value=b'{"records":[]}'):
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                audit(ROOT)


if __name__ == "__main__":
    unittest.main()
