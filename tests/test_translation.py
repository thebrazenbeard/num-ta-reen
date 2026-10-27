"""Behavioral regressions for the offline source-constrained translator."""

import base64
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from numtareen import DataError, Translator, UnknownTermError
from numtareen.engine import _SIMPLE_ALTERNATIVES, format_translation


ROOT = Path(__file__).resolve().parents[1]


class TranslationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.translator = Translator()

    def test_all_corpus_examples_round_trip_by_exact_lookup(self):
        for row in self.translator.corpus:
            with self.subTest(id=row["id"]):
                forward = self.translator.translate(row["orthography"], "nt-en")
                inverse = self.translator.translate(row["english"], "en-nt")
                self.assertEqual(forward["status"], "attested")
                self.assertEqual(inverse["status"], "attested")
                self.assertIn(row["english"], [m["translation"] for m in forward["matches"]])
                self.assertIn(row["orthography"], [m["translation"] for m in inverse["matches"]])

    def test_all_dictionary_entries_remain_bidirectionally_discoverable(self):
        for entry in self.translator.lexicon:
            with self.subTest(headword=entry["headword"]):
                forward = self.translator.translate(entry["headword"], "nt-en")
                self.assertIn(forward["status"], {"lexical", "ambiguous", "attested"})
                reverse = self.translator.translate(entry["gloss"], "en-nt")
                candidates = [m["headword"] for part in reverse.get("parts", [])
                              for m in part.get("matches", [])]
                self.assertIn(entry["headword"], candidates)

    def test_phonemic_diacritics_are_not_stripped(self):
        self.assertEqual(self.translator.translate("nûm")["status"], "lexical")
        self.assertNotEqual(self.translator.translate("num")["parts"],
                            self.translator.translate("nûm")["parts"])
        self.assertNotEqual(self.translator.translate("qesh")["parts"],
                            self.translator.translate("kesh")["parts"])

    def test_unicode_sentence_punctuation_does_not_hide_known_dictionary_entries(self):
        # Unicode punctuation is typography at lexical boundaries, not
        # an unknown headword. Exact attested lookup still runs first.
        for query in ("nûm！", "“nûm…”", "nûm。", "nûm？"):
            with self.subTest(query=query):
                result = self.translator.translate(query, "nt-en")
                self.assertEqual(result["status"], "lexical")
                self.assertEqual(result["unknown_count"], 0)
                self.assertEqual(result["parts"][0]["matches"][0]["headword"], "nûm")

        result = self.translator.translate("align/cohere？", "en-nt")
        self.assertEqual(result["status"], "lexical")
        self.assertEqual(result["parts"][0]["matches"][0]["headword"], "nûm")

        result = self.translator.translate("nûm！ ech。", "nt-en")
        self.assertEqual(result["status"], "lexical")
        self.assertEqual(result["unknown_count"], 0)

    def test_unicode_punctuation_does_not_change_attestation_or_phonemic_forms(self):
        # Do not treat a punctuation-modified sentence as source-attested.
        result = self.translator.translate("Nûm ta=en ech！")
        self.assertNotEqual(result["status"], "attested")
        # Keep chord notation and apostrophes meaningful to lookups.
        self.assertEqual(self.translator.translate("⟦61·113·233⟧=tra vu ech.")["status"],
                         "attested")
        self.assertEqual(self.translator.translate("Ta'qesh.")["status"], "attested")

    def test_unicode_canonicalization_only_not_semantic_collapse(self):
        result = self.translator.translate("Nu\u0302m ta=en ech.")
        self.assertEqual(result["status"], "attested")
        result = self.translator.translate("Ta'qesh.")
        self.assertEqual(result["status"], "attested")
        result = self.translator.translate("Threnn’vahl reen.\nUth’se’run.")
        self.assertEqual(result["status"], "attested")

    def test_extra_token_must_not_inherit_attested_label(self):
        result = self.translator.translate("Nûm ta=en ech. green")
        self.assertNotEqual(result["status"], "attested")
        self.assertIn("green", format_translation(result))
        self.assertEqual(result["unknown_count"] > 0, True)

    def test_known_word_has_provenance_and_restricted_register(self):
        result = self.translator.translate("qesh")
        self.assertEqual(result["status"], "lexical")
        self.assertEqual(result["parts"][0]["matches"][0]["register"], "RT")
        self.assertIn("taboo=", format_translation(result))
        self.assertIn("dictionary line=", format_translation(result))

    def test_true_name_chord_stays_unspoken_with_explicit_warning(self):
        result = self.translator.translate("⟦61·113·233⟧=tra vu ech.")
        self.assertEqual(result["status"], "attested")
        output = format_translation(result)
        self.assertIn("unspoken; chord notation only", output)
        self.assertIn("True-name taboo", output)

    def test_slash_gloss_regex_is_not_ambiguous_or_repetitive(self):
        # Regression for overlapping regex alternatives: matching a/a/a...,X
        # must fail promptly instead of exponentially backtracking.
        self.assertIsNone(_SIMPLE_ALTERNATIVES.fullmatch("a/" * 150 + ","))

    def test_unknown_policies_are_explicit(self):
        marked = self.translator.translate("not-a-canonical-word")
        self.assertEqual(marked["status"], "incomplete")
        self.assertIn("⟦unknown:", format_translation(marked))
        kept = self.translator.translate("not-a-canonical-word", unknown="keep")
        self.assertIn("[untranslated]", format_translation(kept))
        with self.assertRaises(UnknownTermError):
            self.translator.translate("not-a-canonical-word", unknown="error")

    def test_no_fabricated_english_sentence(self):
        result = self.translator.translate("A user-invented sentence", "en-nt")
        self.assertEqual(result["status"], "incomplete")
        self.assertNotIn("attested", format_translation(result))

    def test_reverse_dictionary_gloss_and_ambiguity(self):
        result = self.translator.translate("align/cohere", "en-nt")
        self.assertEqual(result["status"], "lexical")
        self.assertIn("nûm", [x["headword"] for x in result["parts"][0]["matches"]])
        # Synthetic fixtures verify ambiguity without modifying canonical data.
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            lex = {"schema_version": 1, "entry_count": 2, "entries": []}
            for word in ("alpha", "beta"):
                lex["entries"].append({"headword": word, "gloss": "a shared state.", "category": "STATE",
                                       "register": "CF", "taboo": "NONE", "ipa": "a", "source_line": 1})
            corpus = {"schema_version": 1, "record_count": 0, "records": []}
            (path / "lexicon.json").write_text(json.dumps(lex), encoding="utf-8")
            (path / "corpus.json").write_text(json.dumps(corpus), encoding="utf-8")
            result = Translator(path).translate("a shared state", "en-nt")
            self.assertEqual(result["status"], "ambiguous")
            self.assertEqual(len(result["parts"][0]["matches"]), 2)

    def test_segmented_stem_and_clitic_analyses_preserve_ambiguity(self):
        translator = Translator()
        stem = translator.words["nûm"][0]
        clitic = translator.words["=en"][0]
        translator.words["nûm"].append({**stem, "gloss": "synthetic alternate stem"})
        translator.words["=en"].extend([
            {**clitic, "gloss": "synthetic clitic option 2"},
            {**clitic, "gloss": "synthetic clitic option 3"},
        ])
        result = translator.translate("nûm=en")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["ambiguous_count"], 1)
        matches = result["parts"][0]["matches"]
        self.assertEqual(len(matches), 6)
        self.assertTrue(all(len(m["segmentation"]) == 2 for m in matches))
        self.assertEqual(len({tuple(x["gloss"] for x in m["segmentation"]) for m in matches}), 6)

    def test_unique_clitic_segmentation_remains_one_lexical_analysis(self):
        result = Translator().translate("nûm=en")
        self.assertEqual(result["status"], "lexical")
        self.assertEqual(result["ambiguous_count"], 0)
        self.assertEqual(len(result["parts"][0]["matches"]), 1)
        self.assertEqual(len(result["parts"][0]["matches"][0]["segmentation"]), 2)

    def test_segmentation_rejects_combinatorial_overflow_explicitly(self):
        translator = Translator()
        entry = translator.words["nûm"][0]
        translator.words["nûm"].extend({**entry, "gloss": f"synthetic-{index}"}
                                         for index in range(64))
        with self.assertRaisesRegex(ValueError, "segmentation.*limit"):
            translator.translate("nûm=en")

    def test_segmentation_allows_exact_bounded_candidate_count(self):
        translator = Translator()
        entry = translator.words["nûm"][0]
        translator.words["nûm"].extend({**entry, "gloss": f"synthetic-{index}"}
                                         for index in range(63))
        result = translator.translate("nûm=en")
        self.assertEqual(result["status"], "ambiguous")
        self.assertEqual(result["ambiguous_count"], 1)
        self.assertEqual(len(result["parts"][0]["matches"]), 64)

    def test_segmentation_rejects_excessive_clitic_depth_explicitly(self):
        with self.assertRaisesRegex(ValueError, "segmentation.*limit"):
            Translator().translate("nûm" + "=en" * 16)

    def test_malformed_fixture_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / "lexicon.json").write_text("{oops", encoding="utf-8")
            with self.assertRaises(DataError):
                Translator(Path(folder))


