# Held-out morpheme recovery — bounded, source-pinned research

**Research status:** This is a *candidate* benchmark of written, author-annotated
Num’ta’reen interlinear gloss (IGT) recovery. It is not a canonical language
change, fluent Num’ta’reen↔English translation, acoustic evidence, or a learned
language model. Independent hostile qualification is required before treating
the frozen implementation and measurements as accepted.

## Corpus custody and exclusions

- Original author corpus Git blob: `53d9f27d03579a1a3fc700c3394b56f834da784e`.
- Original author lexicon Git blob: `c78dccdf9614d8e8e94c968aac5c07a2e4206bf1`.
- Thirty authored entries exist. E13/E23 are contradictory, and E26 is
  protected; none is eligible for this experiment. E26 must not be processed
  or used as a training example by public research helpers.
- The eligible set is *exactly* the 27 distinct IDs left after exclusions.
  Each leave-one-out fold learns from 26 other examples. This is a tightly
  dependent set of folds, not an independent field validation set.
- Every held-out input is source orthography alone. The held-out authored IGT
  is used **after** predictions have been frozen, solely for scoring.
  Author-provided English free translations never train the analyzer.

The pinned on-disk bytes and the in-memory rows handed to an evaluator are
different custody surfaces. Neither may be silently upgraded to
`SOURCE_PINNED` evidence if the data were modified. A successful test suite
does not substitute for checking that invariant adversarially.

The current research implementation deliberately distinguishes them:

- `evaluate_rows(caller_rows)` returns
  `CALLER_SUPPLIED_UNVERIFIED_IGT_MORPHEME_RECOVERY`, with both source-hash
  attribution fields set to `null`. A caller can mutate these objects;
  dictionary-polysemy flags may also be caller-supplied.
- `evaluate(repo_root)` reads and independently verifies the **raw bytes** of
  both author corpus and lexicon against the two exact pinned Git blob IDs
  before returning `SOURCE_PINNED_TRAIN_ONLY_IGT_MORPHEME_RECOVERY`. It keeps
  the same measurements while making its stronger attribution explicit.

Changing a caller-supplied E01 gold IGT row therefore may change the score,
but cannot impersonate the pinned source grade or hashes. Changing on-disk
source bytes makes `evaluate(repo_root)` fail closed.

## What is predicted

The analyzer learns mappings between observed Num’ta’reen written morphemes
and the author's IGT labels. It uses existing, *provided* `=` clitic
boundaries and narrowly attested transcription alignment conventions.

At each fold, a component receives a label only when the other training
examples give it a unique label. Unknown and ambiguous components abstain.
This tests whether individual morpheme labels transfer to new combinations;
it does not infer a semantic parse, scope, syntax, or English sentence.

Negative/control systems: exact whole-utterance memorization, whole-token IGT
memorization, and copying Num’ta’reen source units into gloss slots. The
separate lexicon-polysemy guard is *post-hoc*, added after two factorized
errors were observed; it can only abstain, and its apparent zero-error result
cannot be treated as independent confirmation.

## Observed exploratory scores (27 folds; 94 tokens, 127 IGT morphemes)

| Measured system | Correct | Wrong | Abstained |
| --- | ---: | ---: | ---: |
| Whole utterance exact memorization | 0/27 utterances | 0 | 27 utterances |
| Whole-token IGT memorization | 97/127 morphemes | 0 | 30 morphemes |
| Source-clitic factorization | **112/127 morphemes** | **2** | **13** |
| Post-hoc lexicon-polysemy veto | 112/127 morphemes | 0 | 15 |

The 15 extra recovered units are evidence of reuse of IGT segment labels in
the *same small curated sample*, not evidence of generalized conversational
translation. The two wrong units are variants of `vahl` (authored `latch`
versus `latch/stabilize`) across held-out E07/E18; the post-hoc veto was
selected after inspecting this discrepancy.

### Falsifiers and limitations

> **An exact 27-ID set alone does not prove source provenance.** A synthetic
> row can reuse `E01` with changed orthography or IGT. Unless the evaluator
> detects that substitution, any `SOURCE_PINNED` output is unsupported.

> **Morpheme recall is not compositional sentence understanding.** A correct
> `PAT` or `CONS` unit does not validate participant scope, consent pragmatics,
> evidential interpretation, or the English meaning of a fresh sentence.

The denominator is 127 authored morphemes, not 127 independently collected
utterances. No external audio, resonance/frequency observations, speaker
identity, or held-out naturalistic dialogue is included. Public and private
API custody boundaries should be tested separately; direct helpers must
reject E26 rather than merely relying on the command-line loader to exclude
it. Hostile Python objects must not be able to modify the reported source
input through overridden string or container behavior.

## Reproduction (after qualification)

From repository root:

```sh
python -m research.heldout_morpheme_probe --repo-root .
python -m unittest -v tests.test_heldout_morpheme_probe
python -m unittest discover -s tests -p 'test_*.py' -q
```

The module is standard-library only. Its report must include provenance
of exact source files, explicit exclusions and limitations; report output
must never silently acquire a stronger evidence grade than its inputs.
Do not place this experimental decoder in the production translation path.
