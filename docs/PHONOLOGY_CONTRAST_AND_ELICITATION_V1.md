# Nûm’ta’reen phonology: source-pinned contrast census

**Status:** Independent model research; not a canonical correction, speaker fieldwork, or acoustic recording. This supplements the repository's linguistic contradiction audit without changing any source entries.

**Reference:** Public num-ta-reen main commit 736388809d710ac25e7e2d1f3bc0c70e31b51ba5. Author grammar Git blob d7bd1a1a07d9052b6795b3824bfc18fc9c50e912, dictionary blob af257a3072d1bd7c6bd1de510258b6fb5ab91264, normalized lexicon blob c78dccdf9614d8e8e94c968aac5c07a2e4206bf1.

## Numerical finding

The grammar I.2 consonant chart (physical extraction lines 517–541) lists /p t k q ʔ s ʃ x h m n ŋ ɾ~r l w j/ and the base vowel chart (lines 542–550) /i a u e o/ with length. I.4 at lines 38–41 permits final /n ŋ k t ʃ x/ and four Conclave-formal onset clusters /ʃr xr kw sw/. The dictionary at lines 7–9 claims native entries strictly comply. A deterministic census of **500 authored dictionary entries** finds:

| IPA diagnostic | Entries flagged | Entries tagged CF |
| --- | ---: | ---: |
| Contains /v/, absent from chart | 139 | 111 |
| Contains /θ/, absent from chart | 93 | 60 |
| Contains /t͡ʃ/, absent from chart | 19 | 18 |
| Ends /m l r ɾ θ v/, absent from listed codas | **161** | **133** |
| Contains /tɾ/, absent from listed four onset clusters | **87** | not segmented |

The 161 is a single aggregated count, with disjoint terminal segments: θ 47, l 37, m 31, ɾ 17, r 16, v 13. Some source entries have slash-separated register labels (CF/FC); register subtotals overlap. Many IPA strings represent compounds or derived words, and /tɾ/ may also occur across structure: **these are flagged substrings, not a validated count of illegal syllables or unique root morphemes**.

Vowel qualities absent from the base chart occur in: ɛ 318 entries, ɑ 161, ʊ 59, ɔ 11, y 9, ɪ 1. **Qualification:** Grammar I.2 line 30 explicitly licenses [ɑ] as an /a/ allophone, so that segment alone does not contradict phonology. The treatment of other vowels remains unresolved.

**Reproducibility (in the repository root):** `python -m research.phonotactics_census`; `python -m unittest discover -s tests -p test_phonotactics_census.py -v`. The module resolves its sibling `data/` and `sources/` directories relative to the installed checkout. For an isolated research workspace only, set `NUMTAREEN_REPO_ROOT` to the exact complete checkout and put the research package on `PYTHONPATH`. The script pins all three Git source blobs, emits only aggregate counts and phonetic symbols, never prints lexemes or E26 notation, and is backed by five passing tests.

## Three author experiments with discriminating outcomes

### P1 — What are /v θ t͡ʃ/?

Source probes: dictionary veyl /vejl/ (line 51), ech /ɛt͡ʃ/ (line 27), =uth /ʔʊθ/ (line 24). They are non-taboo CF-bearing entries, **not** minimal pairs. Independently ask the author if each unexpected segment is (A) an additional contrastive native phoneme; (B) a conditioned allophone of a specifically identified existing phoneme; (C) an IPA transcription needing correction; or (D) register-dependent, other, or unknown. Shuffle option labels when eliciting. For B, require a predictive phonetic environment that derives the cited forms plus two untouched dictionary entries. For A, require at least one author-specified same-register, same-position contrast with distinct interpretation. Coarticulation alone is not phonemic contrast.

**Falsifier:** a proposed allophone function that cannot account for source occurrences without per-entry exceptions. No coined minimal-pair words are canonical evidence.

### P2 — How are word-final /m l/ and cluster /tɾ/ licensed?

Use the already-authored uncomplicated forms nûm /nuːm/ (dict line 49), veyl /vejl/ (51), rhel /rɛl/ (53), and threnn /tɾɛn/ (52). Ask the author to annotate syllable boundaries and perceived lexical identity in careful CF and fast FC pronunciation, then judge: (A) broaden coda/onset inventories; (B) add explicit resyllabification or epenthesis conditions; (C) narrowly bounded register/lexeme exceptions; (D) other/unknown. This is a **syllabification and register experiment**, not a license to create new roots.

**Falsifier:** any revised rule that fails to derive these four already-authorized forms and independent held-out lexicon entries. A one-word adjustment with no predictions does not repair a grammar.

### P3 — Is /q/ ritual restriction lexical or segment-wide?

Grammar I.2 line 27 restricts /q/ to ritual/taboo-adjacent usage. Dictionary qir /qir/ (line 29) explicitly licenses CF/FC/RT and authored E15/E22 place it in normal clauses; qesh /qɛʃ/ (line 106) is RT-only, occurring in E29. **qir and qesh differ in meaning and are not phonemic minimal pairs.** Ask if the *unchanged authored qir sentences* are acceptable CF, FC and RT, and separately test qesh outside RT, then adjudicate (A) lexical exceptions, (B) register-conditioned phonetic realization, (C) overly broad segment rule, or (D) alternative historical/register explanation.

**Falsifier:** a segment-wide ritual ban that cannot explain E15/E22 without quietly relabeling their register; or a lexical rule that cannot predict other authored /q/ items.

## Software and mathematical consequence

The attested phonetic bridge should remain **verbatim**: it must show the source's authored IPA without normalizing uncertain segments or inventing pronounceable novel sentences. Synthetic resonance packet features can be round-trip tested, but numerical carriers must carry an explicit noncanonical/synthetic provenance label, not a native-Ech’ta’reen-acoustics claim. Only future author-approved recordings plus controlled register/phoneme labels and blind held-out comparison could ground phonetic frequency, phase, formant or timing parameters. Keep E26 protected notation WITHHELD, with no generated surrogate.

> **Hostile challenge:** Calling every chart/transcription disagreement allophony is unfalsifiable without a conditioning rule and counterexamples. Current transcriptions are too inconsistent with the advertised inventory to justify a hard phonotactic validator that rewrites or rejects existing dictionary entries. Preserve warnings and an author decision queue until P1–P3 are resolved.
