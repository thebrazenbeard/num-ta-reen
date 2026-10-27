"""Source-bound adversarial audit of word order, focus, and shallow projections.

This is NONCANONICAL diagnostic research on authored interlinear glosses.
It does not infer productive grammar, unseen-sentence translation, or native
Ech'ta'reen acoustic semantics.
"""

from __future__ import annotations

from collections import Counter
import os
from pathlib import Path
from typing import Any

from research.semantic_ir_proposal import (
    EXPECTED_CORPUS_GIT_BLOB_SHA1,
    load_verified_corpus,
)
from research.typed_semantic_channel import decode_frame, encode_corpus_id


def _tokens(text: str) -> tuple[str, ...]:
    # Only these attested plain sentences are accepted here. No general
    # tokenizer/phonological normalization is claimed.
    return tuple(text.removesuffix(".").split())


def _observation(source_id: str, *, repo_root: Path) -> dict[str, Any]:
    return decode_frame(encode_corpus_id(source_id, repo_root=repo_root),
                        repo_root=repo_root).semantic


def _unordered_roles(semantic: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    """Deliberately lossy comparison: discard authored argument order."""
    return tuple(sorted((arg["role"], arg["referent_gloss"])
                        for arg in semantic["arguments"]))


def audit(*, repo_root: str | Path | None = None) -> dict[str, Any]:
    root = Path(repo_root or os.environ.get("NUMTAREEN_ROOT")
                or Path(__file__).resolve().parents[1]).resolve()
    rows = load_verified_corpus(root)  # Git-blob pin; do not trust JSON labels.
    a, b = rows["E02"], rows["E03"]
    sa = _observation("E02", repo_root=root)
    sb = _observation("E03", repo_root=root)

    same_word_bag = Counter(_tokens(a["orthography"])) == Counter(_tokens(b["orthography"]))
    same_role_bag = _unordered_roles(sa) == _unordered_roles(sb)
    order_a = tuple((x["role"], x["atom_index"]) for x in sa["arguments"])
    order_b = tuple((x["role"], x["atom_index"]) for x in sb["arguments"])
    typed_frames_different = encode_corpus_id("E02", repo_root=root) != encode_corpus_id("E03", repo_root=root)
    implicit_focus_unlabeled = not sa["discourse"] and not sb["discourse"]
    note = b["notes"]

    # Three distinct axes with independently attested controls:
    # E01/E05 overt FOC, E20/E21 consent, E01/E08 Q.
    contrast_axes: dict[str, bool] = {}
    for label, before_id, after_id, key in (
        ("overt_focus", "E01", "E05", "discourse"),
        ("consent", "E20", "E21", "consent"),
        ("question", "E01", "E08", "interrogative"),
    ):
        before = _observation(before_id, repo_root=root)
        after = _observation(after_id, repo_root=root)
        contrast_axes[label] = before[key] != after[key]

    return {
        "status": "SOURCE_BOUND_NONCANONICAL",
        "source_corpus_git_blob_sha1": EXPECTED_CORPUS_GIT_BLOB_SHA1,
        "same_surface_word_bag": same_word_bag,
        "same_unordered_argument_roles": same_role_bag,
        "argument_order_e02": order_a,
        "argument_order_e03": order_b,
        "typed_frames_distinct": typed_frames_different,
        "explicit_discourse_metadata_empty_for_both": implicit_focus_unlabeled,
        "e03_source_note_mentions_focus": "contrast/focus" in note,
        "different_authored_english": a["english"] != b["english"],
        "independent_contrast_axes": contrast_axes,
        "qualification_eligible": False,
        "unseen_translation_demonstrated": False,
        "interpretation": (
            "E02/E03 differ in authored argument order and rendering. "
            "Their attested late-agent contrastive focus is in the E03 note; "
            "typed atom indices retain order, but the explicit FOC-tag list "
            "does not encode it as an inferred discourse claim."
        ),
    }


if __name__ == "__main__":
    import json
    print(json.dumps(audit(), sort_keys=True, indent=2, ensure_ascii=False))
