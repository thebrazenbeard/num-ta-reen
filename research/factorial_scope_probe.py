"""Retrospective *exploratory* source-pinned four-cell marker factoring probe.

Not a Num'ta'reen translator, grammar amendment, or acoustic/semantic proof.
Only E01/E08/E15 are ever visible to the predictor; E22 is accessed by the
evaluator AFTER a prediction has been produced. Caller rows are unverified.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


SOURCE_CORPUS_BLOB = "53d9f27d03579a1a3fc700c3394b56f834da784e"
TRAIN_IDS = ("E01", "E08", "E15")
HELDOUT_ID = "E22"
ALL_IDS = frozenset((*TRAIN_IDS, HELDOUT_ID))
REQUESTED_FACTORS = (True, True)  # (LOOP, Q): experimental target, not an E22 read.
UNVERIFIED = "CALLER_SUPPLIED_UNVERIFIED_ROWS"
PINNED = "SOURCE_PINNED_AUTHOR_CORPUS_EXPLORATORY_MARKER_PROBE"


def _git_blob(content: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(content)).encode() + b"\x00" + content).hexdigest()


def source_rows(repo_root: Path) -> dict[str, dict[str, Any]]:
    """Load exact archived author text; do not expose E26 or inspect its chord."""
    content = (repo_root / "data" / "corpus.json").read_bytes()
    if _git_blob(content) != SOURCE_CORPUS_BLOB:
        raise ValueError("unverified corpus content")
    payload = json.loads(content)
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != 30:
        raise ValueError("unexpected author corpus")
    ids = [row.get("id") for row in records]
    if len(set(ids)) != 30 or set(ids) != {f"E{i:02d}" for i in range(1, 31)}:
        raise ValueError("unexpected source IDs")
    by_id = {row["id"]: row for row in records}
    return {rid: by_id[rid] for rid in ALL_IDS}


def _plain_row(row: Mapping[str, Any]) -> None:
    # Method-spoofing Mapping subclasses can return benign values from get()
    # and protected contents from __getitem__(). Require a plain, stable dict.
    if type(row) is not dict:
        raise ValueError("row must be a plain, stable dict")
    for key in ("id", "orthography", "igt"):
        if type(row.get(key)) is not str:
            raise ValueError("row fields must be plain strings")
    for key in ("orthography", "igt"):
        if "⟦" in row[key] or "⟧" in row[key]:
            raise ValueError("protected notation")


def _igt_features(igt: str) -> tuple[bool, bool]:
    pieces = igt.split()
    if len(pieces) % 2:
        raise ValueError("unpaired IGT")
    glosses = tuple(pieces[1::2])
    return "LOOP" in glosses, "Q" in glosses


def _uncapitalize(text: str) -> str:
    if not text or not text[0].isupper():
        raise ValueError("baseline must begin with uppercase")
    return text[0].lower() + text[1:]


@dataclass(frozen=True)
class LearnedFactors:
    base: str
    preposed_loop: str
    postposed_question: str

    def synthesize(self, *, loop: bool, question: bool) -> str:
        text = self.base
        if loop:
            text = self.preposed_loop + _uncapitalize(text)
        if question:
            if not text.endswith("."):
                raise ValueError("cannot apply question without final period")
            text = text[:-1] + self.postposed_question
        return text


def learn(training: Mapping[str, Mapping[str, Any]]) -> LearnedFactors:
    """Only training data is accepted; heldout E22 cannot enter this API."""
    if type(training) is not dict or set(training) != set(TRAIN_IDS):
        raise ValueError("exactly E01/E08/E15 training rows required")
    for rid in TRAIN_IDS:
        _plain_row(training[rid])
        if training[rid]["id"] != rid:
            raise ValueError("mismatched train ID")
    expected = {"E01": (False, False), "E08": (False, True),
                "E15": (True, False)}
    for rid, factors in expected.items():
        if _igt_features(training[rid]["igt"]) != factors:
            raise ValueError("training semantic labels violate observed contrast")
    base = training["E01"]["orthography"]
    question = training["E08"]["orthography"]
    loop = training["E15"]["orthography"]
    if not base.endswith(".") or not question.startswith(base[:-1]):
        raise ValueError("question is not an observable suffix contrast")
    q_tail = question[len(base) - 1:]
    if not q_tail.startswith(" ") or not q_tail.endswith("?"):
        raise ValueError("unrecognized question transformation")
    de_capitalized = _uncapitalize(base)
    if not loop.endswith(de_capitalized):
        raise ValueError("loop is not an observable prefix contrast")
    loop_prefix = loop[: -len(de_capitalized)]
    if not loop_prefix or not loop_prefix.endswith(" "):
        raise ValueError("unrecognized loop transformation")
    return LearnedFactors(base, loop_prefix, q_tail)


def predict(training: Mapping[str, Mapping[str, Any]]) -> dict[str, str | None]:
    """Prediction function *cannot* see E22, and does not open files."""
    model = learn(training)
    return {
        "whole_sentence_lookup": None,  # no training example for two factors
        "source_token_copy": training["E15"]["orthography"],
        "marker_composition": model.synthesize(
            loop=REQUESTED_FACTORS[0], question=REQUESTED_FACTORS[1]),
    }


def evaluate_rows(rows: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    """Honest API: caller-controlled rows can never claim source attestation."""
    if not isinstance(rows, Mapping) or set(rows) != ALL_IDS:
        raise ValueError("exact four-ID corpus subset required; E26 prohibited")
    training = {rid: rows[rid] for rid in TRAIN_IDS}
    hypotheses = predict(training)  # heldout is deliberately not read yet
    heldout = rows[HELDOUT_ID]
    _plain_row(heldout)
    if heldout["id"] != HELDOUT_ID:
        raise ValueError("heldout ID mismatch")
    gold = heldout["orthography"]  # scoring only; IGT never read for prediction
    return {
        "evidence": UNVERIFIED,
        "design": "RETROSPECTIVE_EXPLORATORY",
        "train_ids": list(TRAIN_IDS),
        "heldout_id": HELDOUT_ID,
        "gold_igt_used_for_prediction": False,
        "requested_features": {"LOOP": True, "Q": True},
        "outcomes": {
            name: {"prediction": output, "state": "abstain" if output is None else
                   "exact" if output == gold else "wrong"}
            for name, output in hypotheses.items()
        },
    }


def evaluate_repo(repo_root: Path) -> dict[str, Any]:
    """Only raw-byte pin validation can upgrade the source grade."""
    rows = source_rows(repo_root)
    result = evaluate_rows(rows)
    result["evidence"] = PINNED
    result["source_corpus_git_blob"] = SOURCE_CORPUS_BLOB
    return result
