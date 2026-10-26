# Contributing to Nûm’ta’reen

The language belongs to the *Wreckforge Chronicles* worldbuilding canon. New terms are welcome as **proposals**, but adding a plausible-looking form does not make it authoritative.

## Canon boundary

- `sources/` reproduces the supplied reference sources and their provenance. Never overwrite these files with speculative fixes.
- `data/lexicon.json` and `data/corpus.json` are parsed **attested** data from the updated source documents. Each record must remain traceable to its source.
- `proposals/` houses tentative vocabulary, grammar hypotheses and examples. Prefix every proposed entry with a stable proposal ID and explicit `status: "proposed"`.
- Only the author/project owner may promote proposed material to canon. Promotion should record which proposal, the authorial decision, revised examples and collision checks.

## Before proposing a word

1. Search all 500 canonical headwords and the full 30-sentence corpus for an existing expression.
2. Explain the semantic need in terms of Ech’ta’reen state-sharing rather than translating an English word uncritically.
3. Check the updated phoneme inventory (including `/l/`), syllable constraints, diacritics, apostrophe boundaries and reserved ritual `/q/`.
4. State register (`CF`, `FC`, `RT`, `AC`), relevant taboo and whether the item is a root, derivation, clitic or multiword expression.
5. Give at least one contextual example with an **explicitly proposed** gloss; don't present new example sentences as previously attested.
6. Check collisions and dangerous near-matches (e.g. `nûm` versus `num`, `kesh` versus `qesh`).
7. Surface gaps or contradictions rather than silently editing them out. Current examples include an incomplete compact IPA inventory table and a source disagreement on `keth` IPA.

## Translator principles

- Canonical corpus sentences take precedence over dictionary-derived glosses.
- Unknown words and multiple English candidates remain visible.
- Role, echo-status, consent, taboo and register information must not be silently discarded.
- A written transliteration is not identical to the native resonance channel.
- A safe failure or explicit "unknown" is preferable to a confident invented translation.

Run `python -m unittest discover -s tests -v` before proposing changes.
