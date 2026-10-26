"""Malformed JSONL frames must not terminate a source-bound translation session."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from numtareen.engine import AmbiguityOverflowError, Translator
from numtareen.interop import _lexical_alternatives, handle_request, to_reference_record


ROOT = Path(__file__).resolve().parents[1]


class InteropJsonlRecoveryTests(unittest.TestCase):
    def test_total_budget_counts_every_analysis_across_segmented_tokens(self):
        # The engine's Cartesian expansion may return six distinct analyses
        # for each token. The wire budget applies to their sum, not each token.
        matches = [{"segmentation": [{"headword": f"synthetic-stem-{s}"},
                                     {"headword": f"=synthetic-clitic-{c}"}]}
                   for s in range(2) for c in range(3)]
        lexical_part = {"kind": "lexical", "token": "synthetic", "matches": matches}
        in_budget = {"parts": [lexical_part] * 10}
        over_budget = {"parts": [lexical_part] * 11}
        self.assertEqual(len(_lexical_alternatives(in_budget, "nt-en")), 60)
        with self.assertRaises(AmbiguityOverflowError):
            _lexical_alternatives(over_budget, "nt-en")

    def test_total_reference_alternative_budget_is_bounded_across_tokens(self):
        translator = Translator()
        at_limit = " ".join(["nûm=en"] * 64)
        over_limit = " ".join(["nûm=en"] * 65)

        allowed = to_reference_record(translator, at_limit, direction="nt-en")
        self.assertEqual(len(allowed["alternatives"]), 64)
        self.assertFalse(allowed["qualification_eligible"])
        self.assertTrue(all(candidate["kind"] == "lexical_segmentation"
                            for candidate in allowed["alternatives"]))

        with self.assertRaises(AmbiguityOverflowError):
            to_reference_record(translator, over_limit, direction="nt-en")

        request = {"request_id": "total-limit", "direction": "nt-en", "text": over_limit}
        response = handle_request(translator, request)
        self.assertFalse(response["ok"])
        self.assertEqual(response["request_id"], "total-limit")
        self.assertEqual(response["error"]["code"], "AMBIGUITY_LIMIT")
        recovered = handle_request(translator, {"direction": "nt-en", "text": at_limit})
        self.assertTrue(recovered["ok"])
        self.assertEqual(len(recovered["record"]["alternatives"]), 64)

    def test_ambiguity_limit_is_not_reported_as_invalid_text_and_recovers(self):
        translator = Translator()
        request = {"request_id": "overflow", "direction": "nt-en", "text": "nûm=en"}
        with patch("numtareen.interop.to_reference_record",
                   side_effect=AmbiguityOverflowError("segmentation analysis limit exceeded")):
            response = handle_request(translator, request)
        self.assertFalse(response["ok"])
        self.assertEqual(response["error"]["code"], "AMBIGUITY_LIMIT")
        self.assertEqual(response["request_id"], "overflow")
        recovered = handle_request(translator, {"direction": "nt-en", "text": "Nûm ta=en ech."})
        self.assertTrue(recovered["ok"])
        self.assertEqual(recovered["record"]["evidence_class"], "AUTHOR_ATTESTED_CORPUS")

    def test_deep_nesting_duplicate_members_and_nan_do_not_kill_session(self):
        # All four frames are comfortably below the 65,536-byte request cap.
        malicious = [
            ("[" * 12000 + "0" + "]" * 12000).encode("ascii"),
            b'{"direction":"nt-en","direction":"en-nt","text":"unknown"}',
            b'{"direction":"nt-en","text":"unknown","extra":NaN}',
        ]
        valid = json.dumps(
            {"request_id": "after-errors", "direction": "nt-en", "text": "Nûm ta=en ech."},
            ensure_ascii=False,
        ).encode("utf-8")
        process = subprocess.run(
            [sys.executable, "-m", "numtareen.interop"],
            input=b"\n".join([*malicious, valid]) + b"\n",
            cwd=ROOT,
            capture_output=True,
            timeout=15,
            check=False,
        )

        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8", "replace"))
        self.assertEqual(process.stderr, b"")
        responses = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(len(responses), 4)
        for response in responses[:3]:
            self.assertIs(response["ok"], False)
            self.assertEqual(response["error"]["code"], "MALFORMED_JSON")
        self.assertIs(responses[3]["ok"], True)
        self.assertEqual(responses[3]["request_id"], "after-errors")
        self.assertEqual(responses[3]["record"]["evidence_class"], "AUTHOR_ATTESTED_CORPUS")
        self.assertIs(responses[3]["record"]["qualification_eligible"], False)


if __name__ == "__main__":
    unittest.main()
