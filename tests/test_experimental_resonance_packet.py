"""Executable falsification tests for the noncanonical v65 proposal."""

import math
import random
import unittest

from numtareen.experimental_resonance_packet import (
    CHANNEL_STEP_HZ,
    Codebook,
    DEFAULT_CODEBOOK,
    DEFAULT_FREQUENCIES,
    FEATURES,
    InvalidPacket,
    LABELS,
    MAX_CALIBRATED_DETUNE_HZ,
    MAX_FEATURE_PILOT_RATIO,
    Packet,
    PER_CARRIER_GAIN,
    PILOT_HZ,
    RATE,
    ROLES,
    SAMPLES,
    WIDE_SAMPLES,
    STATUS,
    UncertainSignal,
    all_symbolic_packets,
    decode,
    encode,
    include_role,
    invert_state,
    overlay,
    structural_codeword,
)


class SymbolicStructureTests(unittest.TestCase):
    def test_exhaustive_finite_code_space_is_injective(self):
        packets = tuple(all_symbolic_packets())
        self.assertEqual(len(packets), 3072)
        self.assertEqual(len({structural_codeword(p) for p in packets}), len(packets))
        self.assertTrue(all(len(structural_codeword(p)) == len(FEATURES) for p in packets))

    def test_roles_are_independently_composable_not_sentence_ids(self):
        a = Packet(roles=frozenset({"AGT"}))
        b = Packet(roles=frozenset({"PAT"}))
        both = Packet(roles=frozenset({"AGT", "PAT"}))
        base = {name: value for name, value in structural_codeword(Packet())}
        ab = {name: value for name, value in structural_codeword(both)}
        self.assertEqual(ab["role.AGT"], "present")
        self.assertEqual(ab["role.PAT"], "present")
        self.assertEqual(ab["role.SRC"], base["role.SRC"])
        self.assertNotEqual(structural_codeword(a), structural_codeword(b))
        self.assertNotEqual(structural_codeword(a), structural_codeword(both))

    def test_role_union_idempotence_commutativity_and_inversion_involution(self):
        base = Packet(evidence="witnessed")
        self.assertEqual(include_role(include_role(base, "AGT"), "AGT"), include_role(base, "AGT"))
        self.assertEqual(include_role(include_role(base, "AGT"), "PAT"),
                         include_role(include_role(base, "PAT"), "AGT"))
        self.assertEqual(invert_state(invert_state(base)), base)
        self.assertNotEqual(structural_codeword(invert_state(base)), structural_codeword(base))
        self.assertEqual(include_role(invert_state(base), "SRC"),
                         invert_state(include_role(base, "SRC")))

    def test_unknown_values_fail_closed(self):
        with self.assertRaises(InvalidPacket):
            Packet(roles=frozenset({"TRUE_NAME"}))
        with self.assertRaises(InvalidPacket):
            Packet(evidence="mind_reading")
        with self.assertRaises(InvalidPacket):
            Packet(roles=("AGT",))

    def test_carrier_spacing_and_nyquist(self):
        self.assertEqual(STATUS, "NONCANONICAL_EXPERIMENTAL_STRUCTURE_ONLY")
        self.assertEqual(len(DEFAULT_FREQUENCIES), len(LABELS))
        self.assertGreater(CHANNEL_STEP_HZ, 100)
        self.assertLess(max(DEFAULT_FREQUENCIES), RATE / 2)
        frequencies = sorted((PILOT_HZ, *DEFAULT_FREQUENCIES))
        self.assertTrue(all(b - a >= 100 for a, b in zip(frequencies, frequencies[1:])))
        with self.assertRaises(InvalidPacket):
            Codebook((*DEFAULT_FREQUENCIES[:-1], DEFAULT_FREQUENCIES[0]))


