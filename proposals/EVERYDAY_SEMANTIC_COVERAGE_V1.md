# Everyday communication coverage — evidence-constrained language expansion V1

**Status: NONCANONICAL RESEARCH PROPOSAL.** No entries below are new Nûm’ta’reen words, sanctioned constructions, or changes to the 500-entry source dictionary or 30-utterance corpus.

## Frozen source binding and evidence classes

- Inspected public `thebrazenbeard/num-ta-reen` at `ed9a94d53d17db6415de172858773714644e01ba`.
- Canonical-source priority is the **amended** `sources/reference_grammar_v2_updated_lphoneme.txt` and `sources/dictionary_v2_updated_lphoneme.txt`, as specified by `sources/SOURCES.md`; originals are historical comparisons.
- Normalized dictionary blob: `c78dccdf9614d8e8e94c968aac5c07a2e4206bf1` (500 unique entries).
- Normalized corpus blob: `53d9f27d03579a1a3fc700c3394b56f834da784e` (E01–E30).
- **CORPUS** means at least one provided full utterance performs the narrow speech act. **PARTIAL** means a related corpus structure exists but lacks the requested distinction. **LEXICAL** means a dictionary gloss suggests a relevant component without an attested full utterance. **GAP** means neither source demonstrates the requested distinction, even if there are related root forms.
- A lexeme's presence is not proof that arbitrary composition, pragmatics, or conjugation works. A corpus English free translation is not a reversible generative grammar.
- E26 true-name realization is withheld. Its protective paraphrase may be referenced, never filled with a waveform/chord.

## Empirical coverage pattern

The source corpus is unusually rich in alignment, Veil-crossing, boundary warnings, record-latching, evidentiality, and consent: E01–E30 cover witness `ech`, cross-echo verification `reen`, echo `qir`/`ruun`, patient/agent roles, prohibition, scoped consent, negation, topicalization, and at least two question types.

The 500-entry dictionary also contains many abstract and procedure-specific derivatives (`mek` request, `pesh` offer, `har` share, `nuk` confirm, `suv` refusal, `yem` affinity, `renk` coherence hunger). **Those do not by themselves establish conversational sentences** such as “Please help me,” “I accept,” or “Where are we?” The attested 30 sentences offer no direct versions of most ordinary conversational moves.

Selected exact lexical audit trail in `sources/dictionary_v2_updated_lphoneme.txt`: `=ru` line 21, `rhel` line 53, `sën` line 59, `yem` line 190, `pesh` line 196, `mek` line 201, `shen` line 239, `suv` line 242, `wem` line 263, `nuk` line 266, `har` line 296, `renk` line 345, `tah` line 360, `huth` line 362, `neth` line 411, `sëth` line 414. All line numbers are the **source-text** line numbers retained on the normalized entries, not lines of the JSON file.

## Prioritized semantic slots

Citation notation: `E##` = corpus utterance; `lex:` = exact amended dictionary headword (lookup supplies the original source line); `§` = amended reference grammar section. Classifications concern **the requested function**, not the mere existence of related words.

