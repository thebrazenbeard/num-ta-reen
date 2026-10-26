"""NONCANONICAL, source-bound, typed *symbolic* Num'ta'reen observation channel.

This is not a Num'ta'reen translator, grammatical generator, native signal,
resonance model, or acoustic implementation. It can faithfully serialize the
author's bounded, verified interlinear-gloss observations without reducing
them to opaque utterance IDs or an English paraphrase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
import struct
from typing import Any

from research.semantic_ir_proposal import (
    EVIDENCE,
    EXPECTED_CORPUS_GIT_BLOB_SHA1,
    analyze_corpus_id,
)


SCHEMA = "numtareen.experimental.typed_semantic_channel.v1"
ACCEPTED = "SOURCE_BOUND_NONCANONICAL"
ABSTAIN = "ABSTAIN"
MAGIC = b"NTSP1"
HEADER_SIZE = len(MAGIC) + 4 + 32  # ASCII magic, unsigned big-endian length, SHA-256
MAX_DOCUMENT_BYTES = 16 * 1024


class ChannelError(ValueError):
    """A channel frame is corrupt, noncanonical, invalid or unattested."""


class AbstentionError(ValueError):
    """A source observation must not be encoded as accepted semantics."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


@dataclass(frozen=True)
class EncodeResult:
    status: str
    reason: str | None
    frame: bytes | None


@dataclass(frozen=True)
class DecodedPacket:
    """Verify against the pinned source again on EVERY public export.

    Frozen dataclasses are forgeable with direct construction/`replace`, so
    constructor success or equality is NOT source attestation. An untrusted
    edited `_canonical_document` cannot return semantics or claim an ID.
    """

    _canonical_document: bytes = field(repr=False)
    _repo_root: str | Path | None = field(default=None, repr=False)

    def _verified(self) -> dict[str, Any]:
        frame = _frame_document(self._canonical_document)
        return _verify_document_against_source(frame, repo_root=self._repo_root)

    @property
    def source_id(self) -> str:
        return self._verified()["provenance"]["source_id"]

    @property
    def semantic(self) -> dict[str, Any]:
        return self._verified()["semantic"]

    @property
    def provenance(self) -> dict[str, Any]:
        return self._verified()["provenance"]

    def reencode(self) -> bytes:
        """Reconstruct the precise deterministic symbolic carrier frame."""
        self._verified()
        return _frame_document(self._canonical_document)


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _frame_document(document: bytes) -> bytes:
    if not 0 < len(document) <= MAX_DOCUMENT_BYTES:
        raise ChannelError("invalid bounded document length")
    return MAGIC + struct.pack(">I", len(document)) + hashlib.sha256(document).digest() + document


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ChannelError("duplicate JSON field")
        result[key] = value
    return result


def _bad_constant(value: str) -> None:
    raise ChannelError("nonfinite numeric field")


