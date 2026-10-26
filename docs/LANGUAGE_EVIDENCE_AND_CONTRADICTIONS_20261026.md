# Nûm’ta’reen: attestation, structure and unresolved author decisions

Status: **evidence audit and language-development proposals, not canon**.  
Subject: `thebrazenbeard/num-ta-reen@ed9a94d53d17db6415de172858773714644e01ba`, tree `36e6f4e812a5b6b1cbf380ec3be621cd76f3f486`.  
Review type: model source inspection plus deterministic text counts; **not** speaker fieldwork, acoustic measurement, or human canon approval.

## Evidence precedence

The repository's `sources/SOURCES.md` names two current authorities: `sources/reference_grammar_v2_updated_lphoneme.txt` (Git blob `d7bd1a1a07d9052b6795b3824bfc18fc9c50e912`) and `sources/dictionary_v2_updated_lphoneme.txt` (blob `af257a3072d1bd7c6bd1de510258b6fb5ab91264`). Earlier `language_core_v1.txt`, original v2 grammar and original dictionary are historical comparisons; the amendment introduced /l/ explicitly into the inventory. The raw Word-to-text extracts are **not layout-exact**. The phoneme/vowel inventory table appears at the end of the extracted grammar (lines 517–550), despite heading I.2 at lines 24–30.

- Canonical normalized lexicon: 500 author-dictionary entries, `data/lexicon.json` Git blob `c78dccdf9614d8e8e94c968aac5c07a2e4206bf1`.
- Canonical normalized bilingual corpus: 30 authored examples E01–E30, `data/corpus.json` blob `53d9f27d03579a1a3fc700c3394b56f834da784e`.
- **Do not confuse:** 500 **authored lexical entries** with 500 naturally attested tokens, 30 **authored example sentences** with independent alien-speaker observations, and proposed compositional rules with established usage. The export establishes a fictional reference design.
- E26 contains a protected true-name notation in original field material. Do not print, regenerate, measure, or infer that chord; diagnostics may report only `WITHHELD`.

## Positive structure already defensible from current author material

| Feature | Source evidence | Attestation class / degree |
| --- | --- | --- |
| Human-readable orthography approximates native resonance/timing communication; it is not the physical substrate | Grammar I.1 lines 18–23; corpus V.0 line 374 | AUTHOR_GRAMMAR |
| Phonemic /ʔ/ corresponds to orthographic apostrophe `’`; /l/ is current full phoneme | Grammar lines 26–28, 42–46, 517–541; original v2 line 538 lacks /l/ | AUTHOR_GRAMMAR, explicit amendment |
| Default state packet uses predicate-initial clause, role-clitic arguments, echo/evidential layer | Grammar III.1–2 lines 152–180; E01–E03 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE |
| Clitics `=ka` AGT, `=en` PAT, `=ru` SRC, `=va` GOAL, `=shi` INST, `=uth` CONS attach to a host | Grammar II.4 lines 97–107; dictionary lines 19–24; E01/E02/E20/E21 | AUTHOR_LEXICON + several AUTHOR_UTTERANCEs |
| Topic `=tra` and focus `=sha` are discourse operators | Grammar III.3 lines 181–193; dictionary lines 25–26; E04/E05/E24 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE |
| Inversion `vael-` differs from clausal `vu` negation; `ta’qesh` is warning/prohibition | Grammar III.7 lines 226–239; E10/E11/E17/E19/E30 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE |
| Interrogative `hë` after echo layer; WH material in situ | Grammar III.6 lines 209–225; E08/E09/E22 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE |
| Structural `qir` LOOP and `ruun` RET precede the proposition in attested corpus, while `ech` WIT and `reen` VRF close it | Grammar IV.1 lines 261–280; E15/E16/E22 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE; clarify syntax hierarchy before new generation |
| `=uth` on predicate and participant is semantically distinct: governed act vs participant assent | Grammar IV.3 lines 292–301; E18/E21 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE; absence can imply coercion but not proof of coercion |
| Evidence commitment, consent, and collapse taboos constrain allowable utterances | Grammar IV.2–5 lines 281–316; E17/E18/E25/E27 | AUTHOR_PRAGMATIC_RULE; E26 intentionally withheld |
| Four registers CF/FC/RT/AC differ; contact loans `‹…›` are not native words | Grammar lines 146–150, 317–336; dictionary format lines 10–16; E28/E29 | AUTHOR_GRAMMAR + AUTHOR_UTTERANCE |

### Narrow compositional anchors