| ID | Priority | Target communicative function | Evidence/class | Missing contrast or decisive test |
| --- | --- | --- | --- | --- |
| C01 | P0 | Open contact / greet without forcing intimacy | **LEXICAL**: `vex`, `nuk`, `=uth` | Greeting versus mere open-channel status; opt-in and no implied consent |
| C02 | P0 | Farewell / end a conversation cleanly | **LEXICAL**: `rexh`, `kak` | Social leave-taking versus physical release or interface termination |
| C03 | P0 | Introduce oneself by role or safe tag | **PARTIAL**: E02/E09; lex: `na=ka`, `nak` | Predicate “I am called X” without tabooed true-name or assumed third-person markers |
| C04 | P0 | Ask permission for a specific action | **PARTIAL**: E14/E18/E21; lex: `mek`, `huth`, `=uth` | Request ≠ consent already granted; distinguish predicate- from participant-scope (§IV.3) |
| C05 | P0 | Grant, withhold, or refuse permission | **LEXICAL**: `shen`, `suv`, `nuk` | Guarded yes, hard refusal, mere receipt acknowledgment, each with scope |
| C06 | P0 | Withdraw previously granted consent | **GAP**; related lex: `rexh`, `kak`, `=uth` | Revocation during an ongoing act and evidence of recipient's receipt; never infer silence = yes (§IV.3) |
| C07 | P0 | Halt danger / prohibit crossing | **CORPUS**: E11/E17/E30; lex: `ta’qesh` | Already attested; test alarm brevity and difference from generic “stop” (§III.7, IV.2) |
| C08 | P0 | Ask another to help with a need | **LEXICAL**: `mek`, `renk`, `hesh` | Need-state ≠ request ≠ rescue authorization; `renk` is not food-hunger |
| C09 | P0 | Report safe/unsafe current status | **LEXICAL**: `nex`, `veyl’nex`, `vael’nex` | Whose safety, at which interface, observed vs verified |
| C10 | P0 | Request clarification / correct a translation | **LEXICAL**: `resh`, `threnn’lek` | Ask for rephrasing without asserting equivalence; `lek` is a discouraged contact calque |
| C11 | P0 | Acknowledge reception without validating truth | **LEXICAL**: `nuk`, `threnn’nuk` | “I heard” must not silently upgrade to `reen` verification (§IV.4) |
| C12 | P0 | Declare uncertainty or inability to verify | **GAP**; related `ech`, `reen` | Evidential omission can mean uncertainty/concealment (§IV.2); need non-deceptive explicit uncertainty |
| C13 | P0 | Separate witness from cross-echo corroboration | **CORPUS**: E01/E06/E12/E19; lex: `ech`, `reen` | Attested; protect evidence claims from unjustified elevation (§IV.1–IV.4) |
| C14 | P0 | Offer/share and ask receiver acceptance | **LEXICAL**: `pesh`, `har`, `pesh=uth` | Offering ≠ transfer accomplished; preserve refusal and recipient scope |
| C15 | P0 | Describe bodily distress / request care | **LEXICAL**: `mav`, `ven`, `renk`, `shuv` | Injury/pain/need not reducible to phase saturation; care without involuntary stabilization |
| C16 | P0 | Express reassurance, calm, or affinity | **LEXICAL**: `wem`, `yem`, `sa’wem` | Feeling reported versus calming another person's field; consent to soothing |
| C17 | P0 | Refer safely to unnamed or dead persons | **PARTIAL**: E26/E27; lex: `hax`, `neth`, `sëth` | Role/tag reference without actual protected name; no E26 chord generation (§IV.5) |
| C18 | P0 | Acknowledge harm and undertake repair | **PARTIAL**: E23; lex: `koxra`, `rhem`, `rux` | Distinguish remorse, observed harm, intention, obligation, completed reparation |
| C19 | P1 | Ask *what* | **LEXICAL**: `kô`, `kô=en` | WH.THING specified in §III.6 but no corpus instance; unknown vs forbidden referent |
| C20 | P1 | Ask *where* | **LEXICAL**: `râ`, `râ=va` | WH.LOC specified in §III.6 but no corpus instance; source vs goal vs current place |
| C21 | P1 | Ask *how* | **LEXICAL/CONFLICT**: `sën` | §III.6 = WH.MANNER, §III.8 claims REL; dictionary `së` REL; freeze decision |
| C22 | P1 | Ask *why* or identify a cause | **GAP**: no established WH.CAUSE | Cause, motive, justification and ethical evaluation `keth` must remain distinct |
| C23 | P1 | Give route / source and destination | **PARTIAL**: E20/E21; lex: `=ru`, `=va` | Goal witnessed; source/waypoint/path/return directions not attested as instructions |
| C24 | P1 | Identify proximity, here/there, left/right | **GAP**; related `ta’ren`, `wum` | Salience/marking is not Euclidean distance or direction; identify native spatial frame |
| C25 | P1 | Say before/after, simultaneous, next | **GAP**; related `qir`, `ruun` | Echo-status explicitly replaces tense (§IV.1), but does not provide ordinary event ordering |
| C26 | P1 | Schedule an intended future coordination act | **GAP**; related `tresh`, `ruun` | Commitment, recurrence expectation, and calendar time are distinct propositions |
| C27 | P1 | Specify quantity, one/many, exact number | **GAP**; related `-ren`, `-een` | Single instance vs coherent set ≠ cardinal numerals, distributed count, or approximation |
| C28 | P1 | Compare magnitude/intensity with a unit | **LEXICAL**: `tah` | `tah` marks intensity; source lacks calibrated numerical scale and comparison operator |
| C29 | P1 | Conditional or hypothetical coordination | **GAP/CONFLICT**: `ke` complement, `rhel` §III.8 concessive vs lex restore-balance | Do not infer a valid if/then connective from contested `rhel` |
| C30 | P1 | Request/offer water, food, shelter, rest | **GAP**; related `renk` explicitly not food, `ven` body-hold | Anchor-contact provisioning needs distinct physical-resource semantics, not false native equivalences |

