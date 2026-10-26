# Source-bound semantic structures for Nûm’ta’reen — proposal v4 (noncanonical)

**Status: NONCANONICAL RESEARCH PROPOSAL.** This is a typed reading of the
author's human-language interlinear glosses, not a productive grammar or
independently decoded Ech’ta’reen message. Source: public
`thebrazenbeard/num-ta-reen@ed9a94d53d17db6415de172858773714644e01ba`.
The author lexicon (500 entries), corpus (30 utterances), and original Wreckforge
source documents remain unchanged.

## Semantic commitments warranted by source

The amended reference grammar II.4, III.1–3, III.6–7 and IV.1–5, along with
the authored E01–E30 corpus, support distinguishing at least these layers:

1. **State/event predicate** (e.g. `nûm` in E01, `vahl` in E07).
2. **Participant role**: `=ka` agent, `=en` patient, `=ru` source,
   `=va` goal, `=shi` instrument. A role is not identical to a bare noun.
3. **Discourse anchoring**: `=tra` topic, `=sha` focus; these carry
   information distinct from event participants.
4. **Echo/provenance**: witnessed `ech` versus stronger
   cross-echo-verified `reen`, with structural loop/return operators
   `qir`/`ruun`. An evidential claim is not independently measured truth.
5. **Ethical/consent scope**: `=uth` attached to predicate and participant
   are not interchangeable; absence is not automatically actual coercion.
6. **Polarity and inquiry**: `vael-` inversion is not identical to
   `vu` negation; `hë` is a corpus-attested question particle.

Candidate abstract packet:

```text
AuthorGlossPacket {
  predicate, ordered_roles[], discourse_annotations[],
  structural_echo?, evidential?, polarity?, question?,
  consent_locations[], unresolved_source_conflicts[]
}
```

This packet is an *analytic metalanguage*—not the alien language's native
data structure. Its relationships are hypotheses to test against author
judgments and, eventually, actual communicative samples.

## Five source-bound, testable contrasts

| Authored examples | Distinction | What a translator must not erase |
| --- | --- | --- |
| E01 / E05 | Baseline alignment versus explicit predicate focus `=sha` | Focus is not a synonym of the predicate; E05 carries salience |
| E01 / E08 | Witnessed statement versus final `hë?` | Scope of a question may differ from truth commitment |
| E01 / E15 | State packet versus preposed `qir` LOOP | Repetition/recurrence is not English past tense |
| E07 / E18 | Stabilization versus predicate-and-patient `=uth` | Consent locus and autonomy, not a single consent boolean |
| E02 / E03 | Same agent and patient in different order | Pragmatic highlighting without reversing agent/patient |

E04 includes the topicalized Veil/boundary even without a conventional role
clitic. A tree that drops that topic is not semantically preserving. Conversely,
E23's `rhel` restorative sense is strongly supported by corpus and dictionary,
but conflicts with grammar III.8's concessive use; the prototype **does not**
produce a confident scope tree for it. The `së`/`sën` relativizer/manner
conflict similarly remains unresolved. No code elects a new canonical rule.

## Code as a falsifiable *supporting* instrument

`research/semantic_ir_proposal.py` and
`tests/test_semantic_ir_proposal.py` isolate source-backed observations.
The module loads `data/corpus.json` and independently verifies its exact
Git content-object digest
`53d9f27d03579a1a3fc700c3394b56f834da784e` before assigning
`SOURCE_VERIFIED_AUTHOR_INTERLINEAR_GLOSS`. It rejects arbitrary callers
who reuse E01's ID with invented or altered IGT, even if those forms look
grammatically plausible. The row check compares canonical JSON rather than
attacker-overridable `str.__eq__`; after matching, the packet is built from
the *loaded pinned row*, never from a caller's lookalike object. Its explicit
`analyze_unverified_igt` entrypoint
never claims source provenance or generates a scope tree.

