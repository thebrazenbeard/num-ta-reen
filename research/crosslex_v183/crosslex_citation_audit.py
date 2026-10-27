"""Source-pinned, noncanonical literal check of illustrative example links.

Only three explicitly allowlisted public corpus records are inspected. E26 and
all other records are neither emitted nor used to infer new language forms.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


CORPUS_BLOB = "53d9f27d03579a1a3fc700c3394b56f834da784e"
LEXICON_BLOB = "c78dccdf9614d8e8e94c968aac5c07a2e4206bf1"
SOURCE_REPORT_BLOB = "932a579ac4f55f2452b178c9844360469e4a6884"

# Headword, the dictionary's cited utterance, expected literal occurrence.
# Outcomes are discovered, not hardcoded: positive controls occur in source.
AUDIT_PAIRS = (
    ("=en", "E01"),
    ("=va", "E20"),
    ("=ru", "E20"),
    ("=shi", "E23"),
)
PUBLIC_ALLOWLIST = frozenset({"E01", "E20", "E23"})


def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\x00" + data).hexdigest()


def _pinned_json(path: Path, expected_blob: str) -> dict:
    raw = path.read_bytes()
    actual = git_blob_sha(raw)
    if actual != expected_blob:
        raise ValueError(f"source Git blob mismatch for {path.name}")
    result = json.loads(raw)
    if type(result) is not dict:
        raise ValueError("unexpected source object")
    return result


def audit(repo_root: Path) -> dict:
    corpus = _pinned_json(repo_root / "data" / "corpus.json", CORPUS_BLOB)
    lexicon = _pinned_json(repo_root / "data" / "lexicon.json", LEXICON_BLOB)
    report_bytes = (repo_root / "docs" / "SOURCE_PARSE_REPORT.md").read_bytes()
    if git_blob_sha(report_bytes) != SOURCE_REPORT_BLOB:
        raise ValueError("source parse report changed")
    if b"illustrative links" not in report_bytes:
        raise ValueError("illustrative reference semantics missing")
    rows = corpus.get("records")
    entries = lexicon.get("entries")
    if type(rows) is not list or type(entries) is not list:
        raise ValueError("unexpected normalized source shape")

    # The *whole* pinned corpus file is necessarily read and JSON-parsed above.
    # From each non-allowlisted row, read only its ID to exclude it; do not
    # inspect or emit E26 orthography/IGT/IPA in the linguistic analysis.
    public = {}
    for row in rows:
        if type(row) is not dict:
            raise ValueError("unexpected record")
        record_id = row.get("id")
        if record_id not in PUBLIC_ALLOWLIST:
            continue
        if record_id in public or type(row.get("orthography")) is not str:
            raise ValueError("bad public record")
        public[record_id] = row["orthography"]
    if set(public) != PUBLIC_ALLOWLIST:
        raise ValueError("missing public records")

    required = {headword for headword, _ in AUDIT_PAIRS}
    dictionary = {}
    for entry in entries:
        if type(entry) is not dict:
            raise ValueError("unexpected entry")
        word = entry.get("headword")
        if word in required:
            if word in dictionary:
                raise ValueError("duplicate headword")
            dictionary[word] = entry
    if set(dictionary) != required:
        raise ValueError("required dictionary headwords absent")

    findings = []
    for headword, example_id in AUDIT_PAIRS:
        entry = dictionary[headword]
        refs = entry.get("example_refs")
        source_text = entry.get("source_text")
        if (type(refs) is not list or example_id not in refs or
                type(source_text) is not str or f"Ex: {example_id}" not in source_text):
            raise ValueError("dictionary's author example reference not confirmed")
        # Ex: links are explicitly ILLUSTRATIVE (SOURCE_PARSE_REPORT.md:26).
        # Literal comparison is defensible for these standalone clitics; it
        # neither invalidates links nor establishes full lexical attestation.
        attested = headword in public[example_id]
        findings.append({
            "headword": headword,
            "illustrative_example_ref": example_id,
            "literal_clitic_in_illustrative_orthography": attested,
            "classification": (
                "LITERAL_PRESENT_IN_ILLUSTRATIVE_EXAMPLE" if attested
                else "LITERAL_ABSENT_FROM_ILLUSTRATIVE_EXAMPLE"
            ),
        })

    return {
        "evidence": "SOURCE_PINNED_ILLUSTRATIVE_LINK_LITERAL_COMPARISON",
        "canon_mutation": False,
        "example_ref_semantics": "ILLUSTRATIVE_LINK_NOT_REQUIRED_HEADWORD_ATTESTATION",
        "protected_E26": "WITHHELD_NOT_ACCESSED_FOR_ANALYSIS",
        "raw_corpus_json_parsed": True,
        "corpus_git_blob": CORPUS_BLOB,
        "lexicon_git_blob": LEXICON_BLOB,
        "source_report_git_blob": SOURCE_REPORT_BLOB,
        "findings": findings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.repo_root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
