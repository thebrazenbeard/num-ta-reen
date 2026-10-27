"""Research-only English multiword dictionary span discovery contract."""

import base64
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from numtareen.engine import Translator
from numtareen.gloss_spans import discover_english_gloss_spans


ROOT = Path(__file__).resolve().parents[1]


class GlossSpanTests(unittest.TestCase):
    def make_translator(self, folder: Path) -> Translator:
        glosses = ("a", "a shared", "shared state", "state", "a shared state")
        lexicon = {"schema_version": 1, "entry_count": len(glosses), "entries": [
            {"headword": f"test-{i}", "gloss": gloss + ".", "category": "TEST",
             "register": "CF", "taboo": "NONE", "ipa": "t", "source_line": i + 1}
            for i, gloss in enumerate(glosses)
        ]}
        (folder / "lexicon.json").write_text(json.dumps(lexicon), encoding="utf-8")
        (folder / "corpus.json").write_text(
            json.dumps({"schema_version": 1, "record_count": 0, "records": []}), encoding="utf-8")
        return Translator(folder)

    def test_all_overlapping_source_phrases_remain_visible(self):
        with tempfile.TemporaryDirectory() as temp:
            explorer = self.make_translator(Path(temp))
            found = discover_english_gloss_spans(explorer, "I saw a shared state!")
        spans = {(row["start"], row["end"], row["english_span"])
                 for row in found["spans"]}
        self.assertEqual(spans, {
            (2, 3, "a"), (2, 4, "a shared"), (2, 5, "a shared state"),
            (3, 5, "shared state"), (4, 5, "state"),
        })
        self.assertEqual(found["status"], "partial")
        self.assertEqual([item["token"] for item in found["uncovered"]], ["I", "saw"])
        # Spans for "a" and "shared state", for example, are disjoint;
        # overlap is a positional relation, not a blanket ambiguity flag.
        self.assertEqual(len(found["overlapping_span_pairs"]), 7)
        self.assertTrue(all(item["candidates"][0]["source_line"] > 0 for item in found["spans"]))

    def test_no_fluent_generation_and_no_silent_parse_choice(self):
        with tempfile.TemporaryDirectory() as temp:
            explorer = self.make_translator(Path(temp))
            found = discover_english_gloss_spans(explorer, "a shared state")
        self.assertEqual(found["status"], "candidates")
        self.assertEqual(len(found["spans"]), 5)
        self.assertNotIn("translation", found)
        self.assertNotIn("Num'ta'reen sentence", found)
        self.assertIn("no sentence generated", found["note"])

    def test_synonymous_candidates_are_not_merged_or_ranked(self):
        with tempfile.TemporaryDirectory() as temp:
            explorer = self.make_translator(Path(temp))
            duplicate = dict(explorer.glosses["a shared state"][0])
            duplicate["headword"] = "alternate-headword"
            explorer.glosses["a shared state"].append(duplicate)
            found = discover_english_gloss_spans(explorer, "a shared state")
        candidates = next(row["candidates"] for row in found["spans"]
                          if row["english_span"] == "a shared state")
        self.assertEqual([row["headword"] for row in candidates],
                         ["test-4", "alternate-headword"])

    def test_internal_parenthetical_preserved_in_multiword_gloss(self):
        found = discover_english_gloss_spans(Translator(),
                                             "this is home-realm (endonym), perhaps")
        self.assertTrue(any("home-realm (endonym)" == row["english_span"]
                            for row in found["spans"]))

    def test_empty_unknown_and_bounded_inputs(self):
        translator = Translator()
        with self.assertRaisesRegex(ValueError, "nonempty"):
            discover_english_gloss_spans(translator, "")
        with self.assertRaisesRegex(ValueError, "character bound"):
            discover_english_gloss_spans(translator, "x" * 4097)
        with self.assertRaisesRegex(ValueError, "token bound"):
            discover_english_gloss_spans(translator, "x " * 33)
        result = discover_english_gloss_spans(translator, "gobbledegook123")
        self.assertEqual(result["status"], "none")
        self.assertEqual(result["uncovered"][0]["token"], "gobbledegook123")

    def test_real_multiword_source_gloss_found_within_english_clause(self):
        translator = Translator()
        # This multiword dictionary entry is recorded in lexicon.json, not
        # generated from presumed Num'ta'reen syntax.
        result = discover_english_gloss_spans(translator, "I noticed witnessed alignment. yesterday")
        self.assertTrue(any(
            row["english_span"] == "witnessed alignment"
            and any(entry["headword"] == "ech’nûm" for entry in row["candidates"])
            for row in result["spans"]
        ))
        self.assertEqual(result["status"], "partial")

    def test_str_subclass_cannot_substitute_unrelated_words(self):
        class Inject(str):
            def split(self, *args, **kwargs):
                return ["witnessed", "alignment"]

        original = "I never said this"
        found = discover_english_gloss_spans(Translator(), Inject(original))
        self.assertEqual(found["input"], original)
        self.assertEqual(found["token_count"], 4)
        self.assertFalse(any(
            candidate["headword"] == "ech’nûm"
            for span in found["spans"] for candidate in span["candidates"]
        ))

    def test_loaded_custom_dictionary_never_masquerades_as_author_source(self):
        with tempfile.TemporaryDirectory() as temp:
            found = discover_english_gloss_spans(
                self.make_translator(Path(temp)), "a shared state"
            )
        self.assertIn("loaded dictionary", found["note"].lower())
        self.assertNotIn("source-attested", found["note"].lower())

    def test_cli_powershell_safe_ascii_transport_and_direction_gate(self):
        sentence = 'Witnessed alignment; "$?" 😀'
        encoded = base64.b64encode(sentence.encode("utf-8")).decode("ascii")
        command = [sys.executable, "-m", "numtareen", "--direction", "en-nt",
                   "--text-base64", encoded, "--gloss-spans"]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual(output["input"], sentence)
        self.assertEqual(output["schema"], "numtareen.experimental.english_gloss_spans.v0")
        self.assertNotIn("😀", result.stdout)  # JSON is ASCII-escaped for old consoles
        invalid = subprocess.run([sys.executable, "-m", "numtareen", "--text", "foo",
                                  "--gloss-spans"], cwd=ROOT, capture_output=True,
                                 encoding="utf-8")
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn("requires --direction en-nt", invalid.stderr)
        invalid_policy = subprocess.run([sys.executable, "-m", "numtareen",
                                         "--direction", "en-nt", "--text", "foo",
                                         "--unknown", "error", "--gloss-spans"],
                                        cwd=ROOT, capture_output=True, encoding="utf-8")
        self.assertNotEqual(invalid_policy.returncode, 0)
        self.assertIn("does not apply --unknown policy", invalid_policy.stderr)


if __name__ == "__main__":
    unittest.main()
