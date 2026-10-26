"""Evidence hygiene tests for a noncanonical semantic-slot proposal.

These tests validate source references and scope labels. They cannot establish
that a proposed linguistic construction is grammatical or semantically learned.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE if (HERE / "data" / "lexicon.json").exists() else HERE.parent / "cross-integration-num"
PROPOSAL = HERE / "proposals" / "EVERYDAY_SEMANTIC_COVERAGE_V1.md"
LEXICON = SOURCE / "data" / "lexicon.json"
CORPUS = SOURCE / "data" / "corpus.json"


class CoverageProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PROPOSAL.read_text(encoding="utf-8")
        cls.lexicon = json.loads(LEXICON.read_text(encoding="utf-8"))
        cls.corpus = json.loads(CORPUS.read_text(encoding="utf-8"))

    def test_source_sizes_match_declared_scope(self) -> None:
        self.assertEqual(500, len(self.lexicon["entries"]))
        self.assertEqual(30, len(self.corpus["records"]))

    def test_exactly_thirty_distinct_priority_slots(self) -> None:
        rows = re.findall(r"^\| (C\d{2}) \| (P[01]) \|", self.text, flags=re.MULTILINE)
        self.assertEqual([f"C{i:02d}" for i in range(1, 31)], [name for name, _ in rows])
        self.assertEqual(30, len(set(name for name, _ in rows)))

    def test_only_known_corpus_ids_cited(self) -> None:
        ids = set(re.findall(r"\bE\d{2}\b", self.text))
        available = {record["id"] for record in self.corpus["records"]}
        self.assertLessEqual(ids, available)
        self.assertIn("E26", ids)

    def test_selected_source_line_provenance(self) -> None:
        by_word = {item["headword"]: item["source_line"] for item in self.lexicon["entries"]}
        expected = {"=ru": 21, "rhel": 53, "sën": 59, "mek": 201, "suv": 242,
                    "nuk": 266, "har": 296, "renk": 345, "huth": 362, "neth": 411}
        for word, line in expected.items():
            with self.subTest(word=word):
                self.assertEqual(line, by_word[word])

    def test_contrast_deck_orthographies_are_exactly_attested(self) -> None:
        by_id = {record["id"]: record["orthography"] for record in self.corpus["records"]}
        examples = {
            "E01": "Nûm ta=en ech.",
            "E02": "Nûm na=ka ta=en ech.",
            "E03": "Nûm ta=en na=ka ech.",
            "E06": "Threnn’vahl reen.",
            "E07": "Vahl ta=en ech.",
            "E08": "Nûm ta=en ech hë?",
            "E10": "Vael’nûm ta=en ech.",
            "E15": "Qir nûm ta=en ech.",
            "E18": "Vahl=uth ta=en=uth ech.",
            "E19": "Threnn’vahl vu ech.",
            "E20": "Kesh na=ka veyl=va ech.",
            "E21": "Kesh=uth na=ka veyl=va ech.",
        }
        for utterance_id, orthography in examples.items():
            with self.subTest(utterance=utterance_id):
                self.assertEqual(orthography, by_id[utterance_id])
                self.assertIn(orthography, self.text)

    def test_gaps_are_not_presented_as_canon(self) -> None:
        self.assertIn("NONCANONICAL RESEARCH PROPOSAL", self.text)
        self.assertIn("not newly generated sentences", self.text)
        self.assertIn("without an attested full utterance", self.text)
        self.assertIn("E26 true-name realization is withheld", self.text)
        self.assertNotRegex(self.text, r"\b\d+(?:\.\d+)?\s*(?:Hz|kHz)\b")


if __name__ == "__main__":
    unittest.main()
