"""Attestation requires the pinned source snapshot and literal caller input."""

import json
import tempfile
import unittest
from pathlib import Path

from numtareen.engine import DATA_DIR, Translator, format_translation, normalize


class SpoofedText(str):
    def translate(self, _mapping):
        return "Nûm ta=en ech."


class AttestationIntegrityTests(unittest.TestCase):
    def test_packaged_corpus_still_reports_source_attested(self):
        result = Translator().translate("Nûm ta=en ech.")
        self.assertEqual(result["status"], "attested")
        self.assertIn("source-attested", format_translation(result))

    def test_byte_identical_source_copy_is_still_attested(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            for name in ("corpus.json", "lexicon.json"):
                (target / name).write_bytes((DATA_DIR / name).read_bytes())
            self.assertEqual(Translator(target).translate("Nûm ta=en ech.")["status"], "attested")

    def test_modified_corpus_cannot_claim_original_attestation(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / "lexicon.json").write_bytes((DATA_DIR / "lexicon.json").read_bytes())
            data = json.loads((DATA_DIR / "corpus.json").read_text(encoding="utf-8"))
            data["records"][0]["english"] = "Invented false meaning."
            (target / "corpus.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            translator = Translator(target)
            result = translator.translate("Nûm ta=en ech.")
            self.assertEqual(result["status"], "unverified")
            self.assertEqual(result["matches"][0]["translation"], "Invented false meaning.")
            self.assertNotIn("source-attested", format_translation(result))
            reverse = translator.translate("Invented false meaning.", "en-nt")
            self.assertEqual(reverse["status"], "unverified")

    def test_str_subclass_cannot_rewrite_match(self):
        raw = SpoofedText("__not_an_authored_sentence__")
        result = Translator().translate(raw)
        self.assertEqual(result["input"], "__not_an_authored_sentence__")
        self.assertEqual(result["status"], "incomplete")
        self.assertEqual(normalize(raw), "__not_an_authored_sentence__")

    def test_in_memory_corpus_mutation_cannot_claim_attestation(self):
        translator = Translator()
        translator.corpus[0]["english"] = "Malicious in-memory rewrite."
        result = translator.translate("Nûm ta=en ech.")
        self.assertEqual(result["status"], "unverified")

    def test_reindexed_corpus_row_cannot_claim_attestation(self):
        translator = Translator()
        translator.sentences["nt-en"]["fake source wording"] = [translator.corpus[0]]
        result = translator.translate("fake source wording")
        self.assertEqual(result["status"], "unverified")

    def test_custom_lexicon_grade_does_not_claim_authored_dictionary(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder)
            (target / "corpus.json").write_bytes((DATA_DIR / "corpus.json").read_bytes())
            data = json.loads((DATA_DIR / "lexicon.json").read_text(encoding="utf-8"))
            data["entries"][0]["gloss"] = "synthetic unapproved dictionary gloss"
            (target / "lexicon.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            result = Translator(target).translate(data["entries"][0]["headword"])
            self.assertEqual(result["status"], "lexical")
            self.assertEqual(result["lexicon_file_verified"], False)
            self.assertEqual(result["lexicon_candidate_verified"], False)
            self.assertIn("unverified", format_translation(result).lower())

    def test_packaged_lexicon_reports_file_verification_separately(self):
        result = Translator().translate("nûm")
        self.assertEqual(result["lexicon_file_verified"], True)
        self.assertEqual(result["lexicon_candidate_verified"], True)
        self.assertEqual(result["status"], "lexical")

    def test_modified_reverse_candidate_does_not_inherit_source_grade(self):
        translator = Translator()
        translator.glosses["agent role"][0]["headword"] = "FAKE-AUTHORED-HEADWORD"
        result = translator.translate("agent role", "en-nt")
        self.assertEqual(result["parts"][0]["matches"][0]["headword"],
                         "FAKE-AUTHORED-HEADWORD")
        self.assertTrue(result["lexicon_file_verified"])
        self.assertFalse(result["lexicon_candidate_verified"])
        self.assertFalse(result["parts"][0]["matches"][0]["source_candidate_verified"])
        self.assertIn("candidate unverified", format_translation(result).lower())

    def test_modified_forward_candidate_does_not_inherit_source_grade(self):
        translator = Translator()
        translator.words["nûm"][0]["gloss"] = "INVENTED ALIGNMENT"
        result = translator.translate("nûm")
        self.assertEqual(result["parts"][0]["matches"][0]["gloss"],
                         "INVENTED ALIGNMENT")
        self.assertTrue(result["lexicon_file_verified"])
        self.assertFalse(result["lexicon_candidate_verified"])
        self.assertIn("candidate unverified", format_translation(result).lower())

    def test_mutated_segmented_clitic_is_not_source_verified(self):
        translator = Translator()
        translator.words["=en"][0]["gloss"] = "FAKE ROLE"
        result = translator.translate("nûm=en")
        self.assertFalse(result["lexicon_candidate_verified"])
        segmentation = result["parts"][0]["matches"][0]["segmentation"]
        self.assertTrue(segmentation[0]["source_candidate_verified"])
        self.assertFalse(segmentation[1]["source_candidate_verified"])

    def test_no_lexical_candidate_does_not_imply_tampering(self):
        result = Translator().translate("__unseen_no_lexical_candidate__")
        self.assertEqual(result["status"], "incomplete")
        self.assertIsNone(result["lexicon_candidate_verified"])
        self.assertNotIn("candidate unverified", format_translation(result).lower())

    def test_reindexed_forward_lexicon_candidate_loses_verified_grade(self):
        translator = Translator()
        translator.words["invented-token"] = translator.words["nûm"]
        result = translator.translate("invented-token")
        self.assertEqual(result["status"], "lexical")
        self.assertFalse(result["lexicon_candidate_verified"])

    def test_reindexed_reverse_lexicon_candidate_loses_verified_grade(self):
        translator = Translator()
        translator.glosses["invented meaning"] = translator.glosses["agent role"]
        result = translator.translate("invented meaning", "en-nt")
        self.assertEqual(result["status"], "lexical")
        self.assertFalse(result["lexicon_candidate_verified"])

    def test_legitimate_slash_gloss_alternative_keeps_candidate_verification(self):
        result = Translator().translate("align", "en-nt")
        self.assertEqual(result["status"], "lexical")
        self.assertTrue(result["lexicon_candidate_verified"])


if __name__ == "__main__":
    unittest.main()
