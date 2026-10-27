"""Exact UTF-8 transport for the source-attested pronunciation reference.

This wrapper is intentionally separate from translation and does not infer IPA
for unattested strings. It exists because Windows PowerShell 5.1 can rewrite
quotes in native process arguments; only Base64 ASCII crosses that boundary.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys
from pathlib import Path


MAX_INPUT_BYTES = 8192


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline author-attested IPA lookup")
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--text-base64", required=True, help="strict Base64 of UTF-8 text")
    args = parser.parse_args(argv)
    try:
        # Base64 must not exceed the bounded UTF-8 input. Reject excessive
        # input before allocating a decoded buffer.
        if len(args.text_base64) > 4 * ((MAX_INPUT_BYTES + 2) // 3):
            raise ValueError("oversized text")
        text = base64.b64decode(
            args.text_base64.encode("ascii"), validate=True
        )
        if len(text) > MAX_INPUT_BYTES:
            raise ValueError("oversized text")
        phrase = text.decode("utf-8", errors="strict")
        # The repo root is explicit and source verification remains the
        # responsibility of AttestedPronunciationGuide.
        root = args.repo_root.resolve()
        sys.path.insert(0, str(root))
        from numtareen.phonetic_bridge import AttestedPronunciationGuide

        result = AttestedPronunciationGuide(root).lookup(phrase)
    except (UnicodeError, ValueError, OSError, binascii.Error) as exc:
        # Never echo the submitted phrase, including withheld true-name text.
        print("Error: invalid input or source evidence", file=sys.stderr)
        return 1
    # ASCII JSON survives PowerShell 5.1 and a redirected cp1252 terminal.
    print(json.dumps(result.as_dict(), ensure_ascii=True, sort_keys=True))
    return 0 if result.status.startswith("ATTESTED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
