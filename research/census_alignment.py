"""Exploratory corpus collision census, never a translator.

From a checkout containing the semantic IR proposal:
  python -m research.census_alignment

Output is only IDs and counts, never utterances or protected notation.
The research projection refuses all unresolved and protected entries.
"""

import json

from research.alignment_projection import project_lossy
from research.semantic_ir_proposal import load_verified_corpus


def census() -> dict:
    packets = {}
    rejected = []
    # Enumerate actual SHA-pinned source IDs; a future source revision must not
    # silently disappear merely because an experiment once had 30 rows.
    source_ids = sorted(load_verified_corpus())
    for key in source_ids:
        try:
            packets[key] = project_lossy(key).packet
        except ValueError:
            rejected.append(key)
    groups = {}
    for key, packet in packets.items():
        groups.setdefault(packet, []).append(key)
    return {
        "authored_rows": len(source_ids),
        "projected_rows": len(packets),
        "rejected_ids": rejected,
        "distinct_synthetic_packets": len(groups),
        "collisions_by_authored_id": [
            ids for ids in groups.values() if len(ids) > 1
        ],
    }


if __name__ == "__main__":
    print(json.dumps(census(), indent=2, ensure_ascii=True))
