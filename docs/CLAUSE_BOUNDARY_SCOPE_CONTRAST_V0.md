# Clause and operator scoping: authored warning packets (research V0)

Status: **noncanonical, source-verified contrast**, not a Num’ta’reen parser,
translator, fluent generator, prosodic model, or semantic-qualification claim.
Source: `data/corpus.json`, Git blob `53d9f27d03579a1a3fc700c3394b56f834da784e`;
current grammar `sources/reference_grammar_v2_updated_lphoneme.txt`, III.7,
IV.1–2, and authored E11/E17/E19/E27/E30. The source's IGT is English
expository annotation, not an instrument-recorded signal.

## Verified bounded distinctions

| Authored row | Observed clause structure | Consequence of flattening |
| --- | --- | --- |
| E11 | One warning packet: `PROH`, `cross`, `EVID.WIT` | Cannot equate PROH alone with all witness-bearing warnings. |
| E17 | One alarm packet: `PROH`, with no overt evidential | Absence is licensed in alarm context; it cannot be fabricated as WIT. |
| E19 | One statement: `record.LCH`, `NEG`, `EVID.WIT` | Negation and witnessing occur in the same authored packet. |
| E27 | Record statement with `EVID.VRF`, then a separate silence-respect expression | Silence-respect is not semantic permission or evidence of assent. |
| E30 | Three sentences/packets: `PROH` / `boundary-THR`+`EVID.WIT` / `cross`+`NEG` | Do not copy the middle packet's witness onto the final negative crossing. |

The existing V0 typed semantic carrier faithfully retains original atom indices
and has `scope_unestablished: true`; it does **not** make E30's three clause
boundaries available as an attested typed contrast. This is an incremental
source-bound *audit*, not a claim the earlier carrier fabricated evidence.

## Falsification and limits

- The E30 text has punctuation-supported three sentences and IGT has five
  pairwise form/gloss atoms. The manually checked pairing is `[0] / [1,2] / [3,4]`.
- E27 is two orthographic packets and three IGT pairs, mapped `[0,1] / [2]`.
- The audit deliberately supports only five listed authored rows; unsupported
  rows and the protected E26 return `SourceBoundaryUnavailable`.
- Mutated or absent corpus content fails the pinned Git-blob test.
- The **hypothesis** that these boundaries generalize productively to arbitrary
  utterances remains untested; prosodic rise, echo operator association, and
  whether a single connected acoustic signal maps to orthographic sentences
  are still unknown.
- The **hostile failure** to test next: swapping punctuation or moving `ech`
  across packet boundaries must never silently create a source-attested frame.

Run `python -m unittest discover -s tests -p 'test_clause_boundary_audit.py' -v`
from a repository containing the pinned `data/corpus.json` and this research
module, or point `NUMTAREEN_TEST_REPO_ROOT` at the checked-out corpus root.