## Five micro-grammars to develop (proposed semantic constraints, not forms)

1. **Consent transaction**: `REQUEST(action, scope, speaker) → ACCEPT|DECLINE|COUNTEROFFER → ACT → REVOKE?`. Consent marking cannot mean “permission exists” without an identified grantor, recipient, scope, and possibly expiry. Test E18 versus E07 (stabilization with/without explicit consent).
2. **Evidence-custody report**: `OBSERVE(event, witness, echo_anchor)` is not `CORROBORATE(event, witnesses/echoes)`. A simple acknowledgment must not license `reen`. Test E01 vs E06/E19.
3. **Safe identity reference**: `REFERENCE(tag|role|record_id, access_policy)`. Provide public non-true-name handles without inventing chord content; negative tests intentionally block prohibited generation (E26).
4. **Request/repair dialogue**: `REQUEST_CLARIFICATION(target_span, suspected_mismatch)`, `OFFER_ALTERNATIVE(annotation)`, `CONFIRM_RECEIPT`—different from `CONFIRM_TRUTH`. Anchor-contact `lek` cannot be silently treated as a native exact synonym.
5. **Event navigation**: `MOVE(actor, source?, goal?, path?)` plus independent `ORDER(event_A,event_B)`. Goal `=va` in E20 is secure; source `=ru` and temporal ordering need authored, tested utterances.

These are **English metalanguage models** for future elicitation and do **not** define Nûm’ta’reen syntax.

## Source-bound learner contrast deck (existing canon only)

These are practice prompts over **exact corpus IDs**, not newly generated sentences. The test asks which *attested contrast* a learner notices; it does not license substitution beyond these cases.

| Contrast | Attested forms | What the learner should identify | Quality |
| --- | --- | --- | --- |
| Polar question | E01 `Nûm ta=en ech.` / E08 `Nûm ta=en ech hë?` | Clause-final `hë` changes a witnessed report to a polar question | Strong near-minimal |
| State inversion | E01 / E10 `Vael’nûm ta=en ech.` | `vael-` changes aligned to misaligned; not mere Boolean punctuation | Strong near-minimal |
| Loop status | E01 / E15 `Qir nûm ta=en ech.` | `qir` introduces recurrence, not English past/future tense | Strong near-minimal |
| Agency | E01 / E02 `Nûm na=ka ta=en ech.` | Adding `na=ka` explicitly attributes action to first-person agent | Pragmatic contrast |
| Role order/focus | E02 / E03 `Nûm ta=en na=ka ech.` | Same two roles with late agent creates contrastive focus; not role reversal | Pragmatic contrast |
| Consent | E07 `Vahl ta=en ech.` / E18 `Vahl=uth ta=en=uth ech.` | Distinguish no explicit consent from consent-marked predicate **and** patient; do not infer E07 is automatically a violation | Two correlated changes |
| Permission for crossing | E20 `Kesh na=ka veyl=va ech.` / E21 `Kesh=uth na=ka veyl=va ech.` | `=uth` adds permission-governed framing while preserving witnessed crossing/goal | Strong near-minimal |
| Negated record | E06 `Threnn’vahl reen.` / E19 `Threnn’vahl vu ech.` | E19 contains negation **and a different evidential**; this is a deliberately confounded example, never a pure `vu` minimal pair | **Not** a controlled minimal pair |

