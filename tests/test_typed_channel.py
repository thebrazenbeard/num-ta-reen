"""Source-bound tests; no native waveform or alien signaling is inferred."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch

from research.typed_semantic_channel import (
    ABSTAIN,
    ACCEPTED,
    AbstentionError,
    ChannelError,
    canonical_semantics,
    decode_frame,
    encode_corpus_id,
    encode_or_abstain,
    inspect_frame,
)
from research.alignment_projection import project_lossy


# Works when integrated into the real repository at tests/, and with a source
# fixture specified by environment for isolated scratch checkout testing.
ROOT = Path(os.environ.get("NUMTAREEN_REPO_ROOT", Path(__file__).resolve().parents[1])).resolve()


class TypedChannelTests(unittest.TestCase):
    def source(self, corpus_id):
        return encode_corpus_id(corpus_id, repo_root=ROOT)

    def semantic(self, corpus_id):
        return canonical_semantics(self.source(corpus_id), repo_root=ROOT)

    def old_packet(self, corpus_id):
        # Existing v82 source-root contract, isolated from global environment.
        with patch.dict(os.environ, {"NUMTAREEN_REPO_ROOT": str(ROOT)}):
            return project_lossy(corpus_id).packet

    def test_lossy_predicate_collision_now_distinct(self):
        self.assertNotEqual(self.semantic("E01"), self.semantic("E07"))
        a, b = json.loads(self.semantic("E01")), json.loads(self.semantic("E07"))
        self.assertEqual([p["gloss"] for p in a["predicates"]], ["align"])
        self.assertEqual([p["gloss"] for p in b["predicates"]], ["latch/stabilize"])

    def test_lossy_topic_focus_collision_now_distinct(self):
        self.assertNotEqual(self.semantic("E01"), self.semantic("E05"))
        doc = json.loads(self.semantic("E05"))
        self.assertEqual([d["kind"] for d in doc["discourse"]], ["FOC"])

    def test_lossy_interrogative_collision_now_distinct(self):
        self.assertNotEqual(self.semantic("E01"), self.semantic("E08"))
        self.assertTrue(json.loads(self.semantic("E08"))["interrogative"])

    def test_lossy_argument_order_collision_now_distinct(self):
        self.assertNotEqual(self.semantic("E02"), self.semantic("E03"))
        self.assertEqual([a["role"] for a in json.loads(self.semantic("E02"))["arguments"]], ["AGT", "PAT"])
        self.assertEqual([a["role"] for a in json.loads(self.semantic("E03"))["arguments"]], ["PAT", "AGT"])

    def test_dual_consent_loci_remain_separate(self):
        doc = json.loads(self.semantic("E18"))
        self.assertEqual(doc["consent"]["atom_indices"], [0, 1])
        self.assertEqual([a["consent_marked"] for a in doc["arguments"]], [True])
        self.assertEqual(doc["consent"]["predicate_indices"], [0])
        self.assertEqual(doc["consent"]["argument_indices"], [1])
        self.assertEqual(doc["consent"]["unattached_indices"], [])

    def test_echo_evidential_and_predicate_consent_are_distinct(self):
        self.assertNotEqual(self.semantic("E01"), self.semantic("E15"))
        self.assertEqual(json.loads(self.semantic("E15"))["echo"][0]["operator"], "LOOP")
        self.assertNotEqual(self.semantic("E20"), self.semantic("E21"))
        self.assertEqual(json.loads(self.semantic("E21"))["consent"]["predicate_indices"], [0])
        self.assertEqual(json.loads(self.semantic("E06"))["evidential"][0]["operator"], "EVID.VRF")

    def test_all_unconflicted_unprotected_rows_roundtrip(self):
        accepted = []
        refused = []
        for n in range(1, 31):
            sid = f"E{n:02d}"
            result = encode_or_abstain(sid, repo_root=ROOT)
            if result.status == ACCEPTED:
                accepted.append(sid)
                frame = result.frame
                self.assertEqual(frame, self.source(sid))
                parsed = decode_frame(frame, repo_root=ROOT)
                self.assertEqual(parsed.source_id, sid)
                self.assertEqual(frame, parsed.reencode())
                self.assertEqual(json.loads(self.semantic(sid)), parsed.semantic)
                self.assertIn(parsed.semantic["ambiguity"]["composition_status"],
                              ("PARTIAL_SINGLE_PREDICATE", "UNRESOLVED_MULTI_CLAUSE_OR_PREDICATE"))
                self.assertEqual(parsed.semantic["ambiguity"]["unmapped_atom_indices"], [])
            else:
                refused.append((sid, result.reason))
        self.assertEqual(len(accepted), 27)
        self.assertEqual([sid for sid, _ in refused], ["E13", "E23", "E26"])

    def test_source_conflicts_and_protection_and_unknown_abstain(self):
        for sid, reason in (("E13", "SOURCE_CONFLICT"),
                            ("E23", "SOURCE_CONFLICT"),
                            ("E26", "PROTECTED_SOURCE"),
                            ("E99", "UNKNOWN_SOURCE")):
            with self.subTest(sid=sid):
                result = encode_or_abstain(sid, repo_root=ROOT)
                self.assertEqual(result.status, ABSTAIN)
                self.assertEqual(result.reason, reason)
                self.assertIsNone(result.frame)
                with self.assertRaises(AbstentionError):
                    self.source(sid)

    def test_checksum_length_and_truncated_frames_rejected(self):
        frame = self.source("E01")
        for invalid in (b"", frame[:15], frame[:-1], frame + b"x",
                        frame[:9] + b"0" + frame[10:],
                        frame[:45] + b"!" + frame[46:],
                        b"NOPE!" + frame[5:]):
            with self.subTest(invalid=invalid[:14]), self.assertRaises(ChannelError):
                decode_frame(invalid, repo_root=ROOT)

    def test_rehashed_forged_semantic_data_rejected(self):
        frame = self.source("E01")
        doc = inspect_frame(frame)
        doc["semantic"]["interrogative"] = True
        canonical = json.dumps(doc, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        payload = b"NTSP1" + struct.pack(">I", len(canonical)) + hashlib.sha256(canonical).digest() + canonical
        with self.assertRaises(ChannelError):
            decode_frame(payload, repo_root=ROOT)

    def test_forged_decodedpacket_dataclass_cannot_export_source_claims(self):
        authentic = decode_frame(self.source("E01"), repo_root=ROOT)
        document = inspect_frame(self.source("E01"))
        document["semantic"]["interrogative"] = True
        doctext = json.dumps(document, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
        forged = replace(authentic, _canonical_document=doctext)
        for getter in (lambda: forged.semantic, lambda: forged.source_id,
                       lambda: forged.provenance, forged.reencode):
            with self.assertRaises(ChannelError):
                getter()
        document = inspect_frame(self.source("E01"))
        document["provenance"]["source_id"] = "E07"
        doctext = json.dumps(document, ensure_ascii=False, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode("utf-8")
        forged_id = replace(authentic, _canonical_document=doctext)
        with self.assertRaises(ChannelError):
            _ = forged_id.source_id

    def test_noncanonical_duplicate_keys_and_oversized_frames_rejected(self):
        frame = self.source("E01")
        canonical = frame[41:]
        bad = canonical[:-1] + b',"semantic":null}'
        forged = b"NTSP1" + struct.pack(">I", len(bad)) + hashlib.sha256(bad).digest() + bad
        with self.assertRaises(ChannelError):
            decode_frame(forged, repo_root=ROOT)
        with self.assertRaises(ChannelError):
            inspect_frame(b"NTSP1" + struct.pack(">I", 1000000) + b"\0" * 32)

    def test_deeply_nested_corrupt_frame_fails_closed(self):
        bad = b"[" * 1300 + b"0" + b"]" * 1300
        forged = b"NTSP1" + struct.pack(">I", len(bad)) + hashlib.sha256(bad).digest() + bad
        with self.assertRaises(ChannelError):
            decode_frame(forged, repo_root=ROOT)

    def test_mutated_corpus_invalidates_encode_and_decode(self):
        original_frame = self.source("E01")
        with tempfile.TemporaryDirectory() as td:
            data = Path(td) / "data"
            data.mkdir()
            original = (ROOT / "data" / "corpus.json").read_bytes()
            (data / "corpus.json").write_bytes(original + b" ")
            result = encode_or_abstain("E01", repo_root=td)
            self.assertEqual((result.status, result.reason),
                             (ABSTAIN, "SOURCE_ATTESTATION_FAILED"))
            with self.assertRaises(ChannelError):
                decode_frame(original_frame, repo_root=td)

    def test_source_provenance_only_in_envelope(self):
        e1 = inspect_frame(self.source("E01"))
        self.assertIn("source_id", e1["provenance"])
        self.assertNotIn("source_id", e1["semantic"])
        self.assertNotIn("english", e1["semantic"])
        self.assertNotIn("utterance_id", e1["semantic"])

    def test_old_lossy_packet_collisions_contrast_with_typed_features(self):
        # Compare to the *actual* previously tested v82 projection, not a
        # handwritten caricature or a corpus-ID lookup table.
        for lhs, rhs in (("E01", "E07"), ("E01", "E05"),
                         ("E01", "E08"), ("E02", "E03")):
            with self.subTest(lhs=lhs, rhs=rhs):
                self.assertEqual(self.old_packet(lhs), self.old_packet(rhs))
                self.assertNotEqual(self.semantic(lhs), self.semantic(rhs))
        self.assertEqual(self.old_packet("E18").consent, "present")
        self.assertEqual(json.loads(self.semantic("E18"))["consent"]["atom_indices"], [0, 1])

    def test_exploratory_distinct_semantic_observations_vs_old_packet_count(self):
        accepted = [f"E{n:02d}" for n in range(1, 31)
                    if encode_or_abstain(f"E{n:02d}", repo_root=ROOT).status == ACCEPTED]
        self.assertEqual(len(accepted), 27)
        self.assertEqual(len(set(self.semantic(sid) for sid in accepted)), 27)
        self.assertEqual(len(set(self.old_packet(sid) for sid in accepted)), 16)


if __name__ == "__main__":
    unittest.main()
