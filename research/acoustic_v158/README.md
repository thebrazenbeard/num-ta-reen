# V158 acoustic redundancy — frozen noncanonical research bundle

**Status:** synthetic, public, unkeyed eight-state detector. This is neither
native Ech’ta’reen/Num’ta’reen phonetics nor a translation, identity,
authentication, source separation, or real-world audio recognizer.

This isolated bundle is deliberately under `research/`; no package entry
point in `numtareen/`, production translator, source corpus, or canon imports
it. It must not be used to derive or emit protected utterance E26/source audio.

## Experiment and dependency custody

| File | Role | SHA-256 |
| --- | --- | --- |
| `geometric_pilot_code.py` | Frozen 4-slot V138 baseline dependency | `d0888950d55f6d25fa25768125f44886b32874ccb84c0f62d5fb01414765080d` |
| `redundant_geometric_code.py` | Frozen 8-slot V158 code | `b2cdc57514ea41675f5a50c3cd9ccf4734ac54cf65fa6b612721daa8d9e8267f` |
| `v158_benchmark.py` | Preregistered C2–C5 fixed methods | `7356042db8be6c35b88813433d3bd592362a4b5bb62ca3d8fb76a543f6aff74b` |
| `test_redundant_geometric_code.py` | Frozen C-series tests | `08e403710c48780a55dbff218e104265e7b7394d6ecba8beb622005c6130542a` |
| `test_v158_hostile.py` | Fresh V163 *independent* exploratory hostile tests | `0edabc467b7f0e74a8167a27189f4eb81814bea8b17605bc64fdaf1f97d839e8` |

The original frozen import names are preserved byte-for-byte. The
repository-level `tests/test_acoustic_v158.py` only adds the directory to
`sys.path`, imports those original tests for standard test discovery, checks
their hashes, and checks the actual frame duration. If hashes change,
prior validation/review does **not** transfer to the new code.

## Reproduction (Python standard library, no neural/audio hardware)

From the repository root:

```bash
python research/acoustic_v158/v158_benchmark.py
python -m unittest discover -s tests -p test_acoustic_v158.py -v
python -m unittest discover -s tests -v
```

The first command runs **preregistered C-series** only. The second includes
**post-result independent V163 hostile** controls; they are not retroactive
confirmatory trials. The third runs the broader Num’ta’reen regression suite,
which may additionally skip optional external peers on machines without
UNVTRSLR installed.

## What the frozen evidence actually establishes

| Population | V138 accepted | V158 accepted | Interpretation |
| --- | ---: | ---: | --- |
| Preregistered synthetic valid frame cases | — | 48/48 correct | Bounded in-contract single source; zero wrong states |
| Preregistered extreme differential drifts | — | 16/16 correct | Specific independently drifting carriers under declared ±5% limits |
| Preregistered random *shaped* malformed frames (fixed seed `0xA582`) | 47/50 | 0/50 | Fewer false accepts on *this* synthetic distribution and seed |
| Preregistered equal-amplitude distinct-state mixtures | — | 0/8 | Abstentions for eight selected pairs only |
| Directly rendered public forgeries | — | 8/8 | **Authentication fails by construction** |
| Independent V163 shaped negatives (seed `0xC0DEC0DE`) | 100/128 | **4/128** | Falsifies any universal zero-false-accept claim; 96% relative reduction on this sample |
| Independent V163 valid randomized singles | — | 128/128 correct | Outside preregistration, still synthetic |
| Independent V163 mismatched public checks | — | 0/96 | Detects the tested inconsistent public tails |

If the PRNG draw model were repeatedly and independently sampled, descriptive
95% Wilson intervals for the **V158** shaped-negative acceptance probability
would be 0–7.14% for the preregistered 0/50 sample and 1.22–7.76% for the
independent 4/128 sample. They are *not* empirical field rates or
distribution-free confidence bounds. Fixed-seed repeats do not add independent
samples, and the two sampling populations are not a fair universal estimator.

Each slot is 960 samples at 16 kHz, or 60 ms. V138 uses four slots
(240 ms), V158 eight slots (480 ms): the greater redundancy doubles frame
duration, symbol count and implied minimum framing latency. Never market the
observed false-accept reduction as a same-duration or same-bandwidth gain.
No noisy-room, microphone, channel-convolution, speech, or biological signal
data were used.

Post-result exploratory V158 X1 and independent V163 testing found weaker
concurrent minority sources (including a 10%-amplitude component) can pass
as a dominant state. Any public participant can synthesize or replay a valid
frame. Neither unique source nor origin authenticity is supported.

## Review and next honest falsifiers

- `V158_RESEARCH_RECORD.md` retains exact freeze/confirmatory C-series and
  separately labeled post-result X-series logs.
- `V158_MATH_MODEL.md` documents formal code construction and limits.
- `V163_INDEPENDENT_REVIEW.md` records the separate native reviewer's
  *conditional* synthetic-only PASS, exact source fingerprints, and failures.
- An **additional fresh hostile** must review the integrated adapter/source
  custody on its new Git head, and probe new negative seeds, clipped/noisy
  channels, timing drift, chosen-candidate attacks, bit-for-bit replay,
  mixture amplitudes and controlled equal-*duration* baselines. Report
  false accepts, wrong decodes and abstentions separately. Treat any new
  threshold or tuning as exploratory until a fresh preregistration is frozen
  *before* new confirmation.
- A proposal to map these artificial integers to authored language meanings
  requires independent attested semantic evidence and author approval, not
  merely encoder–decoder round trips.
