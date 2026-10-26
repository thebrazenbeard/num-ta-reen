# Typed semantic channel v1 — NONCANONICAL research prototype

**Status:** `SOURCE_BOUND_NONCANONICAL` for 27 attested, unconflicted,
unprotected interlinear-gloss observations; `ABSTAIN` for source conflicts,
unknown sources, protected material, or failed source integrity.

This is a **reversible *symbolic* representation of source-observed linguistic
structure**. It is not an authored Ech’ta’reen resonance encoding, speech
synthesizer, universal translator, acoustic code, frequency assignment,
licensed productive grammar, or evidence of human/alien perception.

## Why this exists

The earlier explicitly synthetic `numtareen.experimental_resonance_packet.Packet`
is a deliberately lossy six-axis structural projection (3,072 possible states).
The independently executable `research.census_alignment` census found **27 accepted
authored observations mapped to only 16 structural packets**. Those collisions
cannot be repaired by merely choosing unused numeric packet IDs: that would
assign arbitrary IDs to utterances without a compositional semantic channel.

This prototype carries the *observed parts*, with their order and attachment:

| Typed field | Retained from source-verified v91/v4 `SemanticPacket` |
| --- | --- |
| Predicate | Ordered predicate atom indices, authored form, predicate gloss |
| Arguments | Ordered indices, referent glosses, semantic role, consent flag |
| Topic/focus | `TOP` / `FOC`, preserving source atom loci |
| Question/polarity | Interrogative plus question loci, ordered `NEG` / `PROH` |
| Echo/evidential | Ordered `LOOP`/`RET`/`CLP` and source `EVID.*` observations |
| Consent | All atom loci, split by predicate, argument, unattached loci |
| Clause links | Ordered `COMP` / `REL` observations; composition remains unresolved |
| Ambiguity | Explicit partial/unresolved status, unknown scope, conflicts/unmapped indices |
| Surface observations | All ordered original atom forms, glosses, and tags retained |

The authored corpus ID is kept **only in provenance**, not used as a semantic
symbol or arbitrary utterance codeword. The output contains no English sentence
translation. Syntactically different authored utterances can share some feature
values without being collapsed or assigned new invented semantics.

## Source precedence and refusal policy

1. Original, amended Wreckforge sources (not modified here):
   `sources/reference_grammar_v2_updated_lphoneme.txt` and
   `sources/dictionary_v2_updated_lphoneme.txt`.
2. Source rows in `data/corpus.json`, content-pinned to Git blob
   `53d9f27d03579a1a3fc700c3394b56f834da784e` by the v91/v4 analyzer.
3. v91/v4 `research.semantic_ir_proposal.SemanticPacket`, freshly rederived from
   the pinned corpus for both encode and decode, preserves author IGT evidence.
4. The present `research/typed_semantic_channel.py` serialization is **noncanonical
   software engineering only**. Any proposed scope or phonetic mapping ranks
   below the authenticated source and cannot revise it.

**Mandatory refusals:** E13 (`RELATIVIZER_FORM_CONFLICT`), E23
(`RHEL_FUNCTION_CONFLICT`), E26 (protected, source withheld), any unknown ID,
unmapped source atoms, and unavailable/modified corpus source. `E26` has no
representation or derived audio here, and protected original notation must
not enter experimental artifacts. There is no API to encode arbitrary
unverified glosses as verified observations.

Status and ambiguity are deliberately separate: accepted means the **partial
author-IGT observation was source-bound and serialized faithfully**, not that
its complete grammar, semantic scope, or physical signaling is known. For
multi-predicate or linked constructions, `composition_status` is
`UNRESOLVED_MULTI_CLAUSE_OR_PREDICATE`. Even single-predicate packets carry
`scope_unestablished: true`.

## Deterministic mathematical carrier (symbolic only)

Frame v1 is:

1. `NTSP1` (five ASCII version bytes).
2. Four bytes, unsigned big-endian JSON payload byte count.
3. SHA-256 of the payload (32 bytes, **accidental corruption detection only**).
4. UTF-8 JSON with `sort_keys=True`, no whitespace, no nonfinite numbers,
   exact separator convention; maximum payload 16 KiB.

