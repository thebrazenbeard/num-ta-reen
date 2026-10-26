"""EXPERIMENTAL structural-signal encoder; not Nûm’ta’reen canon.

This prototype tests whether *independently typed grammatical features* can
be composed and recovered through separate acoustic carriers.  Carrier labels
are chosen by an arbitrary codebook; no learned or natural semantic grounding
is claimed.  It carries no words, utterances, or true-name chords.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product
import math
import random
from typing import Mapping


STATUS = "NONCANONICAL_EXPERIMENTAL_STRUCTURE_ONLY"
RATE = 12_000
SAMPLES = 1_920  # Narrow scope: 160 ms; frequency resolution about 6.25 Hz.
WIDE_SAMPLES = 2_880  # Wide scope: 240 ms; proposal, not a linguistic threshold.
PILOT_HZ = 701.0
CHANNEL_STEP_HZ = 157.0
PER_CARRIER_GAIN = 0.060
# This synthetic receiver is qualified only inside this calibrated detuning
# interval. Accepting encoder inputs outside it would invite false confidence
# about waveforms that the matching decoder cannot recover.
MAX_CALIBRATED_DETUNE_HZ = 3.0
# A clean frame uses equal-amplitude field carriers and pilot. Excess energy
# on one field may indicate a competing injected signal, not a new value.
# This detects gross interference; it is NOT an integrity/authentication code.
MAX_FEATURE_PILOT_RATIO = 1.35

ROLES = ("AGT", "PAT", "SRC", "GOAL", "INST")
FEATURES: tuple[tuple[str, tuple[str, ...]], ...] = (
    *(("role." + role, ("absent", "present")) for role in ROLES),
    ("evidence", ("unmarked", "witnessed", "verified")),
    ("echo", ("plain", "loop", "return", "collapse")),
    ("consent", ("unmarked", "present")),
    ("inversion", ("normal", "inverse")),
    ("scope", ("narrow", "wide")),
)
LABELS = tuple((field, choice) for field, choices in FEATURES for choice in choices)
DEFAULT_FREQUENCIES = tuple(
    PILOT_HZ + CHANNEL_STEP_HZ * (index + 1)
    for index in range(len(LABELS))
)


class InvalidPacket(ValueError):
    """A feature or packet configuration is outside this bounded codebook."""


class UncertainSignal(ValueError):
    """The signal is absent, corrupted, or insufficiently unambiguous."""


@dataclass(frozen=True)
class Packet:
    """Small typed grammatical envelope, deliberately excluding lexical sense."""

    roles: frozenset[str] = frozenset()
    evidence: str = "unmarked"
    echo: str = "plain"
    consent: str = "unmarked"
    inversion: str = "normal"
    scope: str = "narrow"

    def __post_init__(self) -> None:
        if not isinstance(self.roles, frozenset) or not self.roles.issubset(ROLES):
            raise InvalidPacket("roles must be a frozenset of attested role labels")
        choices = {name: allowed for name, allowed in FEATURES}
        for name in ("evidence", "echo", "consent", "inversion", "scope"):
            if getattr(self, name) not in choices[name]:
                raise InvalidPacket(f"unrecognized {name} option")


def feature_values(packet: Packet) -> dict[str, str]:
    values = {"role." + role: ("present" if role in packet.roles else "absent") for role in ROLES}
    values.update(
        evidence=packet.evidence,
        echo=packet.echo,
        consent=packet.consent,
        inversion=packet.inversion,
        scope=packet.scope,
    )
    return values


def include_role(packet: Packet, role: str) -> Packet:
    """Proposed typed composition: add a participant role, not a new word."""
    if role not in ROLES:
        raise InvalidPacket("unrecognized participant role")
    return replace(packet, roles=packet.roles | {role})


def invert_state(packet: Packet) -> Packet:
    """Structural involution inspired by attested vael- inversion morphology."""
    return replace(packet, inversion="inverse" if packet.inversion == "normal" else "normal")


@dataclass(frozen=True)
class Codebook:
    """Explicitly arbitrary mapping from typed labels to acoustic carriers."""

    frequencies: tuple[float, ...] = DEFAULT_FREQUENCIES

    def __post_init__(self) -> None:
        if len(self.frequencies) != len(LABELS):
            raise InvalidPacket("the codebook requires one carrier per feature choice")
        if any(not math.isfinite(f) or f <= 0 or f >= RATE / 2 for f in self.frequencies):
            raise InvalidPacket("carriers must be finite and below Nyquist")
        all_f = sorted((PILOT_HZ, *self.frequencies))
        if any(b - a < 100 for a, b in zip(all_f, all_f[1:])):
            raise InvalidPacket("carriers require at least 100 Hz separation")

    def mapping(self) -> dict[tuple[str, str], float]:
        return dict(zip(LABELS, self.frequencies))

    def permuted(self, seed: int) -> "Codebook":
        pool = list(self.frequencies)
        random.Random(seed).shuffle(pool)
        return Codebook(tuple(pool))


DEFAULT_CODEBOOK = Codebook()


def active_frequencies(packet: Packet, codebook: Codebook = DEFAULT_CODEBOOK) -> tuple[float, ...]:
    lookup = codebook.mapping()
    return (PILOT_HZ, *(lookup[(name, value)] for name, value in feature_values(packet).items()))


def structural_codeword(packet: Packet) -> tuple[tuple[str, str], ...]:
    """Injective finite symbol encoding before any acoustic/nuisance losses."""
    return tuple(feature_values(packet).items())


def all_symbolic_packets():
    """Exactly 3,072 typed packets; no lexical/word identity is encoded."""
    for flags in product((False, True), repeat=len(ROLES)):
        roles = frozenset(role for role, flag in zip(ROLES, flags) if flag)
        for evidence, echo, consent, inversion, scope in product(
            ("unmarked", "witnessed", "verified"),
            ("plain", "loop", "return", "collapse"),
            ("unmarked", "present"),
            ("normal", "inverse"),
            ("narrow", "wide"),
        ):
            yield Packet(roles, evidence, echo, consent, inversion, scope)


def encode(
    packet: Packet,
    *,
    codebook: Codebook = DEFAULT_CODEBOOK,
    gain: float = 1.0,
    phase: float = 0.0,
    detune_hz: float = 0.0,
    noise_sigma: float = 0.0,
    noise_seed: int = 0,
) -> tuple[float, ...]:
    """Synthesizes a calibrated fixed-length floating-point test frame.

    Nuisances are synthetic and controlled, not independently recorded sound.
    Phase is global; there is no synchronization/framing solution here.
    """
    if (not math.isfinite(gain) or gain <= 0 or not math.isfinite(phase)
            or not math.isfinite(detune_hz)
            or abs(detune_hz) > MAX_CALIBRATED_DETUNE_HZ
            or not math.isfinite(noise_sigma) or noise_sigma < 0 or noise_sigma > .1):
        raise InvalidPacket("invalid synthetic nuisance parameter")
    carriers = active_frequencies(packet, codebook)
    samples = []
    noise = random.Random(noise_seed)
    count = WIDE_SAMPLES if packet.scope == "wide" else SAMPLES
    for index in range(count):
        t = index / RATE
        sample = gain * PER_CARRIER_GAIN * sum(
            math.cos(2 * math.pi * (f + detune_hz) * t + phase)
            for f in carriers
        )
        if noise_sigma:
            sample += noise.gauss(0, noise_sigma)
        samples.append(sample)
    return tuple(samples)


def _amplitudes(frame: tuple[float, ...], codebook: Codebook) -> Mapping[float, float]:
    if len(frame) not in (SAMPLES, WIDE_SAMPLES) or any(not math.isfinite(x) for x in frame):
        raise UncertainSignal("wrong frame length or non-finite sample")
    # Hann taper limits leakage from non-integer carrier periods. A quadrature
    # magnitude avoids dependence on an arbitrary global phase origin.
    n = len(frame)
    window = [0.5 - 0.5 * math.cos(2 * math.pi * i / (n - 1)) for i in range(n)]
    denominator = sum(window)
    weighted = [x * w for x, w in zip(frame, window)]
    energies = {}
    for f in (PILOT_HZ, *codebook.frequencies):
        re = 0.0
        im = 0.0
        for i, x in enumerate(weighted):
            angle = 2 * math.pi * f * i / RATE
            re += x * math.cos(angle)
            im += x * math.sin(angle)
        energies[f] = 2 * math.hypot(re, im) / denominator
    return energies


def decode(frame: tuple[float, ...], *, codebook: Codebook = DEFAULT_CODEBOOK) -> Packet:
    """Rejects erasure and double-carrier ambiguities; not speech recognition."""
    energies = _amplitudes(frame, codebook)
    pilot = energies[PILOT_HZ]
    if pilot < .010:
        raise UncertainSignal("missing calibrated pilot")
    mapping = codebook.mapping()
    recovered = {}
    for name, choices in FEATURES:
        ranked = sorted(((energies[mapping[(name, choice)]], choice) for choice in choices), reverse=True)
        winner_energy, winner = ranked[0]
        runner_energy = ranked[1][0]
        if (winner_energy < .28 * pilot
                or winner_energy > MAX_FEATURE_PILOT_RATIO * pilot
                or runner_energy > .67 * winner_energy):
            raise UncertainSignal(f"{name}: erased or competing feature carriers")
        recovered[name] = winner
    # Scope is redundantly conveyed by duration as a structural temporal
    # relation.  A trusted frame boundary is still an explicit assumption.
    duration_scope = "wide" if len(frame) == WIDE_SAMPLES else "narrow"
    if recovered["scope"] != duration_scope:
        raise UncertainSignal("scope duration disagrees with its carrier")
    roles = frozenset(role for role in ROLES if recovered["role." + role] == "present")
    return Packet(
        roles=roles,
        evidence=recovered["evidence"],
        echo=recovered["echo"],
        consent=recovered["consent"],
        inversion=recovered["inversion"],
        scope=recovered["scope"],
    )


def overlay(a: tuple[float, ...], b: tuple[float, ...]) -> tuple[float, ...]:
    """Diagnostic collision attack: simultaneous independent packets."""
    if len(a) not in (SAMPLES, WIDE_SAMPLES) or len(a) != len(b):
        raise InvalidPacket("frame size mismatch")
    return tuple((x + y) / 2 for x, y in zip(a, b))
