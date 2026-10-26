"""Tests for an evidence-bound, NONCANONICAL pronunciation reference.

In an ordinary Num’ta’reen checkout, run `python -m unittest discover -s
tests -p test_phonetic_bridge.py`. For isolated proposal staging, set
NUMTAREEN_REPO_ROOT to the exact canonical checkout and PYTHONPATH to this
proposal package directory. Neither the test nor CLI needs network access.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from numtareen.phonetic_bridge import AttestedPronunciationGuide


REPO_ROOT = Path(os.environ.get(
    "NUMTAREEN_REPO_ROOT", str(Path(__file__).resolve().parents[1])
)).resolve()


class AttestedPronunciationGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = AttestedPronunciationGuide(REPO_ROOT)

    def test_complete_e01_uses_corpus_not_concatenated_lexemes(self):
        x = self.guide.lookup("Nûm ta=en ech.")
        self.assertEqual(x.status, "ATTESTED_UTTERANCE")
        self.assertEqual(x.source_locator, "E01")
        self.assertEqual(x.ipa, "/ˈnuːm tɑʔˈɛn ɛt͡ʃ/")
        self.assertEqual(x.evidence_class, "AUTHOR_ATTESTED_CORPUS")
        self.assertTrue(x.laryngeal_interruptions_attested)
        self.assertTrue(x.phonemic_length_attested)
        self.assertIsNone(x.scope_or_resonance_frequency_hz)

    def test_dictionary_clitic_does_not_assert_connected_speech(self):
        x = self.guide.lookup("=en")
        self.assertEqual(x.status, "ATTESTED_LEXEME")
        self.assertEqual(x.ipa, "/ɛn/")
        self.assertEqual(x.source_locator, "line:20")
        self.assertEqual(x.source_document, "sources/dictionary_v2_updated_lphoneme.txt")
        self.assertFalse(x.laryngeal_interruptions_attested)
        self.assertIn("does not establish pronunciation", " ".join(x.caution))

    def test_unicode_normalization_preserves_length_contrast(self):
        self.assertEqual(self.guide.lookup("nu\u0302m").status, "ATTESTED_LEXEME")
        self.assertEqual(self.guide.lookup("nûm").ipa, self.guide.lookup("nu\u0302m").ipa)
        self.assertNotEqual(self.guide.lookup("num").ipa, self.guide.lookup("nûm").ipa)

    def test_amended_l_phoneme_not_dropped(self):
        self.assertIn("l", self.guide.lookup("veyl").ipa)

    def test_unknown_fails_closed(self):
        x = self.guide.lookup("a never attested sentence")
        self.assertEqual(x.status, "UNKNOWN")
        self.assertIsNone(x.ipa)
        self.assertIsNone(x.laryngeal_interruptions_attested)

    def test_e13_conflict_visible_not_resolved(self):
        x = self.guide.lookup("Veyl sekh së nûm reen.")
        self.assertEqual(x.source_locator, "E13")
        self.assertTrue(any("Source conflict" in line for line in x.caution))
        self.assertIsNone(x.scope_or_resonance_frequency_hz)

    def test_multiline_attestation_preserves_corpus_ipa(self):
        x = self.guide.lookup("Threnn’vahl reen.\nUth’se’run.")
        self.assertEqual(x.source_locator, "E27")
        self.assertIn("ʔ", x.ipa)
        self.assertEqual(
            self.guide.lookup("Threnn’vahl reen.\r\nUth’se’run.").ipa,
            x.ipa,
        )

    def test_protected_e26_not_echoed_without_embedded_chord_literal(self):
        # Read rather than embed the source's unspoken field notation.
        corpus = json.loads((REPO_ROOT / "data" / "corpus.json").read_text(encoding="utf8"))
        source = next(row["orthography"] for row in corpus["records"] if row["id"] == "E26")
        for text in ("E26", source, "⟦opaque-protected-placeholder⟧"):
            x = self.guide.lookup(text)
            self.assertEqual(x.status, "WITHHELD")
            self.assertIsNone(x.ipa)
            self.assertNotIn(source, str(x.as_dict()))

    def test_controls_and_surrogates_rejected(self):
        for bad in ("nûm\x00", "nûm\ud800", "\n", "x" * 8193):
            with self.assertRaises(ValueError):
                self.guide.lookup(bad)

    def test_forged_same_count_corpus_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for sub in ("data", "sources"):
                (root / sub).mkdir()
            from numtareen.phonetic_bridge import SOURCE_SHA256
            for path in SOURCE_SHA256:
                shutil.copy2(REPO_ROOT / path, root / path)
            corpus_path = root / "data" / "corpus.json"
            corpus = json.loads(corpus_path.read_text(encoding="utf8"))
            corpus["records"][0]["ipa"] = "/FAKE/"
            corpus_path.write_text(json.dumps(corpus, ensure_ascii=False), encoding="utf8")
            self.assertEqual(len(corpus["records"]), 30)
            with self.assertRaisesRegex(ValueError, "source snapshot mismatch"):
                AttestedPronunciationGuide(root)

    def test_modified_dictionary_source_refused_even_with_original_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for sub in ("data", "sources"):
                (root / sub).mkdir()
            from numtareen.phonetic_bridge import SOURCE_SHA256
            for path in SOURCE_SHA256:
                shutil.copy2(REPO_ROOT / path, root / path)
            dictionary = root / "sources" / "dictionary_v2_updated_lphoneme.txt"
            dictionary.write_bytes(dictionary.read_bytes() + b"\n# tampered")
            with self.assertRaisesRegex(ValueError, "source snapshot mismatch"):
                AttestedPronunciationGuide(root)

    def test_windows_checkout_crlf_on_source_txt_accepted(self):
        # .gitattributes pins data JSON to LF, but extracted source text may
        # undergo platform-specific Git end-of-line conversion.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for sub in ("data", "sources"):
                (root / sub).mkdir()
            from numtareen.phonetic_bridge import SOURCE_SHA256
            for path in SOURCE_SHA256:
                shutil.copy2(REPO_ROOT / path, root / path)
                if path.startswith("sources/"):
                    text = (root / path).read_bytes().replace(b"\r\n", b"\n")
                    (root / path).write_bytes(text.replace(b"\n", b"\r\n"))
            self.assertEqual("ATTESTED_LEXEME", AttestedPronunciationGuide(root).lookup("nûm").status)

    def test_cli_from_clean_checkout_preserves_evidence(self):
        cmd = [sys.executable, "-m", "numtareen.phonetic_bridge",
               "--repo-root", str(REPO_ROOT), "Nûm ta=en ech."]
        complete = subprocess.run(cmd, capture_output=True, text=True, check=False)
        self.assertEqual(0, complete.returncode, complete.stderr)
        result = json.loads(complete.stdout)
        self.assertEqual(result["evidence_class"], "AUTHOR_ATTESTED_CORPUS")
        self.assertEqual(result["source_locator"], "E01")

    def test_cli_preserves_ipa_with_legacy_windows_codepage(self):
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "cp1252"
        complete = subprocess.run(
            [sys.executable, "-m", "numtareen.phonetic_bridge", "--repo-root",
             str(REPO_ROOT), "Nûm ta=en ech."],
            env=env, capture_output=True, encoding="cp1252", check=False,
        )
        self.assertEqual(0, complete.returncode, complete.stderr)
        self.assertTrue(complete.stdout.isascii())
        self.assertEqual("/ˈnuːm tɑʔˈɛn ɛt͡ʃ/", json.loads(complete.stdout)["ipa"])


if __name__ == "__main__":
    unittest.main()
