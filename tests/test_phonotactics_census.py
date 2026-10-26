"""Regression for exact diagnostic counts, never a grammar-validity test."""

import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research.phonotactics_census import census, git_blob_sha, SOURCE, GRAMMAR, DICTIONARY, REPO


class PhonotacticsCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = census()

    def test_pinned_raw_author_sources(self):
        self.assertTrue((REPO / "data" / "lexicon.json").is_file())
        shas = self.report["source_git_blobs"]
        self.assertEqual(git_blob_sha(SOURCE), shas["lexicon"])
        self.assertEqual(git_blob_sha(GRAMMAR), shas["grammar"])
        self.assertEqual(git_blob_sha(DICTIONARY), shas["dictionary"])

    def test_windows_crlf_checkout_keeps_git_object_digest_but_mixed_eol_fails(self):
        original = b"inventoried\nsource\n"
        expected = hashlib.sha1(b"blob " + str(len(original)).encode() + b"\x00" + original).hexdigest()
        with TemporaryDirectory() as directory:
            source = Path(directory) / "checkout.txt"
            source.write_bytes(original)
            self.assertEqual(git_blob_sha(source), expected)
            source.write_bytes(original.replace(b"\n", b"\r\n"))
            self.assertEqual(git_blob_sha(source), expected)
            source.write_bytes(b"inventoried\r\nsource\n")
            self.assertNotEqual(git_blob_sha(source), expected)

    def test_exact_no_false_aggregate(self):
        self.assertEqual(self.report["entries"], 500)
        self.assertEqual(self.report["flagged_terminal_total"], 161)
        self.assertEqual(sum(self.report["flagged_terminal_by_symbol"].values()), 161)

    def test_inventory_candidates_not_only_contact_entries(self):
        self.assertEqual(
            self.report["omitted_consonant_occurrence_entries"],
            {"v": 139, "theta": 93, "tsh": 19},
        )
        self.assertEqual(
            self.report["omitted_consonant_entries_with_cf_register"],
            {"v": 111, "theta": 60, "tsh": 18},
        )

    def test_coda_flags_are_register_overlaps_not_partition(self):
        # A CF/FC entry counts in both registers. Their sum is NOT 161.
        registers = self.report["flagged_terminal_register_counts"]
        self.assertEqual(registers["CF"], 133)
        self.assertGreater(sum(registers.values()), 161)

    def test_no_protected_source_material_or_lexemes_in_report(self):
        # Output deliberately keeps counts, segment symbols and source hashes;
        # it never includes the source's per-entry IPA or protected notation.
        self.assertEqual(
            set(self.report),
            {
                "source_git_blobs", "entries", "listed_codas",
                "omitted_consonant_occurrence_entries",
                "omitted_consonant_entries_with_cf_register",
                "vowel_symbols_beyond_grammars_base_chart",
                "vowel_symbol_ɑ_explanation", "flagged_terminal_total",
                "flagged_terminal_by_symbol", "flagged_terminal_category_counts",
                "flagged_terminal_register_counts",
                "contains_tap_cluster_t_alveolar_tap",
            },
        )


if __name__ == "__main__":
    unittest.main()
