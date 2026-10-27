"""Source-attested Num'ta'reen consent contrasts, not productive grammar.

Distinguishes explicit CONS clitic evidence from lexical record.GRANT,
respect-silence, ordinary NEG/PROH, and unattested permission withdrawal.
No output is a learner-grounding claim or an inference of consent from silence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from research.semantic_ir_proposal import load_verified_corpus
from research.typed_semantic_channel import (
    AbstentionError,
    decode_frame,
    encode_corpus_id,
)


def audit(repo_root: str | Path) -> dict[str, Any]:
    """Require the pinned authored corpus and exact-source typed round-trips."""
    root = Path(repo_root).resolve()
    rows = load_verified_corpus(root)
    records: list[dict[str, Any]] = []
    abstained: list[str] = []
    for eid in sorted(rows):
        try:
            decoded = decode_frame(encode_corpus_id(eid, repo_root=root), repo_root=root)
        except AbstentionError:
            abstained.append(eid)
            continue
        sem = decoded.semantic
        atoms = sem["atoms"]
        observations = {a["gloss"] for a in atoms}
        consent = sem["consent"]
        if not (
            consent["atom_indices"] or "record.GRANT" in observations
            or "SOFT-respect.silence" in observations
            or sem["polarity"]
            or eid == "E07"  # The explicit, unconsented source contrast.
        ):
            continue
        records.append({
            "source_id": eid,
            "explicit_cons_indices": list(consent["atom_indices"]),
            "predicate_cons_indices": list(consent["predicate_indices"]),
            "participant_cons_indices": list(consent["argument_indices"]),
            "unattached_cons_indices": list(consent["unattached_indices"]),
            "record_grant_predicate": "record.GRANT" in observations,
            "respect_silence_predicate": "SOFT-respect.silence" in observations,
            "polarity": [p["operator"] for p in sem["polarity"]],
            "scope_unestablished": sem["ambiguity"]["scope_unestablished"],
            "qualifies_as_independent_consent": False,
        })
    return {
        "source_git_blob_sha1": "53d9f27d03579a1a3fc700c3394b56f834da784e",
        "source_evidence": "SOURCE_VERIFIED_AUTHOR_INTERLINEAR_GLOSS",
        "observations": records,
        "abstained_source_ids": abstained,
        "revocation_rule": "UNESTABLISHED_BY_AUTHORED_CORPUS",
        "infer_permission_from_silence": False,
    }
