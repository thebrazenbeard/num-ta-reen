# Consent, permission, silence and refusal: a source-constrained contrast

**Status: NONCANONICAL RESEARCH.** The authored examples establish observations,
not a full productive consent/revocation grammar. Nothing here authorizes
performing an action or inferring permission from silence.

## Verified distinctions in the original authored material

| Corpus ID | Authored material (structural summary) | Observation |
| --- | --- | --- |
| E07 | `Vahl ta=en ech.` | Stabilization witnessed; no overt CONS marking. Source notes coercion risk. |
| E18 | `Vahl=uth ta=en=uth ech.` | Same base predicate, CONS on both predicate and participant. |
| E14 | `Uth’nûm=uth.` | Softened alignment offer, one predicate CONS; prospective imperative-like reading. |
| E21 | `Kesh=uth na=ka veyl=va ech.` | Consent-marked crossing predicate, no participant CONS. |
| E12 | `Threnn’ul’esh ke nûm ta=en reen.` | Lexical `record.GRANT`, **not** morphological CONS. |
| E27 | `Threnn’vahl reen. Uth’se’run.` | Respect-silence condolence, **not** assent or authorization. |
| E30 | `Ta’qesh. Veyl’sekh ech. Kesh vu.` | Prohibition and ordinary negation, **not** an explicit previously granted permission being revoked. |

The corpus has 30 author-supplied records. Typed transport accepts 27 source
records; E13/E23 are unresolved and E26 protected. This audit reports ten
source IDs relevant to consent, record access, silence, prohibition or NEG.
Explicit CONS indices are E14 `[0]`, E18 `[0,1]`, and E21 `[0]`.
The typed transport records E18's predicate attachment at `[0]` and
participant attachment at `[1]`, without claiming general semantic scope.

This matters because an implementation that treats `record.GRANT`,
`SOFT-respect.silence`, `NEG`, `PROH`, and `CONS` as interchangeable
authorization flags would turn a language distinction into a safety and
translation error. The source does **not** justify that.

## Creator elicitation: two genuinely novel scope probes

Both **unattested/NOT CANON** below. The corpus gives E07 and E18 but does not
individually isolate predicate CONS from participant CONS in stabilization:

1. `Vahl=uth ta=en ech.` — does this mark consent-governance of the *act*
   while remaining silent about that particular participant's approval?
2. `Vahl ta=en=uth ech.` — does this mark the participant's permission
   independently from predicate-wide consent framing?

Ask whether each is permitted in ordinary/conclave registers, whether witness
scope changes, and whether the two choices affect truth conditions or just
pragmatics. Record rejection, uncertainty, or differences as data.

**Unsettled revocation:** E30's `vu` negates crossing, but nothing in the
attested examples proves it cancels a prior `=uth` grant. Please choose
whether revocation needs a distinct operator, a temporal/discourse rule, or
is still an undecided part of the language. Do **not** infer a rule from NEG,
PROH, silence, or `record.GRANT`.

## Executable qualification

`consent_scope_audit.py` uses the source-verifying typed frame implementation
and retains explicit predicate/participant attachments; source tampering is
rejected. Six source-bound tests passed, including:

- independent preservation of the E07/E18 consent contrast;
- E14/E21 predicate-only versus E18 predicate-plus-participant marking;
- E12/E27/E30 not promoted to CONS;
- two novel input forms never incorrectly labeled attested by the translator;
- no display of protected E26; tampered corpus denied.

This tests **recorded meaning preservation**, not full translation of unseen
utterances, lexical recognition of novel scope forms, or independent consent
grounding. All scope outcomes remain explicitly unknown.
