# Nûm’ta’reen creator decision packet — productive mini-grammar v1

**Status:** `NONCANONICAL_ELICITATION_INSTRUMENT`, not a new Wreckforge source. **Author decision required:** Patrick A. Sims. This instrument freezes existing evidence and tests *where* a new creator ruling is needed. None of its metalanguage templates are attested Nûm’ta’reen utterances. Do not add generated words/sentences to the 500-entry dictionary or 30-example corpus without a versioned, explicit decision.

**Source set:** `num-ta-reen` amended `sources/reference_grammar_v2_updated_lphoneme.txt`, amended `sources/dictionary_v2_updated_lphoneme.txt`, normalized `data/corpus.json` E01–E30, and merged evidence audit PR #13 (`docs/LANGUAGE_EVIDENCE_AND_CONTRADICTIONS_20261026.md`). The amended source pair has equal priority; their conflicts do not resolve themselves by code preference. Source plain-text extraction is not DOCX-layout-exact; the phoneme table was flattened to grammar extract lines 517–550. The original amended DOCX should be reviewed before adopting phonetic corrections.

## First three author decisions (short session)

1. **Inventory/phonotactics — P1 + P3:** Do `/v θ t͡ʃ/` and final `/m l r/` belong in the native inventory/allowed codas, have systematic allophonic/re-syllabification rules, represent faulty dictionary transcriptions, **or follow a mixed register-conditioned analysis**? Inspect the original DOCX table before applying a correction. **Evidence:** grammar I.2/I.4 versus dictionary lines 24/27/29/49/51/53.
2. **Lexeme/grammar conflicts — S1 + S2:** Should `së=REL`, `sën=WH.MANNER`, and `rhel=RESTORE.BALANCE` be exclusive rules, with grammar III.8 corrected **and dictionary `së`'s manner-linker sense narrowed**? Or are REL/MANNER or restorative/concessive senses intentionally polyfunctional? Dictionary line 34 itself permits `së` as a manner linker; this is **not** a one-source typo repair. **Evidence:** corpus E13/E23 + dictionary lines 34/53/59 versus grammar III.8. An alternative needs a newly authored contrastive example, not an inferred translation.
3. **New productive consent semantics — S4:** How does a patient revoke a *previously granted* `=uth` permission while stabilization continues—(A) dedicated REVOKE operator, (B) existing `suv` under an approved scope, (C) nonlexical state transition, or (D) another rule? Force different outcomes for prospective refusal, active revocation and silence/unknown. **Evidence:** IV.3; E07/E18; dictionary `suv` line 242. No candidate native utterance yet exists.

These three are enough to begin one controlled grammar addendum. The remaining eight cards are optional follow-up instruments, not an eleven-question burden for one conversation.

## How Patrick can adjudicate each card

Select **one substantive analysis or an explicitly mixed/other answer**, and separately answer the *discriminating case*. The A/B/C letters below are stable **engineering references only**, not a poll order or recommendation. The facilitator must independently randomize and conceal the A/B/C presentation order **per card** with a preregistered seed; include **D: mixed register-conditioned analysis** as a distinct selectable response on every elicitation form, plus a free-text other/unsure field. Existing card-specific D hypotheses can be supplied as prompts under D, never as a substitute for allowing mixed-register answers. Do **not** show “A (candidate)” or this instrument's supposed preference during blinded choice. Record displayed-order mapping, seed commitment, and author response before unblinding. Every card names a provisional research hypothesis, **not** a request to rubber-stamp it. `APPROVE` must identify (i) whether the correction supersedes a sentence in the amended grammar/dictionary, (ii) whether it applies to CF/FC/RT/AC registers, (iii) whether the suggested contrast is grammatical, and (iv) what different meaning, if any, it encodes. An “unsure” or mixed answer preserves the conflict as `UNRESOLVED` until the mixed rule is independently specified and tested; it does not justify a productivity claim.

### P1 — Consonant inventory: phonemes or broad phonetic symbols?

**Known:** Extracted amended inventory omits `/v/`, `/θ/` and `/t͡ʃ/`, but the amended dictionary uses `veyl /vejl/` (line 51), `=uth /ʔʊθ/` (24), and `ech /ɛt͡ʃ/` (27); grammar I.2 lines 24–30, 517–541. `/l/` is explicitly phonemic under the amendment.

