"""Source-attested orthographic/IPA interruption census, not a phoneme generator.

The punctuation ``’`` and clitic attachment ``=`` carry independent grammar
information. Comparing their number with IPA /ʔ/ counts is a *diagnostic*;
even equal totals do not establish one-to-one alignment of each event.

No E26 notation, lexical spellings or corpus sentences are emitted.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from pathlib import Path


SOURCE_BLOBS = {
    "data/corpus.json": "53d9f27d03579a1a3fc700c3394b56f834da784e",
    "data/lexicon.json": "c78dccdf9614d8e8e94c968aac5c07a2e4206bf1",
    "sources/reference_grammar_v2_updated_lphoneme.txt": "d7bd1a1a07d9052b6795b3824bfc18fc9c50e912",
    "sources/dictionary_v2_updated_lphoneme.txt": "af257a3072d1bd7c6bd1de510258b6fb5ab91264",
}


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _verified_bytes(root: Path, path: str) -> bytes:
    raw = (root / path).read_bytes()
    # Exact LF Git blobs; permit only ordinary checkout CRLF conversion for
    # original Word-to-text sources, never silent Unicode or accent repair.
    stable = raw
    if path.startswith("sources/") and raw.count(b"\r\n"):
        if raw.count(b"\n") != raw.count(b"\r\n") or raw.count(b"\r") != raw.count(b"\r\n"):
            raise ValueError("mixed source newlines")
        stable = raw.replace(b"\r\n", b"\n")
    if _git_blob_sha(stable) != SOURCE_BLOBS[path]:
        raise ValueError(f"source mismatch: {path}")
    return raw


def scan_record(record: dict) -> dict | None:
    """Count signs and transcribed phones, exposing counts and IDs only.

    This is deliberately NOT an alignment algorithm. The cumulative count of
    orthographic glottal-capable boundaries may happen to equal IPA /ʔ/ even
    when individual boundaries are phonetically different.
    """
    ident = record.get("id")
    if ident == "E26":
        return None
    if not isinstance(ident, str) or not ident.startswith("E"):
        raise ValueError("unexpected corpus identifier")
    orth = record.get("orthography")
    ipa = record.get("ipa")
    if not isinstance(orth, str) or not isinstance(ipa, str) or not ipa.startswith("/"):
        raise ValueError(f"missing orthography or IPA for {ident}")
    orth = unicodedata.normalize("NFC", orth)
    apostrophes = orth.count("’") + orth.count("'")
    equals = orth.count("=")
    glottal = ipa.count("ʔ")
    boundary_total = apostrophes + equals
    return {
        "id": ident,
        "apostrophe_marks": apostrophes,
        "clitic_attachment_marks": equals,
        "candidate_boundary_marks": boundary_total,
        "transcribed_glottal_stops": glottal,
        "ipa_minus_boundary_marks": glottal - boundary_total,
    }


def census(repo_root: str | Path) -> dict:
    root = Path(repo_root)
    verified = {path: _verified_bytes(root, path) for path in SOURCE_BLOBS}
    corpus = json.loads(verified["data/corpus.json"].decode("utf-8"))
    if corpus.get("record_count") != 30 or len(corpus.get("records", [])) != 30:
        raise ValueError("unexpected corpus size")
    records = [item for record in corpus["records"] if (item := scan_record(record)) is not None]
    if len(records) != 29:
        raise ValueError("protected E26 must be the only excluded record")
    return {
        "schema": "numtareen.research.glottal_boundary_census.v0",
        "status": "AUTHOR_TEXT_DIAGNOSTIC_NOT_SEGMENT_ALIGNMENT",
        "source_git_blobs": SOURCE_BLOBS,
        "nonprotected_authored_examples": len(records),
        "observed_equal_count": sum(r["ipa_minus_boundary_marks"] == 0 for r in records),
        "observed_extra_ipa_glottals": sum(r["ipa_minus_boundary_marks"] > 0 for r in records),
        "observed_fewer_ipa_glottals": sum(r["ipa_minus_boundary_marks"] < 0 for r in records),
        "records": records,
        "limits": [
            "CORPUS_EXAMPLES_ARE_AUTHOR_DOCUMENTATION_NOT_SPEAKER_RECORDINGS",
            "COUNTS_DO_NOT_DETERMINE_ONE_TO_ONE_BOUNDARY_ALIGNMENT",
            "E26_PROTECTED_NOT_PROCESSED",
            "NO_PRODUCTIVE_GRAPHEME_TO_PHONEME_RULE_ESTABLISHED",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(census(args.repo_root), ensure_ascii=True, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
