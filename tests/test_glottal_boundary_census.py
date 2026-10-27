"""Offline, pinned, noncanonical source interruption research."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from research.glottal_boundary_census import SOURCE_BLOBS, census, scan_record


ROOT = Path(os.environ.get(
    "NUMTAREEN_REPO_ROOT",
    str(Path(__file__).resolve().parents[1]),
))


class GlottalBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = census(ROOT)
        cls.index = {row["id"]: row for row in cls.report["records"]}

    def test_complete_protected_exclusion(self):
        self.assertEqual(self.report["nonprotected_authored_examples"], 29)
        self.assertNotIn("E26", self.index)
        self.assertNotIn("⟦", json.dumps(self.report, ensure_ascii=False))

    def test_canonical_source_custody(self):
        self.assertEqual(
            self.report["source_git_blobs"]["data/corpus.json"],
            "53d9f27d03579a1a3fc700c3394b56f834da784e",
        )
        self.assertEqual(len(SOURCE_BLOBS), 4)

    def test_clitic_boundary_is_not_an_apostrophe(self):
        e01 = self.index["E01"]
        self.assertEqual(e01["apostrophe_marks"], 0)
        self.assertEqual(e01["clitic_attachment_marks"], 1)
        self.assertEqual(e01["transcribed_glottal_stops"], 1)

    def test_consent_scoped_clitics_keep_each_boundary(self):
        e18 = self.index["E18"]
        self.assertEqual(e18["clitic_attachment_marks"], 3)
        self.assertEqual(e18["transcribed_glottal_stops"], 3)

    def test_root_initial_uth_shows_nonbijective_map(self):
        self.assertEqual(self.index["E14"]["ipa_minus_boundary_marks"], 1)
        self.assertEqual(self.index["E27"]["ipa_minus_boundary_marks"], 1)

    def test_adversarial_missing_ipa_event_remains_visible(self):
        row = scan_record({"id": "E99", "orthography": "a’b=c", "ipa": "/abʔc/"})
        self.assertEqual(row["candidate_boundary_marks"], 2)
        self.assertEqual(row["transcribed_glottal_stops"], 1)
        self.assertEqual(row["ipa_minus_boundary_marks"], -1)

    def test_composed_and_decomposed_vowels_are_not_stripped(self):
        row = scan_record({"id": "E99", "orthography": "Nu\u0302m ’ a", "ipa": "/nuːmʔa/"})
        self.assertEqual(row["apostrophe_marks"], 1)
        self.assertEqual(row["clitic_attachment_marks"], 0)

    def test_source_tamper_rejected(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp)
            for rel in SOURCE_BLOBS:
                target = fake / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / rel, target)
            raw = (fake / "data/corpus.json").read_text(encoding="utf-8")
            (fake / "data/corpus.json").write_text(raw + " ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "source mismatch"):
                census(fake)


if __name__ == "__main__":
    unittest.main()