- **A (candidate):** Add `/v θ t͡ʃ/` as distinct phonemes and repair the inventory table.
- **B:** These are allophones/phonetic sequences of listed phonemes; prescribe *conditioned* mapping rules for each.
- **C:** Dictionary IPA is a field approximation/transcription inconsistency; amend selected IPA while keeping inventory.
- **D:** A register-specific mixed analysis; state which segment contrasts where.

**Discriminator:** Does a *same-register, same-vowel, same-stress* substitution `[v]↔[w]`, `[θ]↔[t]`, or `[t͡ʃ]↔[ʃ]` change identity/meaning, or merely accent? Ask for two creator-approved nonce frames per contrast, across contrast-permitting positions; **do not** pretend the current endonym-vs-common-name comparison is a controlled minimal pair. **Falsifier:** under A, failure to find contrast across controlled, contrast-permitting environments **plus** a predictive complementary/free-variation account would weigh against distinct phonemes; free variation or neutralization **in one context alone does not disprove phonemic contrast elsewhere**. Under B, a creator-confirmed meaning-distinguishing same-context pair refutes the claimed universal allophony. **Output gate:** inventory supplement + accepted/rejected frame records; no automatic grapheme-to-IPA generator before this.

### P2 — Vowel quality, quantity and genuine minimal pairs

**Known:** Tail inventory lists `/i a u e o/` with length (lines 542–550), while dictionary/IGT use `[ɛ ʊ ɔ y]` among other transcriptions. Grammar I.6 lines 56–72 presents `nûm /nuːm/` vs `num /num/` as a length illustration, but the source also describes `num` as a **clipped form**; this is not an independently controlled, same-register lexical minimal pair. Register, truncation, and duration are confounded. I.5 correlates duration with scope, without numbers.

- **A (candidate):** Five underlying qualities; document context-specific allophones plus independently contrastive length.
- **B:** Broader contrastive vowel inventory; repair tabulation and minimal pairs.
- **C:** Formal/field-register inventory split; register-tag every exceptional quality.
- **D:** Other explicitly testable inventory.

**Discriminator:** In the *same morphological context and register*, does short/long vowel change root meaning, scope only, or both? Test length with new same-register matched frames; use `nûm/num` only as a confounded source illustration, not as validation. For `[ɛ]↔[e]` and `[ʊ]↔[u]`, require controlled nonce forms with predicted acceptability and creator phonetic rendering. **Falsifier:** claimed categorical allophones that distinguish two same-context lexical meanings; context-specific neutralization alone cannot settle inventory-wide contrast. **Output gate:** contrast table with short/long and word/scope levels separately; never infer hertz or milliseconds.

### P3 — Codas, onset clusters and syllable analysis

**Known:** Grammar I.4 lines 36–41 permits codas `/n ŋ k t ʃ x/` and CF onset clusters `/ʃr xr kw sw/`, while canonical `nûm /nuːm/`, `veyl /vejl/`, `rhel /rɛl/`, `qir /qir/`, `threnn /tɾɛn/` disagree (dictionary lines 29,49,51–53). The PR #13 audit flags **161** dictionary IPA endings under a terminal-symbol heuristic, including **133** entries tagged CF; those counts are flags, *not* 161 verified illicit syllabifications.

- **A (candidate):** Explicitly license coda `/m l r/` and onset `/tɾ/`, then determine remaining variants case by case.
- **B:** Analyze apparent final consonants as extrasyllabic/moraic or resyllabified, with phonetic evidence and a predictive rule.
- **C:** Restrict these as lexical/register exceptions with a finite exception register.
- **D:** A new syllabification system with a stated decision procedure.

**Discriminator:** Have Patrick syllabify and pronounce each named **attested** form in isolation and in a vowel-following phrase; annotate whether coda persists, epenthesis appears, or register changes it. **Falsifier:** an unlisted ordinary CF root with the same newly prohibited structure, or an A-licensed novel form rejected without further condition. **Output gate:** updated phonotactic validator *only after* approved constraints.

### P4 — `/q/` ritual restriction versus ordinary `qir`

**Known:** Grammar I.2 line 27 calls `/q/` ritual/taboo-adjacent; dictionary `qir` line 29 is CF/FC/RT and occurs in ordinary E15/E22; `qesh` line 106 is RT-only. `kesh` vs `qesh` is an attested lexical near-pair with register/meaning confounded.

- **A (candidate):** `/q/` occurs freely in approved structural operators such as `qir`; restriction applies to *certain lexemes* (e.g. `qesh`).
- **B:** Field/conclave `qir` realizes another consonant and the IPA spelling is a register-wide abstraction.
- **C:** `qir` itself licenses a special nonritual exception; retain general restriction.
- **D:** Different register system; specify contextual rule.

