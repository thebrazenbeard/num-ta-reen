# Nûm’ta’reen — language overview

Nûm’ta’reen is the Ech’ta’reen language/communication mode from *The Wreckforge Chronicles*. The name denotes resonance-based **state-sharing**, rather than a straightforward spoken human language. The written words below are a field transliteration of a richer multimodal signal; written text cannot convey all its timing and resonance.

## Canonical source hierarchy

1. `sources/reference_grammar_v2_updated_lphoneme.txt` — current grammar.
2. `sources/dictionary_v2_updated_lphoneme.txt` — current 500-entry lexicon.
3. `sources/language_core_v1.txt` — historical reference and prior grammar.
4. The original, non-updated V2 source exports — historical comparison only where superseded.

`sources/SOURCES.md` records the original OneDrive filenames, hashes, and precedence decisions. The extracted `.txt` files are readable source exports, not reconstructed or newly invented canon.

## Distinctive language features

- **Apostrophes are phonemic.** `’` marks a glottal interruption (`/ʔ/`), not a typographical flourish. ASCII `'` can be accepted as input convenience without changing the canonical output.
- **Vowel distinctions matter.** `nûm` (align/cohere) and `num` (a momentary clipped alignment tick) are distinct. Accent-stripping would corrupt meaning.
- **There is no ordinary tense system.** Echo-status/evidentiality is grammaticalized: for example `ech` (witnessed), `reen` (cross-echo verified), `qir` (loop), and `ruun` (return-pattern).
- **Role and consent clitics matter.** `=ka` agent; `=en` patient; `=ru` origin; `=va` goal; `=shi` means; `=uth` permission/consent. Omitting consent changes pragmatics and potentially makes an utterance coercive.
- **Several registers are documented.** `CF` Conclave formal, `FC` field clipped, `RT` ritual, `AC` Anchor creole/contact. Ritual or taboo items must remain explicitly tagged.
- **The updated sources correct `/l/`.** The `UPDATED_lphoneme` grammar treats `/l/` as a full phoneme. Older statements to the contrary are superseded; affected dictionary items include `lek`, `shel`, `qir’lek`.

## Translation contract

1. An exact match to a sentence in the grammar's annotated corpus can be reported as a **source-attested translation**.
2. A dictionary match can be reported as an **approximate lexical gloss** with part-of-speech/register/taboo provenance.
3. An unknown phrase must remain **unknown**, not silently become an invented Ech’ta’reen sentence.
4. Reverse English lookup may have many candidates. It is not safe to assume every dictionary gloss is a complete sentence or every source sentence has a unique inverse.
5. Written input does not encode native resonance/prosody; true-name chord notation is unspoken and must not be assigned a pronounceable translation.

## Examples from the revised grammar

| Field transliteration | Source free translation |
| --- | --- |
| `Nûm ta=en ech.` | “You are aligned (I witness it).” |
| `Ta’qesh.` | “Stop. Do not proceed.” |
| `Vahl=uth ta=en=uth ech.` | “You are being stabilized, with consent (witnessed).” |
| `Kesh na=ka veyl=va ech.` | “I cross toward the boundary (witnessed).” |

See `data/lexicon.json` and `data/corpus.json` for searchable canonical records and provenance. The translation interface is a constrained glossary-and-attested-example tool, **not** a trained language model or a claim of unrestricted fluent translation.
