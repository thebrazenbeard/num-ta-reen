# Controlled Num’ta’reen word-order/focus falsification V0

**Evidence class:** SOURCE_BOUND_NONCANONICAL. **Not canon, a translator, or a
measurement of unseen-sentence generalization.**

## Frozen claim and source

- Public Num’ta’reen `main` inspected at
  `b63ac4791fc8599236b60237d3d1900bdba37bb9`.
- Authored `data/corpus.json` Git blob:
  `53d9f27d03579a1a3fc700c3394b56f834da784e`.
- Typed-semantic module locally inspected Git blob:
  `adfae0c2db8805b5a63bbaefa46ba99c683db103`.
- Parsed semantic-IR module locally inspected Git blob:
  `9e34143eab85a6e48b897a7834ba658abc3bf78c`.
- The code reloads and verifies the pinned authored corpus before producing
  results. E26 is not requested or emitted by the audit.

**Hypothesis H1:** an unordered word/role multiset is a sufficient encoding
of attested clause meaning, including contrastive focus.

**Falsifier:** E02 and E03 have exactly the same orthographic tokens and role
inventory, but the author supplies two different English renderings and an
explicit E03 note that late AGT signals contrast/focus in clipped briefings.
If H1 holds, a deterministic unordered encoder would have to assign two
different outputs to the same input—impossible without extra context or
order-sensitive data.

| Source | Authored orthography | Authored gloss of salient roles | Authored English |
| --- | --- | --- | --- |
| E02 | `Nûm na=ka ta=en ech.` | AGT preceding PAT | I align you (witnessed). |
| E03 | `Nûm ta=en na=ka ech.` | PAT preceding AGT | It is you I’m aligning (and it’s me doing it). |

This is one attested contrast pair, not a proof of a universally productive
scrambling rule or a statistical accuracy estimate on unknown speakers.

## What the typed representation does and does not retain

- **Preserves:** source atom indices, original forms/glosses, AGT/PAT role
  assignments, and their ordering. E02's (AGT@1,PAT@2) differs from E03's
  (PAT@1,AGT@2); source-verified frames differ.
- **Does not infer:** a separate `FOC` tag from E03's late AGT. Both E02
  and E03 have `discourse=[]`, because the current `discourse` projection
  reports overt tagged TOP/FOC, not every contextual focus implication.
  **This is an explicit projection limit, not a demonstrated data-loss bug
  in the full frame.** An order-blind downstream consumer can still lose
  the distinction by projecting to a role bag.
- Other source controls isolate different semantic dimensions:
  E01↔E05 overt `=sha` focus, E20↔E21 `=uth` consent, and E01↔E08
  interrogation. Their corresponding typed features differ.
- A novel permutation has no source ID and is **not** reinterpreted as
  attested grammar.

## Executable proof and controls

From the Num’ta’reen repository root:

```sh
python -m unittest discover -s tests -p test_contrastive_focus_audit.py -v
python -m research.contrastive_focus_audit
```

**Observed: 6/6 tests PASS** (all source-bound; no network or model inference).
Tests include source SHA1 tamper refusal and no protected notation disclosure.

> **Hostile challenge:** These examples are only one author’s controlled
> reference set. An order-aware encoder distinguishing E02/E03 shows
> preservation of source order, not that it has learned a grammar. The
> English free renderings are evidence of intended interpretation, but
> do not establish how independent speakers would understand an unseen
> permutation. Any future focus rule requires more contrastive elicitation,
> ideally natural dialogue context and independent validation.

## Creator-facing research question

In clipped briefings, does moving `na=ka` behind `ta=en`
**systematically** signal contrastive focus on the patient, or is E03
a formula with context-specific emphasis? A safe elicitation pairs the
two *already attested* utterances across neutral versus corrective
contexts, asks Patrick for focus/scope judgments, and records refusals.
Do not auto-create a new grammar rule from this audit.