**Discriminator:** How does an ordinary CF speaker pronounce E15 `Qir nûm ta=en ech.`? Is using `qir` in a greeting taboo? A raw `[q]` recording/judgment, not the existing `kesh/qesh` semantic switch, should decide. **Falsifier:** many CF `/q/` roots with no lexical exceptions under C. **Output gate:** segment/register rule and negative word-formation tests.

### S1 — `së` relative clause versus `sën` manner question

**Known:** Grammar III.6 line 216 and dictionary line 59 label `sën` WH.MANNER; grammar III.8 line 244 calls `sën` REL, while E13 uses written `së` as REL and dictionary line 34 lists `së` as **REL and manner linker**. Thus dictionary `së` already overlaps the manner function attributed to `sën`, at least in an FC-related scope; it is not exclusively relative. Both dictionary IPAs are `/sɛn/`. The equal-priority amended sources cannot settle that conflict automatically.

- **A (candidate):** Correct III.8 to REL `së`, reserve `sën` for WH.MANNER **and explicitly supersede/narrow dictionary `së`'s manner-linker meaning**; homophony requires context or newly specified timing. This is a proposed **two-source semantic change**, not a typo-only correction.
- **B:** Both are polyfunctional and interchangeable as REL in specified contexts; publish examples of both.
- **C:** Distinct phonemic pronunciations are missing in dictionary IPA; fix the contrast.
- **D:** Other morphology/prosody rule.

**Discriminator:** Present three *English semantic scenarios*: “the boundary **that** aligns,” “**how** is the boundary aligned?,” and a **noninterrogative manner-linking** “the manner in which the boundary aligns.” Ask Patrick for independently authored native utterances in the **same** register, IPA, scope and meaning; separately test FC, where the manner linker is documented. **Falsifier:** a creator-confirmed manner-linker `së` or canonical REL `sën` under strict A, or claimed distinct phonemes with no contrast in any controlled environment under C; same-context homophony with a contextual disambiguator does not alone falsify a semantic distinction. **Output gate:** `REL`, `WH.MANNER` and `MANNER.LINK` parser entries become productive only for approved contrasts, with explicit dictionary/grammar supersession IDs.

### S2 — `rhel` restorative predicate versus concessive linker

**Known:** Grammar II.3 line 94 and E23 use `rhel` as restore balance/coherence; amended dictionary line 53 agrees. Grammar III.8 line 243 alone calls it CONC “even if.”

- **A (candidate):** Keep restorative `rhel`; III.8 is a drafting error, with concessive marker presently **unknown**.
- **B:** Licensed polysemy: `rhel` means restore and CONC in distinct syntactic frames; specify separation.
- **C:** Two homophonous etyma/orthographic forms; provide independent IPA or boundary contrast.
- **D:** Other approved analysis.

**Discriminator:** Can a native utterance express “**Even if** the threshold returns, do not cross” using `rhel` without describing restoration? Ask Patrick to provide a controlled source utterance or explicitly reject it. **Falsifier:** successful CONC usage under A or restorative reading impossible in E23 under a replacement-only rule. **Output gate:** no connective generation until the decision and an attested concessive example exist.

### S3 — Echo/evidential operator attachment and scope

**Known:** Grammar II.5 line 109 calls echo-status generally clause-final; IV.1 lines 261–280 and E15/E16/E22 put `qir` LOOP or `ruun` RET before the predicate, `ech` WIT or `reen` VRF after it, and `hë` Q after evidence (E08/E22). IV.1 says structural echo then evidential is default **when stacked**, but does not establish arbitrary nesting or multiple operators of each class.

- **A (candidate):** Two grammatical strata: preposed structural LOOP/RET/CLP and final evidential WIT/VRF, then optional question; one operator of each until tested.
- **B:** Surface position varies freely by register, with a semantic/prosodic scope rule independent of order.
- **C:** The alleged stack is a single holistic particle contour rather than discrete operators.
- **D:** Other typed operator grammar.

**Discriminator:** Compare E01↔E15 (one LOOP) and E01↔E08 (one Q), then ask Patrick whether **unattested** `RET(LOOP(P))` and `LOOP(RET(P))` denote different states, are synonymous, or are forbidden. Supply *semantic trees* first; Patrick supplies any acceptable native sentence. **Falsifier:** legal different-scope stacking under strict A without a provision, or lexical operators not independently replaceable under B. **Output gate:** typed AST with reject/ambiguity for unapproved orderings; no arbitrary combinations.

