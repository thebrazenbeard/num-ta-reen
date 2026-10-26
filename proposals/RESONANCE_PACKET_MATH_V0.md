# Noncanonical resonance packet — mathematical experiment v65

**Status:** `NONCANONICAL_EXPERIMENTAL_STRUCTURE_ONLY`. This is **not** a new grammar rule, a phoneme-to-frequency conversion, a true-name synthesizer, or a discovered Ech’ta’reen encoding. It is a falsifiable proof of concept that typed structural features can be composed into a recoverable synthetic signal. The existing Wreckforge dictionary and corpus are not modified.

## What the source actually supports

In the amended *Nûm’ta’reen Reference Grammar v2.0* (current `num-ta-reen@ed9a94d53d17db6415de172858773714644e01ba`, `sources/reference_grammar_v2_updated_lphoneme.txt`):

- Part I.1 identifies native communication as **multimodal resonance modulation and timing discontinuities**, with a speakable transliteration as an analytic rather than native substrate.
- Part I.5 describes prosodic duration as affecting scope, but gives no absolute frequency or timing thresholds.
- Part II.4 records `=ka`, `=en`, `=ru`, `=va`, `=shi` as participant roles; Part II.5 records witnessed/verified evidence and loop/return/collapse operators; Part III.1 describes predicate-first **state packets**.
- The text supplies **no measured native waveforms**, no mapping from a role to hertz, and no demonstrated algorithm from acoustic energy to semantics. True-name chords are separately protected (Part IV.5); no such material is ingested or generated here.

Thus the source supports a *typed feature hypothesis*, **not** any particular audio codebook.

## Experimental encoding

The Python `Packet` is a finite typed grammatical envelope, not a sentence: five independently present/absent participant roles, three evidence states, four echo modes, two consent states, two inversion states, and two scope states. That yields `2^5 × 3 × 4 × 2 × 2 × 2 = 3072` distinct structural combinations, exhaustively proven injective by the symbolic test. Structural operations also form a small testable algebra: `include_role` is idempotent and commutative across roles, while `invert_state` is an involution and commutes with role inclusion. These are properties of the *proposal*, not established Ech’ta’reen grammar.

For each typed field, exactly **one** carrier out of its discrete alternatives is active. Every field has its own carrier set: a role is not translated into an English token, and adding a participant changes only that participant's feature carrier. The encoder overlays the active carriers linearly:

\[
s[n]=gA\sum_{f\in C(p)}\cos\big(2\pi(f+\delta)n/f_s+\phi\big)+\epsilon[n]
\]

Here `p` is a `Packet`, `C(p)` contains a fixed pilot and one carrier per field, `f_s = 12000` samples/s, `A=0.06` per active carrier, `g` is gain, `δ` is common frequency detuning, `φ` is arbitrary phase, and `ε` is synthetic Gaussian noise. The pilot is 701 Hz. Candidate field carriers are **arbitrarily assigned** as `701 + 157*j` Hz for `j=1…23`, from 858 to 4312 Hz. They are 157 Hz apart and below the 6 kHz Nyquist limit. **These numbers have no canonical phonosemantic status.**

Wide scope has **two redundant indicators**: a field carrier and a longer fixed frame (240 ms rather than 160 ms). If the duration and carrier disagree—e.g., if a wide frame is truncated to the shorter frame—the decoder rejects instead of silently inventing the scope. This is a proposed physical interpretation of the source's duration/scope correlation, **not** an assertion of its original timing scale.

The decoder uses Hann-windowed quadrature projections for each frequency (phase-insensitive), normalizes confidence relative to the pilot, and refuses weak or competitive choices. The signal still assumes a known start and end of a frame, a calibrated channel, and a single packet; native frame synchronization is unsolved.

### Hostile-review hardening (v72 candidate)

Independent hostile review found that v65's encoder accepted clean ±10 Hz
detuning even though its decoder could not recover those signals reliably. The
**accepted encoder nuisance domain is now limited to ±3 Hz**, the range in the
existing demonstrated recovery tests. Values outside that range fail on
encoding; this is calibration honesty, not an improvement in field tolerance.

