import unittest
from unittest.mock import patch
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.positional_census import after_evidential, audit, clauses

SOURCE_PATH = ROOT / "data" / "corpus.json"


class PositionAuditTests(unittest.TestCase):
    def test_preserve_clause_boundaries_for_multi_clause_e27(self):
        self.assertEqual(
            len(clauses("Threnn’vahl reen.\nUth’se’run.")), 2
        )

    def test_polar_question_after_evidential_not_argument(self):
        self.assertEqual(after_evidential(("nûm", "ta=en", "ech", "hë")), ("hë",))

    def test_attested_contact_goal_after_evidential(self):
        example = clauses("Nûm na=ka ta=en ech ‹airlock›=va.")
        self.assertEqual(after_evidential(example[0]), ("‹airlock›=va",))

    def test_no_unprotected_true_name_content_in_census(self):
        report = audit(SOURCE_PATH)
        self.assertEqual(report, audit())
        self.assertNotIn("E26", repr(report))
        self.assertNotIn("⟦", repr(report))
        self.assertEqual(report["included_records"], 27)

    def test_only_source_attested_post_evidential_argument(self):
        report = audit(SOURCE_PATH)
        self.assertEqual(
            report["post_evidential_argument_cases"],
            [{"id": "E28", "clause": 1}],
        )
        self.assertIn("E08", report["question_only_tails"])

    def test_census_rejects_tampered_source_instead_of_forging_pinned_provenance(self):
        # A path containing altered data may not report the trusted blob SHA.
        tampered = SOURCE_PATH.read_bytes().replace(b'"E28"', b'"E99"', 1)
        self.assertNotEqual(tampered, SOURCE_PATH.read_bytes())
        with patch.object(Path, "read_bytes", return_value=tampered):
            with self.assertRaisesRegex(ValueError, "does not match"):
                audit(SOURCE_PATH)


if __name__ == "__main__":
    unittest.main()