### S4 — Consent grant, withdrawal and evidence

**Known:** Grammar IV.3 lines 292–301 and E18 distinguish predicate-`=uth` consent-governed act and participant-`=uth` asserted grant; E07 lacks both and is noted to *risk* coercion, not prove it. `suv` means refusal/closure (dictionary line 242), but no corpus example demonstrates revoking a previous grant during an ongoing act.

- **A (candidate):** A new explicit `REVOKE` speech act/operator is needed; existing `=uth` remains grant/scope annotation.
- **B:** Compositional `suv` + existing scope markers expresses revocation; Patrick must supply an approved full utterance.
- **C:** Withdrawal is enacted as a two-sided echo state transition, not an ordinary field-language utterance.
- **D:** Other consent model.

**Discriminator:** Three *nonverbal semantic* cases: (i) patient consented and now revokes during intervention; (ii) patient refuses a merely proposed intervention; (iii) patient is silent. Require different **semantic, operational and ethical consequences** (not assumed human legal codes), participant/act scope, time of effect, and whether witnessing/review (`ech`/`reen`) reports revocation without constituting consent. **Falsifier:** a construction treating silence as assent or conflating withdrawal with never-granted refusal. **Output gate:** no translation of “I revoke consent” until adopted; safety warnings preserve `UNKNOWN`.

### S5 — Evidential uncertainty and trustworthy acknowledgment

**Known:** Grammar IV.2 lines 281–291 says omission of evidential in CF may mean uncertainty, unwillingness, or concealment; clipped alerts permit omission (E17). `ech` is local witness, `reen` cross-echo verified (IV.4/E01/E06); `nuk` is a field confirmation ping, *not* full reen (dictionary line 266). These are distinct epistemic commitments.

- **A (candidate):** Add a dedicated explicit “unverified/uncertain” status to disambiguate the CF omission.
- **B:** Distinguish ambiguity using existing register/context particles or structured pause/resonance cues.
- **C:** The ambiguity is deliberate cultural pragmatics; a responsible translation must retain a set of interpretations, not reduce to one English statement.
- **D:** Other evidence-custody protocol.

**Discriminator:** Ask for three approved utterances: “I received your report,” “I witnessed the event,” and “I independently verified the event.” Include a fourth “I do not know whether it happened.” Do not treat `nuk` as `reen`. **Falsifier:** a rule mapping simple acknowledgment to independent verification without additional evidence. **Output gate:** translate truth-commitment as separate feature, abstain on ambiguous omissions.

### S6 — Everyday contact, repair, help and leave-taking

**Known:** Dictionary offers `mek` request (line 201), `pesh` offer (196), `har` share (296), `suv` refusal (242), `nuk` brief acknowledgment (266), `renk` coherence need (345), but the 30 utterances establish almost no ordinary greeting, clarification, help-request, or farewell construction. PR #13 classifies these semantic **slots**, not canonical sentences.

- **A (candidate):** Productive **call-and-response state packets** with request/accept/refuse/repair/farewell functions constructed from approved existing roots.
- **B:** Distinct conventional social formulae; coin only necessary terms through a separate source amendment.
- **C:** Contact etiquette is primarily non-lexical (timing/resonance/consent cues), with human speech a deliberately lossy paraphrase.
- **D:** Register-conditioned hybrid; state which actions occur where.

**Discriminator:** For each of four situations—first safe contact, “please help with a need,” “I did not understand; restate without changing truth status,” and “end exchange without rejecting the other”—Patrick chooses which *social obligations* the packet creates, then writes one **new** approved utterance and one rejected near-miss. **Falsifier:** a proposed “hello” that unwittingly grants consent or a help-request that asserts rescue already happened. **Output gate:** the first author-approved everyday mini-dialogue, with turn taking and refusal scope, not a 100-word synthetic vocabulary dump.

### M1 — Mathematical encoding: syntax, semantics or physical resonance?

**Known:** Grammar I.1 lines 18–23 says Ech’ta’reen physical communication uses resonance modulation and timing discontinuity; I.5 lines 47–55 suggests duration and scope interactions. No waveforms, carriers, hertz thresholds, or acoustic-to-meaning algorithm are supplied. The currently reviewed noncanonical 3,072-packet codec assigns arbitrary frequency labels and explicitly has no native semantic grounding.

