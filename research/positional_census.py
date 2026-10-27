"""Source-bound positional diagnostics; does not interpret or generate language.

The public authored corpus records 30 excerpts, some with multiple clauses.
This deliberately limited census detects material appearing after an overt
WIT/VRF evidential in the same punctuated clause. It cannot infer prosody,
register, or semantic scope from transliterated text.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
# When this module is installed at research/positional_census.py, this path
# resolves within the checked-out num-ta-reen repository.
DEFAULT_CORPUS = HERE.parent / "data" / "corpus.json"
SOURCE_MAIN_COMMIT = "14892e64983d91d9cdf2f580dcba57654624a6c1"
EXPECTED_CORPUS_BLOB = "53d9f27d03579a1a3fc700c3394b56f834da784e"
PROTECTED = {"E13", "E23", "E26"}
EVIDENTIAL = {"ech", "reen"}
INTERROGATIVE = {"hë"}
ARG_ROLES = {"ka", "en", "ru", "va", "shi"}


def clauses(orthography: str) -> tuple[tuple[str, ...], ...]:
    """Split only overt sentence punctuation; keep clitics with their hosts."""
    pieces = re.findall(r"[^.!?]+(?:[.!?]|$)", orthography.replace("\n", " "))
    return tuple(
        tuple(
            unicodedata.normalize("NFC", word)
            .strip()
            .rstrip(".!?")
            .casefold()
            for word in piece.split()
        )
        for piece in pieces
        if piece.strip()
    )


def after_evidential(tokens: tuple[str, ...]) -> tuple[str, ...]:
    indices = [i for i, token in enumerate(tokens) if token in EVIDENTIAL]
    if not indices:
        return ()
    return tokens[max(indices) + 1 :]


def audit(path: Path = DEFAULT_CORPUS) -> dict[str, Any]:
    raw = path.read_bytes()
    # The commit is context, not proof. Refuse altered bytes before emitting
    # evidence counts carrying a pinned source revision identity.
    actual_blob = hashlib.sha1(
        b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    ).hexdigest()
    if actual_blob != EXPECTED_CORPUS_BLOB:
        raise ValueError("authored corpus does not match expected Git blob")
    doc = json.loads(raw.decode("utf-8"))
    results: list[dict[str, Any]] = []
    for record in doc["records"]:
        eid = record["id"]
        if eid in PROTECTED:
            continue
        for idx, chunk in enumerate(clauses(record["orthography"]), 1):
            tail = after_evidential(chunk)
            role_hosts = [
                token for token in chunk
                if any(re.search(fr"={role}(?:=|$)", token) for role in ARG_ROLES)
            ]
            result = {
                "record_id": eid,
                "clause_number": idx,
                "has_evidential": any(token in EVIDENTIAL for token in chunk),
                "role_clitic_hosts": len(role_hosts),
                "post_evidential_token_count": len(tail),
                "post_evidential_only_question": bool(tail)
                and all(t in INTERROGATIVE for t in tail),
                "post_evidential_role_clitic": any(
                    any(re.search(fr"={role}(?:=|$)", token) for role in ARG_ROLES)
                    for token in tail
                ),
            }
            results.append(result)
    return {
        "source_main_commit": SOURCE_MAIN_COMMIT,
        "source_blob": actual_blob,
        "total_records": doc["record_count"],
        "included_records": sum(r["id"] not in PROTECTED for r in doc["records"]),
        "included_clauses": len(results),
        "with_evidential": sum(x["has_evidential"] for x in results),
        "question_only_tails": [
            x["record_id"] for x in results
            if x["post_evidential_only_question"]
        ],
        "post_evidential_argument_cases": [
            {"id": x["record_id"], "clause": x["clause_number"]}
            for x in results if x["post_evidential_role_clitic"]
        ],
        "without_evidential": [
            {"id": x["record_id"], "clause": x["clause_number"]}
            for x in results if not x["has_evidential"]
        ],
    }


if __name__ == "__main__":
    print(json.dumps(audit(), indent=2, ensure_ascii=False, sort_keys=True))
