"""Black-box checks of the documented offline Python CLI contract.

This deliberately exercises a subprocess rather than importing translator internals:
the README promises that a clean clone can run ``python -m numtareen``.
"""

import base64
import json
import os
import subprocess
import sys
import unicodedata
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS = json.loads((ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))
RECORDS = {item["id"]: item for item in CORPUS["records"]}


def run_cli(*args, input_text=None):
    # A locale-independent subprocess contract matters for PowerShell and piping.
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "numtareen", *args],
        cwd=ROOT,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        env=env,
        check=False,
        timeout=10,
    )


class CliContractTests(unittest.TestCase):
    def test_attested_numtareen_to_english(self):
        source = RECORDS["E01"]
        proc = run_cli("--direction", "nt-en", "--text", source["orthography"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(source["english"], proc.stdout)

    def test_attested_english_to_numtareen(self):
        source = RECORDS["E17"]
        proc = run_cli("--direction", "en-nt", "--text", source["english"])
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(source["orthography"], proc.stdout)

    def test_equivalent_unicode_normalization(self):
        source = RECORDS["E01"]
        decomposed = unicodedata.normalize("NFD", source["orthography"])
        self.assertNotEqual(decomposed, source["orthography"])
        proc = run_cli("--direction", "nt-en", "--text", decomposed)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(source["english"], proc.stdout)

    def test_utf8_base64_text_transport(self):
        source = RECORDS["E01"]
        encoded = base64.b64encode(source["orthography"].encode("utf-8")).decode("ascii")
        proc = run_cli("--direction", "nt-en", "--text-base64", encoded)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(source["english"], proc.stdout)

    def test_malformed_base64_transport_is_error(self):
        proc = run_cli("--direction", "nt-en", "--text-base64", "not-valid!base64")
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("No module named", proc.stderr)

    def test_unknown_text_is_not_reported_as_fluent_translation(self):
        proc = run_cli("--direction", "nt-en", "--text", "__unattested_token_4829__")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertRegex(proc.stdout.lower(), r"unknown|unattested|incomplete")
        self.assertNotIn("attested sentence", proc.stdout.lower())

    def test_unknown_policy_error_returns_nonzero(self):
        proc = run_cli(
            "--direction", "nt-en", "--unknown", "error",
            "--text", "__unattested_token_4829__",
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("No module named", proc.stderr)

    def test_invalid_direction_fails(self):
        proc = run_cli("--direction", "not-a-direction", "--text", "Nûm")
        self.assertNotEqual(proc.returncode, 0)
        self.assertNotIn("No module named", proc.stderr)
        self.assertRegex(proc.stderr.lower(), r"direction|invalid choice")

    def test_interactive_direction_switching(self):
        proc = run_cli(
            "--direction", "nt-en", "--interactive",
            input_text=":direction en-nt\nStop. Do not proceed.\n:quit\n",
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn(RECORDS["E17"]["orthography"], proc.stdout)


if __name__ == "__main__":
    unittest.main()
