"""Print only aggregate capacity diagnostics; no source words or E26 notation."""

from collections import Counter
import json
import math
import os
from pathlib import Path

from numtareen.experimental_resonance_packet import FEATURES
from research.alignment_projection import project_lossy
from research.semantic_ir_proposal import analyze_corpus_id, load_verified_corpus
from research.typed_semantic_channel import decode_frame, encode_corpus_id


def census(repo_root: str | Path | None = None) -> dict:
    repo = Path(repo_root or os.environ.get("NUMTAREEN_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()
    ids = sorted(load_verified_corpus(repo))
    eligible = []
    excluded = []
    for corpus_id in ids:
        packet = analyze_corpus_id(corpus_id, repo_root=repo)
        if packet.withheld or packet.unresolved_conflicts or packet.unmapped_atoms:
            excluded.append(corpus_id)
        else:
            eligible.append(corpus_id)
    structural = Counter(project_lossy(cid).packet for cid in eligible)
    semantic = set()
    for cid in eligible:
        frame = encode_corpus_id(cid, repo_root=repo)
        packet = decode_frame(frame, repo_root=repo)
        semantic.add(json.dumps(packet.semantic, sort_keys=True, ensure_ascii=False))
    axis_capacity = math.prod(len(choices) for _, choices in FEATURES)
    collided = [n for n in structural.values() if n > 1]
    return {
        "source_entries": len(ids),
        "eligible": len(eligible),
        "excluded_ids_only": excluded,
        "old_structural_packet_types": len(structural),
        "old_colliding_groups": len(collided),
        "old_colliding_pairs": sum(n * (n - 1) // 2 for n in collided),
        "new_typed_observation_types": len(semantic),
        "old_total_synthetic_states": axis_capacity,
        "minimum_opaque_bits_for_eligible_ids": math.ceil(math.log2(len(eligible))),
        "minimum_fixed_width_bits_for_3072_states": math.ceil(math.log2(axis_capacity)),
    }


if __name__ == "__main__":
    print(json.dumps(census(), sort_keys=True, ensure_ascii=True))
