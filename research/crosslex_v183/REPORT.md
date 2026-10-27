# Num’ta’reen cross-lexical morphology: source-bound evidence audit

**Status:** research note, no canonical corrections or invented utterances.

Source custody (Git blobs on `thebrazenbeard/num-ta-reen@00f3864d8d1d483b15104a0ccd13ec70da0a6cfc`): corpus `53d9f27d03579a1a3fc700c3394b56f834da784e`, lexicon `c78dccdf9614d8e8e94c968aac5c07a2e4206bf1`, parse report `932a579ac4f55f2452b178c9844360469e4a6884`, current grammar `d7bd1a1a07d9052b6795b3824bfc18fc9c50e912`. Do not read, render, or infer E26's protected chord.

## A correction that matters

The dictionary's `Ex:` references are *illustrative*. `docs/SOURCE_PARSE_REPORT.md` explicitly says they do **not** assert literal occurrence of a headword in the referenced utterance. I initially misread `=ru → E20` and `=shi → E23` as citation contradictions. **That interpretation was wrong and is retired.** Both clitics are authored grammar/dictionary facts, but the referenced E20/E23 orthographies contain neither corresponding literal string. Their illustrative references must not be promoted into `AUTHOR_UTTERANCE` evidence for the individual morpheme.

`crosslex_citation_audit.py` reports exactly that narrower fact, with `=en → E01` and `=va → E20` positive literal controls. The 4/4 test suite source-pins all three relevant files, rejects modified source bytes, and tests fail-closed behavior around hostile E26 accessors. No source file is changed.

**E26 custody clarification:** Source hashing necessarily reads and JSON-parses the complete archived corpus, including E26's raw bytes. The linguistic audit checks the E26 record ID only to exclude it; it neither accesses its orthography/IGT/IPA for analysis nor emits those fields. The structured result labels this as `WITHHELD_NOT_ACCESSED_FOR_ANALYSIS`, and separately discloses `raw_corpus_json_parsed: true`. An earlier `WITHHELD_NOT_READ` label overstated the exclusion and is retired.

## Where the authored corpus actually crosses lexical contexts

| Surface pattern | Independent authored contexts (E26 excluded) | What is supported | What is **not** established |
| --- | --- | --- | --- |
| Patient `=en` | `ta=en` E01/E02/E03 and many; `veyl=en` E23; `kesh=en` E24 | A role clitic appears on at least **three distinct hosts** (person, boundary, crossing). | Full productivity on arbitrary hosts or sentence generation. |
| Agent `=ka` | `na=ka` E02/E03/E20/E21/E23/E24; interrogative `mën=ka` E09 | Same role label spans multiple predicates; WH-host use is separately authored. | That changing argument order always preserves identical focus or referent. |
| Goal `=va` | `veyl=va` E20/E21; loan `‹airlock›=va` E28 | A role clitic spans a native host and a contact loan. | Native phonotactic treatment of arbitrary loans or an origin `=ru` utterance. |
| Predicate consent `=uth` | `kesh=uth` E21 versus plain `kesh` E20; `vahl=uth` E18; `uth’nûm=uth` E14 | Clitic or consent-related morphology occurs with **at least three predicates**. E20/E21 is an isolated predicate-suffix contrast. | A single interchangeable form for all consent scopes; E07→E18 also changes `ta=en` to `ta=en=uth` (participant consent). |
| Focus `=sha` | `nûm=sha` E05, `keth=sha` E24 | Suffix occurs on two distinct predicates/semantic hosts. | An isolated focus minimal pair for `keth`; E24 changes many other words from E05. |
| Question `hë?` | `nûm` E08/E22, `kesh` E09 with `mën=ka` WH | Final Q particle appears across two predicates; E01↔E08 and E15↔E22 are local contrasts. | A cross-predicate polar-question transformation: E09 is a WH question and lacks a matched Kesh declarative. |
| Clause NEG `vu` | record-latching E19; crossing in E30's third clause | Same surface NEG across two lexical propositions. | Shared position/scope or equivalence to inverse prefix `vael-` (E10). |
| Structural `qir` | E15/E22, both `nûm` context | Exact local recurrence/question 2×2 is attested with E01/E08. | Cross-lexical productive LOOP, semantic scope commutativity, or acoustic code assignment. |
| WIT `ech` / VRF `reen` | Many distinct predicates, e.g. `nûm`, `kesh`, `vahl` with `ech`; `threnn’vahl`, `rhel`, `keth` with `reen` | Both evidential layers are authored across several contexts. | A matched same-proposition `ech`↔`reen` contrast; absent in this corpus. |

## Bounded held-out probes worth doing next

1. **Morphological host transfer:** Hide E23's `veyl=en` and E24's `kesh=en` *whole surface forms* from a learner; teach it the authored `=en` PAT rule on `ta=en` and known lexical host boundaries. Ask for the two held-out host-plus-role forms. Compare to exact whole-token memorization, source-copy, dictionary/grammar-oracle controls. This is a retrospective **orthographic composition** benchmark because the grammar explicitly supplies the rule; it would not prove novel speech productivity.
2. **Prospective creator elicitation:** For E20 crossing and E07 stabilization, Patrick supplies three missing cells each of the LOOP × polar-Q grid (original baseline retained). Freeze all predictions *before* he authors the held-out forms. Require explicit roles, evidential commitments, register, and consent loci; allow **AUTHOR_DECLINES** rather than inventing taboo/unsafe expressions. Ask whether LOOP structurally scopes over evidential verification or only event recurrence; ask whether `hë` questions the state or the speaker's witness; test suffix order without presuming semantic commutativity.
3. **Consent-scope separation:** E20↔E21 changes predicate `=uth` only, whereas E07↔E18 changes both predicate and participant. Request author examples isolating participant `=uth` while predicate scope stays fixed. No inference that missing `=uth` means actual non-consent.
4. **Evidential matched pair:** Request the *same* proposition with `ech` and `reen` only if the author's fictional evidence context justifies both. This would distinguish role-stable evidential swap from an English tense paraphrase.

## Hostile alternative explanations

- Most examples are constructed for the grammar, not independent spontaneous speaker data. Orthographic clitic sharing can reflect author design rather than natural productive competence.
- The lexicon/grammar already list the morphemes. Source-aware code may look like it inferred a rule from holdout although it merely read the answer from the dictionary; separate dictionary-oracle baseline is mandatory.
- Wh-question E09, alarm E30, loan E28, and consent-locus E18 carry confounds; they cannot count as clean single-factor contrasts.
- Cross-lexical morphology must not be promoted into acoustically realized Ech’ta’reen resonance parameters. The author has not supplied native signal recordings/codebook. E26 stays withheld.

**Decision requested from Patrick only if creating new canon:** approve an elicitation session, not pre-generated forms. Existing authorship is preserved intact.
