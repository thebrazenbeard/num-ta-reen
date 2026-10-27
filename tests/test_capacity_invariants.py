"""Noncanonical capacity/identity checks against source-authored observations.

No waveform or protected chord is generated. All source data are checked by
the existing pinned-corpus analyzer, not reproduced here.
"""

from collections import Counter, defaultdict
import hashlib
import json
import math
import os
from pathlib import Path
import random
import struct
import unittest

from numtareen.experimental_resonance_packet import FEATURES, all_symbolic_packets
from research.alignment_projection import project_lossy
from research.semantic_ir_proposal import analyze_corpus_id, load_verified_corpus
from research.typed_semantic_channel import (
    HEADER_SIZE, MAGIC, ChannelError, decode_frame, encode_corpus_id, inspect_frame,
)


ROOT = Path(os.environ.get("NUMTAREEN_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()


def observations():
    rows = load_verified_corpus(ROOT)
    accepted = []
    refused = []
    for corpus_id in sorted(rows):
        p = analyze_corpus_id(corpus_id, repo_root=ROOT)
        if p.withheld or p.unresolved_conflicts or p.unmapped_atoms:
            refused.append(corpus_id)
        else:
            accepted.append(corpus_id)
    return accepted, refused


class CapacityInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ids, cls.refused = observations()

    def test_c1_projection_is_not_injective_on_attested_observations(self):
        self.assertEqual(len(self.ids), 27)
        self.assertEqual(self.refused, ["E13", "E23", "E26"])
        groups = defaultdict(list)
        for corpus_id in self.ids:
            groups[project_lossy(corpus_id).packet].append(corpus_id)
        self.assertEqual(len(groups), 16)
        collided = [ids for ids in groups.values() if len(ids) > 1]
        self.assertEqual(len(collided), 5)
        self.assertEqual(sum(len(g) * (len(g) - 1) // 2 for g in collided), 21)
        # A pair with distinct source predicates but identical packet.
        self.assertEqual(project_lossy("E01").packet, project_lossy("E07").packet)
        self.assertNotEqual(analyze_corpus_id("E01", repo_root=ROOT).predicates,
                            analyze_corpus_id("E07", repo_root=ROOT).predicates)

    def test_c2_capacity_is_not_semantic_injectivity(self):
        axes_product = math.prod(len(choices) for _, choices in FEATURES)
        self.assertEqual(axes_product, 3072)
        self.assertEqual(len(tuple(all_symbolic_packets())), axes_product)
        self.assertEqual(math.ceil(math.log2(len(self.ids))), 5)
        self.assertEqual(math.ceil(math.log2(axes_product)), 12)
        self.assertGreater(axes_product, len(self.ids))

    def test_c3_typed_source_observations_remain_distinct_and_round_trip(self):
        semantic_fingerprints = set()
        for corpus_id in self.ids:
            frame = encode_corpus_id(corpus_id, repo_root=ROOT)
            decoded = decode_frame(frame, repo_root=ROOT)
            self.assertEqual(decoded.source_id, corpus_id)
            self.assertEqual(decoded.reencode(), frame)
            semantic_fingerprints.add(json.dumps(decoded.semantic, sort_keys=True, ensure_ascii=False))
        self.assertEqual(len(semantic_fingerprints), len(self.ids))

    def test_c4_length_framing_and_digest_non_authentication(self):
        first = encode_corpus_id("E01", repo_root=ROOT)
        second = encode_corpus_id("E07", repo_root=ROOT)
        stream = first + second
        segments = []
        while stream:
            self.assertTrue(stream.startswith(MAGIC))
            declared = struct.unpack(">I", stream[len(MAGIC):len(MAGIC)+4])[0]
            n = HEADER_SIZE + declared
            segments.append(stream[:n])
            stream = stream[n:]
        self.assertEqual(segments, [first, second])
        with self.assertRaises(ChannelError):
            decode_frame(first + b"suffix", repo_root=ROOT)
        with self.assertRaises(ChannelError):
            decode_frame(first[:-1], repo_root=ROOT)

        # Anyone can recompute unkeyed SHA-256; only the SOURCE recheck
        # rejects a syntactically valid but false semantic claim.
        body = inspect_frame(first)
        body["provenance"]["source_id"] = "E07"
        data = json.dumps(body, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
        forged = MAGIC + struct.pack(">I", len(data)) + hashlib.sha256(data).digest() + data
        self.assertEqual(inspect_frame(forged)["provenance"]["source_id"], "E07")
        with self.assertRaises(ChannelError):
            decode_frame(forged, repo_root=ROOT)

    def test_c5_bijective_relabeling_cannot_remove_collisions(self):
        all_packets = tuple(all_symbolic_packets())
        index = {packet: i for i, packet in enumerate(all_packets)}
        rng = random.Random(1729)
        permutation = list(range(len(all_packets)))
        rng.shuffle(permutation)
        old = Counter(index[project_lossy(cid).packet] for cid in self.ids)
        new = Counter(permutation[index[project_lossy(cid).packet]] for cid in self.ids)
        self.assertEqual(sorted(old.values()), sorted(new.values()))
        self.assertEqual(len(old), len(new))


if __name__ == "__main__":
    unittest.main()
