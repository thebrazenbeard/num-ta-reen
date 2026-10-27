# Num’ta’reen: post-evidential contact tail (noncanonical elicitation)

**Status:** source-attested structural exception; semantic interpretation undecided. This document is a creator-facing research prompt, **not a grammar amendment**.

The census now verifies the exact authored corpus Git blob
`53d9f27d03579a1a3fc700c3394b56f834da784e` before reporting evidence.
The cited main commit is contextual metadata, not an authentication signature.

## What the authored material actually says

- Grammar II.5 (source line 109): echo-status operators are clause-final by default, but Conclave formal may attach them to the predicate.
- Grammar III.1 (lines 153–161): predicate, role-marked arguments, then relatively stable final echo-status is the default *state-packet* pattern.
- Grammar IV.6 (lines 335–336): marked Common loans are Anchor contact-layer, not baseline grammar.
- Corpus **E28** (lines 502–506): `Nûm na=ka ta=en ech ‹airlock›=va.` has `ech` EVID.WIT followed by a **role-clitic GOAL-marked loan**. The author’s free rendering says the alignment is witnessed **toward** the airlock; no explanatory syntax note specifies the tail’s scope.

The new source-census counts **27 analyzed excerpts / 30 punctuated clauses**, excluding E13/E23 unresolved conflict cases and protected E26. **25 clauses contain overt WIT/VRF**, with three ordinary interrogative tails after the evidential (E08/E09/E22) and only **one role-marked argument afterward: E28**. The five clauses without WIT/VRF include prospective consent, alarm or chaining contexts; the census makes no claim of a rule about their status.

E28 is neither a reason to silently reorder evidence nor proof that ordinary Ech’ta’reen grammar licenses arbitrary trailing arguments. It is specifically a **contact-lexeme** occurrence.

## Three mutually competing hypotheses for Patrick

1. **Contact-tail adjunct:** `ech` certifies the preceding core proposition; a GOAL-marked contact adjunct can be adjoined afterward with the same event referent.
2. **Afterthought/repair:** `ech` closes the witnessed proposition; the subsequent GOAL is a discourse repair or elaboration with an independent inference, not part of the same scope.
3. **Transcription/ordering anomaly:** The intended ordinary parse has the GOAL before the final evidential, and E28 is an imperfect field record.

All three fit the **one** attested example; none can be selected by a model's confidence.

## Source-falsifiable elicitation pair

| Stimulus | Attestation | Question |
|---|---|---|
| `Nûm na=ka ta=en ech ‹airlock›=va.` | **E28 authored** | Does witness marking cover the goal phrase, the alignment alone, or a preceding finished clause? |
| `Nûm na=ka ta=en ‹airlock›=va ech.` | **Novel test stimulus, NOT CANON** | Same truth conditions? Different scope/focus/register? Grammatically acceptable? |

Ask for native or creator-authored *contrastive* translations and register labels, not an unconstrained “translate these.” Record refusal/unknown as evidence rather than filling in grammar.

## Software consequence

For any source-observation AST:

- Preserve original token order, including every role-clitic host **after** the WIT/VRF marker.
- Expose an explicit `post_evidential_attachment_scope: unknown` until the author resolves it.
- Do not silently normalize E28 to a clause-final evidential or drop the GOAL as stray text.
- Treat an unattested reordered construction as **unvalidated**, even if a finite parser accepts it.

The source-bound `positional_census.py` and six tests check this bounded source property and reject altered source bytes. They do **not** decode alien resonance, establish productive syntax, or predict unseen sentences.
