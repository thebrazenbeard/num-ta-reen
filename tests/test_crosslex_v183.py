"""Discover the source-bound, noncanonical cross-lexical evidence audit.

The upstream experimental tests are kept alongside the research module;
this adapter anchors their source root to the actual repository checkout.
No lexical or corpus data is rewritten.
"""

from __future__ import annotations

import hashlib
import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "crosslex_v183"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

_spec = importlib.util.spec_from_file_location(
    "_numtareen_crosslex_research_tests",
    RESEARCH / "test_crosslex_citation_audit.py",
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("crosslex research suite unavailable")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)


class PublishedCrosslexCitationTests(_module.CitationAuditTests):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = ROOT

    def test_repository_root_is_independent_of_process_cwd(self) -> None:
        self.assertTrue((self.root / "data" / "corpus.json").is_file())
        self.assertTrue((self.root / "docs" / "SOURCE_PARSE_REPORT.md").is_file())


class CrosslexResearchCustodyTests(unittest.TestCase):
    FROZEN = {
        "crosslex_citation_audit.py": "7c9f4cb700f99cac1966bda42e61b2009cd6473599a6d43c19759a65750ccff1",
        "test_crosslex_citation_audit.py": "e19b9c6d21590a6dedc316f9e16cabdda8b4b68311fbd14e5a4684c09838b1c1",
        "REPORT.md": "d7e21da10430873a43bd42b98faacea18f981a0420b24d2bebf81c07a946a9c7",
    }

    def test_exact_packaged_research_bytes(self) -> None:
        for filename, expected in self.FROZEN.items():
            with self.subTest(filename=filename):
                digest = hashlib.sha256((RESEARCH / filename).read_bytes()).hexdigest()
                self.assertEqual(digest, expected)


if __name__ == "__main__":
    unittest.main()
