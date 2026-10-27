# Num’ta’reen four-cell marker-presence microgrammar probe — exploratory research v173

## Repository integration and reproducibility

The v173 investigation below records historical commands run in the analyst's
isolated scratch checkout. Those scratch paths are retained as **historical
execution evidence**, not as instructions to run in a published checkout.
From the Num’ta’reen repository root, use:

```bash
python -m unittest discover -s tests -p test_factorial_scope_probe.py -v
python -c "import json; from pathlib import Path; from research.factorial_scope_probe import evaluate_repo; print(json.dumps(evaluate_repo(Path('.')), ensure_ascii=False, indent=2))"
```

The test module resolves its corpus relative to its own published repository
root, independent of current working directory. No source utterance or lexicon
is changed; source-pinned claims require the exact authored corpus Git blob.
The experiment is retrospective and only demonstrates **surface marker
composition in one lexical context**. The question/LOOP semantic scope order
and general productive capability remain unknown.

## Frozen plan (2026-10-27, before result inspection)

**Question.** Does the currently attested corpus support a productive, falsifiable semantic scope rule beyond memorizing individual words or entire English glosses?

**H1 — bounded compositional scope.** A source-bound morpheme or grammatical marker occurs with enough distinct neighboring forms to predict a consistent semantic relation in held-out authored corpus examples. **Falsifier:** each relevant contrast can be explained only by whole-form memorization, contradictory source readings, or English-gloss projection.

**H2 — acoustic semantics separable from lexical attestation.** Written sources do not license treating speculative carrier frequencies or packet dimensions as proof of phonemic semantic contrasts. **Falsifier:** source text explicitly attests contrastive frequency/resonance assignments and relevant minimal pairs.

**C1 (confirmatory, source inspection):** Inventory all authored corpus lines and source grammar examples for evidentiality, negation, temporality, modality, possession/relation and clause boundaries. Freeze per-line source IDs, exact Git blob and status; count distinct contexts by function.

**C2 (confirmatory, minimal pair check):** Identify any actually attested productive grammatical contrast; test whether the same morpheme appears in at least two independent lexical contexts and whether corpus includes a falsifying counterexample. No invented native strings allowed.

**C3 (confirmatory, authority check):** Cross-check source grammar prose vs derived docs/data and disclose conflicts/protected E26.

**E1 (exploratory):** Propose the smallest next elicitation set necessary to discriminate a compositional rule from memorization; propose a preregisterable hold-out benchmark.

**Stopping rules.** Stop after examining canonical source text and current data/docs sufficient to decide H1/H2, or if canonical source cannot be validated. Do not promote proposed forms, sound/frequency maps, or inflections to canon. No GitHub mutations.

## Evidence log

Pending.

### R01 — authoritative source custody

- [SOURCE] `thebrazenbeard/num-ta-reen@e12a0a3914f3676c79b9e93d03b797245c5198c1`, GitHub REST tree. `data/corpus.json` blob `53d9f27d03579a1a3fc700c3394b56f834da784e`, updated grammar blob `d7bd1a1a07d9052b6795b3824bfc18fc9c50e912`, `research/semantic_ir_proposal.py` blob `9e34143eab85a6e48b897a7834ba658abc3bf78c`.
- [SOURCE] Current grammar III.6, IV.1; the orthographic polar question marker `hë` is clause-final and `qir` is a structural LOOP operator before the proposition in the actual examples. Grammar I.1–I.5 describes resonance/timing **qualitatively** but supplies no numerical native waveforms or frequency-to-feature calibration.
- [REVIEW] Earlier repo `docs/SEMANTIC_ACOUSTIC_ALIGNMENT_AUDIT.md` explicitly establishes 3,072 synthetic Packet states but collisions among semantically distinct authored examples. `docs/CONSENT_SCOPE_CONTRAST_V0.md` already analyzes the two consent loci and warns against promoting a new productive consent grammar; this review does not duplicate that as a novel result.

### R02 — C1/C2: one complete crossed four-cell paradigm

| Corpus ID | LOOP via preposed `qir` | Polar Q via final `hë?` | Other components |
| --- | --- | --- | --- |
| E01 | absent | absent | `nûm`, 2.PAT, WIT |
| E08 | absent | present | identical base |
| E15 | present | absent | identical base |
| E22 | present | present | identical base |

