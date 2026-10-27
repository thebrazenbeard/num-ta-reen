# Num’ta’reen / English Bilingual Evaluation v117

## Frozen preregistration — 2026-10-27 UTC

**Question:** How much bilingual translation coverage can be demonstrated without leaking an authored example into the test set or inventing any Num’ta’reen grammar?

**H1 (memorization):** A source-pinned exact-pair lookup will achieve perfect coverage on its own training examples, but zero exact-pair coverage when each test item is withheld and no identical source-side duplicate remains. Falsifier: at least one genuinely withheld input yields an exact lookup hit absent duplicates.

**H2 (lexical limits):** A source-pinned lexical translator with token-level dictionary evidence should cover some isolated single words, but should abstain or flag incompleteness on unseen multiword utterances rather than claim source-verified fluent sentences. Falsifier: explicit overconfident claimed sentence-perfect translations without licensed grammatical evidence.

**H3 (bidirectional asymmetry):** English-to-Num’ta’reen lexical inversion will produce ambiguous candidates for at least one English key and must preserve multiple alternatives rather than pick a canonical word. Falsifier: no ambiguous English key exists in the full authored dictionary after conservative normalization.

### Confirmatory experiments (frozen)

- **C1:** Parse the repo’s authoritative bilingual source pairs, enumerate eligible examples and exact normalized duplicates, run leave-one-out exact-pair retrieval independently in each direction, record coverage and exact correctness.
- **C2:** Parse the source lexicon, compute bilingual lexical ambiguity with documented deterministic normalization; evaluate in-vocabulary single-word lookup and unknown-word abstention without fabricating grammar.
- **C3:** Create adversarial held-out negatives by perturbing held-out inputs with an unattested token; measure whether each baseline refuses source-attested exact translation. Report separately any unsafe false positives.
- **C4:** Run source-independent unit tests on the harness itself, including reversed direction, duplicate detection, ambiguity, no-leakage, and protected/missing data exclusion.

### Exploratory experiments

- **E1:** Compare any existing repository translator without modifying its code. Document its interface and source provenance; record observed coverage/errors against same controls if feasible.

**Stopping:** At most one benchmark implementation, one focused test suite, and one documented exploratory comparison. Never modify canonical sources or public GitHub; a separate reviewer is required for a confirmed verdict. Source data hashes and exact command outputs must be logged below. Lack of source-compatible data is reported as a blocker, not replaced by synthetic labels.

## Evidence log (append only)

### EV1 — Authoritative live source identity

2026-10-27, GitHub `thebrazenbeard/num-ta-reen` `main@14892e64983d91d9cdf2f580dcba57654624a6c1`, tree `cae9f0063200716b7212df2eb28fffb52ef5ea9b`.

Git blob identities read from live tree and checked against local `git hash-object`:

| Path | Exact Git blob |
|---|---|
| `data/corpus.json` | `53d9f27d03579a1a3fc700c3394b56f834da784e` |
| `data/lexicon.json` | `c78dccdf9614d8e8e94c968aac5c07a2e4206bf1` |
| `numtareen/engine.py` | `9c4d7ba4e2ccd0ba9f4c9513a463fac0a399eb60` |

Byte-for-byte content SHA-256 in local `num-integration-union-v60`: corpus `5bc4c939e728e9e5bce1875eafcba9e71609570281bebb87dc7e64e2e9a6d229`; lexicon `208d5daa5953383cccbac6a145df795531691ec60248256dc2e18a5651c6ba08`; engine `e27ed7454fc4ea9bebfdaadbfe9e03d9b9e922f0a690806df021575db436cd79`. No external dependency documentation was needed (standard-library-only evaluator).

### EV2 — C1 and C3 confirmatory evaluation

`python ling-bilingual-eval-v117/eval_bilingual.py num-integration-union-v60` exited **0**. Decisive output:

| Direction | Source-known exact | Exact leave-one-out | Bag-of-words leave-one-out | Added-unknown false-attested |
|---|---:|---:|---:|---:|
| NT→EN | 27/27 | 0/27 | 2 guesses, both incorrect | 0/27 |
| EN→NT | 27/27 | 0/27 | 0/27 | 0/27 |

30 authored corpus entries existed; excluded conflict/protected E13/E23/E26. All 27 eligible source inputs are unique in each direction, so there were no duplicate-input fold leaks. Word-order-sensitive E02/E03 have the same unordered token bag but different authored English readings. Even the two bag hits are **wrong**, demonstrating that ignoring order destroys argument focus; it is not evidence that a bag retriever generalizes.

### EV3 — C2 conservative lexical census

Same command exited **0**: 500 attested dictionary entries, 500 distinct normalized NT headwords, 510 English exact/explicit slash-alternative gloss keys. Both directions had **0 ambiguous exact-key collisions** and the unattested sentinel resolved nowhere. H3 is **rejected** on the current dictionary under this matching rule. This says nothing about semantic synonymy, polysemy, or real-world context ambiguity.

