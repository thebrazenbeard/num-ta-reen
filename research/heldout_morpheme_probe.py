"""Bounded, source-pinned NT->IGT morpheme transfer experiment.

This is a *research* analyzer, not a translator.  Every fold learns mappings
solely from other author-annotated examples.  The observed "=" morphology is
factorized; unknown roots and ambiguous labels are explicitly withheld.
English free translations and test-fold IGT are never features.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import unicodedata

CORPUS_GIT_BLOB = "53d9f27d03579a1a3fc700c3394b56f834da784e"
LEXICON_GIT_BLOB = "c78dccdf9614d8e8e94c968aac5c07a2e4206bf1"
WITHHELD = frozenset({"E13", "E23", "E26"})
ELIGIBLE_IDS = frozenset(f"E{i:02d}" for i in range(1, 31)) - WITHHELD
PROTECTED_ID = "E26"
MAX_SOURCE_BYTES = 100_000
_WHITESPACE = re.compile(r"\s+")
_APOSTROPHES = str.maketrans({"'": "’", "‘": "’", "ʼ": "’"})


def normalized_surface(word: str) -> str:
    """Keep phonemic accents and clitic '=', only ignore sentence terminators."""
    if type(word) is not str:
        raise TypeError("word must be an ordinary string")
    normalized = unicodedata.normalize("NFC", word.translate(_APOSTROPHES))
    return normalized.removesuffix(".").removesuffix("?").casefold()


def tokens(sentence: str) -> tuple[str, ...]:
    if type(sentence) is not str:
        raise TypeError("source sentence must be ordinary text")
    return tuple(normalized_surface(part) for part in _WHITESPACE.split(sentence.strip()) if part)


def _git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def source_rows(root: str | Path) -> tuple[dict, ...]:
    raw = (Path(root) / "data" / "corpus.json").read_bytes()
    if not 0 < len(raw) <= MAX_SOURCE_BYTES or _git_blob_sha(raw) != CORPUS_GIT_BLOB:
        raise ValueError("source corpus provenance mismatch")
    try:
        obj = json.loads(raw)
        records = obj["records"]
        ids = {row["id"] for row in records}
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("malformed corpus") from exc
    if obj.get("record_count") != 30 or len(records) != 30 or ids != {
        f"E{i:02d}" for i in range(1, 31)
    }:
        raise ValueError("unexpected author corpus record set")
    # Privacy: E26 is never processed at the orthography/IGT level.
    return tuple(row for row in records if row["id"] not in WITHHELD)


def author_polysemy_flags(root: str | Path) -> frozenset[str]:
    """Independent author dictionary veto, not a held-out IGT label source."""
    raw = (Path(root) / "data" / "lexicon.json").read_bytes()
    if not 0 < len(raw) <= 600_000 or _git_blob_sha(raw) != LEXICON_GIT_BLOB:
        raise ValueError("source lexicon provenance mismatch")
    try:
        obj = json.loads(raw)
        entries = obj["entries"]
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError("malformed lexicon") from exc
    if obj.get("entry_count") != 500 or len(entries) != 500:
        raise ValueError("unexpected author lexicon size")
    return frozenset(normalized_surface(row["headword"])
                     for row in entries if "/" in row["gloss"])


def _require_nonprotected_row(row: dict) -> None:
    """Fail before IGT/source processing if a caller supplies protected E26."""
    if type(row) is not dict or type(row.get("id")) is not str:
        raise ValueError("corpus row requires an ordinary ID")
    if row["id"] == PROTECTED_ID:
        raise ValueError("protected E26 cannot be used by public IGT helpers")


def annotated_pairs(row: dict) -> tuple[tuple[str, str, str], ...]:
    """Align source orthographic words with authored IGT form/gloss slots.

    Hyphens in *author IGT forms* sometimes correspond to visible apostrophes
    in source writing.  Accept only that narrowly attested transcription
    convention; exclude any nonaligning clause rather than invent an analysis.
    """
    _require_nonprotected_row(row)
    forms = row["igt"].split()
    surface = tokens(row["orthography_index"])
    if len(forms) % 2 or len(forms) // 2 != len(surface):
        raise ValueError(f"unaligned author IGT slots in {row['id']}")
    pairs = tuple(zip(surface, forms[::2], forms[1::2]))
    for written, form, _ in pairs:
        if normalized_surface(form.replace("-", "’")) != written:
            raise ValueError(f"unmatched author IGT token in {row['id']}")
    return pairs


def _parts(word: str) -> tuple[str, ...]:
    split = word.split("=")
    if not split or any(not part for part in split):
        raise ValueError("bad clitic segmentation")
    return (split[0],) + tuple("=" + part for part in split[1:])


def _gloss_parts(gloss: str) -> tuple[str, ...]:
    return tuple(gloss.split("="))


def learn(rows: tuple[dict, ...]) -> tuple[dict[str, frozenset[str]], dict[str, frozenset[str]]]:
    """Learn whole-token and segment labels *only* from training IGT."""
    # Preflight *all* rows before learning from even one, including public API
    # callers that bypass source_rows() and hand-build their training examples.
    for row in rows:
        _require_nonprotected_row(row)
    whole: dict[str, set[str]] = defaultdict(set)
    segments: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        for surface, _igt_form, gloss in annotated_pairs(row):
            whole[surface].add(gloss)
            morphemes, labels = _parts(surface), _gloss_parts(gloss)
            if len(morphemes) != len(labels):
                raise ValueError(f"invalid authored clitic/gloss alignment in {row['id']}")
            for morpheme, label in zip(morphemes, labels):
                segments[morpheme].add(label)
    return ({k: frozenset(v) for k, v in whole.items()},
            {k: frozenset(v) for k, v in segments.items()})


def predict(word: str, segment_map: dict[str, frozenset[str]]) -> tuple[str | None, ...]:
    """Return only unambiguous labels; abstain per unseen/ambiguous component."""
    return tuple(next(iter(labels)) if len(labels := segment_map.get(unit, frozenset())) == 1
                 else None for unit in _parts(normalized_surface(word)))


def evaluate_rows(rows: tuple[dict, ...], *, polysemous_roots: frozenset[str] = frozenset()) -> dict:
    """27-fold held-out evaluation of *unverified caller-supplied* rows.

    Matching eligible IDs is not source attestation: callers may replace the
    in-memory gold IGT or dictionary flags without modifying repository files.
    Only evaluate(root), after checking both raw source blob hashes, can issue
    the repository-source evidence grade.
    """
    if (len(rows) != len(ELIGIBLE_IDS) or
            any(type(r) is not dict or type(r.get("id")) is not str for r in rows) or
            {r["id"] for r in rows} != ELIGIBLE_IDS):
        raise ValueError("benchmark requires exactly 27 unique eligible source IDs")
    aggregate = defaultdict(int)
    folds = []
    for held in rows:
        training = tuple(row for row in rows if row["id"] != held["id"])
        whole, segments = learn(training)
        # Exploratory post-hoc safety rule: a dictionary-polysemous root needs
        # two independent training contexts before predicting its IGT label.
        # This cannot make a false root mapping true; it only abstains more.
        support: dict[str, set[str]] = defaultdict(set)
        for training_row in training:
            for written, _, _ in annotated_pairs(training_row):
                support[_parts(written)[0]].add(training_row["id"])
        # Freeze predictions before reading this fold's gold IGT/gloss fields.
        held_tokens = tokens(held["orthography_index"])
        predictions = tuple(predict(word, segments) for word in held_tokens)
        guarded = tuple(((None,) + pred[1:]) if
                        _parts(word)[0] in polysemous_roots and
                        len(support[_parts(word)[0]]) < 2
                        else pred
                        for word, pred in zip(held_tokens, predictions))
        remembered = tuple(next(iter(labels)) if len(labels := whole.get(word, frozenset())) == 1
                           else None for word in held_tokens)
        whole_utterances = {tuple(tokens(r["orthography_index"])) for r in training}
        phrase_seen = held_tokens in whole_utterances
        gold = annotated_pairs(held)
        score = defaultdict(int)
        score["tokens"] = len(gold)
        score["phrase_memorization_hits"] = int(phrase_seen)
        score["source_copy_correct_morphemes"] = 0
        for (surface, _form, gloss), pred, safe, memo in zip(
                gold, predictions, guarded, remembered):
            expected = _gloss_parts(gloss)
            assert len(pred) == len(expected)
            score["gold_morphemes"] += len(expected)
            score["source_copy_correct_morphemes"] += sum(
                source_unit.casefold() == expected_unit.casefold()
                for source_unit, expected_unit in zip(_parts(surface), expected)
            )
            if memo == gloss:
                score["whole_token_exact"] += 1
                score["whole_token_correct_morphemes"] += len(expected)
            else:
                score["whole_token_abstained"] += 1
            if all(part is not None for part in pred) and pred == expected:
                score["factorized_token_exact"] += 1
            for guess, expected_unit in zip(pred, expected):
                if guess is None:
                    score["factorized_morpheme_abstained"] += 1
                elif guess == expected_unit:
                    score["factorized_morpheme_correct"] += 1
                    if memo != gloss:
                        score["factorized_correct_without_whole_token_match"] += 1
                else:
                    score["factorized_morpheme_wrong"] += 1
            for guess, expected_unit in zip(safe, expected):
                if guess is None:
                    score["guarded_morpheme_abstained"] += 1
                elif guess == expected_unit:
                    score["guarded_morpheme_correct"] += 1
                else:
                    score["guarded_morpheme_wrong"] += 1
        # No gold strings, transcriptions, or protected source exposed.
        folds.append({"id": held["id"], **dict(score)})
        for key, value in score.items():
            aggregate[key] += value
    return {
        "schema": "numtareen.research.heldout_morpheme_probe.v0",
        "source_corpus_git_blob": None,
        "source_lexicon_git_blob": None,
        "eligible_heldout_folds": len(rows),
        "excluded_ids": sorted(WITHHELD),
        "training_per_fold": len(rows) - 1,
        "scores": dict(aggregate),
        "folds": folds,
        "evidence": "CALLER_SUPPLIED_UNVERIFIED_IGT_MORPHEME_RECOVERY",
        "guard": "POST_HOC_EXPLORATORY_POLYSEMY_AND_SINGLE_CONTEXT_ABSTENTION",
        "limitations": [
            "Only orthographic NT to partial author IGT; not English sentence translation.",
            "Author's '=' clitic boundary is provided, not discovered by a model.",
            "Every fold's held-out IGT is used for scoring only.",
            "A correct gloss unit is a partial analysis, not a fluent utterance.",
            "Only 27 eligible curated examples: no independent real-world distribution.",
            "Novel stems and ambiguous labels abstain; absent word-order composition.",
            "Safety gate was selected after inspecting baseline failures; do NOT treat its scores as independent confirmation.",
            "evaluate_rows() does not attest caller-supplied gold IGT or dictionary flags; use evaluate(repo_root) for source-verified evidence.",
        ],
    }


def evaluate(root: str | Path) -> dict:
    # Both inputs are read and authenticated against the exact Git blobs
    # *before* their derived result is allowed to claim SOURCE_PINNED.
    rows = source_rows(root)
    polysemous_roots = author_polysemy_flags(root)
    result = evaluate_rows(rows, polysemous_roots=polysemous_roots)
    result["source_corpus_git_blob"] = CORPUS_GIT_BLOB
    result["source_lexicon_git_blob"] = LEXICON_GIT_BLOB
    result["evidence"] = "SOURCE_PINNED_TRAIN_ONLY_IGT_MORPHEME_RECOVERY"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.repo_root), indent=2, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