class CommandLineTests(unittest.TestCase):
    def invoke(self, *args, input_text=None):
        return subprocess.run([sys.executable, "-m", "numtareen", *args], cwd=ROOT,
                              input=input_text, text=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, encoding="utf-8", check=False)

    def test_bidirectional_examples(self):
        result = self.invoke("--direction", "nt-en", "--text", "Nûm ta=en ech.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("You are aligned", result.stdout)
        result = self.invoke("--direction", "en-nt", "--text", "Stop. Do not proceed.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ta’qesh.", result.stdout)

    def test_legacy_output_code_page_does_not_crash_unicode_response(self):
        # Simulates Windows' legacy redirected cp1252 output in a child process.
        # A direct CLI call must not rely on the PowerShell wrapper to set UTF-8.
        env = dict(os.environ, PYTHONIOENCODING="cp1252:strict")
        result = subprocess.run(
            [sys.executable, "-m", "numtareen", "--direction", "nt-en", "--text", "Nûm ta=en ech."],
            cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("You are aligned", result.stdout)
        self.assertIn("/ˈnuːm", result.stdout)

    def test_base64_transport_preserves_metacharacters_and_unicode(self):
        payload = 'He said "hello"; $() 😀'  # This must remain data, never executed.
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        result = self.invoke("--text-base64", encoded, "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["input"], payload)

    def test_invalid_base64_and_invalid_utf8_fail(self):
        for value in ("@@@", "//4="):
            with self.subTest(value=value):
                result = self.invoke("--text-base64", value)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Base64", result.stderr)

    def test_strict_unknown_policy_returns_error(self):
        result = self.invoke("--unknown", "error", "--text", "something-not-in-the-lexicon")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown", result.stderr)

    def test_invisible_terminal_controls_are_visible_escapes(self):
        payload = "x\x1b[2J\u202e"
        for args in (("--text", payload), ("--text", payload, "--unknown", "error"),
                     ("--text", payload, "--json")):
            with self.subTest(args=args):
                result = self.invoke(*args)
                combined = result.stdout + result.stderr
                self.assertNotIn("\x1b", combined)
                self.assertNotIn("\u202e", combined)
                self.assertIn("\\u001b", combined)
                self.assertIn("\\u202e", combined)

    def test_interactive_direction_change(self):
        result = self.invoke("--interactive", input_text=":direction en-nt\nStop. Do not proceed.\n:quit\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ta’qesh.", result.stdout)


if __name__ == "__main__":
    unittest.main()