- E01 `Nûm ta=en ech.` ⇒ predicate/coherence + 2.PAT + witnessed.
- E02 `Nûm na=ka ta=en ech.` and E03 `Nûm ta=en na=ka ech.` preserve role assignments but alter information structure. The free translations differ pragmatically, not by swapping agent and patient.
- E18 `Vahl=uth ta=en=uth ech.` simultaneously marks consent-governed act and participant grant. Flattening both to generic “help” loses authored ethics.
- E20 `Kesh na=ka veyl=va ech.` and E21 `Kesh=uth na=ka veyl=va ech.` isolate one additional consent marker.
- E15 `Qir nûm ta=en ech.` compared with E01 isolates a loop operator; E22 adds `hë?`.
- E13 `Veyl sekh së nûm reen.` attests relativizer spelling `së` (not `sën`), with corroborating dictionary evidence below.

These support **testable local transformations** only. They do not license unrestricted English→Nûm’ta’reen novel sentences.

## Material same-authority inconsistencies (do not silently repair)

| ID / severity | Current contradictory evidence | Bounded adjudication |
| --- | --- | --- |
| L1 / high: segment inventory | Grammar inventory, lines 523–550, lists /p t k q ʔ s ʃ x h m n ŋ ɾ~r l w j/ and vowels /i a u e o/ with length. Yet dictionary lists /v/ (e.g., `veyl` line 51), /θ/ (`=uth` line 24), affricate /t͡ʃ/ (`ech` line 27), many broad vowel qualities /ɛ ʊ ɔ y/. Only [ɑ] is explicitly noted as /a/ allophone (grammar line 30). | Author must choose: expand contrastive inventory; document phonetic allophones/phonemic normalization; or amend inconsistent IPA transcriptions. No automatic substitution from spelling. |
| L2 / high: phonotactics vs basic forms | Grammar I.4, lines 38–41, only permits final /n ŋ k t ʃ x/, but `nûm /nuːm/` (dict line 49), `veyl /vejl/` (51), `rhel /rɛl/` (53), `qir /qir/` (29) violate listed codas. Conclave onset clusters are only /ʃr xr kw sw/ (line 39), yet `threnn /tɾɛn/` (dict 52) has /tɾ/. | Either inventory has omitted native phonotactic licenses, IPA mixes a field allophone with phonotactics, or lexemes are exceptions; source does not decide. |
| L3 / high: REL vs WH.MANNER | Grammar III.6 line 216 calls `sën` WH.MANNER; grammar III.8 line 244 calls **same** `sën` REL, while the actual E13 sentence and IGT use `së` (lines 250–253 and 434–437). Amended dictionary lines 34 and 59 distinguish `së` relativizer vs `sën` manner, both with transcribed /sɛn/. | Strongly suggests grammar III.8 orthographic slip, **not yet an approved correction**. Even if distinct graphemes, identical IPA requires context or an unrecorded prosodic difference. |
| L4 / high: `rhel` | Grammar II.3 line 94, dictionary line 53, and corpus E23 (grammar lines 475–478) use `rhel` as restore balance/coherence; grammar III.8 line 243 labels it CONC “even if”. | Restore-sense has direct corpus support; concessive has no identified positive corpus instance. Treat concessive as unresolved homonym/polyfunction/typographical error, never as freely productive connector. |
| L5 / medium: restricted /q/ vs ordinary `qir` | Grammar line 27 restricts /q/ to ritual/taboo-adjacent usage; dictionary line 29 licenses `qir /qir/` in CF/FC/RT and E15/E22 use it unmarked. `qesh` is indeed RT-only (dictionary 106; E29). | Could make restriction lexical (`qesh`) rather than segment-wide; first determine whether `qir` is a sanctioned exception or different realization outside ritual. |
| L6 / medium: one root, divergent IPA | Dictionary `keth /kɛt/` (line 55), but authored E24 IPA has /kɛθ…/ (grammar line 480). Elsewhere `uth` consistently /ʔʊθ/. | Do not normalize silently; request explicit E24 recording, dialect/register allophony rule, or erratum. |
| L7 / medium: operational syntax of echo operators | II.5 line 109 says echo-status markers are generally clause-final; IV.1 lines 269–280 and E15/E16 place LOOP/RET before predicate and WIT/VRF after. | Define two strata—preposed structural echo-status and postposed evidential—as a **candidate analysis**, then validate from other authored sentences. |
| L8 / low: source-extraction layout | Grammar phoneme inventory appears after corpus lines 517–550, instead of I.2. Original DOCX extraction is not layout-exact (sources/SOURCES.md). | Field report must cite both logical section and physical extract line; do not treat tail placement as intended grammar order. |

**Reproducible deterministic count** (dictionary `UPDATED_lphoneme`, 500 entry IPA strings): 161 end in a letter representing /m/, /l/, /r/, /ɾ/, /θ/ or /v/, all excluded from the I.4 coda list. This is a broad **flagged terminal-segment count**, not a validated syllabification or number of distinct illicit native roots: it includes derivatives, field registers and clitics. Of the 161 strings, 133 have a register tag containing CF. That strongly rejects the proposition that every mismatch is contact creole. The count should become a data integrity report with manual adjudication, not a destructive auto-fixer.

