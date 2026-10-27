"""Adversarial two-repository tests: V1 remains unmodified and unqualified."""

from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import unittest

from research.typed_reference_bridge_v0 import (
    SCHEMA, SidecarError, build_sidecar, json_bytes, parse_sidecar,
)
from research.semantic_ir_proposal import load_verified_corpus
from research.typed_semantic_channel import MAGIC
from unvtrslr.reference_evidence import (
    ReferenceEvidenceError, parse_reference_evidence,
)


# This module deliberately does not match test_*.py: it is a two-repository
# integration qualification with Python >=3.11 and an installed public peer.
# tests.yml independently verifies standalone support on Python 3.10.
ROOT = Path(os.environ.get("NUMTAREEN_ROOT", Path(__file__).resolve().parents[1])).resolve()
if not os.environ.get("UNVTRSLR_ROOT"):
    raise RuntimeError("UNVTRSLR_ROOT is required for typed sidecar peer qualification")
PEER_ROOT = Path(os.environ["UNVTRSLR_ROOT"]).resolve()
if not (PEER_ROOT / "src" / "unvtrslr" / "reference_evidence.py").is_file():
    raise RuntimeError("UNVTRSLR_ROOT must point to an actual public-peer checkout")


class TypedSourceSidecarTests(unittest.TestCase):
    def test_all_eligible_source_observations_have_source_verified_sidecars(self):
        ids = sorted(load_verified_corpus(ROOT))
        accepted = []
        refused = []
        for corpus_id in ids:
            try:
                v0 = build_sidecar(corpus_id, repo_root=ROOT)
                decoded = parse_sidecar(json_bytes(v0), repo_root=ROOT)
                self.assertEqual(decoded, v0)
                accepted.append(corpus_id)
            except SidecarError:
                refused.append(corpus_id)
        self.assertEqual(len(accepted), 27)
        self.assertEqual(refused, ["E13", "E23", "E26"])
        self.assertIsNone(parse_reference_evidence(
            build_sidecar("E01", repo_root=ROOT)["reference_evidence_v1"]
        ).semantic_atoms)

    def test_uncertain_and_protected_sources_are_refused_without_content_echo(self):
        for corpus_id in ("E13", "E23", "E26", "E99"):
            with self.subTest(corpus_id=corpus_id):
                with self.assertRaises(SidecarError) as caught:
                    build_sidecar(corpus_id, repo_root=ROOT)
                self.assertNotIn("⟦", str(caught.exception))
                self.assertNotIn("⟧", str(caught.exception))

    def test_v1_receives_only_v1_and_keeps_qualification_false(self):
        v0 = build_sidecar("E01", repo_root=ROOT)
        record = v0["reference_evidence_v1"]
        parsed = parse_reference_evidence(record)
        self.assertEqual(parsed.evidence_class, "AUTHOR_ATTESTED_CORPUS")
        self.assertFalse(parsed.qualification_eligible)
        self.assertFalse(parsed.learner_visible)
        self.assertIsNone(parsed.semantic_atoms)
        self.assertEqual(parsed.source_independence, "SINGLE_AUTHOR_REFERENCE")
        with self.assertRaises(ReferenceEvidenceError):
            parse_reference_evidence(v0)

    def test_actual_universal_translator_cli_accepts_v1_but_refuses_v0_as_v1(self):
        v0 = build_sidecar("E01", repo_root=ROOT)
        environment = dict(__import__("os").environ)
        environment["PYTHONPATH"] = str(PEER_ROOT / "src")
        for payload, expected_rc in (
            (v0["reference_evidence_v1"], 0), (v0, 2)
        ):
            completed = subprocess.run(
                [sys.executable, "-m", "unvtrslr.reference_evidence_cli", "--bare"],
                input=json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n",
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=environment, timeout=20, check=False,
            )
            self.assertEqual(completed.returncode, expected_rc)
            if expected_rc == 0:
                summary = json.loads(completed.stdout)
                self.assertEqual(summary["validated_records"], 1)
                self.assertFalse(summary["qualification_eligible"])
                self.assertEqual(summary["claim_ceiling"],
                                 "AUTHOR_SUPPLIED_REFERENCE_ONLY_NOT_GROUNDED")

    def test_tampered_v1_translation_rejected_even_when_schema_valid(self):
        v0 = build_sidecar("E01", repo_root=ROOT)
        bad = copy.deepcopy(v0)
        bad["reference_evidence_v1"]["target_text"] = "Forged sentence."
        parse_reference_evidence(bad["reference_evidence_v1"])
        with self.assertRaises(SidecarError):
            parse_sidecar(json_bytes(bad), repo_root=ROOT)

    def test_qualification_visibility_and_semantic_atoms_never_cross(self):
        for key, forged in (
            ("qualification_eligible", True),
            ("learner_visible", True),
            ("source_independence", "INDEPENDENT_OBSERVATIONS"),
            ("status", "LEARNED_GROUNDING"),
            ("schema", "unvtrslr-reference-evidence-v1"),
        ):
            bad = copy.deepcopy(build_sidecar("E01", repo_root=ROOT))
            bad[key] = forged
            with self.subTest(field=key), self.assertRaises(SidecarError):
                parse_sidecar(json_bytes(bad), repo_root=ROOT)
        bad = build_sidecar("E01", repo_root=ROOT)
        bad["reference_evidence_v1"]["semantic_atoms"] = ["INVENTED:meaning"]
        with self.assertRaises(SidecarError):
            parse_sidecar(json_bytes(bad), repo_root=ROOT)

    def test_forged_source_and_recomputed_frame_checksum_rejected(self):
        left = build_sidecar("E01", repo_root=ROOT)
        right = build_sidecar("E07", repo_root=ROOT)
        spoof = copy.deepcopy(left)
        spoof["typed_frame_base64"] = right["typed_frame_base64"]
        with self.assertRaises(SidecarError):
            parse_sidecar(json_bytes(spoof), repo_root=ROOT)
        spoof = copy.deepcopy(left)
        wire = base64.b64decode(spoof["typed_frame_base64"])
        document = json.loads(wire[len(MAGIC) + 36:].decode("utf-8"))
        document["provenance"]["source_id"] = "E07"
        body = json.dumps(document, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":")).encode("utf-8")
        forged = MAGIC + struct.pack(">I", len(body)) + hashlib.sha256(body).digest() + body
        spoof["typed_frame_base64"] = base64.b64encode(forged).decode("ascii")
        with self.assertRaises(SidecarError):
            parse_sidecar(json_bytes(spoof), repo_root=ROOT)

    def test_noncanonical_json_or_extra_fields_are_refused(self):
        valid = build_sidecar("E01", repo_root=ROOT)
        for raw in (
            json_bytes(valid).replace(b'"schema":', b'"schema":"fake","schema":', 1),
            json_bytes(valid) + b"\n",
            b"\xff",
            b" " * 65_537,
            # 60,000 bytes remain under MAX_SIDECAR_BYTES yet exceed the
            # native JSON decoder's nesting ceiling on tested CPython.
            b"[" * 30_000 + b"]" * 30_000,
        ):
            with self.subTest(size=len(raw)), self.assertRaises(SidecarError):
                parse_sidecar(raw, repo_root=ROOT)
        bad = copy.deepcopy(valid)
        bad["fake"] = True
        with self.assertRaises(SidecarError):
            parse_sidecar(json_bytes(bad), repo_root=ROOT)

    def test_replay_has_no_freshness_and_still_never_qualifies(self):
        # V0 makes no anti-replay promise or deployment claim. Replaying an
        # immutable research reference must not create independent evidence.
        original = json_bytes(build_sidecar("E01", repo_root=ROOT))
        one = parse_sidecar(original, repo_root=ROOT)
        two = parse_sidecar(original, repo_root=ROOT)
        self.assertEqual(one, two)
        self.assertFalse(one["qualification_eligible"])
        self.assertEqual(one["source_independence"], "SINGLE_AUTHOR_REFERENCE")


if __name__ == "__main__":
    unittest.main()
