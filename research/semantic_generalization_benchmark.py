"""NONCANONICAL evaluation harness for source-bound semantic generalization.

This is a *negative-control* experiment. It does not invent Nûm'ta'reen
utterances, train a translator, or grade novel syntax without author labels.
The 30-row source corpus is publicly readable and therefore not a blind set.
"""

from __future__ import annotations

import hashlib
import json
import random
from collections import defaultdict
from dataclasses import asdict, dataclass

from numtareen.engine import Translator, normalize
from research.alignment_projection import project_lossy
from research.semantic_ir_proposal import (
    EVIDENCE, SemanticPacket, analyze_corpus_id, load_verified_corpus,
)


SCHEMA = "numtareen.research.generalization_negative_controls.v0"
SEED = 20261026
PACKET_CAPACITY = 3072

# Source-attested near contrasts, *not* author-tested productive minimal pairs.
# Different lexemes may accompany a grammatical difference (e.g. E07/E18).
CONTRASTS = (
    ("E01", "E05", "predicate_focus"),
    ("E01", "E08", "question"),
    ("E02", "E03", "argument_order"),
    ("E01", "E15", "echo_loop"),
    ("E07", "E18", "predicate_and_argument_consent"),
)

# These prompts have no creator-approved target sentences or meanings. They
# are therefore proposal-only, excluded from every numerical accuracy claim.
UNSCORED_PROBES = (
    ("P01", "novel_lexical_predicate", ("E01", "E07")),
    ("P02", "question_scope_outside_attested_context", ("E01", "E08")),
    ("P03", "focus_topic_combination", ("E04", "E05")),
    ("P04", "new_argument_order_and_referent", ("E02", "E03")),
    ("P05", "consent_grant_vs_active_revocation", ("E18", "E20", "E21")),
    ("P06", "predicate_vs_participant_consent", ("E07", "E18")),
    ("P07", "echo_loop_under_question", ("E08", "E15")),
    ("P08", "unknown_stem_and_clitic", ("E01",)),
)


@dataclass(frozen=True)
class BenchmarkObservation:
    corpus_id: str
    feature_tags: tuple[str, ...]
    semantic_signature: str
    acoustic_packet: str


def _features(ir) -> tuple[str, ...]:
    tags = ["predicate"]
    if ir.arguments:
        tags.append("argument")
    if len(ir.arguments) > 1:
        tags.append("multi_argument_order")
    if ir.discourse:
        tags.append("topic_or_focus")
    if ir.interrogative:
        tags.append("question")
    if ir.evidentials:
        tags.append("evidential")
    if ir.echo_operators:
        tags.append("echo")
    if ir.consent_locations:
        tags.append("consent")
    if ir.polarity:
        tags.append("polarity")
    return tuple(tags)