The four authored text examples share the same core. There is a complete **written form / English IGT** 2×2 factorial design. It supports separability of these *marker-presence values in this exact lexical context*, but **not** commutative semantic scope (Q(LOOP(p)) need not mean LOOP(Q(p))), productive insertion across arbitrary predicates, universal competence or an observed native acoustic 2-bit channel.

### R03 — C2: inadequate independent lexical contexts

`qir` occurs in E15 and E22, both `nûm` alignment. The corpus has a distinct lexical polar-question context E09 (`kesh`, WH question), but lacks a second independent 2×2 `qir`×`hë` paradigm. Hence **strict H1 remains unconfirmed**. The meaningful next test is creator-authored crossing and stabilization paradigms; do not generate them as canon.

### R04 — exploratory E1 benchmark and deviations

- **Reason for pivot:** the single complete 2×2 paradigm emerged only after C1 source inspection, so a train-on-three, score-fourth evaluation is *retrospective exploratory*, not a preregistered confirmatory outcome. No independent blind generalization claim follows.
- [EXECUTED] `python -m unittest discover -s ling-semantic-depth-v173 -p 'test_factorial_scope_probe.py' -v`, from scratch root: first run failed (8 passed, 1 error) because my negative-control test incorrectly tried to index absent E20 in a four-row source subset. Test fixture corrected without changing hypothesis, second run exited 0, **9/9 tests passed**.
- [EXECUTED] `python -c 'import sys,json,pathlib;sys.path.insert(0,"ling-semantic-depth-v173");import factorial_scope_probe as p; print(json.dumps(p.evaluate_repo(pathlib.Path("num-main-live-v142")),ensure_ascii=False,indent=2))'`, exited 0. Training IDs E01/E08/E15; heldout ID E22; source copy predicts E15 (wrong), whole-sentence lookup abstains, prefix-plus-suffix marker composition predicts source E22 orthography exactly. This is **one heldout string**, not a rate estimate of language productivity.
- [TEST] A held-out row spy raises on any pre-prediction field read; post-prediction gold counterfactual alters scoring while leaving prediction unchanged; raw corpus Git digest mutation is rejected; forged caller rows always carry `CALLER_SUPPLIED_UNVERIFIED_ROWS`; E26 and protected delimiters are refused. This tests code-path custody, not guarantees about independent model memorization from earlier corpus exposure.
- [LIMIT] The role of E22 as target, semantic factors LOOP=1/Q=1, and overall source family were selected with knowledge of this authored dataset. A fresh creator-approved cross-lexical dataset remains necessary for a confirmatory verdict.

### R05 — H2 and mathematical implication

- [SOURCE] Grammar I.1–I.5 posits correlations between resonance bands, timing, vowel length and scope but lacks any measured numeric carrier map or minimal-pair native signal recordings. Thus physical interpretation is underdetermined, consistent with H2.
- [MATHEMATICAL INFERENCE] If the four observed symbolic feature combinations must remain independently distinguishable, any lossless code at this abstraction needs **at least log2(4) = 2 binary choices**, before synchronization, source detection or redundancy. This is **not** a measured bitrate or frequency assignment; it cannot identify Ech’ta’reen native semantics.

## Review status

Own implementation and tests complete; independent hostile verification **pending**. Therefore v173 is not a confirmed productive grammar and is not merge-qualified.

### R06 — pre-freeze hostile-row safeguard

- [REVIEW/PIVOT] Before independent artifact freeze I recognized a potential row-method spoof: accepting arbitrary `Mapping` rows then validating via `.get()` but processing via `__getitem__()` could permit one caller object to provide benign values during validation and protected notation afterward. Source-pinned repository loading uses ordinary JSON dicts, but the lower-level unverified API should also not emit the protected value.
- [FIX] Internal rows now require an exact built-in `dict`; an outer spy Mapping remains permitted for a custody test. Added an adversarial row-subclass regression that is rejected before content access. No change to the source dataset, prediction, baseline or metric.
- [EXECUTED] `python -m unittest discover -s ling-semantic-depth-v173 -p 'test_factorial_scope_probe.py' -v` from scratch root, exit **0**, `Ran 10 tests in 0.004s` / `OK`. The source and E22 prediction remain the same.
- [STATUS] Artifact is now frozen pending independent hostile review. All conclusions remain **exploratory**, and this is not a formal security proof.
