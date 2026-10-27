# V158 — public redundant geometric frame (experimental only)

This is a mathematical *artifact* for a possible multimodal fictional-language encoding, **not** a native Nûm’ta’reen alphabet, acoustic recording, complete translator, sender authenticator, or claim about Ech’ta’reen physiology.

## Model

Eight synthetic states s = 0,…,7. An eight-slot frame is transmitted at 16 kHz, 960 samples per slot (60 ms); total 480 ms, twice V138's four-slot 240 ms.

| Slot | Intended content |
| ---: | --- |
| 0 | 180 Hz pilot plus 600 Hz reference (both scaled by their channel) |
| 1 | Pilot only (guard) |
| 2 | Pilot plus state carrier 650 × 1.30^s Hz |
| 3 | Pilot only (guard) |
| 4 | Pilot plus check A at 700 × 1.30^((3s+1) mod 8) Hz |
| 5 | Pilot only (guard) |
| 6 | Pilot plus check B at 750 × 1.30^((5s+2) mod 8) Hz |
| 7 | Pilot only (guard) |

These are **public redundancy** fields. A decoder compares carrier/reference log ratios, not absolute frequency, and requires the selected state to satisfy both independent check slots under log residual ≤ 0.112. It also enforces pilot continuity and carrier absence in guard slots. Both check permutations are bijections over the eight states, but they are not cryptographic checksums or message authentication codes.

With two independently scaled carriers under equal individual drift bound δ, the worst ratio factor is (1+δ)/(1−δ). Adjacent geometric bands of ratio R are disjoint in ideal exact-frequency measurement when:

    R > ((1+δ)/(1−δ))².

For R=1.30, the ideal critical drift is (sqrt(1.30)−1)/(sqrt(1.30)+1) ≈ 0.06555, i.e. about ±6.55%. The tested bound is ±5%, leaving a positive *ideal* spacing margin. Finite 60 ms spectral estimation, channel convolution and competing sources can still cause other failures.

## Confirmatory source-bound synthetic experiment

Frozen before execution in RESEARCH_RECORD.md; baseline V138 geometric_pilot_code.py SHA-256 d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d.

To reproduce in this scratch workspace from its parent directory:

    PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m unittest -v test_redundant_geometric_code
    PYTHONPATH=ling-acoustic-v138:ling-acoustic-redundancy-v158 python -m v158_benchmark

Observed at the frozen seed/conditions:

| Confirmatory task | V138 | V158 |
| --- | ---: | ---: |
| 50 shape-matched unrelated random codewords accepted | 47 | 0 |
| V158 generated positives correctly decoded | not retested on 8-slot whole frame | 48/48 |
| Extreme declared slot drift correctly decoded | not retested on 8-slot whole frame | 16/16 |
| Eight equal-source mixtures accepted as unique | prior V138 patched strong-mixture gate | 0 |
| Public direct forgeries correctly decoded | forgeable | 8/8 |

These controlled counts are **not** field error rates and should not be generalized to natural-language or acoustic scenes. The frame's 2× duration and two extra code carriers are an explicit cost.

## Hostile evidence and limits

The additional post-result X1 stress test accepted **all eight** of the evaluated minority-source mixtures when the weaker source was 1%, 5%, 10% or 15% of the total waveform, falsely returning the majority as if it were a unique source. It abstained on all eight pairs at 25%, 35%, 45% and 50% minority fractions. Thus V158 improves a **bounded single-source packet acceptance test**, not source separation.

Anyone who reads this source can render a fully valid packet for any state and replay it; 8/8 public forgeries pass. To authenticate a sender, a distinct secret-keyed MAC, nonce, replay window, and key-management design would be necessary. None exists here, and adding a checksum does not provide it.

**Possible next experiment, not a commitment:** compare redundancy against equal-duration/equal-energy baselines, acoustically realistic impulse responses, independently generated near-codebook adversaries, and variable-time mixtures. No claim of canonical alien frequency/resonance is justified without Patrick's explicit language-worldbuilding choices and much stronger evidence.
