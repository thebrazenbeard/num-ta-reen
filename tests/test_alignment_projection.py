"""NONCANONICAL falsification regressions for the typed acoustic packet.

From a checkout that contains semantic_ir_proposal, run:
  python -m unittest tests.test_alignment_projection -v

No authored phonosemantics, sentence translation, or audio synthesis.
"""

import unittest

from research.alignment_projection import project_lossy, require_lossless
from research.census_alignment import census
from research.semantic_ir_proposal import analyze_corpus_id
from numtareen.experimental_resonance_packet import Packet, structural_codeword


class ProjectionFalsificationTests(unittest.TestCase):
    def packet(self, corpus_id: str) -> Packet:
        return project_lossy(corpus_id).packet

    def test_no_utterance_claims_lossless(self):
        for corpus_id in ("E01", "E02", "E05", "E08", "E15", "E18", "E20", "E21"):
            with self.subTest(corpus_id=corpus_id), self.assertRaises(ValueError):
                require_lossless(corpus_id)

    def test_distinct_predicates_collapse_e01_e07(self):
        self.assertEqual(self.packet("E01"), self.packet("E07"))

    def test_focus_collapse_e01_e05(self):
        self.assertEqual(self.packet("E01"), self.packet("E05"))
        self.assertIn("discourse_topic_focus", project_lossy("E05").discarded)

    def test_question_collapse_e01_e08(self):
        self.assertEqual(self.packet("E01"), self.packet("E08"))
        self.assertIn("interrogative", project_lossy("E08").discarded)

    def test_argument_order_collapse_e02_e03(self):
        self.assertEqual(self.packet("E02"), self.packet("E03"))
        self.assertIn("argument_order", project_lossy("E02").discarded)

    def test_loop_distinction_preserved_e01_e15(self):
        self.assertNotEqual(structural_codeword(self.packet("E01")),
                            structural_codeword(self.packet("E15")))

    def test_predicate_consent_distinction_preserved_e20_e21(self):
        self.assertNotEqual(self.packet("E20"), self.packet("E21"))
        self.assertEqual(self.packet("E21").consent, "present")

    def test_dual_consent_loci_e18_reduced_to_one_bit(self):
        ir = analyze_corpus_id("E18")
        self.assertEqual(len(ir.consent_locations), 2)
        self.assertEqual(self.packet("E18").consent, "present")
        self.assertIn("consent_loci_reduced_to_boolean", project_lossy("E18").discarded)

    def test_evidential_and_echo_are_distinct_assignments(self):
        self.assertEqual(self.packet("E01").evidence, "witnessed")
        self.assertEqual(self.packet("E15").echo, "loop")
        self.assertEqual(self.packet("E06").evidence, "verified")

    def test_source_conflicts_fail_closed_e13_e23(self):
        for corpus_id in ("E13", "E23"):
            with self.subTest(corpus_id=corpus_id), self.assertRaises(ValueError):
                project_lossy(corpus_id)

    def test_protected_true_name_fails_closed_by_id(self):
        with self.assertRaises(ValueError):
            project_lossy("E26")

    def test_exploratory_collision_groups_are_source_ids_only(self):
        # Exploratory characterization, not a preregistered test.
        self.assertEqual(
            census()["collisions_by_authored_id"],
            [
                ["E01", "E05", "E07", "E08", "E29"],
                ["E02", "E03", "E09"],
                ["E04", "E11", "E19", "E30"],
                ["E06", "E27"],
                ["E15", "E22"],
            ],
        )

    def test_exploratory_full_corpus_projection_collapses_27_to_16(self):
        # Post-result EXPLORATORY regression, NOT a preregistered hypothesis
        # test. The counts characterize an intentionally lossy codebook map.
        summary = census()
        self.assertEqual(summary["authored_rows"], 30)
        self.assertEqual(summary["projected_rows"], 27)
        self.assertEqual(summary["rejected_ids"], ["E13", "E23", "E26"])
        self.assertEqual(summary["distinct_synthetic_packets"], 16)


if __name__ == "__main__":
    unittest.main()
