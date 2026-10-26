"""Source-bound interoperability checks for Num'ta'reen as a UNVTRSLR pack.

Run from a clean checkout of num-ta-reen with:
    python -m unittest discover -s tests -p test_unvtrslr_interop.py -v

For an isolated audit copy, set NUMTAREEN_ROOT to the checked-out repository.
These checks deliberately do not train the UNVTRSLR semantic bridge using
bilingual corpus labels as if they were independent observations.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0, str(ROOT))

from numtareen import Translator  # noqa: E402


# Exact main subjects recorded when this test was authored. Review/update
# these only after a source-provenance diff, not as a generic version bump.
SOURCE_BLOBS = {
    "data/corpus.json": "53d9f27d03579a1a3fc700c3394b56f834da784e",
    "data/lexicon.json": "c78dccdf9614d8e8e94c968aac5c07a2e4206bf1",
}


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class NumtareenInteropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.translator = Translator(ROOT / "data")

    def test_original_data_is_pinned_and_not_silently_regenerated(self):
        for relative, expected in SOURCE_BLOBS.items():
            with self.subTest(relative=relative):
                self.assertEqual(git_blob_sha(ROOT / relative), expected)
        self.assertEqual(len(self.translator.corpus), 30)
        self.assertEqual(len(self.translator.lexicon), 500)

    def test_attested_pairs_remain_exact_provenance_bearing_lookup_only(self):
        for row in self.translator.corpus:
            with self.subTest(utterance=row["id"]):
                nt_en = self.translator.translate(row["orthography"], "nt-en")
                en_nt = self.translator.translate(row["english"], "en-nt")
                self.assertEqual(nt_en["status"], "attested")
                self.assertEqual(en_nt["status"], "attested")
                self.assertTrue(any(match["id"] == row["id"] and
                                    match["translation"] == row["english"]
                                    for match in nt_en["matches"]))
                self.assertTrue(any(match["id"] == row["id"] and
                                    match["translation"] == row["orthography"]
                                    for match in en_nt["matches"]))
                self.assertIn("not a general grammatical generation", nt_en["note"])
                self.assertIn("not a general grammatical generation", en_nt["note"])

    def test_unseen_and_partially_known_phrases_never_gain_attested_status(self):
        probes = (
            ("Nûm ta=en ech. imaginary", "nt-en"),
            ("an entirely unattested English phrase", "en-nt"),
            ("nûm imaginary", "nt-en"),
            ("unknown astronomical entity", "en-nt"),
        )
        for text, direction in probes:
            with self.subTest(text=text):
                result = self.translator.translate(text, direction)
                self.assertEqual(result["status"], "incomplete")
                self.assertGreater(result["unknown_count"], 0)
                self.assertNotIn("matches", result)
                self.assertIn("Approximate dictionary glosses only", result["note"])

    def test_language_identity_is_not_erased_by_normalization(self):
        self.assertEqual(self.translator.translate("Nu\u0302m ta=en ech.")["status"], "attested")
        self.assertEqual(self.translator.translate("Ta'qesh.")["status"], "attested")
        self.assertNotEqual(self.translator.translate("nûm"),
                            self.translator.translate("num"))

    def test_utf8_json_cli_is_machine_readable_with_hostile_input_as_data(self):
        query = 'Nûm ta=en ech.\u202e $(echo bad) "\U0001f600"'
        completed = subprocess.run(
            [sys.executable, "-m", "numtareen", "--direction", "nt-en", "--text", query,
             "--json"],
            cwd=ROOT,
            check=False,
            encoding="utf-8",
            capture_output=True,
            timeout=10,
            env={**os.environ, "PYTHONNOUSERSITE": "1"},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        obj = json.loads(completed.stdout)
        self.assertEqual(obj["input"], query)
        self.assertNotEqual(obj["status"], "attested")
        self.assertGreater(obj["unknown_count"], 0)

    def test_bilingual_lookup_is_not_independent_semantic_grounding(self):
        """A corpus match must not masquerade as a learned world relation.

        The UNVTRSLR BridgeLearner expects independently observed context
        distinctions in Episode.context. The Num'ta'reen corpus contains human
        authored English glosses and cannot supply those observations.
        """
        row = self.translator.corpus[0]
        result = self.translator.translate(row["orthography"], "nt-en")
        self.assertEqual(result["status"], "attested")
        # The current API has no independent context provenance, observation
        # IDs or grounded certificate; adapter must preserve this distinction.
        for forbidden in ("grounded", "grounding_certificate", "observed_context",
                          "external_world_evidence", "independent_evaluation"):
            self.assertNotIn(forbidden, result)


class ExportContractTests(unittest.TestCase):
    """Private exporter assertions for the public generic UNVTRSLR importer."""

    @classmethod
    def setUpClass(cls):
        from numtareen.interop import to_reference_record

        cls.export = staticmethod(to_reference_record)
        cls.translator = Translator(ROOT / "data")

    def request(self, *payloads: str) -> list[dict]:
        completed = subprocess.run(
            [sys.executable, "-m", "numtareen.interop"],
            cwd=ROOT,
            input="".join(payloads),
            encoding="utf-8",
            capture_output=True,
            check=False,
            timeout=10,
            env={**os.environ, "PYTHONNOUSERSITE": "1"},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        return [json.loads(line) for line in completed.stdout.splitlines()]

    def test_exporter_marks_all_attested_pairs_nonqualifying(self):
        for row in self.translator.corpus:
            for direction, source in (("nt-en", row["orthography"]),
                                      ("en-nt", row["english"])):
                with self.subTest(id=row["id"], direction=direction):
                    result = self.export(self.translator, source, direction)
                    self.assertEqual(result["schema"], "unvtrslr-reference-evidence-v1")
                    self.assertEqual(result["evidence_class"], "AUTHOR_ATTESTED_CORPUS")
                    self.assertIsNone(result["semantic_atoms"])
                    self.assertIs(result["qualification_eligible"], False)
                    self.assertIn("origin", result)

    def test_lexical_and_unknown_results_do_not_gain_grounding_credit(self):
        for phrase, evidence_class in (("nûm", "AUTHOR_LEXICON_GLOSS"),
                                       ("not-a-numtareen-word", "UNKNOWN")):
            with self.subTest(phrase=phrase):
                result = self.export(self.translator, phrase, "nt-en")
                self.assertEqual(result["evidence_class"], evidence_class)
                self.assertIsNone(result["semantic_atoms"])
                self.assertIs(result["qualification_eligible"], False)
                self.assertIsNone(result.get("target_text"))

    def test_true_name_chord_is_not_rendered_as_emit_ready_signal(self):
        source = next(row for row in self.translator.corpus if row["id"] == "E26")
        result = self.export(self.translator, source["english"], "en-nt")
        self.assertEqual(result["evidence_class"], "AUTHOR_ATTESTED_CORPUS")
        self.assertIsNone(result.get("target_text"))
        self.assertIs(result["qualification_eligible"], False)

    def test_jsonl_transport_recovers_after_malformed_data(self):
        valid = json.dumps({"direction": "nt-en", "text": "Nûm ta=en ech."},
                           ensure_ascii=False) + "\n"
        responses = self.request("{not-json}\n", valid)
        self.assertEqual(len(responses), 2)
        self.assertIn("error", responses[0])
        self.assertIs(responses[1]["ok"], True)
        self.assertEqual(responses[1]["record"]["evidence_class"], "AUTHOR_ATTESTED_CORPUS")

    def test_maximum_frame_size_is_enforced_without_crashing_session(self):
        too_big = json.dumps({"direction": "nt-en", "text": "x" * 70000}) + "\n"
        valid = json.dumps({"direction": "nt-en", "text": "Nûm ta=en ech."},
                           ensure_ascii=False) + "\n"
        responses = self.request(too_big, valid)
        self.assertEqual(len(responses), 2)
        self.assertIn("error", responses[0])
        self.assertIs(responses[1]["ok"], True)
        self.assertEqual(responses[1]["record"]["evidence_class"], "AUTHOR_ATTESTED_CORPUS")

    def test_transport_preserves_unicode_metacharacters_as_untrusted_data(self):
        malicious = '$() `$(touch PWNED)` 😀 \u202e'
        valid = json.dumps({"direction": "nt-en", "text": malicious},
                           ensure_ascii=False) + "\n"
        responses = self.request(valid)
        self.assertEqual(len(responses), 1)
        self.assertIs(responses[0]["ok"], True)
        self.assertEqual(responses[0]["record"]["evidence_class"], "UNKNOWN")
        self.assertIsNone(responses[0]["record"]["semantic_atoms"])
        self.assertIs(responses[0]["record"]["qualification_eligible"], False)


@unittest.skipUnless(os.environ.get("UNVTRSLR_ROOT"),
                     "Set UNVTRSLR_ROOT for actual two-repository parser qualification")
class TwoRepositoryRoundTripTests(unittest.TestCase):
    """Exercise the *actual* public importer with private source envelopes.

    Keep this suite in the private repository only: records never belong in
    UNVTRSLR's public repository, logs, or CI artifacts.
    """

    @classmethod
    def setUpClass(cls):
        from numtareen.interop import to_reference_record

        public_root = Path(os.environ["UNVTRSLR_ROOT"]).resolve()
        sys.path.insert(0, str(public_root / "src"))
        from unvtrslr.reference_evidence import (
            CLAIM_CEILING,
            ReferenceEvidenceError,
            parse_reference_evidence_json,
        )
        cls.export = staticmethod(to_reference_record)
        cls.parse = staticmethod(parse_reference_evidence_json)
        cls.error_type = ReferenceEvidenceError
        cls.ceiling = CLAIM_CEILING
        cls.translator = Translator(ROOT / "data")

    def bridge(self, phrase: str, direction: str):
        envelope = self.export(self.translator, phrase, direction)
        encoded = json.dumps(envelope, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return envelope, self.parse(encoded)

    def test_all_thirty_private_attestations_both_directions_public_parser(self):
        for row in self.translator.corpus:
            for direction, phrase in (("nt-en", row["orthography"]),
                                      ("en-nt", row["english"])):
                with self.subTest(id=row["id"], direction=direction):
                    envelope, parsed = self.bridge(phrase, direction)
                    self.assertEqual(parsed.evidence_class, "AUTHOR_ATTESTED_CORPUS")
                    self.assertEqual(parsed.claim_ceiling, self.ceiling)
                    self.assertIs(parsed.qualification_eligible, False)
                    self.assertIsNone(parsed.semantic_atoms)
                    self.assertEqual(parsed.origin_repo, "thebrazenbeard/num-ta-reen")
                    self.assertEqual(parsed.origin_commit,
                                     "cdfbea09cc8b4a1648cde733953986c7d694d496")
                    if row["id"] == "E26":
                        self.assertIsNone(parsed.target_text)
                        self.assertTrue(parsed.withheld)
                        self.assertIsNone(envelope["source_text"])

    def test_actual_jsonl_process_to_public_parser_sixty_records(self):
        requests = []
        for row in self.translator.corpus:
            for direction, phrase in (("nt-en", row["orthography"]),
                                      ("en-nt", row["english"])):
                requests.append(json.dumps({"direction": direction, "text": phrase},
                                           ensure_ascii=False, separators=(",", ":")))
        completed = subprocess.run(
            [sys.executable, "-m", "numtareen.interop"], cwd=ROOT,
            input="\n".join(requests) + "\n", capture_output=True,
            encoding="utf-8", timeout=15, check=False,
            env={**os.environ, "PYTHONNOUSERSITE": "1"},
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        frames = completed.stdout.splitlines()
        self.assertEqual(len(frames), 60)
        for index, line in enumerate(frames):
            with self.subTest(frame=index):
                wrapper = json.loads(line)
                self.assertIs(wrapper["ok"], True)
                self.assertIs(wrapper["record"]["qualification_eligible"], False)
                parsed = self.parse(json.dumps(wrapper["record"], ensure_ascii=False))
                self.assertEqual(parsed.evidence_class, "AUTHOR_ATTESTED_CORPUS")
                self.assertIsNone(parsed.semantic_atoms)

        public = subprocess.run(
            [sys.executable, "-m", "unvtrslr.reference_evidence_cli"],
            input=completed.stdout, capture_output=True, encoding="utf-8",
            cwd=Path(os.environ["UNVTRSLR_ROOT"]).resolve(),
            env={**os.environ,
                 "PYTHONPATH": str(Path(os.environ["UNVTRSLR_ROOT"]).resolve() / "src"),
                 "PYTHONNOUSERSITE": "1"},
            timeout=15, check=False,
        )
        self.assertEqual(public.returncode, 0, public.stderr)
        summary = json.loads(public.stdout)
        self.assertEqual(summary["status"], "REFERENCE_VALIDATION_COMPLETE_NOT_GROUNDED")
        self.assertEqual(summary["validated_records"], 60)
        self.assertEqual(summary["evidence_classes"], {"AUTHOR_ATTESTED_CORPUS": 60})
        self.assertIs(summary["qualification_eligible"], False)
        # The public CLI is aggregate-only; no source utterance crosses into
        # its logs or machine-readable status output.
        self.assertNotIn(self.translator.corpus[0]["orthography"], public.stdout)
        self.assertNotIn(self.translator.corpus[0]["english"], public.stdout)

    def test_unqualified_lexical_and_unknown_cross_import(self):
        for phrase, expected in (("nûm", "AUTHOR_LEXICON_GLOSS"),
                                 ("not-a-numtareen-word", "UNKNOWN"),
                                 ("nûm imaginary", "AUTHOR_PARTIAL_LEXICAL"),
                                 ("Nûm=sha", "AUTHOR_LEXICON_GLOSS")):
            with self.subTest(phrase=phrase):
                _, parsed = self.bridge(phrase, "nt-en")
                self.assertEqual(parsed.evidence_class, expected)
                self.assertIsNone(parsed.target_text)
                self.assertEqual(parsed.claim_ceiling, self.ceiling)

    def test_partial_lexical_material_preserves_loss_without_fluent_claim(self):
        envelope, parsed = self.bridge("nûm imaginary", "nt-en")
        self.assertEqual(parsed.evidence_class, "AUTHOR_PARTIAL_LEXICAL")
        self.assertIsNone(parsed.target_text)
        self.assertIs(parsed.qualification_eligible, False)
        self.assertIsNone(parsed.semantic_atoms)
        self.assertGreater(len(parsed.alternatives), 0)
        self.assertTrue(any("UNKNOWN" in warning or "PARTIAL" in warning
                            for warning in envelope["warnings"]))

    def test_forged_qualification_is_rejected_by_real_importer(self):
        envelope = self.export(self.translator, "Nûm ta=en ech.", "nt-en")
        envelope["qualification_eligible"] = True
        with self.assertRaises(self.error_type):
            self.parse(json.dumps(envelope).encode("utf-8"))

    def test_public_parser_rejects_unknown_status_mislabeling(self):
        envelope = self.export(self.translator, "not-a-numtareen-word", "nt-en")
        envelope["evidence_class"] = "AUTHOR_ATTESTED_CORPUS"
        with self.assertRaises(self.error_type):
            self.parse(json.dumps(envelope).encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
