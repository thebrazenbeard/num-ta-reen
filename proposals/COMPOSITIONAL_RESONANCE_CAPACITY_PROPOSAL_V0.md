# Mathematical capacity and a possible typed-to-resonance research channel

**Status: NONCANONICAL mathematical proposal. No Ech’ta’reen acoustic signal has been decoded here.** Nothing in this note assigns a Wreckforge word to a new frequency, revises source grammar, or establishes that a native speaker perceives the proposed carriers. Author Wreckforge sources, the 500-entry dictionary and the 30-example corpus are preserved.

## Source-checked observation: capacity is not meaning

This analysis is bound to the public `num-ta-reen` source corpus Git blob `53d9f27d03579a1a3fc700c3394b56f834da784e`, the experimental Packet code blob `ed295b300379819c382ef15a294a6242c61346b7`, the reviewed lossy projection blob `4377bc2c324b02a91045ec223baac10548472a78`, and the semantic source analyzer `9e34143eab85a6e48b897a7834ba658abc3bf78c`. `test_capacity_invariants.py` and `capacity_census.py` supply independently runnable evidence under the unchanged source hash pin.

The existing synthetic packet is a cartesian product:

\[
|P| = 2^5_{\text{role presence}}\times3_{\text{evidence}}\times4_{\text{echo}}
 \times2_{\text{consent}}\times2_{\text{inversion}}\times2_{\text{scope}} =3072.
\]

Thus an arbitrary fixed index for every possible Packet requires
\(\lceil\log_2 3072\rceil=12\) bits. An *opaque* index for just 27 known source observations would require as few as \(\lceil\log_2 27\rceil=5\) bits. Neither quantity measures productive language expressivity.

For the actual source-bounded projection: 30 authored examples were checked; 27 eligible observations entered the experiment; E13 and E23 were excluded because of unresolved source interpretation and E26 was withheld. Those 27 produce just **16 distinct old Packet values**, with **five collision groups involving 21 source-observation pairs**. This is a many-to-one *chosen feature mapping*, even though the output space has thousands of unused slots. Relabeling packets with any bijective permutation of 3,072 numbers cannot split one collision: if \(f(x)=f(y)\), then \(\pi(f(x))=\pi(f(y))\) for every bijection \(\pi\).

Examples of **attested contrasts the old feature map erases** include predicate identity (E01/E07), source focus versus baseline (E01/E05), source question marking (E01/E08), and role/argument ordering (E02/E03). A single old `consent="present"` value also cannot encode the *two distinct attachment loci* in E18. The old research packet **does** retain some modeled contrasts, such as `LOOP` and whether any consent marker exists; the failure is selective, not universal.

The newer source-bound typed observation serializer preserves **27 distinct fully recorded source-observation payloads for those 27 eligible examples**, with ordered predicates, arguments/referents, TOP/FOC, question/polarity, evidential/echo and separate consent loci. This is a successful test of *serialization of recorded author glosses*. Retaining every lexical form could trivially distinguish existing examples; it does not establish a generative semantic algebra, translation of unseen Num’ta’reen, or a native acoustic codebook. Public-corpus tests are not blinded independent evaluation.

## Proposed compositional frame (software research; not canon)

Keep three layers strictly separate:

1. **Source-authorized observation layer:** Author interlinear gloss, role tags, scope uncertainty, consent attachment and citation to the exact source digest. No unsupported rule is inferred; conflicts and protected passages abstain.
2. **Typed symbolic transport layer:** A versioned schema stores ordered typed event/participant operators and their attachment. A concrete already-tested noncanonical implementation uses `NTSP1 || uint32(payload_bytes) || SHA256(payload) || canonical_UTF8_JSON(payload)`, bounded to 16 KiB of payload. Unknown required fields or incompatible schema versions refuse decoding. Verified consumers recompute source-derived structure instead of trusting unkeyed hash or caller-supplied provenance objects.
3. **Hypothetical acoustic realization layer:** Only *after* the symbol semantics are constrained by author tests, map framed bits to a finite, experimentally calibrated set of carrier symbols. A deliberately arbitrary candidate would use a \(q\)-ary signal alphabet with \(\log_2q\) nominal bits per symbol, explicit clock/pilot and synchronization, escaping or fixed-length symbol grouping, bounded frame length, and forward-error detection/correction. Do not assign frequencies or claim spectral separability without a measured channel.