The review also injected an anomalously strong competing role carrier that
would silently flip one role. The decoder now rejects a winner whose amplitude
relative to the pilot exceeds **1.35**, alongside its existing low-amplitude
and near-tie rejection. This assumes nominal equal-amplitude carriers and a
trusted pilot; it detects the tested out-of-envelope interference but does not
authenticate a packet. A malicious actor can replace an entire valid packet
with a different valid packet at ordinary amplitudes. There is no cryptographic
MAC, checksum, or physical-layer claim of tamper-proof decoding.

## Reproducible evidence

```powershell
python -m unittest discover -s tests -p test_experimental_resonance_packet.py -v
```

Local Linux/Python 3.12 result after v72 hardening: **17/17 passed**. This includes:

1. Exhaustive distinct symbolic encodings of all **3072** packets, including tests of role composition and inversion algebra.
2. Exact deterministic round trips and all categorical options.
3. Twenty-four randomly sampled structures recovered after separately varied gain (0.45×, 1×, 1.5×), global phase, common ±3 Hz detuning, and independent Gaussian noise (`σ=0.005` in floating amplitude units).
4. Rejection of an erased evidence carrier, missing pilot, malformed frames, wide-frame truncation, and two simultaneous packets that disagree about evidence.
5. **Codebook-permutation null control:** a randomly permuted encoder and decoder still recover all fields when coordinated. Therefore acoustic recoverability from an authored codebook **does not demonstrate naturally grounded semantic relationships**.
6. Hostile detuning regression (out-of-domain ±10 Hz rejected at source; in-domain ±3 Hz round trips), high-energy competing-carrier rejection, and an explicit valid-packet-substitution limitation test.

No native speech, field-mediated perception, human/alien listener, microphone, room impulse response, independent model, or unpaired semantic-learning test was run. The percentages in earlier repository acoustic negative controls are separate tests, not validation of this generator.

## Hostile questions / falsifiers

> **Meaning cannot be inferred from these frequencies alone.** An arbitrary permutation gives an equally functional codec, so the frequencies carry *assigned* labels rather than recovered semantics.

> **Human discriminability is not established.** Psychoacoustic masking/critical-band interactions are real design constraints; sufficient DSP separation does not prove a biological listener can parse simultaneous components. No discrimination study was performed.

> **Packet framing is assumed.** An adversary could spoof a complete independently framed packet or alter timing while preserving both scope indicators. This is not authenticated communication or robust waveform networking.

> **The structure is not a grammar.** It encodes no lexical predicate, no participant referents, no nested operator tree, no pragmatic context, no grounded coercion/consent semantics, and no direct mapping from the original phoneme inventory.

Before moving toward canon: test blind semantic inference under *unknown* codebooks and held-out meanings; test perceptual decoding by real listeners and varied microphones/rooms; test time/frequency warping, harmonics, crosstalk, dropouts, unknown participants and nested scopes; compare alternative models that use arbitrary symbols but equal bandwidth. Any new phonological or frequency law requires Patrick's authorial adoption.

## Primary research comparisons (not fictional-language authorities)

- Shannon, C. E. (1948), [*A Mathematical Theory of Communication*](https://doi.org/10.1002/j.1538-7305.1948.tb01338.x), *Bell System Technical Journal* 27(3), 379–423; [part II](https://doi.org/10.1002/j.1538-7305.1948.tb00917.x), 623–656. The work supplies mathematical communication/channel concepts—not a semantic assignment to acoustic frequencies.
- Plomp, R. & Levelt, W. J. M. (1965), [*Tonal consonance and critical bandwidth*](https://doi.org/10.1121/1.1909741), *Journal of the Acoustical Society of America* 38(4), 548–560. Its auditory frequency-interaction observations motivate measuring masking rather than equating separate spectral peaks with separate perceived symbols.

The actual source-priority and original/amended Wreckforge materials remain in Num’ta’reen. This experiment is a separate **proposal** awaiting adversarial review and author decisions.
