# Nûm’ta’reen and UNVTRSLR: private integration guide

**Status:** engineering proposal, not an installed cross-repository interface and not a change to language canon.

**Visibility:** Keep this guide in the **private** `thebrazenbeard/num-ta-reen` repository. Its examples refer to private Wreckforge language material; do not publish them in the public `thebrazenbeard/unvtrslr` repository, CI logs, artifacts, screenshots, or issue discussions.

## Two different capabilities

| System | What it does now | What it does not do |
| --- | --- | --- |
| Nûm’ta’reen | Offline, source-attested bilingual lookup and marked approximate dictionary glosses; PowerShell 5.1/7 interface | Unrestricted fluent/compositional translation; authentic native resonance decoding |
| UNVTRSLR | Experimental acoustic-unit discovery, grounding of operational relations, source-calibrated inference, ambiguity and held-out qualification machinery | Automatically read Nûm’ta’reen text, reconstruct its physical resonance, or establish universal/true semantic equivalence |

The project goals complement one another, but the working textual dictionary must not be mistaken for independent evidence that an unknown-signal learner discovered those meanings.

## Use the proven textual translator today

From the root of a cloned **private** `num-ta-reen` repository in Windows PowerShell:

```powershell
# Nûm’ta’reen -> English, source-attested example
.\scripts\Translate-Numtareen.ps1 -Direction nt-en -Text 'Nûm ta=en ech.'

# English -> Nûm’ta’reen, source-attested example
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Text 'Stop. Do not proceed.'

# Continuous private translation session
.\scripts\Translate-Numtareen.ps1 -Interactive
```

Requires Python 3.10+; this path uses the Python standard library and checked-in lexicon/corpus only. Interactive commands include `:direction nt-en`, `:direction en-nt`, `:unknown mark|keep|error`, `:help`, and `:quit`. The Python interface also has structured `--json` output: `py -3 -m numtareen --direction nt-en --text 'Nûm ta=en ech.' --json`.

Do not interpret a lexical-gloss result as a grammatical translation. Preserve ambiguity, source IDs, register/taboo information, and unknown markers when building a UI over the JSON response. The source spelling `nûm` is not equivalent to unaccented `num`.

## UNVTRSLR currently uses a different input protocol

UNVTRSLR currently advertises a Python 3.11+ `unvtrslr-translate` CLI, with NumPy/SciPy dependencies. Its V2 pipeline fits a model from evidence episodes, independently freezes a source calibration profile, and then maps query *acoustic evidence* to frozen operational relations. `num-ta-reen`'s PowerShell text input is **not** a drop-in replacement for those training/calibration/query evidence files.

The documented UNVTRSLR stages are:

1. `unvtrslr-translate fit training-episodes.jsonl` — research training data, not a bilingual dictionary import.
2. `unvtrslr-translate calibrate translator.json source-calibration.jsonl` — separate calibration evidence with adequate distinct contrasts.
3. `unvtrslr-translate translate translator.json source-profile.json source-query.jsonl` — only later queries, with the frozen profile.

These command names describe the existing upstream research flow, **not** commands that operate on Nûm’ta’reen utterances today. Dependencies may need installation in advance; offline execution is not the same as offline first-time installation.

## Proposed boundary for the first adapter

The first integration should be a **reference / evaluation adapter**, not a waveform synthesizer or a claim of independent semantic discovery:

- Read the private corpus and dictionary via the existing governed Nûm’ta’reen translator; do not duplicate canonical language data into the public repository.
- Emit a versioned, provenance-bound record with modality (`written_field_transliteration`), direction, input, result state (`attested`, `lexical_gloss`, `ambiguous`, `unknown`), candidate IDs, register restrictions, source hashes, and uncertainty/loss notes.
- Keep a hard boundary between **answer-key/reference records** and the learner-visible experimental observations. If meanings were supplied by the Nûm’ta’reen corpus, label performance as reference lookup or supervised transfer, not emergent grounding.
- Provide a public protocol fixture with opaque invented identifiers (`S1`, `C1`, `E1`) and synthetic text that is **not** a Wreckforge phrase. Public tests should not embed, snapshot, or transmit private language material.
- Require distinct rights/visibility checks before a private fixture or model trained on private language data is exported, uploaded, or committed to UNVTRSLR.
- For later resonance experiments, preserve channels (timing, relative frequency, phase, modulation, roles, consent, echo/evidence, provenance) only as explicitly **hypothetical** schema fields until Patrick defines the actual fictional encoding. No arbitrary hertz assignment becomes canon.

## Acceptance checks for that adapter

1. Private offline smoke: exact attested forward and reverse lookups retain their provenance; ambiguous/unseen inputs fail closed.
2. Unicode: NFC-equivalent spellings may normalize, but contrastive accents and glottal/apostrophe semantics do not collapse; PowerShell round-trips quotes and non-BMP characters.
3. Taboo/true-name material never silently becomes pronounceable or ordinary-register content.
4. Public leakage: examine public staged diffs and build artifacts for private corpus sentences, dictionary entries, names, hashes of private inputs that could aid enumeration, and embedded fixture payloads.
5. Experimental validity: a bridge given answer-key labels cannot claim to have inferred them independently; query batches cannot recalibrate their own source profiles.
6. Loss ledger: `attested`, `approximate`, `unresolved`, `omitted`, and `added` must remain separate from any fluent UI rendering.

## Source bindings for this proposal

- Private `num-ta-reen` main: `cdfbea09cc8b4a1648cde733953986c7d694d496` (README, PowerShell wrapper, sources/proposals).
- Public `unvtrslr` main: `8be8e6f701b44660bf48d53a2a395faa2012956d` (`README.md`, `pyproject.toml`, `docs/REFERENCE_TRANSLATOR_V2.md`, `docs/SEMANTIC_CONSERVATION.md`).

Revalidate both exact heads before implementing or publishing any adapter. The guide is a route to integration, not proof that the two CLIs are already interconnected.