**Practice protocol:** show the two source orthographies and provenance IDs, ask for the semantic distinction, then reveal the exact corpus free translations and notes. Wrong answers should explain which clitic or evidential was overlooked. Do not generate a new alien response by mechanically combining these fragments.

## Elicitation protocol to create real language data

For each P0 slot, seek *three contrastive minimal scenarios*, not one English sentence with an invented translation: (a) intended true case, (b) nearby but semantically different case, (c) prohibited or ambiguous case. Ask Patrick to approve the exact alien communicative distinction first, then choose either a productive existing composition (record its derivation) or a genuinely new native form. Enter approved data as a new versioned source with provenance, IPA/orthography, register, pragmatic conditions, and at least one rejected near-miss. Do not append directly to the 500-entry canonical dictionary until approved.

Example first elicitation set: permission **requested**, permission **granted**, permission **withdrawn** during stabilization. Existing E07 vs E18 already supplies part of the contrast; a third authored case would test whether `=uth` has a revocation channel or whether the language needs a distinct operator.

### First concrete elicitation card: C06 consent withdrawal

**Communicative target:** the patient of an ongoing stabilization revokes an earlier permission while the operator may still be affecting their state. This is a *new semantic problem*, not an attested alien expression.

| Contrast case | Initial condition | Intended outcome | Required semantic distinctions |
| --- | --- | --- | --- |
| A — revocation | E18-like prior explicit patient consent; intervention in progress | Stop or safely release the intervention; communicate that authorization no longer holds | Previous grant, scope, revoking participant, effective point, witnessed acknowledgment |
| B — refusal | No prior permission; intervention proposed but not begun | Reject initiation, not cancel an existing grant | Proposal versus grant, prospective versus ongoing action |
| C — silence | No recorded explicit grant; patient gives no reply | Permission remains **unproven** | Absence of response cannot substitute for an explicit `=uth` grant |

**Authorial decisions to elicit:** Is revocation a new operator, a scoped reuse of existing `suv`/release semantics, or a state-transition unavailable to field-clipped speech? Must the revocation be witnessed by both parties to take effect? Does it interact with `ech` or `reen` only as evidence of the event, not as permission itself? Do not write a Nûm’ta’reen phrase until these questions are resolved; E18 is a source contrast, not proof of a withdrawal construction.

**Candidate new-source record (template, not completed data):**

```yaml
proposal_id: C06-A
status: pending_authorial_decision
semantic_frame: REVOKE_CONSENT
prior_consent: explicit
affected_action: ongoing_stabilization
revoker_role: patient
scope: unresolved
effective_time: unresolved
evidential: unresolved
alien_orthography: null
ipa: null
register: unresolved
source_crosschecks: [E07, E18, "grammar §IV.3"]
rejected_near_misses: [prospective_refusal, nonresponse]
```

## Hard acceptance criteria for a next language revision

- No proposal is counted as attested until a new author-approved utterance and source record exists.
- At least 10 newly approved conversational intents across P0, each with negative/ambiguity examples, independently parsed into roles and scope.
- Explicit treatment of §III.8 `së`/`sën` and `rhel` conflicts; no silent precedence within a same-authority source.
- Productive generalization measured on **held-out combinations**, never the exact author-approved examples used for design.
- Resonance renderer, when present, must separate segmental transliteration from proposed native signal features and preserve lossiness reports; do not claim frequencies convey meaning without an independently specified mapping and decoding tests.
- Taboo, register, and consent safeguards remain intact.

## What this proposal does *not* establish

It does not establish that Ech’ta’reen literally ask or need the same everyday questions humans do; some slots may intentionally have no direct native counterpart. It does not establish a numerical frequency language, a syntactically valid phrase assembled from listed headwords, or the superiority of a neural system over source-bound lookup. Those are separate tests.