### EV4 — C4 controlled unit tests

`python -m unittest -v ling-bilingual-eval-v117/test_bilingual_eval.py` exited **0** and finished `Ran 10 tests in 0.002s` / `OK`. Cases exercise bilingual reversal, NFC/apostrophes without diacritic erasure, exact holdout abstention, conflicting duplicate inputs, order-sensitive bag collision, conservative gloss slash parsing, unknown suffix, and protected exclusions.

### EV5 — E1 exploratory real-engine status probe

`python ling-bilingual-eval-v117/probe_engine.py num-integration-union-v60` exited **0**. For 27 eligible source pairs per direction, in-sample status was `attested` 27/27 in both. When each exact source row was suppressed **in memory** (not from disk):

- NT→EN: **24** `lexical` and **3** `incomplete` (zero sentence-level attested matches).
- EN→NT: **27** `incomplete`.
- Added unknown suffix: all **54** engine responses `incomplete`, **zero** `attested`.

The engine explicitly labels `lexical` as approximate dictionary gloss, **not fluent translation**. Counts do **not** imply the NT→EN engine translated 24 of 27 unseen utterances.

### EV6 — Artifact fingerprints

`sha256sum` exit **0**:

- `eval_bilingual.py`: `a26c555bec87ea5ff915e4f059f824697ba0025cd78d97f56c13e2bdc489df1a`
- `probe_engine.py`: `c7c3efb856dc7a0409bdb3a35b12e595c59ad72273f1bf94b116735df0653469`
- `test_bilingual_eval.py`: `f3da8d1e17a6cf3f028536c86388b449a83517b9bc8d84f8148f25bd05f8d83b`

## Deviations and pivots (append only)

- Initial source evaluation also ran against `integration-numtareen` staged data. That tree's engine blob differed from the live main blob, so I reran **both** evaluation and engine probe against `num-integration-union-v60`, whose exact source and engine Git blobs were independently matched to current GitHub main. The reported EV2/EV3/EV5 numbers are from the main-matched tree.
- A standalone in-memory engine probe was added as exploratory E1, not folded into the confirmatory baseline after seeing results. No source files were changed.

## Verdict

**Producer interpretation only, pending independent hostile review:** H1 supported (zero leave-one-out unseen sentence retrieval); H2 supported in its bounded form (source word evidence does not license fluent unseen-sentence translation); H3 rejected (zero matching English-gloss collisions under conservative normalized exact lookup). The benchmark provides falsifying negatives and source identity, not a newly improved neural translator or a proof of general translation ability.

## Portability and independently reviewed continuation — v126

The original V117 producer record above is preserved intact. Independent
reviewer V124 re-ran the baseline against both the original head and the
Unicode-punctuation repair at main `b15595336ce934e3ed3a44da2b9feedf787c8120`.
The decisive coverage measurements did not change. The reviewer added
216 negative-suffix probes with zero false `attested` results, but cautioned
that these easy negatives do **not** measure real adversarial translation.

The repository-ready implementation lives at:

- `research/bilingual_eval_v0.py` — strict source-pinned pair/bag/gloss census;
- `research/bilingual_engine_probe_v0.py` — real translator, in-memory
  leave-one-out status probe;
- `tests/test_bilingual_eval_v0.py` — standalone invariants and pinned-source
  tamper rejection.

Run offline from the checked-out repository root:

```sh
python -m research.bilingual_eval_v0
python -m research.bilingual_engine_probe_v0
python -m unittest discover -s tests -p test_bilingual_eval_v0.py -v
```

The code now defaults to its containing repository, uses normal module
imports (no sibling workspace directories), and *refuses* authored corpus or
lexicon files whose exact Git blob identities differ from the reviewed bytes:
corpus `53d9f27d03579a1a3fc700c3394b56f834da784e`, lexicon
`c78dccdf9614d8e8e94c968aac5c07a2e4206bf1`. An explicit root argument
or `NUMTAREEN_ROOT` may be used in isolated verification. The engine probe
also refuses data from a different repository root than its imported engine.
This protects the *research benchmark's* provenance; it is not an identity
signature for the author.

### New verification evidence

On 2026-10-27 UTC, a separate staged copy using Python 3.12 executed:

- **11/11 portable tests PASS**, including a newly added source-tampering
  regression;
- paired baseline output remained 27/27 in-sample and 0/27 leave-one-out
  exact for **both** directions;
- held-out real-engine statuses remained 24 lexical/3 incomplete NT→English
  and 27 incomplete English→NT;
- existing staged repository suite: 258 tests, 15 environment-conditional
  skips, exit 0.

Those local results are **not** proof of Python 3.10/3.11/3.13 matrix runs;
GitHub exact-head CI is required after opening the pull request. No new
canonical grammar, lexemes, or translator model are established by this port.
