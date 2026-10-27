"""NONCANONICAL V0 typed-observation sidecar beside, never inside, UNVTRSLR V1.

The public V1 reference parser requires semantic_atoms=null and prohibits
learner visibility and qualification. The V0 envelope is a separate research
transport. Its receipt is not a learned observation, independent corroboration,
or native Ech'ta'reen semantic proof.
"""

from __future__ import annotations

import base64
import binascii
import json
from pathlib import Path
from typing import Any

from numtareen.engine import DATA_DIR, Translator
from numtareen.interop import to_reference_record
from research.semantic_ir_proposal import (
    EXPECTED_CORPUS_GIT_BLOB_SHA1,
    load_verified_corpus,
)
from research.typed_semantic_channel import (
    ACCEPTED,
    AbstentionError,
    ChannelError,
    decode_frame,
    encode_corpus_id,
)
SCHEMA = "numtareen-unvtrslr-typed-reference-sidecar-v0"
ORIGIN_REPO = "thebrazenbeard/num-ta-reen"
SOURCE_INDEPENDENCE = "SINGLE_AUTHOR_REFERENCE"
MAX_SIDECAR_BYTES = 65_536
_KEYS = frozenset({
    "schema", "status", "origin_repo", "corpus_id", "source_git_blob_sha1",
    "reference_evidence_v1", "typed_frame_base64", "qualification_eligible",
    "learner_visible", "source_independence",
})


class SidecarError(ValueError):
    """Untrusted record or source discrepancy; not a fallback to V1."""


def _parse_reference_evidence(record: Any) -> Any:
    """Require actual UNVTRSLR at use time, not during offline module import.

    Num'ta'reen's standalone Python 3.10 interpreter intentionally need not
    install Universal Translator, which currently requires Python >=3.11.
    """
    try:
        from unvtrslr.reference_evidence import parse_reference_evidence
    except ImportError as exc:
        raise SidecarError("public UNVTRSLR validation peer is required") from exc
    return parse_reference_evidence(record)


def _strict_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise SidecarError("duplicate JSON member")
        result[key] = value
    return result


def _reject_nonfinite(_: str) -> None:
    raise SidecarError("nonfinite JSON numeric value")


def _repo_root(value: str | Path | None) -> Path:
    # Source authentication in both existing modules binds actual file content.
    return Path(value or Path(DATA_DIR).parent).resolve()


def build_sidecar(corpus_id: str, *, repo_root: str | Path | None = None) -> dict[str, Any]:
    """Require exact attested evidence in both source-bound implementations."""
    if type(corpus_id) is not str or len(corpus_id) > 16:
        raise SidecarError("invalid corpus identifier")
    root = _repo_root(repo_root)
    try:
        rows = load_verified_corpus(root)
        frame = encode_corpus_id(corpus_id, repo_root=root)
        decoded = decode_frame(frame, repo_root=root)
        row = rows[corpus_id]
        record = to_reference_record(
            Translator(root / "data"), row["orthography"], direction="nt-en"
        )
        parsed = _parse_reference_evidence(record)
        if (record["origin"]["record_id"] != corpus_id
                or parsed.evidence_class != "AUTHOR_ATTESTED_CORPUS"
                or parsed.withheld or parsed.semantic_atoms is not None
                or parsed.qualification_eligible or parsed.learner_visible
                or decoded.source_id != corpus_id):
            raise SidecarError("V1 reference and typed observation do not agree")
        if record["target_text"] != row["english"]:
            raise SidecarError("source translation is not an exact V1 reference")
    except (AbstentionError, ChannelError, KeyError, ValueError, OSError) as exc:
        raise SidecarError("source-bound observation refused") from exc
    sidecar = {
        "schema": SCHEMA,
        "status": ACCEPTED,
        "origin_repo": ORIGIN_REPO,
        "corpus_id": corpus_id,
        "source_git_blob_sha1": EXPECTED_CORPUS_GIT_BLOB_SHA1,
        "reference_evidence_v1": record,
        "typed_frame_base64": base64.b64encode(frame).decode("ascii"),
        "qualification_eligible": False,
        "learner_visible": False,
        "source_independence": SOURCE_INDEPENDENCE,
    }
    if len(_strict_json(sidecar)) > MAX_SIDECAR_BYTES:
        raise SidecarError("sidecar exceeds maximum size")
    return sidecar


def parse_sidecar(raw: bytes | str, *, repo_root: str | Path | None = None) -> dict[str, Any]:
    """Canonical, exact-source revalidation; never returns a learner episode."""
    if type(raw) is str:
        try:
            incoming = raw.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise SidecarError("invalid UTF-8 sidecar") from exc
    elif type(raw) is bytes:
        incoming = raw
    else:
        raise SidecarError("sidecar must be UTF-8 JSON")
    if len(incoming) > MAX_SIDECAR_BYTES:
        raise SidecarError("sidecar exceeds maximum size")
    try:
        packet = json.loads(incoming.decode("utf-8"),
                            object_pairs_hook=_no_duplicate_keys,
                            parse_constant=_reject_nonfinite)
        if type(packet) is not dict or set(packet) != _KEYS:
            raise SidecarError("unexpected sidecar fields")
        if (_strict_json(packet) != incoming
                or packet["schema"] != SCHEMA
                or packet["status"] != ACCEPTED
                or packet["origin_repo"] != ORIGIN_REPO
                or packet["source_git_blob_sha1"] != EXPECTED_CORPUS_GIT_BLOB_SHA1
                or packet["qualification_eligible"] is not False
                or packet["learner_visible"] is not False
                or packet["source_independence"] != SOURCE_INDEPENDENCE):
            raise SidecarError("sidecar protocol mismatch")
        # Parse the *original V1 contract* rather than feeding extra semantic
        # fields into it. V1 must still reject semantic_atoms != null.
        _parse_reference_evidence(packet["reference_evidence_v1"])
        frame = base64.b64decode(packet["typed_frame_base64"], validate=True)
        decoded = decode_frame(frame, repo_root=_repo_root(repo_root))
        if decoded.source_id != packet["corpus_id"]:
            raise SidecarError("typed frame source mismatch")
        expected = build_sidecar(packet["corpus_id"], repo_root=repo_root)
        if _strict_json(expected) != incoming:
            raise SidecarError("sidecar disagrees with source-bound reference")
        return expected
    except (UnicodeDecodeError, json.JSONDecodeError, UnicodeEncodeError,
            binascii.Error, ValueError, TypeError, KeyError,
            RecursionError, ChannelError) as exc:
        raise SidecarError("invalid or unverified sidecar") from exc


def json_bytes(sidecar: dict[str, Any]) -> bytes:
    """Encode a checked sidecar as bounded canonical UTF-8 bytes."""
    return _strict_json(sidecar)