def inspect_frame(frame: bytes) -> dict[str, Any]:
    """Parse frame for diagnostics ONLY; output is NOT source-attested.

    Consumers must call `decode_frame` for verified observations. SHA-256 is
    corruption detection, not an authentication key or a signature.
    """
    if type(frame) is not bytes or len(frame) < HEADER_SIZE:
        raise ChannelError("invalid frame type or truncated header")
    if frame[:len(MAGIC)] != MAGIC:
        raise ChannelError("wrong frame version/magic")
    declared = struct.unpack(">I", frame[len(MAGIC):len(MAGIC) + 4])[0]
    if not 0 < declared <= MAX_DOCUMENT_BYTES:
        raise ChannelError("document exceeds allowed bounds")
    if len(frame) != HEADER_SIZE + declared:
        raise ChannelError("invalid frame length")
    document = frame[HEADER_SIZE:]
    if hashlib.sha256(document).digest() != frame[len(MAGIC) + 4:HEADER_SIZE]:
        raise ChannelError("frame checksum mismatch")
    try:
        decoded = json.loads(document.decode("utf-8"),
                             object_pairs_hook=_unique_pairs,
                             parse_constant=_bad_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise ChannelError("invalid UTF-8 JSON") from exc
    if type(decoded) is not dict:
        raise ChannelError("expected a JSON object")
    try:
        if _canonical_bytes(decoded) != document:
            raise ChannelError("noncanonical JSON representation")
    except (ValueError, TypeError, RecursionError) as exc:
        raise ChannelError("invalid JSON data") from exc
    return decoded


def _observed_operators(atoms: tuple, category: tuple[str, ...]) -> list[dict[str, Any]]:
    allowed = set(category)
    observations = [{"atom_index": atom.index, "operator": atom.gloss}
                    for atom in atoms if atom.gloss in allowed]
    if tuple(entry["operator"] for entry in observations) != category:
        # Callers cannot invent new operators, reorder them, or elide repeats.
        raise AbstentionError("OPERATOR_OBSERVATION_INCONSISTENT")
    return observations


def _semantic_observation(source_id: str, *, repo_root: str | Path | None) -> dict[str, Any]:
    try:
        packet = analyze_corpus_id(source_id, repo_root=repo_root)
        # This rederives and attests the entire source packet rather than
        # trusting a caller-supplied SemanticPacket or an evidence label.
        packet.to_dict(repo_root=repo_root)
    except ValueError as exc:
        if str(exc) == "unknown source corpus ID":
            raise AbstentionError("UNKNOWN_SOURCE") from exc
        raise AbstentionError("SOURCE_ATTESTATION_FAILED") from exc
    except (OSError, KeyError, TypeError) as exc:
        raise AbstentionError("SOURCE_ATTESTATION_FAILED") from exc

    if packet.withheld:
        raise AbstentionError("PROTECTED_SOURCE")
    if packet.unresolved_conflicts:
        raise AbstentionError("SOURCE_CONFLICT")
    if packet.unmapped_atoms:
        raise AbstentionError("UNMAPPED_SOURCE_ATOMS")
    if packet.evidence != EVIDENCE:
        raise AbstentionError("UNVERIFIED_SOURCE")

    atoms = packet.atoms
    predicate_indices = {atom.index for atom in packet.predicates}
    argument_indices = {arg.index for arg in packet.arguments}
    locations = list(packet.consent_locations)
    discourse: list[dict[str, Any]] = []
    for item in packet.discourse:
        raw_index, tag = item.split(":", 1)
        index = int(raw_index)
        if index < 0 or index >= len(atoms) or tag not in ("TOP", "FOC"):
            raise AbstentionError("DISCOURSE_OBSERVATION_INCONSISTENT")
        discourse.append({"atom_index": index, "kind": tag,
                          "form": atoms[index].form, "gloss": atoms[index].gloss})

    return {
        # Source atom indices preserve linear order and distinguish distinct
        # referent/role assignments. Raw authored forms and glosses are
        # retained; none is replaced by an English sentence paraphrase.
        "atoms": [{"index": a.index, "form": a.form, "gloss": a.gloss,
                   "tags": list(a.tags)} for a in atoms],
        "predicates": [{"atom_index": a.index, "form": a.form,
                        "gloss": a.gloss.split("=", 1)[0]}
                       for a in packet.predicates],
        "arguments": [{"atom_index": a.index, "form": a.form,
                       "referent_gloss": a.referent_gloss, "role": a.role,
                       "consent_marked": a.consent_marked}
                      for a in packet.arguments],
        "discourse": discourse,
        "interrogative": packet.interrogative,
        "interrogative_indices": [a.index for a in atoms if a.gloss == "Q"],
        "polarity": _observed_operators(atoms, packet.polarity),
        "echo": _observed_operators(atoms, packet.echo_operators),
        "evidential": _observed_operators(atoms, packet.evidentials),
        "clause_links": _observed_operators(atoms, packet.clause_links),
        "consent": {
            "atom_indices": locations,
            "predicate_indices": [i for i in locations if i in predicate_indices],
            "argument_indices": [i for i in locations if i in argument_indices],
            "unattached_indices": [i for i in locations
                                   if i not in predicate_indices and i not in argument_indices],
        },
        # Deliberate uncertainty: these features are reliable author-IGT
        # observations; full semantic scope, embedding, and fluent generation
        # have NOT been established. Multiple predicates need adjudication.
        "ambiguity": {
            "composition_status": ("PARTIAL_SINGLE_PREDICATE"
                                   if len(packet.predicates) == 1 and not packet.clause_links
                                   else "UNRESOLVED_MULTI_CLAUSE_OR_PREDICATE"),
            "scope_unestablished": True,
            "unresolved_conflicts": list(packet.unresolved_conflicts),
            "unmapped_atom_indices": list(packet.unmapped_atoms),
            "abstained": False,
        },
    }


def encode_corpus_id(source_id: str, *, repo_root: str | Path | None = None) -> bytes:
    """Build a source-verified symbolic frame from compositional observations.

    `source_id` is the *authored corpus citation* in transport provenance,
    NOT a new semantic codeword and NOT how utterances are distinguished.
    """
    if type(source_id) is not str or not source_id:
        raise AbstentionError("UNKNOWN_SOURCE")
    semantic = _semantic_observation(source_id, repo_root=repo_root)
    document = {
        "schema": SCHEMA,
        "status": ACCEPTED,
        "provenance": {
            "source_id": source_id,
            "source_git_blob_sha1": EXPECTED_CORPUS_GIT_BLOB_SHA1,
            "source_evidence": EVIDENCE,
            "output_canonicality": "NONCANONICAL_EXPERIMENTAL_AUTHOR_IGT_OBSERVATION",
        },
        "semantic": semantic,
    }
    return _frame_document(_canonical_bytes(document))


def encode_or_abstain(source_id: str, *, repo_root: str | Path | None = None) -> EncodeResult:
    """Expose explicit acceptance/abstention without emitting a fake frame."""
    try:
        return EncodeResult(ACCEPTED, None, encode_corpus_id(source_id, repo_root=repo_root))
    except AbstentionError as exc:
        return EncodeResult(ABSTAIN, exc.reason, None)


def _verify_document_against_source(
    frame: bytes, *, repo_root: str | Path | None
) -> dict[str, Any]:
    """Source verification shared by decode AND DecodedPacket property access."""
    document = inspect_frame(frame)
    if set(document) != {"schema", "status", "provenance", "semantic"}:
        raise ChannelError("unexpected document fields")
    if document["schema"] != SCHEMA or document["status"] != ACCEPTED:
        raise ChannelError("unsupported typed channel schema or status")
    provenance = document["provenance"]
    if type(provenance) is not dict or type(provenance.get("source_id")) is not str:
        raise ChannelError("missing source provenance")
    source_id = provenance["source_id"]
    try:
        expected = encode_corpus_id(source_id, repo_root=repo_root)
    except AbstentionError as exc:
        raise ChannelError("frame source cannot be attested: " + exc.reason) from exc
    if frame != expected:
        raise ChannelError("frame differs from the pinned source observation")
    return document


def decode_frame(frame: bytes, *, repo_root: str | Path | None = None) -> DecodedPacket:
    """Reject source-mismatched or rewritten semantics; return rechecking view.

    Even a syntactically valid frame with a recomputed checksum does not
    become author attestation: the entire frame must match the fresh encoding
    of the pinned source. All subsequent property exports recheck again.
    """
    _verify_document_against_source(frame, repo_root=repo_root)
    return DecodedPacket(_canonical_document=frame[HEADER_SIZE:], _repo_root=repo_root)


def canonical_semantics(frame: bytes, *, repo_root: str | Path | None = None) -> bytes:
    """Semantic comparison bytes, excluding the authored source citation.

    This independent payload comparison is the key anti-utterance-ID test:
    contrasts must be caused by typed features, not arbitrary record IDs.
    """
    return _canonical_bytes(decode_frame(frame, repo_root=repo_root).semantic)