## Author-decision cards with falsifiers and downstream impact

1. **Phonemic inventory v2.1.** Candidate A: add /v θ t͡ʃ/ and explicit vowel contrasts. Candidate B: preserve inventory and give context-conditioned allophone/cluster rules that map the dictionary consistently. **Falsifier:** any attested minimal pair showing purported allophones contrast lexically, or phoneme assignment that cannot generate `ech`, `uth`, `veyl`. Downstream: IPA generator, speech synthesis, phonotactics validator, acoustic encoding.
2. **Coda and onset repair.** Candidate A: extend codas to include at least /m l r/ subject to native/root position restrictions and add /tɾ/ cluster; Candidate B: introduce syllabic/moraic analyses so apparent codas are reinterpreted. **Falsifier:** canonical acoustic realizations that violate the proposed syllabification, or a lexicon-entry rejection outside narrowly scoped exceptions. Downstream: renderer/recognizer and new-word formation.
3. **Relativizer spelling/phonetics.** Candidate: reserve `së` for REL and `sën` for WH.MANNER, consistent with E13 and dictionary. **Falsifier:** an independent author-endorsed REL utterance using `sën`, or field audio showing a distinct /së/ vs /sën/ consonant/vowel feature not in current IPA. Downstream: parse ambiguity, grammar lessons, semantics-to-surface transform.
4. **`rhel` split.** Candidate: preserve `rhel` restorative predicate, quarantine unattested concessive use pending new independent source evidence. **Falsifier:** author-approved `rhel` with clausal CONC semantics in connected discourse. Downstream: safe subordination and compositional translation.
5. **Ritual /q/ scope.** Candidate: revise register rule to lexical restrictions with ordinary `qir` exception. **Falsifier:** Conclave formal/field clipped utterances in which a different phoneme realizes `qir`, with q-form confined to ritual. Downstream: register-conditioned TTS and forbidden-register validator.
6. **Consent scope and reference ethics.** Candidate: explicitly formalize `predicate=uth` versus `participant=uth`, and do not interpret absence as actual non-consent without context. **Falsifier:** author corpus where participant `=uth` means request/proposal only, or `predicate=uth` asserts participant assent. Downstream: high-stakes translation warning behavior.
7. **Echo-status stratal grammar.** Candidate: preposed LOOP/RET/CLP layer; core state packet; postposed WIT/VRF; interrogative final `hë`. **Falsifier:** same-register authored counterexamples with different scope or ordering. Downstream: semantic AST and reversible generator, avoiding English-tense contamination.
8. **Resonance/prosody semantics.** Candidate: explicit orthogonal axes for coherence, provenance/evidentiality, scope, consent, recurrence, plus formant/phase/duration rendering as a reversible *proposal* only. **Falsifier:** same acoustic code interpreted as conflicting semantic packets without repair metadata, inability to distinguish E01/E15/E18, or loss of E26 privacy. Downstream: mathematically defined physical channel; absolutely no claim of native alien signal realization from text-only references.

## Suggested next **language** experiment, independent of translator infrastructure

Create a small author-reviewed suite of 10–20 **minimal semantic packet pairs**. Prefer pairs already licensed by corpus (E01↔E15 loop, E01↔E08 question, E20↔E21 consent, E02↔E03 argument focus, E07↔E18 consent). For each, define roles, predicate, structural echo, evidential commitment, consent locus and register in an explicit schema. Then test:

1. `parse(surface) → semantic packet` produces unique features only where source makes them determinate; otherwise an ambiguity set or UNKNOWN.
2. `render(packet) → surface` reconstructs **attested** utterances exactly; any novel sentence must be labeled GENERATED_PROPOSAL, not an attested translation.
3. A proposed acoustic feature map `packet → resonance parameters → packet'` round-trips those distinctions with a clear perturbation tolerance and held-out negative controls.
4. The decoder without supervised packet labels or codebook sees **no assumed English meaning**; report null/control scores. E26 receives `WITHHELD` status and no acoustic note/event rendering.
5. Freeze source and tests before adding more vocabulary. Each new form requires an explicit author decision, its lexical relation to existing roots, phonotactic validity and register/taboo safety, rather than bulk generation.

## Non-claims

- Not a corrected or newly canonical grammar.
- Not an acoustic reconstruction of Ech’ta’reen physiology or resonant signal generation.
- Not independent xenolinguistic fieldwork, model-grounded semantics or empirical evidence of universal translation.
- Not permission to disclose E26 protected true-name chord.