The binary `NTSP1` format is self-delimiting at byte level: an exact single-frame decoder accepts only the declared payload length, so a valid frame cannot be a **strict prefix** of another valid single frame with identical initial header. A stream decoder must consume exactly one length-prefixed frame and then restart at the next boundary. The `length` field requires a strict upper bound to avoid attacker-controlled buffering; the existing source-bound prototype limits JSON payload to 16 KiB. The test demonstrates two concatenated valid frames can be separated and truncation/trailing content rejected.

**Integrity is not authentication.** Any attacker can edit JSON and calculate a new SHA-256 checksum; the format's digest detects accidental corruption, not possession of a secret or authorship. The source-bound decoder independently rejects a forged but otherwise correctly checksummed *known-source semantic claim*. Future peer-to-peer authenticity would need a separate threat model and keyed MAC or signatures; authorization to originate canonical language messages would remain a distinct human-author issue.

## Experiments needed before mapping to resonance

The following are **prospective unscored tests**, not results:

| Experiment | Controlled factor | Falsifier or qualification threshold |
| --- | --- | --- |
| A: null codebook | Independently permute the frequency/timing labels while keeping typed payloads constant | Claimed semantic advantage vanishes under arbitrary labels unless calibrated source-grounded acoustic distinctions survive |
| B: channel degradation | Inject additive noise, narrowband interference, detune, time scaling and dropout across preregistered severity levels | Measure exact typed-field recovery, frame rejection, false accept rate and recovery per factor; no tuning on test split |
| C: source withheld | Blinded author-created minimal pairs for ordered roles, FOC/TOP, Q, scope and consent withdrawal | A mapping that cannot recover fresh source-approved contrasts is not a productive language code |
| D: competing tones | Two coordinated perturbations on different feature channels, including a high-energy near-carrier interferer | Decoder must reject ambiguous role/consent, not silently choose a plausible but wrong packet |
| E: register and listener | Different voices, registers, physical transducers, environments and, if appropriate, human listeners | Do not infer real acoustic perceptibility from purely synthetic FFT/tone decoding |

Measure **false semantic acceptance** separately from ordinary bit error, abstention and exact source-field recovery. A model should never increase its coverage score by guessing meanings for E13/E23 or rendering protected E26 material. Use frozen codebook/decoder and sealed author-held-out cases; an investigator scoring its own synthetic packets does not validate native perception.

Information-theoretic channel capacity such as \(C=B\log_2(1+S/N)\) can describe an idealized bandwidth-limited Gaussian channel with specified noise assumptions, but those assumptions have **not** been established for Ech’ta’reen physiology or technology. No band-limited Hertz number, wavelength, harmonic meaning, or sensitivity threshold is claimed here.

## Executed bounded checks

With Python standard library and the source-pinned Num’ta’reen staging module path:

```bash
PYTHONPATH=num-integration-union-v60 NUMTAREEN_REPO_ROOT=num-integration-union-v60 \
  python -m unittest discover -s ling-mathcapacity-v109 -p 'test_capacity_invariants.py' -v
PYTHONPATH=num-integration-union-v60 NUMTAREEN_REPO_ROOT=num-integration-union-v60 \
  python ling-mathcapacity-v109/capacity_census.py
```

All **five confirmatory engineering checks passed**, covering projection collisions, axis capacity, source-verified typed round trips, frame boundary/digest distinction and collision invariance under relabeling. The census reported 30/27/16/27, five collision groups/21 colliding pairs, 3,072 old states, 5-bit known-example opaque lower bound, and 12-bit full-old-packet index. No protected source notation, invented phoneme/frequency or new canonical word appears in test outputs.

> **Independent hostile question:** Could a decoder that merely stores the 27 observed lexical forms appear successful on every regression while having zero performance on withheld compositional examples? Yes. Treat current distinctness as a serialization result only, and require source-authorized novel tests before making a language-understanding claim.
