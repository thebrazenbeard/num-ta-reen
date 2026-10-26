# Nûm’ta’reen OneDrive source extraction report

- Folder: `Documents/Books/The Wreckforge Chronicles/Races, Species, and Other Fauna/Ech'ta'reen (Phase Shifters)/Num'ta'reen Language`.
- Five DOCX sources were read, including both original and amended `UPDATED_lphoneme` dictionary and reference grammar plus the Language Core.
- Canonical machine corpus: [`lexicon.json`](../data/lexicon.json), 500 complete entries; [`corpus.json`](../data/corpus.json), 30 complete E01–E30 source-utterance/English-translation pairs.
- Source-preserving exact fields: `headword`, `ipa`, `category`, `register`, `taboo`, `gloss`, `derivations`, `example_refs`, `source_line`, `source_text`; corpus retains `orthography`, `ipa`, `igt`, `free`, `notes` with source metadata.
- Parsing: 500/500 lexemes match the anchored entry schema, zero malformed entries, zero duplicate headwords under NFC+case-insensitive comparison; 30/30 corpus records have nonblank orthography, IPA, IGT, free translation.
- Verification: `jq -e '[.entry_count, (.entries|length), ([.entries[].headword]|unique|length)] == [500,500,500]' data/lexicon.json` → `true`, exit 0; analogous `[30,30,30]` corpus test exit 0.

## Amended source priority

- Updated reference grammar explicitly adds **/l/** as a phoneme, with [ɫ] allophone; the older grammar lacked it.
- Updated dictionary changes exactly 3 gloss/usage descriptions (`lek`, `shel`, `qir’lek`) to no longer wrongly call /l/ non-inventory, retaining contact/deprecated register labels.
- Use both amended documents as active source. Use Language Core for traceability and older documents for historical comparison.

## Linguistic and translator cautions

- Native communication is described as resonance-based **state-sharing**, with field transliteration as an analytic approximation; simple word-for-word substitution is not semantic equivalence.
- Predicate-first state packets; role clitics `=ka` (agent), `=en` (patient), `=ru` (source), `=va` (goal), `=shi` (means), `=uth` (consent); no ordinary tense; echo operators `ech`, `reen`, `qir`, `ruun`, `na’vyr`.
- Distinguish formal CF, clipped FC, ritual RT and Anchor-creole AC. `RT-ONLY`, `CLP-ADJ`, `TRUE-NAME`, `DEAD-NAME`, `CONTACT/DEPRECATED` tags are semantically significant and should be visible in CLI output.
- Canonical exact full-utterance translations E01–E30 should take priority over gloss-based lexical fallback.
- In E27, source orthography is intentionally two lines: `Threnn’vahl reen.` + `Uth’se’run.`; source IGT is also multiline. Exact fields preserved; `orthography_index` joins whitespace for CLI phrase matching.
- Other substantive unresolved inconsistencies remain in the provided canon: IPA references phonemes (e.g., /v/, /θ/, /ɛ/, /ʊ/) not shown in the compact inventory table, so do not invent an authoritative phoneme validator from that table alone.
- `E26` uses a taboo true-name chord in its orthography; a public command must not silently vocalize chord notation. Consider taboo warnings for exact matching and translation.
- The corpus's `E24` `Keth=sha` IPA is `/kɛθʔʃɑ/` while dictionary `keth` IPA is `/kɛt/`. Retain both source facts, flag for author review, do not normalize silently.
- The dictionary's `E01…E30` `Ex:` references are illustrative links, not evidence that every listed headword literally occurs in that exact corpus utterance; refrain from making a false attestation claim.

## Counts

- Lexical categories: STATE 187, ACT 145, PART 72, ENTITY 25, ECHO 20, ACT/STATE 17, STATE/ACT 15, CLITIC 8, DERIV 8, STATE/ENTITY 1, ENTITY/ACT 1, ENTITY/STATE 1.
- Register: CF 326, RT 76, CF/FC 72, FC 14, AC 10, CF/FC/RT 1, CF/RT 1.
- Taboo: NONE 399, RT-ONLY 47, CLP-ADJ 26, CONTACT/DEPRECATED 10, DEAD-NAME 10, TRUE-NAME 8.

## Source identifiers

- Dictionary amended `62D907BE0B18283C!s62b4aa728f67475394cb4a8a2b28e271`, SHA-256 `30B1F35AF78713D03B51CFCA20A957EB917FFAFA0A0E344D3E859409B5078C4A`.
- Grammar amended `62D907BE0B18283C!sc299f082e49844a6b8d3bb0729591038`, SHA-256 `B47A6F9AF68AC2CA643AA01E59FAAF9C8E738A03D679B95921CB47998E5AF441`.
- Core `62D907BE0B18283C!s8fe0927c309442c3b5ee11580d258186`, SHA-256 `FE14A36C030908A1587B62FE316F53271613FD87C8620095139E9A0D274D6E7F`.
- Dictionary older `62D907BE0B18283C!s760f9623e5a045f9ba04abf0d7b0b730`; Grammar older `62D907BE0B18283C!s49babc28b7514ea38aed5f59296a3488`.

All OneDrive operations were read-only. This report and the extracted source text and machine-readable data are part of the private destination repository.
