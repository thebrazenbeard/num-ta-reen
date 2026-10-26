# Semantic-to-acoustic alignment audit — Num’ta’reen (v82 study, v94 integration)

Status: **NONCANONICAL FALSIFICATION / research**, no new language rule or waveform inferred. The code in `research/alignment_projection.py` deliberately loses authored distinctions; it MUST NOT be exposed as translation. This integration is gated on accepting the separately reviewed `research/semantic_ir_proposal.py` dependency (draft PR #16); without it, the tests must fail rather than invent a semantic parse.

## Frozen research question and plan (before formal probes)

Question: Can each source-attested semantic distinction recovered from Num’ta’reen’s author interlinear glosses be represented in the 3,072-state **synthetic structural** resonance `Packet` without losing meaning or provenance?

Predictions and falsifiers:

- **H1 (complete lossless mapping):** every nonprotected, source-bound scope-supported utterance can be mapped to a unique `Packet`, with a round trip that retains predicate, referents, roles, discourse, evidential scope, multiple consent locations and acoustic dimensions. **Falsifier:** one pair of distinct authored semantic observations maps to the same Packet or a feature cannot be expressed in Packet.
- **H2 (narrow structural projection):** a limited, transparently lossy map of role-presence, single echo/evidential, some inversion, and coarse consent could be defined as a **research hypothesis**, not a complete language translation. **Falsifier:** even these categories do not correspond to source IGT features, or the map silently promotes fabricated content or unapproved choices.
- **H3 (codec semantic grounding):** acoustic carrier values reveal native semantics without the external codebook. **Falsifier:** an arbitrary codebook permutation preserves packet recovery while relabeling frequencies, or published corpus has no measured native audio paired with semantics.

Predeclared methods (all **confirmatory**, to be executed after this section is frozen):

- **A01 Schema-loss audit:** enumerate source-known semantic features and fields of `numtareen.experimental_resonance_packet.Packet`; identify absent dimensions and forced reductions.
- **A02 Corpus contrast matrix:** inspect E01/E05 (FOC), E01/E08 (Q), E01/E15 (LOOP), E07/E18 (dual consent), E02/E03 (argument order), E20/E21 (predicate consent), E13/E23 (source conflicts). For each determine whether `Packet` alone distinguishes; never render E26 content.
- **A03 Executable source-bound projection/collisions:** read pinned corpus via semantic IR; compare native authored IGT observations to the best bounded codec projection where supported; record distinct observations that yield identical packets. Prohibited/ambiguous mapping must return `UNKNOWN`, not a guessed semantic.
- **A04 Algebra and acoustic-label null:** verify source-derived role/echo/consent categories are not semantically recovered merely by codec injectivity; cite existing test `test_permuted_labels_prove_no_inherent_semantic_grounding` and source baseline.

Stopping rules: conclude when A01–A04 yield traceable outcomes, each limitation has an explicit example, no canonical source is altered, and the lead receives a PASS/PARTIAL/FAIL verdict. Do not infer or output E26 numeric true-name chord. Proposed additional experiments after any result are exploratory and logged separately.

## Evidence log

_The log below is append-only; frozen plan above is not edited after probes._

### E01 — source/code snapshot

- `data/corpus.json` (examined in a frozen staging snapshot) Git blob `53d9f27d03579a1a3fc700c3394b56f834da784e` (30 authored records, E01–E30).
- `numtareen/experimental_resonance_packet.py` (examined in a frozen staging snapshot) Git blob `ed295b300379819c382ef15a294a6242c61346b7` (merged research implementation at Num main PR #14).
- `research/semantic_ir_proposal.py` precursor examined at v80 Git blob `d44a1edeee32bbfb7eae4ff319d4e69b8a01a6a2` (historical: this was unmerged at the time of the experiment). The authored IGT is source material, but its machine tree interpretation remains a noncanonical research hypothesis irrespective of integration.
- Original alignment regression `ling-alignment-v82/test_alignment_projection.py` Git blob `e138eb1a6b13b9b8389a2e6eb2155263335b742e` (historical before the exploratory census and integration). Integrated artifacts are `research/alignment_projection.py`, `research/census_alignment.py` and `tests/test_alignment_projection.py`.

### E02 — A01 structural schema inspection (confirmatory)

`Packet` comprises exactly: `roles` (unordered set of present labels), `evidence` (three values), `echo` (four), `consent` (two), `inversion` (two), `scope` (two), corresponding to 3072 combinations. There is **no field for**:

- **Lexical predicate identity** (distinguishing `nûm` alignment from `vahl` stabilization or `kesh` crossing).
- **Individual argument referents or repeated arguments per role** (only the set of role labels survives).
- **Order and pragmatic information structure** (`=tra` topic, `=sha` focus, late agent, contrastive topicalization).
- **Interrogativity, general negation, prohibitive modality** (inversion is not equivalent to `vu` negation).
- **Separate consent locations** (E18 marks both predicate-level and patient-level consent, not reducible to one safe Boolean).
- **Nested/nontrivial operator scope, conflicting parse alternatives,** or register/taboo restrictions.
- **The actual resonance pitch/timing continuum** described fictionally; `scope=narrow|wide` is a synthetic bit and not an authored measurement.

The set-of-roles operator is commutative by implementation, so it intentionally discards the E02/E03 argument order distinction. This is **not a bug in codeword injectivity**; it is a strict information-theoretic mismatch between the codomain and the claimed linguistic content.

### E03 — A02/A03 source-bound contrast matrix (confirmatory)

The executable `project_lossy` function in the test file is intentionally NOT a translator. It checks source-bound author gloss provenance, explicitly records discarded dimensions, uses a synthetic default scope, and refuses conflicting/unmapped/withheld rows. A decoded `Packet` cannot reconstruct those discarded fields; the source ID and loss ledger remain outside the waveform.

| Authored contrast | Source distinction | Synthetic packet comparison | Interpretation |
| --- | --- | --- | --- |
| E01 `nûm` vs E07 `vahl` | **Different lexical predicates**, both witnessed with a PAT role | **Identical** | Fatal to complete semantic representation; the codec encodes no predicate |
| E01 vs E05 | E05 has predicate **focus** `=sha` | **Identical** | Drops information structure |
| E01 vs E08 | E08 adds terminal polar **question** `hë` | **Identical** | Drops interrogativity |
| E02 vs E03 | Ordered AGT/PAT occurrences swapped; corpus notes pragmatic focus | **Identical** | Role set is unordered |
| E01 vs E15 | E15 adds preposed `qir` LOOP | **Different** | One structural contrast representable in assigned echo field |
| E20 vs E21 | E21 adds predicate-scoped `=uth` | **Different** | Presence of a consent mark representable, locus not generally |
| E18 | Predicate `=uth` and patient `=uth` independently attached | One `consent=present` bit | Loses two consent scopes, which may have nonidentical normative implications |
| E13 and E23 | Author source contains unresolved relativizer/restorative-concessive conflicts | Projection **refuses** | Correct abstention, no invented choice |
| E26 | Original author true-name chord annotation protected from spoken realization | Projection **refuses by ID** | No signal/chord output or E26 contents reproduced |

The four equalities above are decisive falsifiers for H1 even though `structural_codeword` is injective over its deliberately smaller **synthetic** domain.

### E04 — executed A03 test receipt (confirmatory)

Historical command, from the original shared scratch root (2026-10-26):

```bash
PYTHONPATH=ling-semantics-v80:num-integration-union-v60 NUMTAREEN_REPO_ROOT=num-integration-union-v60 python -m unittest discover -s ling-alignment-v82 -v
```

Exit code **0**; decisive result `Ran 11 tests in 0.014s` / `OK`. Tests independently verify the loss/collision examples listed above, source-conflict and protected-ID abstention, and two genuine preserved dimensions. This is **test evidence about representation loss**, not author approval or natural-semantic evidence.

### E05 — executed A04 codebook-permutation negative control (confirmatory)

Historical command from the original `num-integration-union-v60/` staging tree:

```bash
python -m unittest tests.test_experimental_resonance_packet.AcousticRoundTripTests.test_permuted_labels_prove_no_inherent_semantic_grounding -v
```

Exit code **0**; decisive result `Ran 1 test in 0.031s` / `OK`. An equally successful permuted codebook shows assigned acoustic carriers are not identified by native-language evidence. Existing Wreckforge grammar Part I.1 reports multimodal resonance modulation and timing but supplies **no measured native waveforms or absolute phonosemantic calibration**.

### E06 — independent authoritative remote blob check

Fetched GitHub's exact published Num tree `63cc68ee9f631252eae351f122310258de3b7d7a` from `https://api.github.com/repos/thebrazenbeard/num-ta-reen/git/trees/63cc68ee9f631252eae351f122310258de3b7d7a?recursive=1` (2026-10-26 UTC). Remote tree entries:

- `data/corpus.json`: `53d9f27d03579a1a3fc700c3394b56f834da784e`;
- `numtareen/experimental_resonance_packet.py`: `ed295b300379819c382ef15a294a6242c61346b7`.

Recomputed local `git hash-object` for both workspace files; local digests exactly equal remote GitHub blobs. This establishes **byte identity of the inspected corpus and code** with that published snapshot, not independent human validation of its linguistic claims.

### E07 — exploratory whole-corpus collision census (post-result)

After seeing the preregistered A02/A03 collisions, I extended coverage to all 30 source IDs. This was **not a preregistered confirmatory test**. The original `ling-alignment-v82/census_alignment.py` computed the census without printing any source utterance or protected notation; after integration, invoke its research-module equivalent:

```bash
python -m research.census_alignment
```

Exit code **0**. Decisive machine result: `authored_rows=30`, `projected_rows=27`, `rejected_ids=[E13,E23,E26]`, `distinct_synthetic_packets=16`. Five collision groups of distinct original corpus IDs: `(E01,E05,E07,E08,E29)`, `(E02,E03,E09)`, `(E04,E11,E19,E30)`, `(E06,E27)`, `(E15,E22)`. These collisions reflect **deliberately missing semantic dimensions**; the count does not prove any of the pairs have equivalent meanings.

I then added a plainly labeled **exploratory regression** `test_exploratory_full_corpus_projection_collapses_27_to_16` to preserve the observed census without retroactively making it confirmatory. Command:

```bash
python -m unittest tests.test_alignment_projection -v
```

Original pre-integration result: exit code **0**, `Ran 12 tests in 0.033s` / `OK`. Test Git blob `ad8a5a02943513fd77463d400b89a9e36a5cba6d`; census script Git blob `b4e768ed5534cef0e8d2071713f67c868e318151`.

## Findings against the frozen hypotheses

- **H1 REJECTED:** Current 3072-packet codec cannot losslessly represent the source's already-known lexemes and clause semantics. The E01/E07 same-packet collision alone suffices; E01/E05/E08 and E02/E03 supply independent falsifiers.
- **Type-preservation qualification:** The impossibility applies to the codec's **documented typed-field semantics** (roles/evidence/echo/consent/inversion/scope). An arbitrary mapping of 30 source IDs into 3072 opaque packet labels would trivially distinguish those IDs, but would no longer preserve the claimed compositional field meanings, referents, or generalization to new utterances. That would be sentence-ID encoding, not a lossless compositional language model.
- **H2 PARTIALLY CONFIRMED:** A narrow analytic projection can assign sources' role presence, witnessed/verified claims, one echo operator, inverse morphology, and a **coarse** consent-mark flag. But source-specific referents, scope, predicate identity, discourse, and consent loci must remain explicit **loss metadata**, so this cannot be called Num’ta’reen translation.
- **H3 REJECTED as demonstrated evidence:** The codec's frequency labels are arbitrary and permutable; source text alone cannot constrain the proposed 701 Hz pilot or 858–4312 Hz feature carrier scheme. This does not disprove that a fictional native encoding *could* exist; it disproves the inference from current codeword round trips to discovered native semantics.

## Qualification gates for meaningful future alignment

1. A structurally complete semantic representation must include predicate identity, ordered role attachments and referents, TOP/FOC salience, question/polarity, explicit consent scope by host, unresolved alternatives and register/taboo boundaries. Do not generate a canonical expression from a packet lacking any of those.
2. The acousto-semantic mapping must be conditional on explicit author-approved rules, versioned as a proposal and blind-tested on at least 20 **new, creator-adjudicated minimal semantic contrasts**. Existing 30 authored English glosses cannot serve both generator and independent semantic evaluator.
3. Acoustic codebooks need measurable calibration, pitch/gain/tempo robustness, interference and human perceptual discrimination tests. The current synthetic codec lacks source-identified native frequencies and any unauthenticated role-carrier substitution remains a known failure mode.
4. Run held-out generalization separately from exact corpus recall. Preserve ambiguity and unknown status; use null labels, permuted codebooks and an equally bandwidth-limited nonlinguistic packet encoder as controls.
5. All input observations require exact source-row and blob digest checks; prohibit E26 native/speech/acoustic rendering and do not claim source confidentiality from a redacted interface.

## Boundaries, deviations and independent review

- A03 is intentionally a *lossy research projection*: it sets a synthetic `scope="narrow"` placeholder and reports the loss. It is not a proposed canonical translator. No new alien spelling, pronunciation or word was generated.
- The v80 semantic analyzer is still independently reviewed/hardened; this audit's decisive packet-field absence results do not depend on its tentative scope tree, only on authored IGT features and the public synthetic codec fields.
- No external SDK or library version was used. No live audio or speaker measurement exists in source. Source inspected locally against exact Git blobs; no independent fieldwork claims.
- **Independent verifier verdict:** v87 independently confirmed the exact original v82 artifacts and reran **12/12** checks, endorsing their falsification finding while explicitly withholding canonical language status. The new v94 integration is mechanically reorganized with an additional exploratory collision-group check; it still requires **independent v94 review**. E04's **11** passing checks remain the earlier pre-census historical receipt.

## Integrated follow-up (v94; not part of frozen preregistration)

The original experiment's `project_lossy` function lived in the unit test, which made the census script import the test module. For integration, the deliberately lossy function moved unchanged in purpose to `research/alignment_projection.py`, and `research/census_alignment.py` imports that explicit research API. Regression tests now live under `tests/` and include an additional exploratory assertion on the **five** collision groups. This rearrangement does not change the conclusions of H1–H3.

Recommended checkout commands, **after** the semantic-IR dependency is integrated:

```bash
python -m unittest tests.test_alignment_projection -v
python -m research.census_alignment
```

Neither 3,072 structural packets nor the synthetic tones have been established as source-grounded native Num’ta’reen semantics. Any future mapping must pass the creator-held-out and protected-source gates above.

### Local integration-probe receipt

On 2026-10-26, with the isolated `ling-alignment-v94/` files first on `PYTHONPATH` and the staged semantic proposal and codec supplied from `num-integration-union-v60/`, `python -m unittest tests.test_alignment_projection -v` passed **13/13**. The standalone `python -m research.census_alignment` returned the unchanged 30 / 27 / 16 counts, five named collision groups, and the same three refused source IDs. The separate staging suite passed **189 tests** with **11 optional crossrepo tests skipped**, using the same two research roots. These are local execution results, **not** integrated `main` CI or independent v94 verification; a final suite on the merged semantic dependency is required.
