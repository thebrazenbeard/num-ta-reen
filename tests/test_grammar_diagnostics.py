"""Source-constrained structural observations, not generated grammar or translation."""

import unittest

from numtareen.engine import DataError, Translator
from numtareen.grammar_diagnostics import diagnose


class GrammarDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.translator = Translator()
        cls.sentences = {row["id"]: row["orthography_index"] for row in cls.translator.corpus}

    def observe(self, entry_id):
        return diagnose(self.sentences[entry_id], translator=self.translator)

    @staticmethod
    def observations(result, marker):
        return [item for item in result["observations"] if item["marker"] == marker]

    def test_reordered_agent_patient_are_both_observed_without_a_parse_verdict(self):
        early_agent = self.observe("E02")
        early_patient = self.observe("E03")
        self.assertEqual([o["marker"] for o in early_agent["observations"] if o["kind"] == "role"],
                         ["=ka", "=en"])
        self.assertEqual([o["marker"] for o in early_patient["observations"] if o["kind"] == "role"],
                         ["=en", "=ka"])
        for result in (early_agent, early_patient):
            self.assertEqual(result["grammar_verdict"], None)
            self.assertEqual(result["semantic_atoms"], None)
            self.assertIs(result["qualification_eligible"], False)
            self.assertEqual(len(self.observations(result, "ech")), 1)

    def test_role_hosts_from_corpus_do_not_claim_nonexistent_dictionary_lines(self):
        result = self.observe("E02")
        for host in ("na", "ta"):
            item = self.observations(result, host)[0]
            self.assertEqual(item["kind"], "attested_argument_host")
            self.assertEqual(item["dictionary_source_lines"], [])
            self.assertEqual(item["source_authority"], "AUTHOR_ATTESTED_CORPUS_E02_E03")

    def test_initial_loop_operator_keeps_position_and_evidential_separate(self):
        result = self.observe("E15")
        loop = self.observations(result, "qir")
        self.assertEqual(len(loop), 1)
        self.assertEqual(loop[0]["token_index"], 0)
        self.assertEqual(loop[0]["kind"], "echo_operator")
        self.assertEqual(self.observations(result, "ech")[0]["kind"], "evidential")

    def test_consent_markers_keep_distinct_hosts(self):
        result = self.observe("E18")
        consent = self.observations(result, "=uth")
        self.assertEqual([(x["host"], x["token_index"]) for x in consent],
                         [("Vahl", 0), ("ta", 1)])
        self.assertEqual(self.observations(result, "=en")[0]["host"], "ta")
        self.assertEqual(result["warnings"], [])

    def test_field_alarm_does_not_require_an_evidential(self):
        result = self.observe("E17")
        self.assertEqual(len(self.observations(result, "ta’qesh")), 1)
        self.assertEqual(self.observations(result, "ta’qesh")[0]["kind"], "prohibition")
        self.assertNotIn("MISSING_EVIDENTIAL", result["warnings"])
        self.assertFalse(result["unknown_tokens"])

    def test_source_disagreements_are_explicit_not_silently_disambiguated(self):
        relative = self.observe("E13")
        restored = self.observe("E23")
        self.assertIn("RELATIVIZER_FORM_CONFLICT",
                      [x["code"] for x in relative["source_conflicts"]])
        self.assertIn("RHEL_FUNCTION_CONFLICT",
                      [x["code"] for x in restored["source_conflicts"]])
        for result in (relative, restored):
            self.assertEqual(result["grammar_verdict"], None)
            self.assertFalse(any(o.get("meaning") == "authoritatively parsed"
                                 for o in result["observations"]))

    def test_protected_true_name_chord_is_fully_withheld(self):
        result = self.observe("E26")
        self.assertIs(result["withheld"], True)
        self.assertIsNone(result["source_text"])
        self.assertEqual(result["observations"], [])
        self.assertEqual(result["unknown_tokens"], [])
        self.assertNotIn("61", repr(result))
        self.assertNotIn("113", repr(result))
        english = self.translator.corpus[25]["english"]
        translated = diagnose(english, translator=self.translator)
        self.assertIs(translated["withheld"], True)
        self.assertIsNone(translated["source_text"])

    def test_marked_contact_loan_keeps_goal_role_and_uncertainty(self):
        result = self.observe("E28")
        goals = self.observations(result, "=va")
        self.assertEqual(len(goals), 1)
        self.assertEqual(goals[0]["host"], "‹airlock›")
        self.assertTrue(any(u["token"] == "‹airlock›" and u["kind"] == "marked_loan"
                            for u in result["unknown_tokens"]))
        self.assertEqual(result["grammar_verdict"], None)

    def test_coercion_caution_not_proof(self):
        without = self.observe("E07")
        with_consent = self.observe("E18")
        self.assertIn("POSSIBLE_COERCION_IMPLICATURE", without["warnings"])
        self.assertNotIn("POSSIBLE_COERCION_IMPLICATURE", with_consent["warnings"])
        self.assertEqual(without["grammar_verdict"], None)

    def test_unknown_and_bounds_are_explicit(self):
        result = diagnose("nûm zzzsynthetic ech", translator=self.translator)
        self.assertIn({"token_index": 1, "token": "zzzsynthetic", "kind": "unknown"},
                      result["unknown_tokens"])
        with self.assertRaisesRegex(ValueError, "length"):
            diagnose("a" * 4097, translator=self.translator)
        with self.assertRaisesRegex(ValueError, "token"):
            diagnose(" ".join(["nûm"] * 129), translator=self.translator)
        with self.assertRaisesRegex(ValueError, "segment"):
            diagnose("nûm" + "=en" * 17, translator=self.translator)

    def test_mutable_indexes_cannot_forge_dictionary_provenance(self):
        forged = {
            "headword": "invented_marker", "gloss": "fake", "category": "CLITIC",
            "register": "CF/FC", "taboo": "NONE", "ipa": "/x/", "source_line": 12345,
        }
        for index in ("words", "glosses", "sentences"):
            with self.subTest(index=index):
                tampered = Translator()
                if index == "sentences":
                    tampered.sentences["nt-en"]["invented_marker"].append(
                        dict(tampered.corpus[0]))
                else:
                    getattr(tampered, index)["invented_marker"].append(forged)
                with self.assertRaises(DataError):
                    diagnose("invented_marker", translator=tampered)

    def test_mutable_canonical_rows_cannot_change_e26_withholding(self):
        english = next(row["english"] for row in self.translator.corpus
                       if row["id"] == "E26")
        tampered = Translator()
        tampered.corpus[:] = [row for row in tampered.corpus if row["id"] != "E26"]
        with self.assertRaises(DataError):
            diagnose(english, translator=tampered)
        tampered = Translator()
        tampered.lexicon[0]["headword"] = "invented_marker"
        with self.assertRaises(DataError):
            diagnose("invented_marker", translator=tampered)

    def test_default_translator_uses_pinned_source(self):
        self.assertTrue(diagnose(self.sentences["E26"])["withheld"])


if __name__ == "__main__":
    unittest.main()
