"""Focused invariants: test fixtures prove benchmark behavior independently."""

from __future__ import annotations

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from research import bilingual_eval_v0 as evaluation


class SourceBoundBenchmarkTests(unittest.TestCase):
    @staticmethod
    def pair(id: str, nt: str, en: str) -> dict:
        return {"id": id, "orthography_index": nt, "english": en}

    def test_lookup_respects_direction(self):
        rows = [self.pair("E01", "Nûm ech.", "Aligned (witnessed).")]
        self.assertEqual(evaluation.lookup(rows, "Nûm ech", "nt-en"), ["Aligned (witnessed)."])
        self.assertEqual(evaluation.lookup(rows, "Aligned (witnessed)", "en-nt"), ["Nûm ech."])
        self.assertEqual(evaluation.lookup(rows, "Nûm ech", "en-nt"), [])

    def test_source_normalization_keeps_diacritics(self):
        self.assertEqual(evaluation.normalize("NU\u0302M."), evaluation.normalize("nûm"))
        self.assertNotEqual(evaluation.normalize("nûm"), evaluation.normalize("num"))

    def test_apostrophe_is_typographical_only(self):
        self.assertEqual(evaluation.normalize("ta'qesh."), evaluation.normalize("Ta’qesh"))

    def test_exact_holdout_abstains(self):
        rows = [self.pair("E01", "Nûm ech.", "Aligned."), self.pair("E02", "Vahl ech.", "Stabilized.")]
        self.assertEqual(evaluation.lookup(rows[1:], rows[0]["orthography_index"], "nt-en"), [])
        self.assertEqual(evaluation.lookup(rows[1:], rows[0]["english"], "en-nt"), [])

    def test_identical_input_duplicate_can_be_ambiguous(self):
        rows = [self.pair("E01", "Nûm ech.", "Aligned."), self.pair("E02", "Nûm ech.", "Stable.")]
        self.assertEqual(evaluation.lookup(rows, "Nûm ech", "nt-en"), ["Aligned.", "Stable."])

    def test_word_order_bag_cannot_resolve_focus(self):
        a = "Nûm na=ka ta=en ech."
        b = "Nûm ta=en na=ka ech."
        self.assertNotEqual(evaluation.normalize(a), evaluation.normalize(b))
        self.assertEqual(tuple(sorted(evaluation.normalize(a).split())),
                         tuple(sorted(evaluation.normalize(b).split())))

    def test_lexical_ambiguity_retains_candidates(self):
        entries = [{"headword": "a", "gloss": "align."},
                   {"headword": "b", "gloss": "align."},
                   {"headword": "c", "gloss": "witness."}]
        found = evaluation.lexical_counts(entries)
        self.assertEqual(found["en_ambiguous_keys"], 1)
        self.assertEqual(found["en_ambiguity_examples"][0]["numtareen_candidates"], ["a", "b"])

    def test_gloss_alternatives_are_bounded(self):
        self.assertEqual(evaluation.collect_gloss_keys({"gloss": "align/cohere."}),
                         ["align/cohere", "align", "cohere"])
        self.assertEqual(evaluation.collect_gloss_keys({"gloss": "someone (near/far)."}),
                         ["someone (near/far)"])

    def test_unknown_suffix_does_not_become_attested(self):
        rows = [self.pair("E01", "Nûm ech.", "Aligned.")]
        self.assertEqual(evaluation.lookup(rows, "Nûm ech. unattestedv117", "nt-en"), [])
        self.assertEqual(evaluation.lookup(rows, "Aligned. unattestedv117", "en-nt"), [])

    def test_all_protected_examples_declared_explicitly(self):
        self.assertEqual(evaluation.PROTECTED_IDS, frozenset({"E13", "E23", "E26"}))

    def test_source_identity_is_validated_not_merely_reported(self):
        self.assertEqual(
            evaluation.git_blob_sha1(b"abc"),
            hashlib.sha1(b"blob 3\0abc").hexdigest(),
        )
        with TemporaryDirectory() as temp:
            data = Path(temp) / "data"
            data.mkdir()
            root_data = evaluation.DEFAULT_ROOT / "data"
            for name in ("corpus", "lexicon"):
                content = (root_data / f"{name}.json").read_bytes()
                (data / f"{name}.json").write_bytes(content)
            rows, entries, hashes = evaluation.load_source(Path(temp))
            self.assertEqual(len(rows), 30)
            self.assertEqual(len(entries), 500)
            self.assertIn("corpus", hashes)
            (data / "corpus.json").write_bytes(
                (data / "corpus.json").read_bytes() + b"\n"
            )
            with self.assertRaisesRegex(ValueError, "pinned authored"):
                evaluation.load_source(Path(temp))


if __name__ == "__main__":
    unittest.main()