class AcousticRoundTripTests(unittest.TestCase):
    SAMPLE = Packet(
        roles=frozenset({"AGT", "PAT", "SRC"}),
        evidence="verified",
        echo="loop",
        consent="present",
        inversion="inverse",
        scope="wide",
    )

    def test_encoder_rejects_clean_out_of_calibration_detuning(self):
        self.assertEqual(MAX_CALIBRATED_DETUNE_HZ, 3.0)
        for detune in (-10.0, -3.001, 3.001, 10.0):
            with self.subTest(detune=detune):
                with self.assertRaises(InvalidPacket):
                    encode(self.SAMPLE, detune_hz=detune)
        for detune in (-3.0, 3.0):
            with self.subTest(detune=detune):
                self.assertEqual(decode(encode(self.SAMPLE, detune_hz=detune)), self.SAMPLE)

    def test_abnormal_competing_role_carrier_is_rejected(self):
        self.assertLess(MAX_FEATURE_PILOT_RATIO, 1.5)
        clean = encode(Packet(roles=frozenset({"AGT"})))
        competing_hz = DEFAULT_CODEBOOK.mapping()[("role.AGT", "absent")]
        for adversarial_amplitude in (0.09, 0.20):
            with self.subTest(amplitude=adversarial_amplitude):
                corrupted = tuple(
                    sample + adversarial_amplitude * math.cos(2 * math.pi * competing_hz * index / RATE)
                    for index, sample in enumerate(clean)
                )
                with self.assertRaises(UncertainSignal):
                    decode(corrupted)

    def test_wholesale_valid_codeword_substitution_is_not_detectable(self):
        # The receiver cannot authenticate intentional alteration to another
        # valid codeword: this is a limitation, not a promised security feature.
        original = Packet(roles=frozenset({"AGT"}))
        replacement = Packet(roles=frozenset())
        self.assertEqual(decode(encode(original)), original)
        self.assertEqual(decode(encode(replacement)), replacement)
        self.assertNotEqual(original, replacement)

    def test_deterministic_exact_roundtrip(self):
        wave = encode(self.SAMPLE)
        self.assertEqual(wave, encode(self.SAMPLE))
        self.assertEqual(len(wave), WIDE_SAMPLES)
        self.assertEqual(decode(wave), self.SAMPLE)

    def test_temporal_scope_is_redundant_and_truncation_detected(self):
        narrow = Packet(roles=frozenset({"PAT"}), scope="narrow")
        wide = Packet(roles=frozenset({"PAT"}), scope="wide")
        self.assertEqual(len(encode(narrow)), SAMPLES)
        self.assertEqual(len(encode(wide)), WIDE_SAMPLES)
        self.assertEqual(decode(encode(wide)), wide)
        # Frame-boundary loss must not silently convert WIDE into NARROW.
        with self.assertRaisesRegex(UncertainSignal, "scope"):
            decode(encode(wide)[:SAMPLES])

    def test_every_category_recovers_under_clean_frames(self):
        candidates = [
            Packet(),
            Packet(evidence="witnessed", echo="return", scope="wide"),
            Packet(evidence="verified", echo="collapse", inversion="inverse"),
            Packet(roles=frozenset(ROLES), consent="present"),
            self.SAMPLE,
        ]
        for packet in candidates:
            with self.subTest(packet=packet):
                self.assertEqual(decode(encode(packet)), packet)

    def test_controlled_gain_phase_detuning_and_noise(self):
        pool = tuple(all_symbolic_packets())
        prng = random.Random(3072)
        candidates = prng.sample(pool, 24)
        for i, packet in enumerate(candidates):
            frame = encode(
                packet,
                gain=(.45, 1.0, 1.5)[i % 3],
                phase=(-1.2, 0.0, 2.3)[i % 3],
                detune_hz=(-3.0, 0.0, 3.0)[i % 3],
                noise_sigma=.005,
                noise_seed=i,
            )
            with self.subTest(index=i):
                self.assertEqual(decode(frame), packet)

    def test_missing_pilot_or_invalid_frame_rejected(self):
        for frame in (tuple(0.0 for _ in range(SAMPLES)), (0.0,),
                      tuple(math.nan for _ in range(SAMPLES))):
            with self.subTest(frame_len=len(frame)):
                with self.assertRaises(UncertainSignal):
                    decode(frame)

    def test_missing_feature_carrier_is_erasure_not_invented_value(self):
        # Suppress all evidence carriers, leaving other fields + pilot unchanged.
        active = [PILOT_HZ]
        encoded = dict(structural_codeword(self.SAMPLE))
        codebook = DEFAULT_CODEBOOK.mapping()
        for field, value in encoded.items():
            if field != "evidence":
                active.append(codebook[(field, value)])
        frame = tuple(
            PER_CARRIER_GAIN * sum(math.cos(2 * math.pi * f * i / RATE) for f in active)
            for i in range(SAMPLES)
        )
        with self.assertRaisesRegex(UncertainSignal, "evidence"):
            decode(frame)

    def test_simultaneous_competing_evidence_is_rejected(self):
        witnessed = Packet(roles=frozenset({"AGT"}), evidence="witnessed")
        verified = Packet(roles=frozenset({"AGT"}), evidence="verified")
        with self.assertRaisesRegex(UncertainSignal, "evidence"):
            decode(overlay(encode(witnessed), encode(verified)))

    def test_permuted_labels_prove_no_inherent_semantic_grounding(self):
        arbitrary = DEFAULT_CODEBOOK.permuted(19)
        self.assertNotEqual(arbitrary.frequencies, DEFAULT_CODEBOOK.frequencies)
        same_structure = encode(self.SAMPLE, codebook=arbitrary)
        # An equally arbitrary, coordinated encoder+decoder pair can recover
        # every feature.  Successful recovery does not discover meanings.
        self.assertEqual(decode(same_structure, codebook=arbitrary), self.SAMPLE)
        try:
            mismatched = decode(same_structure, codebook=DEFAULT_CODEBOOK)
        except UncertainSignal:
            pass
        else:
            self.assertNotEqual(mismatched, self.SAMPLE)

    def test_nuisance_parameters_bounded(self):
        for kwargs in ({"gain": 0}, {"gain": math.inf}, {"noise_sigma": -.1},
                       {"noise_sigma": 1.0}, {"detune_hz": 100}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(InvalidPacket):
                    encode(Packet(), **kwargs)


if __name__ == "__main__":
    unittest.main()