**Packet-integrity gate (v3):** `SemanticPacket` is a Python dataclass, not
an authentication token; calling `dataclasses.replace` can fabricate a new
role, evidential or consent location while leaving the evidence string intact.
Both the public `to_dict()` exporter and `proposed_scope_expression()` therefore
reload the Git-blob-pinned corpus and independently recompute the complete
observation before allowing a `SOURCE_VERIFIED` result. They compare canonical
JSON structures, not user-overridable equality methods, **then build every
scope tree and source-verified export from a freshly parsed, pinned source
packet**. This last step prevents a subclass of `str` from passing JSON equality
while lying via `__str__`, `__repr__` or `.split()` when a consumer renders a
tree. Packet subclasses and non-JSON fields are rejected. A modified E01 witnessed evidential cannot be
relabeled as cross-echo verification and still generate a tree or source-labeled
export. This is deterministic provenance consistency, **not** cryptographic
authenticity, a proof of native semantics or a trust boundary against code
executing with the repository's file-system authority.

Unknown affixed gloss features remain flagged *even when another part of the
atom is known*; source focus/topic features survive in tentative trees;
multiple echo/evidential operators, unresolved source conflicts, and
multi-clause cases refuse a single invented tree. This corrects adversarial
findings against an earlier unmerged prototype.

**Hostile correction (v4):** v3's delimiter gate used `delimiter in text`,
which dispatches an untrusted subclass of `str`'s `__contains__` method.
Such a subclass could lie and pass the actual source-protected E26 IGT to
`parse_igt_pairs`, `analyze_unverified_igt`, or `render_igt_pairs`. V4
requires exact built-in `str` inputs and calls canonical `str.__contains__`
for delimiter checks; the renderer also requires exact bounded tuple/atom
types. Its IGT boundaries reject unsafe control code points and surrogates,
allowing canonical tabs/newlines/carriage returns only as pair separators
(E27 has a source newline), while rejecting whitespace within individual
form/gloss fields and overlong input/output.
The regression suite loads E26 dynamically from the verified pinned corpus;
neither tests nor report copy its protected numeric notation.

The corrected protection on E26 means no public parser/renderer/packet serializer from
this *proposal module* materializes its true-name notation; the notation already exists in
original public repository data, so this is **output nonreproduction**, not
confidentiality. Publication policy remains Patrick's decision.

Run in a complete local Num’ta’reen checkout:

```powershell
python -m unittest discover -s tests -p 'test_semantic_ir_proposal.py' -v
```

In isolated development, set `NUMTAREEN_REPO_ROOT` to an exact checkout
and `PYTHONPATH` to the directory containing `research`; the pinned
hash still applies.

These tests establish deterministic gloss extraction, preservation of
known distinctions, refusal of forged/unlicensed cases, source-row and
in-memory packet consistency, and exact-source provenance. The v4 suite extends
the original 25 tests with subclassed protected-notation ingress and invalid
Unicode/size regressions, including adversarial dataclass replacement, non-JSON values,
protected synthetic atoms, spoofed packet equality, hostile string-equality
overrides and string-subclass display/parse override attacks. **They do not establish productive translation, natural
semantic grounding, human speaker agreement, or native acoustic encoding.**

## Next authorial elicitation

1. Adjudicate `së`/ `sën`, `rhel` and the phoneme/coda inconsistencies
   before expanding productive syntax.
2. Test 20 predeclared scenarios with Patrick: five public calibration
   controls and 15 novel, independently held-out items. Include
   agent/patient order, topical focus, consent grant versus withdrawal,
   question/echo scope, and witness versus cross-echo verification.
3. Request author-created negative examples and register judgments. Record
   every accepted form with exact orthography, IPA or acoustic annotation,
   translated meaning, pragmatic context, and source version.
4. Evaluate a separate, explicitly *invented* resonance codebook under
   pitch, timing, phase, interference and permutation controls; successful
   synthetic decoding does not turn its frequencies into canonical speech.

> **Hostile challenge:** The same English gloss can be re-encoded in an
> arbitrary waveform. Unless new author-approved contrasts and falsifying
> examples determine the mapping, no claim of discovered Ech’ta’reen
> mathematics has been earned.
