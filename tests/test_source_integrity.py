"""Regression checks for the source-derived, non-invented language corpus."""

import json
import unicodedata
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


class CanonicalSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load("lexicon.json")
        cls.corpus = load("corpus.json")

    def test_dictionary_contains_500_distinct_sourced_entries(self):
        entries = self.lexicon["entries"]
        self.assertEqual(self.lexicon["entry_count"], 500)
        self.assertEqual(len(entries), 500)
        canonical = [
            unicodedata.normalize("NFC", entry["headword"]).casefold().replace("'", "’")
            for entry in entries
        ]
        self.assertEqual(len(set(canonical)), 500)
        self.assertTrue(all(entry["source_text"] for entry in entries))
        self.assertTrue(all(entry["gloss"] for entry in entries))

    def test_dictionary_is_a_traceable_export_not_invented_vocabulary(self):
        original = (ROOT / "sources" / "dictionary_v2_updated_lphoneme.txt").read_text(encoding="utf-8").splitlines()
        for entry in self.lexicon["entries"]:
            line = entry["source_line"]
            self.assertGreaterEqual(line, 1)
            self.assertLessEqual(line, len(original))
            self.assertEqual(entry["source_text"], original[line - 1])

    def test_attested_corpus_contains_30_distinct_utterances(self):
        records = self.corpus["records"]
        self.assertEqual(self.corpus["record_count"], 30)
        self.assertEqual(len(records), 30)
        self.assertEqual([item["id"] for item in records], [f"E{i:02d}" for i in range(1, 31)])
        self.assertTrue(all(record["orthography_index"] and record["english"] for record in records))

    def test_independently_verified_examples(self):
        records = {item["id"]: item for item in self.corpus["records"]}
        self.assertEqual(records["E01"]["orthography"], "Nûm ta=en ech.")
        self.assertEqual(records["E01"]["english"], "You are aligned (I witness it).")
        self.assertEqual(records["E17"]["orthography"], "Ta’qesh.")
        self.assertEqual(records["E17"]["english"], "Stop. Do not proceed.")
        self.assertEqual(records["E18"]["orthography"], "Vahl=uth ta=en=uth ech.")
        self.assertEqual(records["E20"]["orthography"], "Kesh na=ka veyl=va ech.")

    def test_v2_l_phoneme_amendment_wins(self):
        grammar = (ROOT / "sources" / "reference_grammar_v2_updated_lphoneme.txt").read_text(encoding="utf-8")
        self.assertIn("v2.0 treats /l/ as a full phoneme", grammar)
        headwords = {item["headword"] for item in self.lexicon["entries"]}
        self.assertTrue({"lek", "shel", "qir’lek"}.issubset(headwords))


if __name__ == "__main__":
    unittest.main()