def semantic_signature(ir) -> str:
    """Extract interpretable source-gloss fields; never include corpus ID.

    This is a source-observation fingerprint, not an inferred native meaning.
    It is computed from pinned IGT and does not accept invented strings.
    """
    # The dataclass type is forgeable. Its source-verifying exporter checks the
    # exact pinned author row and returns freshly parsed built-in objects.
    # Read only that return value, not caller-owned fields or their methods.
    if type(ir) is not SemanticPacket:
        raise ValueError("source observation requires exact semantic packet type")
    verified = SemanticPacket.to_dict(ir)
    if (verified["evidence"] != EVIDENCE or verified["withheld"]
            or verified["unresolved_conflicts"] or verified["unmapped_atoms"]):
        raise ValueError("no complete attested semantic observation")
    fields = {
        "predicate_glosses": [(p["gloss"], p["tags"]) for p in verified["predicates"]],
        "ordered_arguments": [
            (a["role"], a["referent_gloss"], a["consent_marked"])
            for a in verified["arguments"]
        ],
        "discourse": verified["discourse"],
        "question": verified["interrogative"],
        "polarity": verified["polarity"],
        "echo": verified["echo_operators"],
        "evidentials": verified["evidentials"],
        "consent_loci": verified["consent_locations"],
        "clause_links": verified["clause_links"],
    }
    return json.dumps(fields, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def packet_key(packet) -> str:
    """Stable JSON representation of the old synthetic structural packet."""
    p = asdict(packet)
    p["roles"] = sorted(p["roles"])
    return json.dumps(p, sort_keys=True, separators=(",", ":"))


def eligible_observations() -> tuple[dict, tuple[BenchmarkObservation, ...], tuple[str, ...]]:
    """Use the Git-object-pinned source, abstaining on all unlicensed rows."""
    source = load_verified_corpus()
    accepted = []
    refused = []
    for corpus_id in sorted(source):
        ir = analyze_corpus_id(corpus_id)
        if ir.withheld or ir.unresolved_conflicts or ir.unmapped_atoms:
            refused.append(corpus_id)
            continue
        try:
            lossy = project_lossy(corpus_id)
        except ValueError:
            refused.append(corpus_id)
            continue
        accepted.append(BenchmarkObservation(
            corpus_id, _features(ir), semantic_signature(ir), packet_key(lossy.packet)
        ))
    return source, tuple(accepted), tuple(refused)


def _loo_exact_lookup(source: dict, accepted: tuple[BenchmarkObservation, ...]) -> dict:
    """Evaluate training-only sentence memorization under all held-out folds.

    Each test utterance is excluded before building either direction's index.
    A source oracle is intentionally not made available to the prediction.
    """
    errors = []
    feature_folds = defaultdict(int)
    keys = {r.corpus_id for r in accepted}
    for obs in accepted:
        train = [source[x] for x in keys - {obs.corpus_id}]
        nt_index = {normalize(r["orthography_index"]) for r in train}
        en_index = {normalize(r["english"]) for r in train}
        test = source[obs.corpus_id]
        nt_hit = normalize(test["orthography_index"]) in nt_index
        en_hit = normalize(test["english"]) in en_index
        errors.append((obs.corpus_id, nt_hit, en_hit))
        for feature in obs.feature_tags:
            feature_folds[feature] += 1
    return {
        "folds": len(errors),
        "train_rows_per_fold": max(0, len(accepted) - 1),
        "nt_en_exact_hits": sum(x[1] for x in errors),
        "en_nt_exact_hits": sum(x[2] for x in errors),
        "abstaining_folds_both_directions": sum(not n and not e for _, n, e in errors),
        "feature_tagged_folds": dict(sorted(feature_folds.items())),
        "note": "In-repository public corpus; these are stress folds, not sealed blind evaluation.",
    }


def benchmark() -> dict:
    """Return only aggregate scores, corpus IDs and proposal labels (no E26)."""
    source, accepted, refused = eligible_observations()
    if not accepted:
        raise ValueError("no eligible observations")
    signatures = {r.corpus_id: r.semantic_signature for r in accepted}
    acoustics = {r.corpus_id: r.acoustic_packet for r in accepted}
    groups = defaultdict(list)
    for cid, key in acoustics.items():
        groups[key].append(cid)
    collisions = tuple(sorted(
        (tuple(sorted(ids)) for ids in groups.values() if len(ids) > 1),
        key=lambda ids: ids
    ))
    pairs = []
    for left, right, contrast in CONTRASTS:
        if left not in signatures or right not in signatures:
            raise ValueError(f"predeclared source contrast unavailable: {contrast}")
        pairs.append({
            "ids": [left, right],
            "contrast": contrast,
            "source_fingerprints_differ": signatures[left] != signatures[right],
            "synthetic_acoustic_packets_equal": acoustics[left] == acoustics[right],
        })

    # Opaque labels are sampled *without replacement*. Thus they can encode
    # remembered corpus IDs yet provide no rule for a never-seen utterance.
    rng = random.Random(SEED)
    arbitrary = dict(zip(sorted(signatures), rng.sample(range(PACKET_CAPACITY), len(signatures))))
    label_digest = hashlib.sha256(json.dumps(arbitrary, sort_keys=True).encode()).hexdigest()

    # Probe candidate stems are deliberately not constructed as language.
    # An ASCII nonsense token tests the operational unknown policy only.
    unknown = "__NUMTAREEN_OOV_NONCANONICAL_20261026__"
    translator = Translator()
    nt_status = translator.translate(unknown, direction="nt-en")["status"]
    en_status = translator.translate(unknown, direction="en-nt")["status"]

    return {
        "schema": SCHEMA,
        "evidence_class": "SOURCE_VERIFIED_AUTHOR_GLOSS_NEGATIVE_CONTROL",
        "authored_rows": len(source),
        "eligible_rows": len(accepted),
        "refused_ids": list(refused),
        "holdout": _loo_exact_lookup(source, accepted),
        "semantic_fingerprint_unique": len(set(signatures.values())),
        "old_synthetic_packet_unique": len(groups),
        "old_synthetic_collision_groups": [list(x) for x in collisions],
        "old_synthetic_colliding_pairs": sum(len(x) * (len(x) - 1) // 2 for x in collisions),
        "known_source_contrasts": pairs,
        "opaque_random_label_control": {
            "seed": SEED, "slots": PACKET_CAPACITY,
            "unique_labels_assigned_in_sample": len(set(arbitrary.values())),
            "held_out_semantic_generalization_credit": 0,
            "mapping_sha256": label_digest,
            "note": "ID labels fit samples but convey no productive mapping or unseen test prediction.",
        },
        "unknown_input_policy": {"nt_en": nt_status, "en_nt": en_status},
        "unscored_author_probes": [
            {"id": pid, "contrast": tag, "source_anchors": list(anchors),
             "status": "UNSCORED_NEEDS_AUTHOR_CREATED_FORMS_AND_JUDGMENTS"}
            for pid, tag, anchors in UNSCORED_PROBES
        ],
    }


def main() -> int:
    print(json.dumps(benchmark(), ensure_ascii=True, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
