"""NONCANONICAL and deliberately lossy semantic-to-packet projection.

This module is a falsification instrument, not a Num'ta'reen translator,
language specification, semantic encoder, or authored acoustic model.
The returned loss ledger must accompany any packet shown in research.
"""

from dataclasses import dataclass

from research.semantic_ir_proposal import analyze_corpus_id
from numtareen.experimental_resonance_packet import Packet


EVIDENTIAL = {"EVID.WIT": "witnessed", "EVID.VRF": "verified"}
ECHO = {"LOOP": "loop", "RET": "return", "CLP": "collapse"}


@dataclass(frozen=True)
class LossyProjection:
    packet: Packet
    discarded: tuple[str, ...]


def project_lossy(corpus_id: str) -> LossyProjection:
    """Map only verified, resolved authored observations to a *smaller* code.

    Any native meaning omitted by Packet is declared explicitly. Contradicted,
    unmapped, and protected source rows are refused; no native acoustic
    realization or true-name notation is emitted.
    """
    ir = analyze_corpus_id(corpus_id)
    if ir.withheld or ir.unresolved_conflicts or ir.unmapped_atoms:
        raise ValueError("withheld, conflicted or unmapped source observations")
    if len(ir.evidentials) > 1 or len(ir.echo_operators) > 1:
        raise ValueError("unsupported operator stacking")
    lost = ["lexical_predicate", "referent_identity", "channel_scope_unassigned"]
    if len(ir.arguments) > 1:
        lost.append("argument_order")
    if ir.discourse:
        lost.append("discourse_topic_focus")
    if ir.interrogative:
        lost.append("interrogative")
    if ir.polarity:
        lost.append("independent_polarity")
    if ir.clause_links:
        lost.append("clause_links")
    if ir.consent_locations:
        lost.append("consent_loci_reduced_to_boolean")

    evidence = EVIDENTIAL[ir.evidentials[0]] if ir.evidentials else "unmarked"
    echo = ECHO[ir.echo_operators[0]] if ir.echo_operators else "plain"
    # INV is an explicit author gloss. This is NOT a lexical inverse rule.
    inversion = "inverse" if any(p.gloss.startswith("INV-") for p in ir.predicates) else "normal"
    packet = Packet(
        roles=frozenset(x.role for x in ir.arguments),
        evidence=evidence,
        echo=echo,
        consent="present" if ir.consent_locations else "unmarked",
        inversion=inversion,
        scope="narrow",  # synthetic placeholder; NOT authored phonosemantics
    )
    return LossyProjection(packet, tuple(lost))


def require_lossless(corpus_id: str) -> Packet:
    """Fail closed; no authored corpus row admits a lossless Packet encoding."""
    projection = project_lossy(corpus_id)
    if projection.discarded:
        raise ValueError("no source-justified lossless semantic-to-waveform encoding")
    return projection.packet
