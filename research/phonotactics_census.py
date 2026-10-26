#!/usr/bin/env python3
"""Read-only, source-pinned diagnostic of author IPA; never emits lexemes.

The listed segment inventory and coda inventory are hypotheses in the author
reference grammar.  These checks flag inconsistencies, NOT phonetic errors:
many strings are affixed or transcribed across register distinctions.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter
from pathlib import Path


# Installed location is <repo>/research/phonotactics_census.py.
# Explicit root is useful only when verifying an isolated research checkout;
# no source content is accepted unless all three blob hashes match.
REPO = Path(os.environ.get("NUMTAREEN_REPO_ROOT", str(Path(__file__).absolute().parents[1]))).resolve()
SOURCE = REPO / "data" / "lexicon.json"
EXPECTED_BLOB = "c78dccdf9614d8e8e94c968aac5c07a2e4206bf1"
EXPECTED_SOURCE_GRAMMAR = "d7bd1a1a07d9052b6795b3824bfc18fc9c50e912"
EXPECTED_SOURCE_DICTIONARY = "af257a3072d1bd7c6bd1de510258b6fb5ab91264"
GRAMMAR = REPO / "sources" / "reference_grammar_v2_updated_lphoneme.txt"
DICTIONARY = REPO / "sources" / "dictionary_v2_updated_lphoneme.txt"


def git_blob_sha(path: Path) -> str:
    raw = path.read_bytes()
    # GitHub's Windows checkout may materialize the same pinned Git blob
    # with uniform CRLF working-tree line endings. Permit only that exact
    # mechanical transformation; mixed EOLs and stray carriage returns
    # remain mismatches against the committed source object.
    crlf_count = raw.count(b"\r\n")
    if crlf_count and raw.count(b"\n") == crlf_count and raw.count(b"\r") == crlf_count:
        raw = raw.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def assert_sources() -> None:
    for path, expected in (
        (SOURCE, EXPECTED_BLOB),
        (GRAMMAR, EXPECTED_SOURCE_GRAMMAR),
        (DICTIONARY, EXPECTED_SOURCE_DICTIONARY),
    ):
        observed = git_blob_sha(path)
        if observed != expected:
            raise RuntimeError(f"Source digest mismatch for {path.name}: {observed}")


def census() -> dict:
    assert_sources()
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    entries = data["entries"]
    if len(entries) != 500:
        raise ValueError("Unexpected lexicon size")
    # These segment sequences are absent from the printed base consonant
    # chart.  The affricate needs to be matched as a unit.
    omitted = {"v": "v", "theta": "θ", "tsh": "t͡ʃ"}
    with_omitted = {
        segment: sum(needle in entry["ipa"] for entry in entries)
        for segment, needle in omitted.items()
    }
    omitted_in_cf = {
        segment: sum(
            needle in entry["ipa"] and "CF" in entry["register"].split("/")
            for entry in entries
        )
        for segment, needle in omitted.items()
    }
    vowel_symbols = {
        symbol: sum(symbol in entry["ipa"] for entry in entries)
        for symbol in ("ɑ", "ɛ", "ɪ", "ʊ", "ɔ", "y", "ə", "æ", "ɜ", "ø")
    }
    # Only terminal IPA code points that are conspicuously absent from the
    # listed I.4 coda set.  Not necessarily native monosyllabic codas.
    flagged_end = Counter()
    flagged_categories = Counter()
    flagged_registers = Counter()
    for entry in entries:
        ipa = entry["ipa"]
        if ipa and ipa[-1] in "mlrɾθv":
            flagged_end[ipa[-1]] += 1
            flagged_categories[entry["category"]] += 1
            for reg in entry["register"].split("/"):
                flagged_registers[reg] += 1
    # /tɾ/ could be a lexical onset or occur at a compounding boundary.
    # No automatic syllabification is claimed.
    tr_clusters = sum("tɾ" in entry["ipa"] for entry in entries)
    return {
        "source_git_blobs": {
            "lexicon": EXPECTED_BLOB,
            "grammar": EXPECTED_SOURCE_GRAMMAR,
            "dictionary": EXPECTED_SOURCE_DICTIONARY,
        },
        "entries": len(entries),
        "listed_codas": ["n", "ŋ", "k", "t", "ʃ", "x"],
        "omitted_consonant_occurrence_entries": with_omitted,
        "omitted_consonant_entries_with_cf_register": omitted_in_cf,
        "vowel_symbols_beyond_grammars_base_chart": {
            symbol: count for symbol, count in vowel_symbols.items() if count
        },
        "vowel_symbol_ɑ_explanation": "The grammar explicitly proposes [ɑ] as a contextual /a/ allophone.",
        "flagged_terminal_total": sum(flagged_end.values()),
        "flagged_terminal_by_symbol": dict(sorted(flagged_end.items())),
        "flagged_terminal_category_counts": dict(sorted(flagged_categories.items())),
        "flagged_terminal_register_counts": dict(sorted(flagged_registers.items())),
        "contains_tap_cluster_t_alveolar_tap": tr_clusters,
    }


if __name__ == "__main__":
    print(json.dumps(census(), ensure_ascii=True, indent=2, sort_keys=True))
