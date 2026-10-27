"""Source-pinned tests; source location adjustable for isolated research."""

import os
from pathlib import Path
import tempfile
import unittest

from research.clause_boundary_audit import (
    CORPUS_GIT_BLOB_SHA1, EVIDENCE, SourceBoundaryUnavailable,
    attested_clause_observations,
)


class ClauseBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        fallback = root.parent / "num-integration-union-v60"
        cls.repo_root = Path(os.environ.get("NUMTAREEN_TEST_REPO_ROOT", str(root if (root / "data" / "corpus.json").exists() else fallback)))

    def clauses(self, identifier):
        return attested_clause_observations(identifier, repo_root=self.repo_root)

    def test_e30_witnessed_threshold_but_not_negative_crossing(self):
        clauses = self.clauses("E30")
        self.assertEqual(tuple(c.orthography for c in clauses),
                         ("Ta’qesh.", "Veyl’sekh ech.", "Kesh vu."))
        self.assertEqual(tuple(tuple(o.gloss for o in c.operators) for c in clauses),
                         (("PROH",), ("EVID.WIT",), ("NEG",)))
        self.assertEqual([(c.atom_start, c.atom_end_exclusive) for c in clauses],
                         [(0, 1), (1, 3), (3, 5)])

    def test_e27_two_packets_and_silence_not_permission(self):
        clauses = self.clauses("E27")
        self.assertEqual(len(clauses), 2)
        self.assertEqual(tuple(o.gloss for o in clauses[0].operators), ("EVID.VRF",))
        self.assertEqual(clauses[1].atoms, (("uth-se’run", "SOFT-respect.silence"),))
        self.assertEqual(clauses[1].operators, ())

    def test_e19_negation_and_witnessing_share_single_packet(self):
        clauses = self.clauses("E19")
        self.assertEqual(len(clauses), 1)
        self.assertEqual(tuple(o.gloss for o in clauses[0].operators), ("NEG", "EVID.WIT"))

    def test_prohibition_with_and_without_evidential(self):
        self.assertEqual(tuple(o.gloss for o in self.clauses("E11")[0].operators),
                         ("PROH", "EVID.WIT"))
        self.assertEqual(tuple(o.gloss for o in self.clauses("E17")[0].operators),
                         ("PROH",))

    def test_bounded_no_synthetic_or_protected_segmentation(self):
        for identifier in ("E26", "E01", "UNVERIFIED", "E30 "):
            with self.subTest(identifier=identifier):
                with self.assertRaises(SourceBoundaryUnavailable):
                    self.clauses(identifier)

    def test_pinned_source_mutation_fails_closed(self):
        corpus = (self.repo_root / "data" / "corpus.json").read_bytes()
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data").mkdir()
            (root / "data" / "corpus.json").write_bytes(corpus + b" ")
            with self.assertRaisesRegex(SourceBoundaryUnavailable, "source Git blob mismatch"):
                attested_clause_observations("E30", repo_root=root)

    def test_audit_provenance_and_nonqualification(self):
        for entry in self.clauses("E30"):
            self.assertEqual(entry.evidence, EVIDENCE)
            self.assertEqual(entry.source_git_blob_sha1, CORPUS_GIT_BLOB_SHA1)
            self.assertFalse(entry.qualification_eligible)


if __name__ == "__main__":
    unittest.main()
