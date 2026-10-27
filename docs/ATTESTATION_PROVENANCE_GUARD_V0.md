# Authored attestation integrity — bounded adapter contract

This is a software provenance rule, not a new rule of Num’ta’reen.

`Translator().translate()` may label an exact sentence as `attested` only
when the parsed `data/corpus.json` bytes match the pinned authored export
SHA-256 in `numtareen/engine.py`, its loaded row is unchanged, and the input
matches the authored lookup field. The source JSON files use LF on Windows and
Linux via `.gitattributes`.

An exact match from altered, imported, or post-load mutated corpus data is
reported as `unverified` and remains available to callers as a labeled,
unqualified match. `format_translation()` does not call it source-attested.
Custom lexical fixtures continue to support lexical/ambiguous/unknown lookups.

Canonical corpus updates require deliberate source verification and a reviewed
pin change. The pin does **not** authenticate runtime code or defend against a
caller that can arbitrarily edit Python object internals; this is an evidence
label guard at the file/API boundary, not a secure enclave or a signature.

The lexicon file is fingerprinted separately. Lexical fallback results carry
`lexicon_file_verified` as a **file-level** provenance grade, and
`lexicon_candidate_verified` independently checks that every emitted lexical
record still matches its private post-load snapshot. Individual emitted
candidate dictionaries include `source_candidate_verified`; source-inconsistent
records are marked unverified, even when the original file's hash was valid.
The candidate grade is `null` when no lexical candidate was emitted. Neither
grade promotes an approximate dictionary gloss into a source-attested sentence
or authenticates arbitrary caller code.

Programmatic strings are converted to base `str` before any normalization or
lookup. A caller-owned `str` subclass cannot override `.translate()` to make
the searched text differ from the recorded input.

Regression cases: byte-identical copies retain attestation; same-count edited
JSON, in-memory corpus row mutation, key reindexing, and rewriting `str`
subclasses do not. Modified forward and reverse dictionary records and
segmented clitics also lose candidate-level verification. The translator
still does not generate fluent novel Num’ta’reen.
