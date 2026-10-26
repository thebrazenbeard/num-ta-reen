"""Explicit ASCII JSONL text transport for legacy PowerShell and hostile Unicode."""

from __future__ import annotations

import base64
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from numtareen import Translator
from numtareen.engine import DataError
from numtareen.interop import handle_request


ROOT = Path(__file__).resolve().parents[1]


def encoded_request(text: str, direction: str = "nt-en") -> bytes:
    # Mirrors the PS5.1 transport: fixed ASCII JSON with only strict Base64
    # bytes interpolated; no shell-dependent JSON character escaping.
    value = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f'{{"direction":"{direction}","text_base64":"{value}"}}'.encode("ascii")


class JsonlBase64TransportTests(unittest.TestCase):
    def run_frames(self, frames: list[bytes]) -> list[dict]:
        completed = subprocess.run(
            [sys.executable, "-m", "numtareen.interop"],
            input=b"\n".join(frames) + b"\n",
            cwd=ROOT,
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", "replace"))
        self.assertEqual(completed.stderr, b"")
        return [json.loads(line) for line in completed.stdout.splitlines()]

    def test_original_text_and_ascii_base64_modes_agree_with_attested_source(self):
        utterance = Translator().corpus[0]
        original = json.dumps({"direction": "nt-en", "text": utterance["orthography_index"]},
                              ensure_ascii=False).encode("utf-8")
        records = self.run_frames([original, encoded_request(utterance["orthography_index"])])
        self.assertEqual(len(records), 2)
        self.assertTrue(all(row["ok"] for row in records))
        self.assertEqual(records[0]["record"], records[1]["record"])
        self.assertEqual(records[1]["record"]["origin"]["record_id"], utterance["id"])
        self.assertIs(records[1]["record"]["qualification_eligible"], False)

    def test_true_name_chord_utf8_base64_is_attested_but_withheld(self):
        utterance = next(row for row in Translator().corpus if row["id"] == "E26")
        records = self.run_frames([
            encoded_request(utterance["orthography_index"], "nt-en"),
            encoded_request(utterance["english"], "en-nt"),
        ])
        self.assertEqual(len(records), 2)
        for item in records:
            with self.subTest(direction=item["record"]["direction"]):
                self.assertIs(item["ok"], True)
                row = item["record"]
                self.assertEqual(row["evidence_class"], "AUTHOR_ATTESTED_CORPUS")
                self.assertEqual(row["origin"]["record_id"], "E26")
                self.assertIs(row["withheld"], True)
                self.assertIsNone(row["source_text"])
                self.assertIsNone(row["target_text"])
                self.assertEqual(row["alternatives"], [])
                self.assertIs(row["learner_visible"], False)
                self.assertIs(row["qualification_eligible"], False)

    def test_unicode_quotation_and_nonbmp_survive_ascii_transport(self):
        text = 'unattested "quoted" 🚀 nûm'
        row, = self.run_frames([encoded_request(text)])
        self.assertIs(row["ok"], True)
        self.assertEqual(row["record"]["source_text"], text)
        self.assertIsNone(row["record"]["target_text"])

    def test_malformed_b64_and_mutually_exclusive_fields_recover(self):
        bad = [
            b'{"direction":"nt-en","text_base64":"!!!!"}',
            b'{"direction":"nt-en","text_base64":"/w=="}',  # invalid UTF-8
            b'{"direction":"nt-en","text_base64":"YQ==","text":"a"}',
            b'{"direction":"nt-en"}',
            b'{"direction":"nt-en","text_base64":"' + b"QQ==" * 6000 + b'"}',
        ]
        valid = encoded_request(Translator().corpus[0]["orthography_index"])
        rows = self.run_frames([*bad, valid])
        self.assertEqual(len(rows), 6)
        self.assertEqual([r["ok"] for r in rows], [False] * 5 + [True])
        self.assertEqual([r["error"]["code"] for r in rows[:5]],
                         ["INVALID_TEXT_ENCODING", "INVALID_TEXT_ENCODING",
                          "INVALID_REQUEST", "INVALID_REQUEST", "INVALID_TEXT_ENCODING"])

    def test_single_leading_utf8_bom_is_accepted_on_each_jsonl_frame(self):
        # Windows PowerShell 5.1/.NET Framework stream writers may emit a
        # UTF-8 signature before the first byte of a JSONL request. A single
        # signature at byte zero of any frame is transport decoration only.
        valid = encoded_request(Translator().corpus[0]["orthography_index"])
        rows = self.run_frames([b"\xef\xbb\xbf" + valid, valid, b"\xef\xbb\xbf" + valid])
        self.assertEqual(len(rows), 3)
        self.assertTrue(all(row["ok"] for row in rows))
        self.assertEqual(rows[0]["record"], rows[1]["record"])
        self.assertEqual(rows[2]["record"], rows[1]["record"])

    def test_bom_tolerance_is_start_only_and_strict(self):
        valid = encoded_request(Translator().corpus[0]["orthography_index"])
        malformed = [
            b"\xef\xbb\xbf\xef\xbb\xbf" + valid,  # double signature
            valid[:1] + b"\xef\xbb\xbf" + valid[1:],  # interior signature
            b"\xef\xbb\xbf" + valid.replace(b'"direction"', b'"direction" : "nt-en", "direction"'),
            b"\xef\xbb\xbf" + b"\xff" + valid,  # invalid UTF-8
        ]
        rows = self.run_frames([*malformed, valid])
        self.assertEqual(len(rows), 5)
        self.assertEqual([row["ok"] for row in rows], [False] * 4 + [True])
        self.assertEqual([row["error"]["code"] for row in rows[:4]], ["MALFORMED_JSON"] * 4)

    def test_data_error_reports_source_failure_not_invalid_text(self):
        # DataError subclasses ValueError, so catch ordering is observable.
        request = {"direction": "nt-en", "text": "known"}
        with patch("numtareen.interop.to_reference_record", side_effect=DataError("corrupt source")):
            response = handle_request(Translator(), request)
        self.assertEqual(response["error"]["code"], "SOURCE_DATA_ERROR")


if __name__ == "__main__":
    unittest.main()
