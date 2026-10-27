# V176 equal-duration synthetic acoustic comparison — frozen plan

**Freeze:** 2026-10-27, before executing any V176 outcome-generating program.
**Scope:** Synthetic public 8-state detectors; no Num’ta’reen speech, language meaning,
speaker authentication, source uniqueness, human audio, or secure protocol claim.

## Question and falsifiers

Does V158's publicly redundant 480 ms frame reject more *independent-shaped,
malformed* 480 ms acoustic sequences than the simple alternative of **two
independent V138 240 ms frames with matching decoded states**, while preserving
single-source correct decoding under a matched nuisance distribution?

- H1 (possible V158 advantage): among 128 preregistered fresh malformed
  sequences, V158 acceptance is strictly lower than two-V138-consensus
  acceptance. **Falsified** if V158 accepts >= consensus.
- H2 (tolerable positive coverage): on 96 generated in-contract positives per
  format under the same declared nuisance parameter distribution, each
  detector is correct on at least 90/96 with zero wrong decodes. **Falsified**
  by fewer than 90 correct or any confident wrong state. This is a conservative
  floor, not an equivalence or noninferiority margin.
- H3 (no identity security): all eight public V158 rendered examples are
  accepted. If fewer, check for code defects but do not infer authentication.

## Frozen methods, deterministic IDs

Source dependency: exact packaged V138/V158 implementations in
`ling-acoustic-package-v168/research/acoustic_v158/`; no parameter tuning,
code modification, or rerunning alternative seeds before reporting. Hash
custody follows the V158 research README.

- **C176-N**, malformed population: 128 *new fixed-seed* independent-shaped
  480 ms waveforms using the previously disclosed V163 generator family
  `independent_shaped(0x176A501, 128)`. This is only seed holdout, *not*
  independent distribution or adversarial worst case. Exact *same* waveform
  offered to both decoders.
- **C176-P**, matched synthetic positives: 96 states chosen by local
  `Random(0x176B502)`; the corresponding V158 frame and two separate V138
  frames each use the same state and paired nuisance values, with separate
  independent drift and noise-seed draws. Pilot scale .80–1.20; data scale
  .85–1.15; drift .96–1.04 independently per carrier; noise .0–.08; gain
  .30–.70; phase -π–π. All lie inside each renderer's contract. A V138 pair
  is rendered 240+240 ms, V158 480 ms. Evaluate each *format's own valid*
  waveforms; they cannot be evaluated as equivalent waveforms because their
  state carriers intentionally occupy different slots.
- **C176-F**, public-forgery control: eight V158 `render(state)` frames,
  zero noise and default parameters, fed to V158 decoder. Any generator with
  public parameters can synthesize this; acceptance is a negative security
  result.

**Consensus rule:** split 7680 samples at 3840; run unmodified V138 on each
half. Return a state iff both return the same non-None integer; otherwise
abstain. This is a deliberately conservative *two-packet repetition code*
using equal acoustic duration; it is not an information-rate-matched channel
code with the same pattern of carriers or effective synchronization markers.

Report acceptance of malformed waveforms for both (and paired discordance),
positive correct/wrong/abstain for each, and V158 forgeries. Treat strong
claims cautiously: repetition has two base reference+code pairs and V158
has base reference/code plus two public checks; data frequencies/slots and
number of error opportunities differ. No overstatement about equal energy,
bitrate, spectral width, entropy, hardware cost, or speaker/channel validity.

Stopping rule: one complete run of C176-N, C176-P, C176-F at declared seeds;
no retuning. Runtime/validation failure is logged as failure. Subsequent
diagnostic controls are **exploratory** and must be appended separately.

## Evidence log (append only)

- E176-0: Protocol frozen before C176 execution. Planned new source
  `equal_duration_probe.py`; standalone standard-library Python.
- E176-1: Started first and sole confirmatory invocation
  `python equal_duration_probe.py` from this directory with process session
  27661. Source code frozen before output inspection; pending outcome.
- E176-2: First confirmatory invocation completed with **exit 0** and returned
  `duration_ms_each=480`, malformed C176-N `v138_twice_accept=0/128`,
  `v158_accept=1/128`, paired `(both reject=127, repeat-only accept=0,
  V158-only accept=1, both accept=0)`. C176-P: V138×2 96 correct, 0 wrong,
  0 abstain; V158 96 correct, 0 wrong, 0 abstain. C176-F: V158 public
  renders accepted 8/8. Seed decimal 24552705 (negative), 24556802
  (positive). The JSON process output is the decisive evidence from
  `python equal_duration_probe.py`, process session 27661.
- E176-3: H1 **falsified** under this fresh fixed-seed shaped-negative family:
  V158 accepted one waveform and matched-airtime V138 consensus accepted
  none. H2 met for each *separately generated format*; H3 public forgeries
  accepted 8/8. Distinct-frame energy and channel code occupancy are not
  matched, so this result does not establish a globally superior V138 code
  or a field-rate difference. Samples are programmatically generated by
  one code family and not independent microphone observations.
- E176-4: Post-result deterministic regression
  `python -m unittest -v test_equal_duration_probe.py` exit **0**, **4/4
  tests passed** in 28.667 seconds; it reruns the **same** frozen seeds and
  does not enlarge the confirmatory sample. Pure-function tests also check
  consensus same-state acceptance, mixed-state abstention, malformed
  length rejection, and wrong/abstain/correct labeling. Runtime Linux,
  Python 3.12.14. Output fixture `RESULT.json` is the captured first run.

## Outcome interpretation (added after freeze, not part of preregistration)

The original V138 vs V158 claim compared 240 versus 480 milliseconds.
Under this new *matched-airtime* comparison, mere V138 repetition is at
least as selective as V158 on the single tested shaped-negative seed, with
identical measured positive recovery on separately generated in-contract
frames. The strict H1 prediction was falsified, although the difference
of **one** discordant frame is not a general performance claim: the exact
paired McNemar two-sided p-value is **1.0** (one V158-only accept and no
repeat-only accept), and descriptive Wilson 95% intervals are approximately
0–2.91% for 0/128 and 0.14–4.29% for 1/128. The generator family was
already known; a held-out seed is not an independent distribution.

The comparison equalizes **sample count and airtime only**. It does not
equalize per-state entropy, spectral occupancy, transmitted carrier energy,
channel use under interference, latency to partial decisions, renderer
frequency plan, or computational costs. Nor does it establish that repeating
V138 is acoustically equivalent to V158's check code. Both are unkeyed,
publicly forgeable artificial detectors; public V158 forgeries still decode.

### Next falsifiers (unexecuted; prospective)

1. Equal-power/spectral-bandwidth physical-channel trials with controlled
   multipath, masking noise, clipping, clock drift and phase mismatch.
2. A broader *pre-frozen* negative distribution family that does not derive
   its shape from either codec's known guard slots.
3. Explicit sender-collision mixtures, with positive/wrong/abstain and
   unique-source false-association rates compared across equal airtime.
4. Two-pass V138 independent-frame synchronization failures versus V158
   single-frame synchronization on hardware, without treating repetition's
   extra decision opportunities as free.

An **independent fresh reviewer** must rerun and challenge these artifacts;
this author has performed only self-verification. Publication as a
research-only negative result is appropriate *after* independent review.
