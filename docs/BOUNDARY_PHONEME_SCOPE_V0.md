# Field writing vs phonemic interruptions: 29-example audit

**Status:** Research-only linguistic analysis. This does not amend canonical Nûm’ta’reen, define alien physiology, or generate phonemes for unattested words.

**Source:** Public `thebrazenbeard/num-ta-reen` main `f862982353d9ab7666b033492071e25190a1dade`; reference grammar V2 (Git blob `d7bd1a1a07d9052b6795b3824bfc18fc9c50e912`), dictionary V2 (`af257a3072d1bd7c6bd1de510258b6fb5ab91264`), normalized corpus (`53d9f27d03579a1a3fc700c3394b56f834da784e`), lexicon (`c78dccdf9614d8e8e94c968aac5c07a2e4206bf1`). These authored texts are design evidence, not biological recordings.

## New, small linguistic constraint

The grammar describes the field apostrophe as a phonemic glottal interruption, but that **does not mean every transcription `/ʔ/` corresponds to a visible apostrophe**. The corpus also uses grammatical clitic `=` boundaries with IPA glottals:

| Authored example | Orthographic boundary types | Author IPA glottal stops | Narrow result |
| --- | ---: | ---: | --- |
| E01 | 0 apostrophes + 1 clitic `=` | 1 | `/ʔ/` is present without `’` |
| E18 | 0 apostrophes + 3 clitic `=` | 3 | Two different consent loci remain distinguishable in grammar |
| E14 | 1 apostrophe + 1 clitic `=` | 3 | One further IPA onset, not written with a boundary mark |
| E27 | 3 apostrophes + 0 clitic `=` | 4 | One further IPA onset, not written with a boundary mark |

Among **29** nonprotected authored corpus examples, a deterministic count finds **27 with equal totals** of `’` plus `=` versus transcribed `/ʔ/`; **2 (E14/E27) have one additional IPA glottal**; **0 have fewer IPA glottals**. This is aggregate counting, *not* segment-by-segment alignment or an empirical phonotactic law. E26 was excluded before per-record phonetic analysis; protected notation remains WITHHELD.

**Linguistic consequence:** A mathematical codebook must preserve three distinct kinds of evidence recoverably, whether encoded as separate fields or in a demonstrably lossless composite: (1) orthographic glottal sign, (2) clitic-boundary structure, and (3) independently authored phonetic glottal onset. A deterministic acoustic renderer may reproduce a source-written IPA sequence *by exact attested lookup*, but a generated utterance cannot infer IPA from a simple count of apostrophes and `=`. In particular, substituting all `=` with punctuation would destroy consent/role morphology.

## Falsifiers / author questions

1. Does every underlying root-initial `uth` carry phonemic `/ʔ/`, as E14 and the dictionary's `uth’se’run` support? One fresh same-register author-approved root with initial `uth` but no `/ʔ/` would defeat that productive onset rule.
2. Are the IPA interruptions at each `=` obligatory, register-conditioned, or a transcription convention? Ask for the same authored E18 clause read carefully in CF and FC with explicit glottal timestamps. A counterexample would disprove a universal equals-to-glottal rule.
3. Does any unaffixed orthographic apostrophe fail to represent `/ʔ/` in independently authored dialogue? A positive example would defeat unconditional apostrophe realization.

> **Hostile challenge:** Equality of total mark and phoneme counts does not prove boundary positions align. Syllabification, lexical initial glottals, coarticulation, and the fictional native timing layer are unresolved. No claim of productive acoustic translation can rest on this count.

## Reproduce

In an isolated staging directory with the four source Git blobs above, run:

```powershell
python -m research.glottal_boundary_census --repo-root PATH_TO_NUM_TA_REEN
python -m unittest -v tests.test_glottal_boundary_census
```

The census emits only IDs, integer counts, blob pins and limitations; no corpus text or protected chord content. Eight local tests passed on Python 3.12, including tampered-source rejection. Independent hostile v146/v153 findings on test portability, source-privacy assertion strength, and overstatement were corrected; fresh v154 review then passed focused, full-suite, source-pin and privacy-injection checks. This remains a noncanonical research observation, not an IPA generator.
