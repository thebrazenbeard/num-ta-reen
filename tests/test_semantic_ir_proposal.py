"""Adversarial verification of noncanonical, source-bound semantic observations.

Run from a clean Num'ta'reen repository root via:
    python -m unittest discover -s tests -p 'test_semantic_ir_proposal.py' -v
For isolated staging, set NUMTAREEN_REPO_ROOT to an exact source checkout and
PYTHONPATH to the directory containing the research/ module.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from dataclasses import fields, replace
from pathlib import Path

from research.semantic_ir_proposal import (
    EVIDENCE, EXPECTED_CORPUS_GIT_BLOB_SHA1, GlossAtom, SCHEMA,
    analyze_attested, analyze_corpus_id, analyze_unverified_igt,
    load_verified_corpus, parse_igt_pairs, proposed_scope_expression,
    render_igt_pairs,
)


ROOT = Path(os.environ.get("NUMTAREEN_REPO_ROOT", Path(__file__).resolve().parents[1]))


def _pred_node(tree):
    while tree is not None and tree.get("op") != "PRED":
        tree = tree.get("argument")
    return tree


class SourceBoundSemanticIRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = load_verified_corpus(ROOT)

    def analyze(self, rid):
        return analyze_corpus_id(rid, repo_root=ROOT)

    def test_source_digest_frozen_and_thirty_entries(self):
        self.assertEqual(len(self.rows), 30)
        self.assertEqual(EXPECTED_CORPUS_GIT_BLOB_SHA1,
                         "53d9f27d03579a1a3fc700c3394b56f834da784e")

    def test_verified_packet_is_rederived_before_scope_and_dataclass_forgery_fails(self):
        source = self.analyze("E01")
        self.assertEqual(proposed_scope_expression(source)["op"], "EVID.WIT")
        for label, forged in (
            ("false cross-echo verification", replace(source, evidentials=("EVID.VRF",))),
            ("new echo", replace(source, echo_operators=("LOOP",))),
            ("changed participant role", replace(source, arguments=())),
            ("forged consent", replace(source, consent_locations=(0,))),
            ("fabricated focus", replace(source, discourse=("0:FOC",))),
            ("changed corpus identifier", replace(source, corpus_id="E08")),
            ("changed source atoms", replace(source, atoms=source.atoms[:-1])),
        ):
            with self.subTest(label=label):
                self.assertEqual(forged.evidence, EVIDENCE)
                self.assertIsNone(proposed_scope_expression(forged))
                with self.assertRaisesRegex(ValueError, "differs from pinned"):
                    forged.to_dict(repo_root=ROOT)
        self.assertEqual(source.to_dict(repo_root=ROOT)["evidence"], EVIDENCE)

    def test_verified_tree_and_serializer_never_use_caller_string_subclasses(self):
        # JSON compares the stored Unicode value, but Python methods can lie
        # about its display or parsing semantics. Authentication must include
        # a fresh canonical object as the *source* of the returned output.
        class DisplayLie(str):
            def __str__(self):
                return "EVID.VRF"

            def __repr__(self):
                return "EVID.VRF"

        class SplitLie(str):
            def split(self, *args, **kwargs):
                return ["cross"]

        class EqualityLie(str):
            def __eq__(self, other):
                return False

        source = self.analyze("E01")
        forged_evidential = replace(source, evidentials=(DisplayLie("EVID.WIT"),))
        rendered = proposed_scope_expression(forged_evidential, repo_root=ROOT)
        self.assertEqual(type(rendered["op"]), str)
        self.assertEqual(str(rendered["op"]), "EVID.WIT")
        serialized = forged_evidential.to_dict(repo_root=ROOT)
        self.assertEqual(type(serialized["evidentials"][0]), str)
        self.assertEqual(str(serialized["evidentials"][0]), "EVID.WIT")

        forged_predicate = replace(
            source,
            predicates=(replace(source.predicates[0], gloss=SplitLie("align")),),
        )
        tree = proposed_scope_expression(forged_predicate, repo_root=ROOT)
        self.assertEqual(_pred_node(tree)["gloss"], "align")
        self.assertEqual(type(forged_predicate.to_dict(repo_root=ROOT)["predicates"][0]["gloss"]), str)

        # A fake equality method must not turn an authored-evidence packet
        # into a freely serializable unverified result.
        forged_label = replace(source, evidence=EqualityLie(EVIDENCE),
                               evidentials=("EVID.VRF",))
        with self.assertRaisesRegex(ValueError, "differs from pinned"):
            forged_label.to_dict(repo_root=ROOT)

    def test_nested_mutation_and_withheld_id_cannot_launder_source(self):
        consent = self.analyze("E18")
        changed_argument = replace(consent.arguments[0], consent_marked=False)
        self.assertIsNone(proposed_scope_expression(
            replace(consent, arguments=(changed_argument,))))
        protected = self.analyze("E26")
        fabricated = replace(self.analyze("E01"), corpus_id="E26")
        self.assertTrue(protected.withheld)
        self.assertIsNone(proposed_scope_expression(protected))
        self.assertIsNone(proposed_scope_expression(fabricated))
        self.assertTrue(protected.to_dict(repo_root=ROOT)["withheld"])
        with self.assertRaisesRegex(ValueError, "differs from pinned"):
            fabricated.to_dict(repo_root=ROOT)

    def test_public_packet_serializer_blocks_forged_protected_atoms(self):
        source = self.analyze("E01")
        fake = replace(source, atoms=(GlossAtom(0, "⟦synthetic⟧", "M", ()),))
        with self.assertRaisesRegex(ValueError, "protected"):
            fake.to_dict(repo_root=ROOT)
        unprotected = replace(source, atoms=(GlossAtom(0, "invented", "M", ()),))
        with self.assertRaisesRegex(ValueError, "differs from pinned"):
            unprotected.to_dict(repo_root=ROOT)

    def test_equality_spoof_and_non_json_fields_cannot_bypass_source_check(self):
        source = self.analyze("E01")

        class EqualitySpoof(type(source)):
            def __eq__(self, other):
                return True

        mutated = {field.name: getattr(source, field.name)
                   for field in fields(type(source))}
        mutated["evidentials"] = ("EVID.VRF",)
        spoof = EqualitySpoof(**mutated)
        self.assertTrue(spoof == source)  # The exact anti-pattern under test.
        self.assertIsNone(proposed_scope_expression(spoof))
        with self.assertRaisesRegex(ValueError, "exact SemanticPacket"):
            spoof.to_dict(repo_root=ROOT)

        invalid = replace(source, evidentials=(object(),))
        self.assertIsNone(proposed_scope_expression(invalid))
        with self.assertRaisesRegex(ValueError, "unsupported non-JSON"):
            invalid.to_dict(repo_root=ROOT)

    def test_scope_requires_the_pinned_corpus_at_time_of_use(self):
        source = self.analyze("E01")
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "data").mkdir()
            raw = (ROOT / "data" / "corpus.json").read_bytes()
            (folder / "data" / "corpus.json").write_bytes(raw + b" ")
            self.assertIsNone(proposed_scope_expression(source, repo_root=folder))
        self.assertIsNone(proposed_scope_expression(source, repo_root=Path("/nonexistent-numtareen-root")))
        self.assertIsNone(proposed_scope_expression(None))

    def test_all_unprotected_igt_roundtrip_without_reinterpreting(self):
        for rid, record in self.rows.items():
            if rid == "E26":
                continue
            with self.subTest(rid=rid):
                atoms = parse_igt_pairs(record["igt"])
                self.assertEqual(render_igt_pairs(atoms), " ".join(record["igt"].split()))
                self.assertEqual(self.analyze(rid).atoms, atoms)

    def test_forged_e01_igt_cannot_claim_attestation(self):
        forged = dict(self.rows["E01"])
        forged["igt"] = "bogus align x 2=PAT y EVID.WIT"
        with self.assertRaisesRegex(ValueError, "not identical"):
            analyze_attested(forged, repo_root=ROOT)
        with self.assertRaisesRegex(ValueError, "not identical"):
            analyze_attested({"id": "E01", "igt": self.rows["E01"]["igt"]}, repo_root=ROOT)
        self.assertEqual(self.analyze("E01").evidence, EVIDENCE)
        self.assertEqual(self.analyze("E01").schema, SCHEMA)
        self.assertFalse(self.analyze("E01").qualification_eligible)

    def test_caller_string_equality_override_cannot_spoof_author_igt(self):
        class AlwaysEqualText(str):
            def __eq__(self, other):
                return True

            __hash__ = str.__hash__

        source = self.rows["E01"]
        forged = dict(source)
        forged["igt"] = AlwaysEqualText("bogus align x 2=PAT y EVID.WIT")
        self.assertEqual(forged, source)  # A naive dict equality would accept.
        with self.assertRaisesRegex(ValueError, "not identical"):
            analyze_attested(forged, repo_root=ROOT)

    def test_tampered_corpus_bytes_fail_digest_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "data").mkdir()
            raw = (ROOT / "data" / "corpus.json").read_bytes()
            (folder / "data" / "corpus.json").write_bytes(raw + b" ")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_verified_corpus(folder)

    def test_unverified_gloss_does_not_elevate_to_attested(self):
        hypothesis = analyze_unverified_igt("nûm align ta=en 2=PAT ech EVID.WIT")
        self.assertEqual(hypothesis.corpus_id, "UNVERIFIED")
        self.assertEqual(hypothesis.evidence, "UNVERIFIED_SYNTHETIC_GLOSS")
        self.assertFalse(hypothesis.qualification_eligible)

    def test_unknown_tags_even_on_known_atoms_fail_closed(self):
        baseline = analyze_unverified_igt("nûm align ta=en 2=PAT ech EVID.WIT")
        modified = analyze_unverified_igt(
            "nûm align=FUTURE ta=en 2=PAT=INVENTED ech EVID.WIT")
        self.assertEqual(baseline.unmapped_atoms, ())
        self.assertEqual(modified.unmapped_atoms, (0, 1))
        self.assertIsNone(proposed_scope_expression(baseline))
        self.assertIsNone(proposed_scope_expression(modified))

    def test_e01_simple_witnessed_patient(self):
        ir = self.analyze("E01")
        self.assertEqual([x.gloss for x in ir.predicates], ["align"])
        self.assertEqual([(a.referent_gloss, a.role) for a in ir.arguments], [("2", "PAT")])
        self.assertEqual(ir.evidentials, ("EVID.WIT",))
        self.assertEqual(ir.echo_operators, ())
        self.assertEqual(proposed_scope_expression(ir)["op"], "EVID.WIT")

    def test_e02_e03_preserve_argument_order_without_claimed_focus(self):
        left, right = self.analyze("E02"), self.analyze("E03")
        self.assertEqual([a.role for a in left.arguments], ["AGT", "PAT"])
        self.assertEqual([a.role for a in right.arguments], ["PAT", "AGT"])
        self.assertEqual({a.role for a in left.arguments}, {a.role for a in right.arguments})

    def test_e01_vs_e05_focus_is_not_lost(self):
        plain = _pred_node(proposed_scope_expression(self.analyze("E01")))
        focused = _pred_node(proposed_scope_expression(self.analyze("E05")))
        self.assertEqual(plain["discourse"], [])
        self.assertEqual(focused["discourse"][0]["kind"], "FOC")
        self.assertNotEqual(plain, focused)

    def test_e04_topic_boundary_is_preserved(self):
        packet = self.analyze("E04")
        tree = _pred_node(proposed_scope_expression(packet))
        self.assertEqual(packet.discourse, ("0:TOP",))
        self.assertEqual(tree["discourse"][0]["kind"], "TOP")
        self.assertEqual(tree["discourse"][0]["gloss"], "boundary=TOP")

    def test_e08_question_and_e15_loop_are_tentative(self):
        question = proposed_scope_expression(self.analyze("E08"))
        self.assertEqual(question["op"], "Q")
        self.assertEqual(question["argument"]["op"], "EVID.WIT")
        loop = proposed_scope_expression(self.analyze("E15"))
        self.assertEqual((loop["op"], loop["argument"]["op"]), ("EVID.WIT", "LOOP"))

    def test_e18_predicate_and_argument_consent_are_distinct(self):
        ir = self.analyze("E18")
        self.assertEqual(ir.consent_locations, (0, 1))
        self.assertEqual([(a.role, a.consent_marked) for a in ir.arguments], [("PAT", True)])
        self.assertTrue(_pred_node(proposed_scope_expression(ir))["predicate_consent"])

    def test_e19_negation_and_e20_role_assignments(self):
        ir = self.analyze("E19")
        self.assertEqual(ir.polarity, ("NEG",))
        self.assertEqual(proposed_scope_expression(ir)["argument"]["op"], "NEG")
        self.assertEqual([a.role for a in self.analyze("E20").arguments], ["AGT", "GOAL"])

    def test_known_source_conflicts_block_tree(self):
        for rid, name in (("E13", "RELATIVIZER_FORM_CONFLICT"),
                          ("E23", "RHEL_FUNCTION_CONFLICT")):
            packet = self.analyze(rid)
            self.assertIn(name, packet.unresolved_conflicts)
            self.assertIsNone(proposed_scope_expression(packet))

    def test_unattested_operator_stacking_is_refused(self):
        synthetic = analyze_unverified_igt(
            "qir LOOP ruun RET nûm align ta=en 2=PAT ech EVID.WIT reen EVID.VRF")
        self.assertEqual(len(synthetic.echo_operators), 2)
        self.assertEqual(len(synthetic.evidentials), 2)
        self.assertIsNone(proposed_scope_expression(synthetic))

    def test_multi_clause_fails_closed(self):
        self.assertIsNone(proposed_scope_expression(self.analyze("E12")))
        self.assertIsNone(proposed_scope_expression(self.analyze("E30")))

    def test_e26_all_public_parser_entrypoints_guard_notation(self):
        packet = self.analyze("E26")
        self.assertTrue(packet.withheld)
        self.assertEqual(packet.atoms, ())
        self.assertIsNone(proposed_scope_expression(packet))
        serialized = json.dumps(packet.to_dict(), ensure_ascii=False)
        self.assertNotIn("⟦", serialized)
        self.assertNotIn("⟧", serialized)
        with self.assertRaisesRegex(ValueError, "protected"):
            parse_igt_pairs(self.rows["E26"]["igt"])
        with self.assertRaisesRegex(ValueError, "protected"):
            render_igt_pairs((GlossAtom(0, "⟦protected⟧", "NOTATION", ()),))

    def test_invalid_igt_rejected(self):
        with self.assertRaisesRegex(ValueError, "paired"):
            parse_igt_pairs("nûm align ech")
        with self.assertRaisesRegex(ValueError, "conflicting role"):
            analyze_unverified_igt("nûm align ta=en 2=PAT=AGT")


if __name__ == "__main__":
    unittest.main()
