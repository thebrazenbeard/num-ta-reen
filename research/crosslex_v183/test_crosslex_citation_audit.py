"""Focused red/green evidence checks; run with NUMTAREEN_SOURCE_ROOT set."""

from __future__ import annotations

import copy
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

import crosslex_citation_audit as subject


class CitationAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(os.environ["NUMTAREEN_SOURCE_ROOT"])

    def test_exact_positive_and_negative_example_controls(self):
        data = subject.audit(self.root)
        observed = {(x["headword"], x["illustrative_example_ref"]): x["literal_clitic_in_illustrative_orthography"]
                    for x in data["findings"]}
        self.assertEqual(observed, {
            ("=en", "E01"): True,
            ("=va", "E20"): True,
            ("=ru", "E20"): False,
            ("=shi", "E23"): False,
        })
        self.assertEqual(data["protected_E26"], "WITHHELD_NOT_ACCESSED_FOR_ANALYSIS")
        self.assertTrue(data["raw_corpus_json_parsed"])
        self.assertEqual(data["example_ref_semantics"],
                         "ILLUSTRATIVE_LINK_NOT_REQUIRED_HEADWORD_ATTESTATION")

    def test_attestation_stays_bounded_to_literal_example(self):
        data = subject.audit(self.root)
        positive = [f for f in data["findings"]
                    if f["classification"] == "LITERAL_PRESENT_IN_ILLUSTRATIVE_EXAMPLE"]
        gaps = [f for f in data["findings"]
                if f["classification"] == "LITERAL_ABSENT_FROM_ILLUSTRATIVE_EXAMPLE"]
        self.assertEqual({x["headword"] for x in positive}, {"=en", "=va"})
        self.assertEqual({x["headword"] for x in gaps}, {"=ru", "=shi"})
        self.assertFalse(data["canon_mutation"])

    def test_changed_raw_corpus_is_not_source_pinned(self):
        content = (self.root / "data" / "corpus.json").read_bytes()
        self.assertEqual(subject.git_blob_sha(content), subject.CORPUS_BLOB)
        tampered = content.replace(b"Kesh na=ka veyl=va ech.", b"Kesh na=ka veyl=va ech=ru.")
        self.assertNotEqual(subject.git_blob_sha(tampered), subject.CORPUS_BLOB)
        with tempfile.TemporaryDirectory() as temp:
            duplicate = Path(temp)
            (duplicate / "data").mkdir()
            (duplicate / "docs").mkdir()
            (duplicate / "data" / "corpus.json").write_bytes(tampered)
            shutil.copyfile(self.root / "data" / "lexicon.json", duplicate / "data" / "lexicon.json")
            shutil.copyfile(self.root / "docs" / "SOURCE_PARSE_REPORT.md",
                            duplicate / "docs" / "SOURCE_PARSE_REPORT.md")
            with self.assertRaisesRegex(ValueError, "source Git blob mismatch"):
                subject.audit(duplicate)

    def test_protected_record_fields_are_not_inspected(self):
        class ProtectedRow(dict):
            def get(self, key, default=None):
                if key in {"orthography", "igt", "ipa"}:
                    raise AssertionError("protected row field accessed")
                return super().get(key, default)

            def __getitem__(self, key):
                if key in {"orthography", "igt", "ipa"}:
                    raise AssertionError("protected row field indexed")
                return super().__getitem__(key)

        corpus = subject._pinned_json(self.root / "data" / "corpus.json", subject.CORPUS_BLOB)
        lexicon = subject._pinned_json(self.root / "data" / "lexicon.json", subject.LEXICON_BLOB)
        shadow = copy.deepcopy(corpus)
        shadow["records"] = [ProtectedRow({"id": "E26"}) if row.get("id") == "E26" else row
                             for row in shadow["records"]]
        with patch.object(subject, "_pinned_json", side_effect=[shadow, lexicon]):
            # Hardened exact-dict type check rejects a hostile subclass
            # without touching its protected orthography/IGT accessors.
            with self.assertRaisesRegex(ValueError, "unexpected record"):
                subject.audit(self.root)


if __name__ == "__main__":
    unittest.main()
