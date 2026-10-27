"""Source-bounded evaluation; no language model, synthetic lexemes, or grammar invention.

Run: python -m research.bilingual_eval_v0 [<num-ta-reen-root>]

The benchmark separates (a) exact attested translation, (b) dictionary lookup,
and (c) generalizing to an unseen sentence. Only (a) is scored as sentence
translation. Dictionary glosses are intentionally not treated as translations
of entire novel utterances.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import unicodedata


# Canonical corpus conflict rows are withheld pending author arbitration.
PROTECTED_IDS = frozenset({"E13", "E23", "E26"})
EXPECTED_CORPUS_BLOB_SHA1 = "53d9f27d03579a1a3fc700c3394b56f834da784e"
EXPECTED_LEXICON_BLOB_SHA1 = "c78dccdf9614d8e8e94c968aac5c07a2e4206bf1"
_APOSTROPHES = str.maketrans({"'": "’", "‘": "’", "ʼ": "’"})
_WHITESPACE = re.compile(r"\s+")
_ALTERNATIVES = re.compile(r"^[^\s/.,;:()]+(?:/[^\s/.,;:()]+)+\.?$")
_NEGATIVE_SENTINEL = "unattestedv117"  # Deliberately no authentic morpheme claim.
DEFAULT_ROOT = Path(
    os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])
).resolve()


def git_blob_sha1(content: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(content)).encode("ascii") + b"\0" + content
    ).hexdigest()


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text.translate(_APOSTROPHES))
    return _WHITESPACE.sub(" ", text.strip()).removesuffix(".").casefold()


def load_source(root: Path):
    """Read only the reviewed authored source bytes, never forged provenance."""
    data = root / "data"
    docs = {}
    hashes = {}
    required = {
        "corpus": EXPECTED_CORPUS_BLOB_SHA1,
        "lexicon": EXPECTED_LEXICON_BLOB_SHA1,
    }
    for key in ("corpus", "lexicon"):
        content = (data / f"{key}.json").read_bytes()
        if git_blob_sha1(content) != required[key]:
            raise ValueError(f"{key} does not match pinned authored Git blob")
        hashes[key] = hashlib.sha256(content).hexdigest()
        docs[key] = json.loads(content)
    corpus = docs["corpus"]
    lexicon = docs["lexicon"]
    assert corpus["schema_version"] == 1
    assert lexicon["schema_version"] == 1
    assert len(corpus["records"]) == corpus["record_count"]
    assert len(lexicon["entries"]) == lexicon["entry_count"]
    return corpus["records"], lexicon["entries"], hashes


def fields(row: dict, direction: str) -> tuple[str, str]:
    if direction == "nt-en":
        return row["orthography_index"], row["english"]
    if direction == "en-nt":
        return row["english"], row["orthography_index"]
    raise ValueError(direction)


def lookup(rows: list[dict], query: str, direction: str) -> list[str]:
    return [fields(row, direction)[1] for row in rows
            if normalize(fields(row, direction)[0]) == normalize(query)]


def collect_gloss_keys(entry: dict) -> list[str]:
    gloss = entry["gloss"].strip().removesuffix(".")
    out = [normalize(gloss)]
    if _ALTERNATIVES.fullmatch(entry["gloss"].strip()):
        out.extend(normalize(x) for x in gloss.split("/"))
    return list(dict.fromkeys(out))


def lexical_counts(entries: list[dict]) -> dict:
    nt_index: dict[str, set[str]] = defaultdict(set)
    en_index: dict[str, set[str]] = defaultdict(set)
    for e in entries:
        nt_index[normalize(e["headword"])].add(e["gloss"])
        for key in collect_gloss_keys(e):
            en_index[key].add(e["headword"])
    return {
        "lexicon_entries": len(entries),
        "nt_headword_keys": len(nt_index),
        "en_gloss_keys": len(en_index),
        "nt_ambiguous_keys": sum(len(v) > 1 for v in nt_index.values()),
        "en_ambiguous_keys": sum(len(v) > 1 for v in en_index.values()),
        "en_ambiguous_lexemes": sum(len(v) for v in en_index.values() if len(v) > 1),
        "en_ambiguity_examples": [
            {"english_gloss": key, "numtareen_candidates": sorted(values)}
            for key, values in sorted(en_index.items()) if len(values) > 1
        ][:5],
        "unknown_nt_abstains": _NEGATIVE_SENTINEL not in nt_index,
        "unknown_en_abstains": _NEGATIVE_SENTINEL not in en_index,
    }


def evaluate(root: Path) -> dict:
    corpus, lexicon, hashes = load_source(root)
    eligible = [r for r in corpus if r["id"] not in PROTECTED_IDS]
    assert len(eligible) + len(PROTECTED_IDS) == len(corpus)
    assert len({r["id"] for r in corpus}) == len(corpus)
    by_direction = {}
    for direction in ("nt-en", "en-nt"):
        exact_in_sample = 0
        exact_loo_coverage = 0
        exact_loo_correct = 0
        false_positive_negatives = 0
        bag_loo_coverage = 0
        bag_loo_wrong = 0
        bag_loo_correct = 0
        training_duplicate_count = 0
        for heldout in eligible:
            src, gold = fields(heldout, direction)
            train = [r for r in eligible if r["id"] != heldout["id"]]
            if gold in lookup(eligible, src, direction):
                exact_in_sample += 1
            matches = lookup(train, src, direction)
            if matches:
                exact_loo_coverage += 1
                exact_loo_correct += int(gold in matches)
                training_duplicate_count += 1
            mutated = src + " " + _NEGATIVE_SENTINEL
            false_positive_negatives += int(bool(lookup(eligible, mutated, direction)))
            src_bag = tuple(sorted(normalize(src).split()))
            bag_matches = [fields(row, direction)[1] for row in train
                           if tuple(sorted(normalize(fields(row, direction)[0]).split())) == src_bag]
            if bag_matches:
                bag_loo_coverage += 1
                bag_loo_correct += int(gold in bag_matches)
                bag_loo_wrong += int(gold not in bag_matches)
        by_direction[direction] = {
            "evaluation_rows": len(eligible),
            "exact_in_sample_correct": exact_in_sample,
            "exact_leave_one_out_coverage": exact_loo_coverage,
            "exact_leave_one_out_correct": exact_loo_correct,
            "exact_input_duplicate_folds": training_duplicate_count,
            "bag_leave_one_out_coverage": bag_loo_coverage,
            "bag_leave_one_out_correct": bag_loo_correct,
            "bag_leave_one_out_wrong": bag_loo_wrong,
            "negative_unknown_suffix_false_attested": false_positive_negatives,
            "negative_unknown_suffix_trials": len(eligible),
        }
    return {
        "benchmark": "source-bounded-bilingual-eval-v117",
        "root": str(root.resolve()),
        "source_sha256": hashes,
        "total_corpus": len(corpus),
        "eligible_corpus": len(eligible),
        "protected_excluded_ids": sorted(PROTECTED_IDS),
        "directions": by_direction,
        "lexical": lexical_counts(lexicon),
        "limits": [
            "Exact in-sample retrieval is memorization, not generalization.",
            "Leave-one-out exact hits, if any, can arise from duplicate inputs.",
            "A dictionary gloss is not an attested fluent sentence translation.",
            "Adversarial unknown-suffix tests are negative controls only.",
            "No unseen-sentence translation has been demonstrated.",
        ],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path, nargs="?", default=DEFAULT_ROOT)
    args = ap.parse_args()
    print(json.dumps(evaluate(args.root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
