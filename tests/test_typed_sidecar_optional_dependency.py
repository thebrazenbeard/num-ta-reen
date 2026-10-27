"""Standalone import and fail-closed checks independent of the UNV peer.

The sidecar is an opt-in research API. Python 3.10 standalone builds must not
require Universal Translator (which currently requires >=3.11), and no absent
peer may be mistaken for validated semantic observations.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])).resolve()


class OptionalPeerContractTests(unittest.TestCase):
    def test_offline_import_does_not_need_unvtrslr(self):
        code = (
            "from research.typed_reference_bridge_v0 import SidecarError, build_sidecar\n"
            "assert issubclass(SidecarError, ValueError)\n"
            "try:\n"
            "    build_sidecar('E01')\n"
            "except SidecarError:\n"
            "    pass\n"
            "else:\n"
            "    raise AssertionError('validated without public peer')\n"
        )
        env = os.environ.copy()
        # Ignore user/site packages. Include only this repository as source.
        module_root = Path(__file__).resolve().parents[1]
        env["PYTHONPATH"] = os.pathsep.join((str(module_root), str(ROOT)))
        completed = subprocess.run(
            [sys.executable, "-S", "-c", code],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=15,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)


if __name__ == "__main__":
    unittest.main()
