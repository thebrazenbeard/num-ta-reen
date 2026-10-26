"""NONCANONICAL proposal: source-verified interlinear-gloss observations.

This module analyzes human-authored *English interlinear glosses*, not native
signals. Its tentative scope expressions are deliberately partial and cannot
translate or create novel Num'ta'reen expressions. No true-name representation
is returned from its public functions.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping


SCHEMA = "numtareen.proposal.semantic_ir.v1"
EVIDENCE = "SOURCE_VERIFIED_AUTHOR_INTERLINEAR_GLOSS"
EXPECTED_CORPUS_GIT_BLOB_SHA1 = "53d9f27d03579a1a3fc700c3394b56f834da784e"
_ROLES = frozenset({"AGT", "PAT", "SRC", "GOAL", "INST"})
_DISCOURSE = frozenset({"TOP", "FOC"})
_TAGS = _ROLES | _DISCOURSE | {"CONS"}
_EVIDENTIALS = frozenset({"EVID.WIT", "EVID.VRF"})
_ECHO = frozenset({"LOOP", "RET", "CLP"})
_LINKS = frozenset({"COMP", "REL"})
_POLARITY = frozenset({"NEG", "PROH"})
_PREDICATE_GLOSSES = frozenset({
    "align", "cross", "latch/stabilize", "latch", "record.LCH",
    "restore.balance", "ethic.eval", "THR", "INV-align", "SOFT-align",
    "record.GRANT", "boundary-THR", "SOFT-respect.silence", "FORB.ACT",
})
_PROTECTED_DELIMITERS = ("⟦", "⟧")


@dataclass(frozen=True)
class GlossAtom:
    index: int
    form: str
    gloss: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class Argument:
    index: int
    form: str
    referent_gloss: str
    role: str
    consent_marked: bool


@dataclass(frozen=True)
class SemanticPacket:
    schema: str
    corpus_id: str
    evidence: str
    withheld: bool
    atoms: tuple[GlossAtom, ...]
    predicates: tuple[GlossAtom, ...]
    arguments: tuple[Argument, ...]
    echo_operators: tuple[str, ...]
    evidentials: tuple[str, ...]
    discourse: tuple[str, ...]
    clause_links: tuple[str, ...]
    polarity: tuple[str, ...]
    interrogative: bool
    consent_locations: tuple[int, ...]
    unresolved_conflicts: tuple[str, ...]
    unmapped_atoms: tuple[int, ...]
    qualification_eligible: bool = False

    def to_dict(self, *, repo_root: str | Path | None = None) -> dict[str, Any]:
        """Serialize a nonprotected observation without laundering provenance.

        Frozen dataclasses can be forged with `dataclasses.replace`; neither
        they nor `evidence` strings are attestations. For any claim to the
        pinned author source, rederive the whole object before export.
        """
        result, exact_encoding = _safe_packet_serialization(self)
        # Never invoke a caller-owned str subclass's __eq__ to decide whether
        # to enforce source integrity. JSON decoding yields ordinary str.
        if json.loads(exact_encoding)["evidence"] == EVIDENCE:
            try:
                source_packet = analyze_corpus_id(self.corpus_id, repo_root=repo_root)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                raise ValueError("source attestation unavailable for packet serialization") from exc
            authentic_result, authentic_encoding = _safe_packet_serialization(source_packet)
            if exact_encoding != authentic_encoding:
                raise ValueError("packet differs from pinned author source")
            # Never return caller-owned str subclasses or nested objects even
            # when their JSON bytes happen to match the pinned source. A
            # subclass may override __str__, split(), or __repr__ and alter
            # the meaning of a later consumer's display/parse operation.
            return authentic_result
        return result


def _safe_packet_serialization(packet: SemanticPacket) -> tuple[dict[str, Any], str]:
    """Canonical, JSON-only packet comparison; reject subclasses and objects.

    Relying on dataclass `__eq__` can be circumvented with custom nested
    Python objects or subclasses. These objects should never contribute a
    source claim or a tentative semantic tree.
    """
    if type(packet) is not SemanticPacket:
        raise ValueError("expected an exact SemanticPacket")
    data = asdict(packet)
    try:
        encoded = json.dumps(data, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError) as exc:
        raise ValueError("packet has unsupported non-JSON fields") from exc
    if _contains_protected(encoded):
        raise ValueError("protected notation cannot enter packet serializer")
    return data, encoded


def _source_path(repo_root: str | Path | None = None) -> Path:
    if repo_root is None:
        repo_root = os.environ.get("NUMTAREEN_REPO_ROOT")
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]
    return Path(repo_root) / "data" / "corpus.json"


def load_verified_corpus(repo_root: str | Path | None = None) -> dict[str, dict[str, Any]]:
    """Refuse unpinned source snapshots; do not trust JSON metadata alone."""
    content = _source_path(repo_root).read_bytes()
    header = b"blob " + str(len(content)).encode("ascii") + b"\0"
    digest = hashlib.sha1(header + content).hexdigest()  # Git content-object ID
    if digest != EXPECTED_CORPUS_GIT_BLOB_SHA1:
        raise ValueError("corpus source digest mismatch; no attested evidence")
    payload = json.loads(content)
    rows = payload["records"]
    if len(rows) != 30 or {r["id"] for r in rows} != {f"E{i:02d}" for i in range(1, 31)}:
        raise ValueError("unexpected corpus schema or identifier set")
    return {r["id"]: r for r in rows}


def _contains_protected(text: str) -> bool:
    return any(delimiter in text for delimiter in _PROTECTED_DELIMITERS)


def parse_igt_pairs(igt: str) -> tuple[GlossAtom, ...]:
    """Lossless segmentation of ordinary, unprotected glosses only.

    This is not a semantic parser for Num'ta'reen orthography. Unsupported
    categories stay visible to the downstream fail-closed classifier.
    """
    if not isinstance(igt, str):
        raise ValueError("IGT must be text")
    if _contains_protected(igt):
        raise ValueError("protected notation cannot enter IGT parser")
    pieces = igt.split()
    if len(pieces) % 2:
        raise ValueError("IGT must contain paired form/gloss fields")
    if len(pieces) > 128:
        raise ValueError("IGT exceeds bounded proposal token count")
    return tuple(
        GlossAtom(i, pieces[2 * i], pieces[2 * i + 1],
                  tuple(pieces[2 * i + 1].split("=")[1:]))
        for i in range(len(pieces) // 2)
    )


def render_igt_pairs(atoms: tuple[GlossAtom, ...]) -> str:
    if any(_contains_protected(a.form) or _contains_protected(a.gloss) for a in atoms):
        raise ValueError("protected notation cannot enter IGT renderer")
    return " ".join(f"{a.form} {a.gloss}" for a in atoms)


def analyze_corpus_id(corpus_id: str, *, repo_root: str | Path | None = None) -> SemanticPacket:
    """Recommended entrypoint: select exclusively from a pinned source blob."""
    source = load_verified_corpus(repo_root)
    if corpus_id not in source:
        raise ValueError("unknown source corpus ID")
    return analyze_attested(source[corpus_id], repo_root=repo_root)


def analyze_attested(record: Mapping[str, Any], *,
                     repo_root: str | Path | None = None) -> SemanticPacket:
    """Require exact source-row equality before claiming an authored gloss.

    A caller-provided ID is not proof of attestation. This function intentionally
    rejects even IGT-only replicas lacking orthography, IPA, source notes, etc.
    """
    if not isinstance(record, Mapping):
        raise ValueError("corpus row must be a mapping")
    rid = record.get("id")
    if not isinstance(rid, str):
        raise ValueError("source corpus ID required")
    source = load_verified_corpus(repo_root)
    if rid not in source:
        raise ValueError("supplied row is not identical to pinned author source")
    try:
        candidate = json.dumps(dict(record), sort_keys=True, ensure_ascii=False,
                               allow_nan=False)
        expected = json.dumps(source[rid], sort_keys=True, ensure_ascii=False,
                              allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError("supplied row is not identical to pinned author source") from exc
    if candidate != expected:
        raise ValueError("supplied row is not identical to pinned author source")
    verified_row = source[rid]  # Never parse a caller-controlled lookalike.
    if rid == "E26" or any(_contains_protected(str(v)) for v in verified_row.values()):
        return SemanticPacket(SCHEMA, rid, EVIDENCE, True, (), (), (), (),
                              (), (), (), (), False, (), (), ())
    return _build_packet(rid, verified_row["igt"], EVIDENCE)


def analyze_unverified_igt(igt: str) -> SemanticPacket:
    """Classify hypothetical glosses without attributing them to the author.

    Every field is unverified. Callers cannot supply an ID or evidence label.
    Structural hypotheses remain optional and qualification-ineligible.
    """
    return _build_packet("UNVERIFIED", igt, "UNVERIFIED_SYNTHETIC_GLOSS")


def _build_packet(rid: str, igt: str, evidence_class: str) -> SemanticPacket:
    atoms = parse_igt_pairs(igt)
    predicates: list[GlossAtom] = []
    arguments: list[Argument] = []
    echo: list[str] = []
    evidence: list[str] = []
    discourse: list[str] = []
    links: list[str] = []
    polarity: list[str] = []
    consent: list[int] = []
    unmapped: list[int] = []
    conflicts: list[str] = []
    question = False

    for atom in atoms:
        parts = atom.gloss.split("=")
        base = parts[0]
        tags = set(parts[1:])
        roles = tags & _ROLES
        if len(roles) > 1:
            raise ValueError("conflicting role glosses require adjudication")
        role = next(iter(roles), None)
        if role:
            arguments.append(Argument(atom.index, atom.form, base, role,
                                      "CONS" in tags))
        if "CONS" in tags:
            consent.append(atom.index)
        for tag in atom.tags:
            if tag in _DISCOURSE:
                discourse.append(f"{atom.index}:{tag}")
        if atom.gloss in _ECHO:
            echo.append(atom.gloss)
        if atom.gloss in _EVIDENTIALS:
            evidence.append(atom.gloss)
        if atom.gloss in _LINKS:
            links.append(atom.gloss)
        if atom.gloss in _POLARITY:
            polarity.append(atom.gloss)
        if atom.gloss == "Q":
            question = True
        if base in _PREDICATE_GLOSSES:
            predicates.append(atom)
        if atom.form.casefold() == "së":
            conflicts.append("RELATIVIZER_FORM_CONFLICT")
        if atom.form.casefold() == "rhel":
            conflicts.append("RHEL_FUNCTION_CONFLICT")
        known = (role or tags & _DISCOURSE or "CONS" in tags
                 or base in _PREDICATE_GLOSSES or atom.gloss in _ECHO
                 or atom.gloss in _EVIDENTIALS or atom.gloss in _LINKS
                 or atom.gloss in _POLARITY or atom.gloss == "Q")
        if not known or tags - _TAGS or "" in tags:
            unmapped.append(atom.index)

    return SemanticPacket(SCHEMA, rid, evidence_class, False, atoms,
                          tuple(predicates), tuple(arguments), tuple(echo),
                          tuple(evidence), tuple(discourse), tuple(links),
                          tuple(polarity), question, tuple(consent),
                          tuple(dict.fromkeys(conflicts)), tuple(unmapped))


def proposed_scope_expression(
    packet: SemanticPacket, *, repo_root: str | Path | None = None
) -> dict[str, Any] | None:
    """Partial hypothesis; no novel operator stacking or conflict resolution.

    Known topic/focus features are preserved as opaque discourse annotations
    instead of promoting them to unvalidated scope operators. The scope tree
    only runs on exact source-verified observations; synthetic IGT can be
    inspected as typed atoms, never composed into a purported native rule.

    A SemanticPacket is an ordinary frozen dataclass, *not an unforgeable
    attestation*. The evidence string alone proves nothing: recompute the
    full packet from the pinned canonical source on EVERY tree request and
    require structural equality. This forbids `dataclasses.replace` from
    laundering a changed role/evidential/consent marker under an attested ID.
    Deliberate manual construction of a byte-for-byte identical observation
    is harmless because it cannot add new source claims.
    """
    if (type(packet) is not SemanticPacket or packet.evidence != EVIDENCE
            or packet.withheld
            or len(packet.predicates) != 1 or packet.clause_links
            or packet.unmapped_atoms or packet.unresolved_conflicts
            or len(packet.echo_operators) > 1 or len(packet.evidentials) > 1
            or len(packet.polarity) > 1):
        return None
    try:
        _, observed = _safe_packet_serialization(packet)
        independently_derived = analyze_corpus_id(packet.corpus_id, repo_root=repo_root)
        _, authentic = _safe_packet_serialization(independently_derived)
    except (OSError, ValueError, KeyError, TypeError):
        # Missing/mutated corpus means no authenticated source observation.
        return None
    if observed != authentic:
        return None
    # Byte-level equality does not imply behavioral equivalence for arbitrary
    # user-constructed Python subclasses. Build ONLY from newly parsed,
    # pinned source strings after validation, never the supplied packet.
    packet = independently_derived
    pred = packet.predicates[0]
    node: dict[str, Any] = {
        "op": "PRED", "gloss": pred.gloss.split("=")[0],
        "roles": [{"role": a.role, "referent": a.referent_gloss,
                   "consent": a.consent_marked, "atom_index": a.index}
                  for a in packet.arguments],
        "predicate_consent": pred.index in packet.consent_locations,
        "discourse": [{"atom_index": int(s.split(":", 1)[0]),
                       "kind": s.split(":", 1)[1],
                       "form": packet.atoms[int(s.split(":", 1)[0])].form,
                       "gloss": packet.atoms[int(s.split(":", 1)[0])].gloss}
                      for s in packet.discourse],
    }
    for op in packet.polarity:
        node = {"op": op, "argument": node}
    for op in packet.echo_operators:
        node = {"op": op, "argument": node}
    for op in packet.evidentials:
        node = {"op": op, "argument": node}
    if packet.interrogative:
        node = {"op": "Q", "argument": node}
    return node
