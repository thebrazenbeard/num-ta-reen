"""Independent source-attested PowerShell UTF-8 bridge acceptance tests.

The isolated worker checkout can point at canonical sources with
NUMTAREEN_REPO_ROOT; in the merged repository, the default is its root.
"""

import base64
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


PROPOSAL_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(os.environ.get("NUMTAREEN_REPO_ROOT", PROPOSAL_ROOT)).resolve()
SCRIPT = PROPOSAL_ROOT / "scripts" / "phonetic_cli.py"
CORPUS = json.loads((REPO_ROOT / "data" / "corpus.json").read_text(encoding="utf-8"))
ROWS = {row["id"]: row for row in CORPUS["records"]}


def invoke(text=None, *, encoded=None, encoding="utf-8"):
    if encoded is None:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = encoding
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--repo-root", str(REPO_ROOT),
         "--text-base64=" + encoded],
        cwd=REPO_ROOT, env=env, capture_output=True, encoding=encoding,
        errors="strict", timeout=10, check=False,
    )


class PhoneticBase64TransportTests(unittest.TestCase):
    def test_attested_utterance_roundtrip_and_exact_evidence(self):
        record = ROWS["E01"]
        p = invoke(record["orthography"])
        self.assertEqual(p.returncode, 0, p.stderr)
        result = json.loads(p.stdout)
        self.assertEqual(result["status"], "ATTESTED_UTTERANCE")
        self.assertEqual(result["source_locator"], "E01")
        self.assertEqual(result["ipa"], record["ipa"])
        self.assertIsNone(result["scope_or_resonance_frequency_hz"])

    def test_source_attested_lexeme_no_connected_speech_claim(self):
        p = invoke("veyl")
        self.assertEqual(p.returncode, 0, p.stderr)
        x = json.loads(p.stdout)
        self.assertEqual(x["status"], "ATTESTED_LEXEME")
        self.assertIn("does not establish", " ".join(x["caution"]))

    def test_quoted_unicode_nonbmp_unknown_is_never_fluent(self):
        phrase = 'unattested "quoted" nûm 🚀\nnever before observed'
        p = invoke(phrase)
        self.assertEqual(p.returncode, 2, p.stderr)
        x = json.loads(p.stdout)
        self.assertEqual(x["status"], "UNKNOWN")
        self.assertIsNone(x["ipa"])
        self.assertNotIn(phrase, p.stdout)

    def test_multiline_utterance_retains_attested_pronunciation(self):
        record = ROWS["E27"]
        p = invoke(record["orthography"])
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["ipa"], record["ipa"])

    def test_e26_source_guard_no_chord_or_ipa_output(self):
        source = ROWS["E26"]["orthography"]
        for text in (source, "E26"):
            with self.subTest(variant="real" if text == source else "id"):
                p = invoke(text)
                self.assertEqual(p.returncode, 2)
                result = json.loads(p.stdout)
                self.assertEqual(result["status"], "WITHHELD")
                self.assertIsNone(result["ipa"])
                self.assertNotIn(source, p.stdout + p.stderr)

    def test_malformed_utf8_and_base64_rejected_without_echo(self):
        for encoded in ("not+valid?", base64.b64encode(b"\xff").decode("ascii"),
                        "A" * 11000):
            with self.subTest(encoded_length=len(encoded)):
                p = invoke(encoded=encoded)
                self.assertEqual(p.returncode, 1)
                self.assertEqual(p.stdout, "")
                self.assertNotIn(encoded, p.stderr)

    def test_cp1252_stdout_is_ascii_json_round_trip(self):
        p = invoke(ROWS["E01"]["orthography"], encoding="cp1252")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(p.stdout.isascii())
        self.assertEqual(json.loads(p.stdout)["ipa"], ROWS["E01"]["ipa"])

    def _shell(self, name):
        """One executable per test: no PS7 success can substitute for PS5.1.

        Local non-Windows hosts can skip absent shells, while CI sets
        NUMTAREEN_REQUIRE_SHELLS=pwsh,powershell and fails on omissions.
        """
        required = {part.strip().lower() for part in
                    os.environ.get("NUMTAREEN_REQUIRE_SHELLS", "").split(",")
                    if part.strip()}
        unknown = required.difference({"pwsh", "powershell"})
        if unknown:
            self.fail("Invalid NUMTAREEN_REQUIRE_SHELLS configuration")
        shell = shutil.which(name)
        if shell is None:
            if name in required:
                self.fail("Required native PowerShell executable missing: " + name)
            self.skipTest("Native PowerShell executable unavailable: " + name)
        return shell

    def _assert_native_attested(self, shell_name):
        shell = self._shell(shell_name)
        script = str(PROPOSAL_ROOT / "scripts" / "Get-NumtareenPronunciation.ps1")
        # No user text is interpolated into command source: positional args
        # bind to a fixed script and supplied native shell arguments.
        p = subprocess.run(
            [shell, "-NoProfile", "-NonInteractive", "-File", script,
             "-RepoRoot", str(REPO_ROOT), "-Text", ROWS["E01"]["orthography"],
             "-AsJson"],
            cwd=REPO_ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=20, check=False,
        )
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["status"], "ATTESTED_UTTERANCE")

    def test_native_ps7_attested(self):
        self._assert_native_attested("pwsh")

    def test_native_windows_ps51_attested(self):
        self._assert_native_attested("powershell")

    def _assert_native_unknown_and_protected(self, shell_name):
        shell = self._shell(shell_name)
        script = str(PROPOSAL_ROOT / "scripts" / "Get-NumtareenPronunciation.ps1")
        protected = ROWS["E26"]["orthography"]
        for phrase, expected in (
            ('novel "quoted" nûm 🚀', "UNKNOWN"),
            (protected, "WITHHELD"),
        ):
            with self.subTest(expected=expected):
                p = subprocess.run(
                    [shell, "-NoProfile", "-NonInteractive", "-File", script,
                     "-RepoRoot", str(REPO_ROOT), "-Text", phrase, "-AsJson"],
                    cwd=REPO_ROOT, capture_output=True, text=True,
                    encoding="utf-8", errors="replace", timeout=20, check=False,
                )
                self.assertEqual(p.returncode, 0)
                self.assertEqual(json.loads(p.stdout)["status"], expected)
                self.assertNotIn(protected, p.stdout + p.stderr)

    def test_native_ps7_unknown_and_protected(self):
        self._assert_native_unknown_and_protected("pwsh")

    def test_native_windows_ps51_unknown_and_protected(self):
        self._assert_native_unknown_and_protected("powershell")


if __name__ == "__main__":
    unittest.main()