Decoder rejects truncation, trailing bytes, wrong digest, duplicate keys,
invalid UTF-8, noncanonical bytes, oversized input, unsupported status/schema,
and even syntactically valid rehashed semantic forgeries. It recomputes the
*entire* expected observation from the pinned source and checks full-frame
byte equality **on decode and again for every public decoded property/export**.
Directly constructing or `dataclasses.replace`-modifying a `DecodedPacket`
does not bypass this check. SHA-256 alone does **not** authenticate a sender or prevent
someone from computing a new checksum.

The frame's byte structure is machine-checkable and reversible, but it is not
a theory of physical resonance, spectral frequency, phonetic realization,
multi-parameter auditory separability, or source-native Ech’ta’reen math.

## Run the independent tests

From a normal Num’ta’reen repository checkout (Python 3.10+; standard library):

```bash
python -m unittest discover -s tests -p 'test_typed_channel.py' -v
```

The integration uses v91/v4 `research/semantic_ir_proposal.py`,
`research/alignment_projection.py`, `numtareen.experimental_resonance_packet`,
and the source-pinned `data/corpus.json`. The implementation does not import
test modules, and the tests do not rely on a scratch workspace path.

One source-verified reversible use:

```bash
python -c 'from research.typed_semantic_channel import encode_corpus_id, decode_frame; wire=encode_corpus_id("E18"); result=decode_frame(wire); print(result.source_id,result.semantic["consent"],wire==result.reencode())'
```

For application use, call `encode_or_abstain()` and inspect `EncodeResult`:

- `status="SOURCE_BOUND_NONCANONICAL"` with a `frame` on accepted evidence;
- `status="ABSTAIN"` with `frame=None` and a sanitized refusal `reason`
  (`SOURCE_CONFLICT`, `PROTECTED_SOURCE`, `UNKNOWN_SOURCE`, etc.).

**Do not treat `inspect_frame()` as authentication.** It is a deliberately
unverified diagnostics parser. Only `decode_frame(..., repo_root=<pinned
source>)` rederives source provenance and returns a trusted observation.

## Executed acceptance evidence

`17` isolated unit tests passed locally. The tests include:

- All 27 accepted source observations encode–decode–reencode byte exactly;
  E13/E23/E26 abstain and an invented E99 source ID abstains.
- Actual lossy projection collisions E01/E07 (predicate), E01/E05 (focus), E01/E08
  (question), E02/E03 (argument order) are different in this new semantic
  body **even with the source ID removed**.
- E18 retains **two** different consent loci (predicate and argument) whereas
  old Packet reports a single `consent="present"` bit.
- Exploratory census: 27 accepted authored rows produce 27 distinct **full
  observation payloads**, versus 16 old synthetic packets. Some distinction
  comes from retained authored lexical forms. This count must **not** be
  mistaken for proof of compositional language coverage or decoding accuracy.
- Tamper, length, checksum, duplicate-field, deeply nested malformed JSON,
  changed pinned corpus, forged `DecodedPacket` via `dataclasses.replace`,
  and oversized-input rejection;
  changing a semantic field *and recomputing its SHA-256* is still rejected by
  source binding.

Integration-layout smoke check: copying only the v1 source and test files plus
the already developed alignment projection into a temporary local Num’ta’reen
checkout, then running **without `PYTHONPATH` or corpus-root overrides**
from that checkout passed `17/17` typed-channel tests and `219/219` discovery
tests (`11` optional cross-repository tests skipped). This is an executable
local layout check, not an upstream CI or merged-main receipt.

## Open scientific limitations and independent hostile review request

> **Hostile challenge:** Merely copying every source atom preserves differences
> but does not demonstrate a generative semantic algebra or neural decoding.
> Show prediction on independently withheld authored examples with clear
> source permission before calling this a language encoder.

> **Hostile challenge:** Ordered operators are observations, **not yet
> justified binding/scope rules**. Multi-clause linking and how a consent
> marker scopes over nested predicates remain unresolved in these sources.

> **Hostile challenge:** A canonical deterministic byte frame is not an
> acoustic waveform or an authenticated conversation protocol. A future
> frequency/resonance mapping requires explicit spectral constraints,
> reversible decoding under noise, and blinded perceptual or machine-channel
> tests; this prototype proves none of those.

An independent hostile reviewer (v104) probed provenance forgery, altered
decoded objects, source substitution, payload integrity and repository-shaped
execution and found no blocker to research-software integration. The source
provenance is rechecked on each decoded-object export; no native language
authority or acoustic claim follows from that review.
