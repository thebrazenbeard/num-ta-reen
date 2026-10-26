"""Offline dictionary discovery is a reference lookup, never translation."""

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path

from numtareen.engine import DataError, Translator
from numtareen.lexicon_search import format_search, search_lexicon


ROOT = Path(__file__).resolve().parents[1]


def invoke(*args):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, "-m", "numtareen", *args],
        cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        env=env, timeout=10, check=False,
    )


class LexiconSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.translator = Translator()

    def test_exact_gloss_has_original_provenance(self):
        row = search_lexicon(self.translator, "patient role", match="exact")
        self.assertEqual(row["total_matches"], 1)
        item, = row["entries"]
        self.assertEqual((item["headword"], item["source_line"]), ("=en", 20))
        self.assertEqual(row["normalized_data_file"], "data/lexicon.json")
        self.assertEqual(row["source_line_document"],
                         "sources/dictionary_v2_updated_lphoneme.txt")
        self.assertEqual(item["source_line_document"], row["source_line_document"])
        # source_line indexes the authoritative amended text, not the
        # generated data/lexicon.json serialization.
        source_line = (ROOT / item["source_line_document"]).read_text(
            encoding="utf-8"
        ).splitlines()[item["source_line"] - 1]
        self.assertTrue(source_line.startswith("=en "), source_line)
        self.assertEqual((item["category"], item["register"], item["taboo"]),
                         ("CLITIC", "CF/FC", "NONE"))
        self.assertEqual(row["evidence_class"], "AUTHOR_LEXICON_REFERENCE")
        self.assertFalse(row["qualification_eligible"])
        self.assertFalse(row["learner_visible"])
        self.assertIsNone(row["semantic_atoms"])
        self.assertIs(row["fluent_translation"], False)
        self.assertIn("source=sources/dictionary_v2_updated_lphoneme.txt:20",
                      format_search(row))

    def test_normalization_keeps_phonemic_diacritics(self):
        row = search_lexicon(self.translator, unicodedata.normalize("NFD", "nûm"),
                             match="exact", field="headword")
        self.assertEqual([e["headword"] for e in row["entries"]], ["nûm"])
        plain = search_lexicon(self.translator, "num", match="exact", field="headword")
        self.assertNotIn("nûm", [e["headword"] for e in plain["entries"]])

    def test_source_fields_and_taboo_flags_are_unmodified(self):
        sample = next(e for e in self.translator.lexicon if e["taboo"] == "TRUE-NAME")
        result = search_lexicon(self.translator, sample["headword"],
                                field="headword", match="exact", taboo="TRUE-NAME")
        self.assertEqual(result["entries"][0]["taboo"], "TRUE-NAME")
        self.assertEqual(result["entries"][0]["source_line"], sample["source_line"])
        hidden = search_lexicon(self.translator, sample["headword"], field="headword",
                                match="exact", taboo="NONE")
        self.assertEqual(hidden["total_matches"], 0)

    def test_category_and_field_filters(self):
        row = search_lexicon(self.translator, "role", category="CLITIC",
                             field="gloss", match="contains", limit=100)
        self.assertGreater(row["total_matches"], 0)
        self.assertTrue(all(e["category"] == "CLITIC" for e in row["entries"]))
        self.assertTrue(all("role" in e["gloss"] for e in row["entries"]))

    def test_unknown_is_zero_matches_not_invented(self):
        row = search_lexicon(self.translator, "__unattested_xyz__", match="exact")
        self.assertEqual((row["total_matches"], row["entries"], row["truncated"]),
                         (0, [], False))

    def test_in_memory_lexicon_spoof_is_not_attributed_to_canon(self):
        altered = Translator()
        altered.lexicon[0]["gloss"] = "synthetic unapproved gloss"
        with self.assertRaises(DataError):
            search_lexicon(altered, "synthetic unapproved gloss")

    def test_alternate_files_cannot_claim_canonical_origin(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            directory = Path(temp_dir)
            shutil.copyfile(ROOT / "data" / "corpus.json", directory / "corpus.json")
            shutil.copyfile(ROOT / "data" / "lexicon.json", directory / "lexicon.json")
            text = (directory / "lexicon.json").read_text(encoding="utf-8")
            (directory / "lexicon.json").write_text(
                text.replace("agent role.", "synthetic role.", 1), encoding="utf-8"
            )
            with self.assertRaises(DataError):
                search_lexicon(Translator(directory), "synthetic role")

    def test_exact_ranking_and_bounded_output(self):
        row = search_lexicon(self.translator, "role", match="contains", limit=2)
        self.assertLessEqual(len(row["entries"]), 2)
        self.assertEqual(row["truncated"], row["total_matches"] > 2)
        full = search_lexicon(self.translator, "role", match="contains", limit=100)
        self.assertEqual([e["source_line"] for e in row["entries"]],
                         [e["source_line"] for e in full["entries"][:2]])

    def test_invalid_search_options_fail_explicitly(self):
        for kwargs in ({"limit": 0}, {"limit": 101}, {"field": "all"},
                       {"match": "regex"}, {"query": ""}, {"query": "."},
                       {"query": "x" * 257}):
            with self.subTest(kwargs=kwargs):
                query = kwargs.get("query", "x")
                with self.assertRaises(ValueError):
                    search_lexicon(self.translator, query,
                                   **{k: v for k, v in kwargs.items() if k != "query"})

    def test_json_cli_exact_gloss(self):
        p = invoke("--lexicon-search", "patient role", "--match", "exact", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        value = json.loads(p.stdout)
        self.assertEqual(value["entries"][0]["headword"], "=en")
        self.assertFalse(value["qualification_eligible"])

    def test_base64_search_unicode_and_malformed(self):
        payload = base64.b64encode("nûm".encode("utf-8")).decode("ascii")
        p = invoke("--lexicon-search-base64", payload, "--match", "exact",
                   "--field", "headword", "--json")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["entries"][0]["headword"], "nûm")
        bad = invoke("--lexicon-search-base64", "!not-base64!")
        self.assertNotEqual(bad.returncode, 0)
        self.assertNotIn("Traceback", bad.stderr)
        oversized = invoke("--lexicon-search-base64", "YQ==" * 400)
        self.assertNotEqual(oversized.returncode, 0)
        self.assertNotIn("Traceback", oversized.stderr)

    def test_cli_search_separate_from_translation(self):
        p = invoke("--lexicon-search", "patient role", "--text", "Nûm")
        self.assertNotEqual(p.returncode, 0)
        unknown = invoke("--lexicon-search", "__unattested_xyz__", "--json")
        self.assertEqual(unknown.returncode, 0, unknown.stderr)
        self.assertEqual(json.loads(unknown.stdout)["total_matches"], 0)


if __name__ == "__main__":
    unittest.main()
