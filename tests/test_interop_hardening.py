"""Malformed JSONL frames must not terminate a source-bound translation session."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from numtareen.engine import AmbiguityOverflowError, Translator
from numtareen.interop import handle_request


ROOT = Path(__file__).resolve().parents[1]


class InteropJsonlRecoveryTests(unittest.TestCase):
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
