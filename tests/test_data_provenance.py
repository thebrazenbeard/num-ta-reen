"""Cross-check machine data against the checked-in amended source exports.

These assertions do not independently authenticate the original DOCX files:
they guard the traceability of the checked-in UTF-8 exports and derived data.
"""

import json
import unicodedata
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def source_text(path):
    return (ROOT / "sources" / path).read_text(encoding="utf-8")


class DataProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = json.loads((ROOT / "data" / "lexicon.json").read_text(encoding="utf-8"))
        cls.corpus = json.loads((ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))
        cls.dictionary_lines = source_text("dictionary_v2_updated_lphoneme.txt").splitlines()
        cls.grammar = source_text("reference_grammar_v2_updated_lphoneme.txt")

    def test_every_lexeme_retains_complete_line_provenance(self):
        entries = self.lexicon["entries"]
        self.assertEqual(len(entries), self.lexicon["entry_count"])
        prior_source_line = 0
        for entry in entries:
            with self.subTest(headword=entry.get("headword")):
                self.assertIsInstance(entry["source_line"], int)
                line_no = entry["source_line"]
                self.assertGreater(line_no, prior_source_line)
                self.assertLessEqual(line_no, len(self.dictionary_lines))
                self.assertEqual(entry["source_text"], self.dictionary_lines[line_no - 1])
                for field in ("headword", "ipa", "category", "register", "taboo", "gloss"):
                    self.assertIsInstance(entry[field], str)
                    self.assertTrue(entry[field].strip(), field)
                prior_source_line = line_no

    def test_unicode_keys_are_nfc_and_unique_without_erasing_accents(self):
        observed = set()
        for entry in self.lexicon["entries"]:
            word = entry["headword"]
            with self.subTest(headword=word):
                self.assertEqual(word, unicodedata.normalize("NFC", word))
                key = word.casefold().replace("'", "’")
                self.assertNotIn(key, observed)
                observed.add(key)

    def test_example_references_resolve_but_do_not_imply_occurrence(self):
        # The dictionary's "Ex:" links are illustrative. Verify link targets,
        # without falsely claiming each headword occurs in that utterance.
        ids = {record["id"] for record in self.corpus["records"]}
        for entry in self.lexicon["entries"]:
            with self.subTest(headword=entry["headword"]):
                self.assertIsInstance(entry["example_refs"], list)
                self.assertTrue(set(entry["example_refs"]).issubset(ids))

    def test_all_corpus_fields_are_verbatim_in_amended_grammar_export(self):
        records = self.corpus["records"]
        self.assertEqual(len(records), self.corpus["record_count"])
        self.assertEqual(len({item["id"] for item in records}), len(records))
        for record in records:
            with self.subTest(utterance=record["id"]):
                self.assertEqual(
                    record["orthography_index"],
                    " ".join(record["orthography"].split()),
                )
                self.assertEqual(
                    record["english"],
                    record["free"].strip("“”").strip(),
                )
                for field in ("orthography", "ipa", "igt", "free", "notes"):
                    value = record[field]
                    self.assertIsInstance(value, str)
                    if field != "notes":
                        self.assertTrue(value.strip(), field)
                    if value:
                        self.assertIn(value, self.grammar, field)

    def test_homophones_remain_distinct_lexical_records(self):
        # These are real collisions in the amended source's IPA field.
        # A translator must not silently collapse them to one meaning.
        by_ipa = {}
        for entry in self.lexicon["entries"]:
            by_ipa.setdefault(entry["ipa"], set()).add(entry["headword"])
        self.assertTrue({"së", "sën"}.issubset(by_ipa["sɛn"]))
        self.assertTrue({"hem", "hëm"}.issubset(by_ipa["hɛm"]))


if __name__ == "__main__":
    unittest.main()
