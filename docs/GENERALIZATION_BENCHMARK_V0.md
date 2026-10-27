# Num’ta’reen generalization qualification — negative-control benchmark v0

**Status:** NONCANONICAL RESEARCH. No new Num’ta’reen words, grammar rules,
resonance frequencies, or speaker meaning judgments are introduced here. This
instrument addresses a narrower question: **can existing implementations
preserve distinctions in the *authored English interlinear glosses* without
obtaining apparent success from memorizing the 30 public examples?**

## Source and custody

- Source: public `thebrazenbeard/num-ta-reen`, authored corpus `data/corpus.json`.
- The loader verifies Git blob SHA-1
  `53d9f27d03579a1a3fc700c3394b56f834da784e` *before* recognizing the
  30 numbered records. Semantic observations are independently revalidated by
  the source-bound proposal module before their features are scored.
- The original 500-entry dictionary and 30-utterance corpus remain untouched.
- E13 and E23 abstain because source conflicts prevent an unqualified scope
  observation. E26 is withheld from the parser and reports; no true-name chord
  or numeric notation is copied into code, documentation, or test fixtures.
- Every source sample is **already public**. A leave-one-out program here is a
  stress check, **not a cryptographically hidden, independent test**. A model
  pretrained on the repo might have seen every row.

## Current measured baseline

Run from a full repository checkout:

```powershell
py -3 -m research.semantic_generalization_benchmark
py -3 -m unittest discover -s tests -p test_semantic_generalization_benchmark.py -v
```

In an isolated scratch copy, set `NUMTAREEN_REPO_ROOT` to the checkout and
`PYTHONPATH` to a search path including this research package and the
checkout before invoking the same commands. The program returns JSON with
aggregate measurements and corpus IDs, **not source orthography, IGT, or IPA**.

| Probe | Observed outcome | Interpretation |
| --- | --- | --- |
| Source-bound eligibility | 27/30, 3 refused | Constraints are active; no source-conflict promotion |
| Feature-tagged leave-one-out, English→Num | 0/27 exact hits | Memorizing the 26 training sentence strings cannot translate the held-out phrase |
| Feature-tagged leave-one-out, Num→English | 0/27 exact hits | Same result in reverse |
| Source-IGT structured fingerprints | 27 different | Author glosses distinguish the observations; **not** evidence of a productive grammar |
| Old synthetic acoustic packets | 16 different | 11 degrees of source-observation discrimination are lost (27→16); 16 observations participate in collisions |
| Old codec collision groups | 5, comprising 21 colliding pairs | A quantitative semantic-structure preservation failure |
| Opaque 3,072-slot random IDs | 27 distinct sampled labels | Any sufficiently large lookup key space can index these examples without learning a language |
| Opaque-ID held-out semantic credit | 0 | Knowing sampled training IDs supplies no unseen-sentence rule |
| Nonsense-token diagnostic | `incomplete` in both directions | Unknown material remains explicitly untranslated |
| Eight proposed novel-meaning probes | unscored | No author-approved examples exist to justify accuracy numbers |

The leave-one-out folds are **exhaustive and multi-label feature-tagged**, not
a statistically balanced train/test split. A fold excludes one corpus ID from
*both* exact source-utterance indexes; its 26 remaining IDs are the training
side. The dictionary can still produce lexical glosses for individual tokens,
but an approximate lexical gloss is **not** scored as a correct sentence.
The shipping translator can, of course, retrieve a source example when all
30 rows are available. This benchmark constructs a *training-only index*
without the tested row; it does not falsely claim that the shipping translator
was retrained or that a neural generalizer was evaluated.

The random-label control uses a fixed seed (`20261026`) and samples 27 of
3,072 integers without replacement. It intentionally grants perfect
*in-sample* label separation while denying any claim of zero-shot semantics.
This falsifies a tempting but unsound inference: successful 3,072-way
synthetic waveform reconstruction does not imply Num’ta’reen translation.

## The five source-attested near contrasts

These are source-licensed comparisons, not proof of freely compositional
*minimal pairs*. Each is selected *before* running the benchmark:

| IDs | Source-gloss distinction | Old packet behavior |
| --- | --- | --- |
| E01 / E05 | Predicate focus | Collapses |
| E01 / E08 | Statement vs question | Collapses |
| E02 / E03 | Ordered agent and patient | Collapses |
| E01 / E15 | Ordinary statement vs echo LOOP | Distinguished |
| E07 / E18 | Different consent loci and predicate context | Distinguished as a binary presence bit, but locus information is still lost |

The source fingerprint is reconstructed from predicates, ordered role and
referent glosses, topical/focal annotations, question, polarity, echo,
evidential, clause links and each consent locus. It **omits corpus ID** to
avoid a trivial ID-lookup solution. Only source-verified observations can
produce this fingerprint; forged in-memory dataclass fields are refused.

The lossy alignment projection uses `research/alignment_projection.py` and
the already-reviewed `numtareen/experimental_resonance_packet.py` type. The
codec's `scope="narrow"` is a **synthetic placeholder**, never a native
source inference. Its collisions are valid evidence of failure for the
*tested typed feature mapping*, not a mathematical impossibility proof for
all possible 3,072-label encodings.

## What requires new author-created data

Eight predeclared proposal-only contrast categories are emitted as `P01`–`P08`:

1. Previously unseen lexical predicate.
2. Question scope outside an attested sentence.
3. Topic and focus in a new joint context.
4. Novel participant ordering/referents.
5. Grant vs *active withdrawal* of consent.
6. Predicate vs participant consent locus.
7. Echo LOOP within a question.
8. Unknown stem plus clitic behavior.

Each requires Patrick to specify orthography, pronunciation/acoustic
realization as appropriate, pragmatics, semantic distinctions, and explicit
negative examples. No proposed new expression should enter canonical
`data/*.json` until he approves an exact versioned source amendment.

The already merged creator decision packet proposes a rigorous extension:
five **public** calibration controls plus **15 novel blind** author-created
cases, independently sealed with hashes, randomized nonleading prompts,
frozen implementation and one scoring pass. Its 20 total cases must never be
misreported as 20 held-out examples. The benchmark implemented here does
**not** claim that blind experiment has occurred.

## Acceptance gate for a future trainable translator

Record, for each precommitted test item, at least:

- Source custody, exact source revision, and whether the item was visible to
  any training or retrieval pipeline.
- Bidirectional full-utterance accuracy on novel approved cases, not just
  lexical token overlaps.
- Explicit refusal/abstention rate; calibration on ambiguous, unknown, and
  conflicting inputs. Do not score an honest refusal as a fluent translation.
- Preservation of predicate identity, ordered participants, focus/topic,
  polarity, Q/echo, provenance claim, and each consent scope.
- Baselines: exact source lookup, dictionary gloss only, opaque ID lookup,
  and the older synthetic acoustic structure.
- Separate testing of a **physical** channel (frequency, timing, phase,
  interference, ambient noise, adversarial tampering). No physical or
  semantic success is assumed from a JSON/codec round trip.

> **Hostile challenge:** Because the corpus is public and only 30 utterances
> large, even perfect source-example accuracy could be memorization or
> retrieval. A measured advantage becomes evidence of compositional learning
> only after independently held-out, author-approved contrasts survive
> falsifiers against the trivial ID and lexical baselines.