- **A (candidate):** Native resonance is a *structured multichannel code*: orthogonal logical features (roles, evidence, echo state, consent scope) map to independently modulated spectral/phase/time features.
- **B:** A holistic, context-dependent resonance state; segmental/typed human transcription loses interactions and must not be treated as physically reversible.
- **C:** A hybrid: discrete structural anchors plus continuous state qualities and nonlinear prosody, requiring a probabilistic decoder.
- **D:** Other dimensional/channel model with a falsifiable mapping.

**Discriminator:** Hold root/patient constant and compare E01 vs E08 (question), E01 vs E15 (loop), E07 vs E18 (two consent changes), E01 vs E10 (state inversion). Ask which *physical variable family* should change for each (relative timing, phase, harmonic relation, amplitude envelope, synchronized silence, or undefined); **no numeric parameter is canonized**. Demand predictions that could distinguish independent features and controls with permuted labels. **Falsifier:** different semantic packets forced to the same observable state under the proposed nuisance freedoms, or a permutation-null model scoring equally on unpaired creator judgments. **Output gate:** versioned feature-to-channel hypothesis plus synthetic tests, with “unobserved native signal” warning until empirical/creator evidence.

## Recommended author session: six decisions before implementation

Take **P1, P3, S1, S2, S3, S4 first**. Those settle the most damaging conflicts, define safe constituent/operator scope, and permit more than table lookup. Then P2/P4/S5/S6/M1 expand phonetics, communication and physical modeling. Do not ask Patrick to approve arbitrary Hertz values or a whole invented lexicon.

Every accepted card becomes a *separate versioned source addendum* with explicit supersession target, canonical source ID, exact orthography + IPA where relevant, register, gloss, negative contrast, and approval date. Two independent human/model checks should ensure: (1) original source lines remain quoted accurately, and (2) candidate tests were preregistered before the answers. This records author intent, not objective field measurements.

### Minimal held-out productivity gate, after the first decisions

Freeze 20 creator-judgment cases **before** adding examples to a translator: four each of (a) role permutation, (b) echo/evidence scope, (c) consent grant/revoke/refuse, (d) relativization/question/**manner linker**, (e) basic contact/repair. Within each four: one known-attested control (explicitly labeled **non-held-out calibration**), one creator-approved *unseen* composition, one deliberately illegal near-miss, and one ambiguous case requiring abstention. Keep the actual held-out and calibration subsets separate in reports; do not score the already-public attested items as generalization.

**Custody/preregistration protocol:** Before any translation-model inference on these items, an evaluation custodian distinct from the implementation/tuning team freezes (1) exact UTF-8 item bytes with stable item IDs; (2) scenario, register and scoring rubric; (3) a cryptographically sampled randomization seed commitment (`SHA-256(seed)`) for both shuffled creator-choice option order and held-out presentation order; (4) a manifest with `SHA-256` per item and whole-manifest digest; and (5) creation time plus immutable commit/object ID or other dated, read-back-verifiable sealed location. Custodian keeps the seed, item content, gold judgments and label mapping private until the evaluation lock; only hashes/IDs, counts and rubric may be released beforehand. Following creator judgments, publish/release the seed and mappings to reproduce randomization, subject to consent for unpublished creative content. An inability to preserve independent custody must be explicitly reported as `UNBLINDED/EXPLORATORY`.

**Leakage and blinding:** An author-facing facilitator must conceal candidate labels, defaults, model predictions and expected outcomes; elicit grammaticality and semantic contrasts before showing engine output. Implementers may inspect the public 30-row corpus and preregistered rubric but **must not** see or infer hidden item text or Patrick's answers, train/fine-tune on held-out cases, iterate grammar/rules against held-out scores, use the custodian to relay hints, or reclassify failed items after scoring. Freeze the translator commit and prompt/configuration hash *before* one blind pass, then unseal predictions and judgments together; corrections require a **new** held-out batch and independent custody. Reuse of items makes them development data, never again held-out evidence.

Score exact construction legality, feature retention, abstention and false acceptance separately, by register as well as overall. The corpus remains source evidence; it is not a hidden test set after models have read it. Only approval of *novel* held-out cases can justify “productive mini-grammar,” and even then only within the tested sublanguage.

**Explicit non-claims:** No independent Ech’ta’reen speaker data; no canonical pronunciations newly created; no observed native waveforms; no automatic evidence that language is compositional merely because Python ASTs and synthetic packet codecs round-trip. E26 original true-name notation is not an elicitation target and must never be acoustically rendered.
