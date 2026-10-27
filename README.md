# Nûm’ta’reen

> Fictional language and state-sharing communication system of the Ech’ta’reen, from *The Wreckforge Chronicles*.

This repository turns Patrick A. Sims’s existing worldbuilding documents into a versioned language reference, a 500-entry digital dictionary, a 30-utterance attested bilingual corpus, and a **PowerShell-friendly, offline Num’ta’reen ⇄ English interface**.

The original OneDrive folder and documents remain untouched. This repository is **public** and contains text extracts, searchable data, and code—not the manuscript. Public visibility does not grant a license to reuse the fictional language or source documents. The two `UPDATED_lphoneme` sources take precedence over older drafts.

## Translate from PowerShell

Requirements: Windows PowerShell or PowerShell 7, and Python 3.10 or newer installed. No API key, paid service, online model, or package installation is required.

Open PowerShell in the cloned repository folder, then run:

```powershell
# Num’ta’reen → English (attested full sentence)
py -3 -m numtareen --direction nt-en --text "Nûm ta=en ech."

# English → Num’ta’reen (attested full sentence)
py -3 -m numtareen --direction en-nt --text "Stop. Do not proceed."

# Interactive mode: enter phrases and switch directions without restarting
py -3 -m numtareen --direction en-nt --interactive
```

If `py` is unavailable, use `python` instead. The convenience PowerShell wrapper in `scripts/` is an alternative once you've cloned the repository.

```powershell
# PowerShell 5.1 or PowerShell 7, from the cloned repository root
.\scripts\Translate-Numtareen.ps1 -Direction nt-en -Text 'Nûm ta=en ech.'
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Text 'Stop. Do not proceed.'
.\scripts\Translate-Numtareen.ps1 -Interactive
```

Interactive commands: `:direction nt-en`, `:direction en-nt`, `:unknown mark|keep|error`, `:help`, `:quit`. Python also supports `--json` for structured, provenance-preserving results. The PowerShell wrapper sends one-shot text using an exact UTF-8 transport to preserve quotes, Unicode, and punctuation on Windows PowerShell 5.1.

### Explore English phrases in the dictionary (experimental)

For an English sentence that is not in the authored corpus, inspect **all overlapping** dictionary phrases without inventing a Num’ta’reen sentence:

```powershell
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -GlossSpans -Text 'I noticed witnessed alignment yesterday'
# Equivalent Python entrypoint; returns structured JSON
py -3 -m numtareen --direction en-nt --gloss-spans --text 'I noticed witnessed alignment yesterday'
```

The JSON identifies matched source-dictionary candidates and uncovered words; even complete lexical coverage is **not** evidence of a grammatical translation. This is distinct from ordinary bidirectional lookup. See [the gloss-span research contract](docs/ENGLISH_GLOSS_SPAN_EXPLORER_V0.md). `--interactive --json` is explicitly rejected because interactive prompts are not a machine-readable JSON protocol.

### Search the dictionary (not translation)

Search the existing 500 author-provided entries without asking the translator
to invent a sentence meaning:

```powershell
# Exact English gloss → original headword and dictionary source line
py -3 -m numtareen --lexicon-search "patient role" --match exact --json

# Literal substring search with original classification labels preserved
py -3 -m numtareen --lexicon-search "role" --field gloss --category CLITIC --limit 10

# PowerShell 5.1-safe, exact UTF-8 query transport
$queryB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("nûm"))
py -3 -m numtareen --lexicon-search-base64 $queryB64 --field headword --match exact
```

Options: `--match exact|contains`, `--field headword|gloss|both`, optional
`--category`, `--register`, `--taboo` (literal classification filters), and
`--limit` from 1 to 100. Results include IPA, register/taboo, source line,
total match count, and truncation status. `source_line` points into the amended
`sources/dictionary_v2_updated_lphoneme.txt`, not the normalized
`data/lexicon.json`; machine-readable results name both files separately.
The default is a 25-entry limit with
exact matches ranked first; missing terms return zero matches. This is an
offline **author-lexicon reference** only: dictionary glosses are not fluent
English translations or learned grounding, and true-name chord notation
remains untranslated.

### What kind of translation is this?

- **Attested sentence:** an exact match from the 30 annotated utterances is returned with the source free translation.
- **Lexical gloss:** a recognized individual word or defined expression can be glossed approximately; this does *not* guarantee a grammatically fluent sentence.
- **Ambiguous English input:** the tool reports choices instead of silently selecting an invented one-to-one inverse.
- **Unknown or restricted material:** unknown words are marked (configurable); ritual, taboo, and contact-register forms remain labeled and cannot silently become ordinary speech.

The system deliberately does **not** invent canonical words or translate true-name chord notation into pronounceable names. Accent marks and glottal stops matter: `nûm` and `num` are not interchangeable.

### Source-attested pronunciation lookup (experimental teaching aid)

For an existing **whole corpus utterance** or an individual dictionary headword, retrieve the author-supplied IPA and provenance. It does not create pronunciations for new sentences or assign acoustic frequencies:

```powershell
py -3 -m numtareen.phonetic_bridge --repo-root . "Nûm ta=en ech."
py -3 -m numtareen.phonetic_bridge --repo-root . "veyl"
```

For a readable IPA string instead of JSON's portable Unicode escapes, use PowerShell's JSON parser:

```powershell
(py -3 -m numtareen.phonetic_bridge --repo-root . "Nûm ta=en ech." | ConvertFrom-Json).ipa
```

The input source snapshot is content-pinned to the current Wreckforge extracts; altered or spoofed files are refused. The E26 true-name notation is withheld from phonetic rendering. See the [noncanonical phonetic bridge proposal](proposals/PHONETIC_BRIDGE_V0.md) for its explicit source discrepancies and human-teaching boundaries.

On Windows, the separate [PowerShell pronunciation guide](docs/POWERSHELL_TEACHING_UX_V1.md) offers readable, source-labeled results without manually decoding JSON. It uses strict Base64 UTF-8 transport to preserve IPA, quotation marks, and non-BMP input across Windows PowerShell 5.1 and PowerShell 7:

```powershell
$pronunciation = .\scripts\Get-NumtareenPronunciation.ps1 -Text 'Nûm ta=en ech.'
$pronunciation.ipa
```

Unattested phrases return `UNKNOWN` without invented phonetics. The two Windows shell variants have independent regression gates.

## Repository contents

| Path | Purpose |
| --- | --- |
| `sources/` | Text extractions of all five provided Word documents, plus source precedence and original file hashes |
| `data/lexicon.json` | 500 canonical dictionary entries with IPA, category, register, taboo, and line-level provenance |
| `data/corpus.json` | 30 source-attested bilingual utterances with IPA, interlinear glosses and field notes |
| `numtareen/` | Python standard-library-only translator and terminal interface |
| `scripts/` | PowerShell launcher |
| `docs/LANGUAGE_OVERVIEW.md` | Grammar summary, linguistic constraints and examples |
| `docs/LANGUAGE_EVIDENCE_AND_CONTRADICTIONS_20261026.md` | Evidence audit and unresolved phonological, syntactic, and semantic source conflicts |
| `docs/SOURCE_PARSE_REPORT.md` | Source extraction checks and unresolved internal inconsistencies |
| `proposals/` | Proposed extensions for Patrick’s editorial approval; **not** canon by default |
| `tests/` | Offline source, translation and safety regressions |

## Growing the language

The supplied dictionary is substantial but does not fully define everyday communication. Additions therefore use a visible two-stage workflow:

1. **Proposal** — identify an unmet semantic domain, describe native state/resonance distinctions, propose forms and example usages, and check against the existing dictionary and phonology.
2. **Canonization** — Patrick reviews/changes/accepts proposals. Only explicitly accepted entries move into canonical datasets. Proposed meanings remain excluded from default translation.

The [30-slot everyday communication coverage proposal](proposals/EVERYDAY_SEMANTIC_COVERAGE_V1.md) distinguishes attested utterances, dictionary-only vocabulary, and missing structures. The [source contradiction audit](docs/LANGUAGE_EVIDENCE_AND_CONTRADICTIONS_20261026.md) documents unresolved phoneme inventory, phonotactic, relativizer, restorative/concessive, and echo-operator questions. Neither file is canon; author review and contrastive examples are still required. We do not overwrite or silently reinterpret the supplied documents.

The [phonological contrast audit](docs/PHONOLOGY_CONTRAST_AND_ELICITATION_V1.md) adds an executable source-pinned 500-entry census and three controlled author experiments. It flags inventory/coda transcription mismatches for investigation, **not** as automatically invalid words. Reproduce with `py -3 -m unittest discover -s tests -p test_phonotactics_census.py -v` or `py -3 -m research.phonotactics_census`; no pronunciation table or dictionary entry is altered.

The [held-out morpheme research](docs/HELDOUT_MORPHEME_GENERALIZATION_V0.md) measures how far author-annotated IGT labels transfer to unseen combinations when 27 eligible corpus examples are held out one at a time. Initial exploratory measurements recover 112/127 morphemes (2 wrong, 13 abstained), compared with 97/127 for whole-token memorization. This is **not** English sentence generation, a fluent translator, or native acoustic decoding; source attestation and caller-supplied data must remain separate evidence grades. Reproduce with `py -3 -m research.heldout_morpheme_probe --repo-root .` after its independent research qualification.

The [four-cell marker-presence study](docs/FACTORIAL_MARKER_COMPOSITION_V0.md) tests a **single retrospective authored paradigm**: E01/E08/E15 supply a base clause and separately observed `qir`/`hë?` markers; without using E22 as training text, their written forms compose to its attested surface string. Whole-sentence memorization abstains and one-token-copy gets it wrong. This is not a blind productivity result or proof that question and recurrence have commutative semantic scope. Run `py -3 -m unittest discover -s tests -p test_factorial_scope_probe.py -v`; [creator elicitation targets](docs/FACTORIAL_ELICITATION_PLAN_V0.md) identify the missing cross-lexical evidence.

For the mathematical layer, [`proposals/RESONANCE_PACKET_MATH_V0.md`](proposals/RESONANCE_PACKET_MATH_V0.md) describes a **noncanonical synthetic structural codec**. It distinguishes 3,072 assigned feature combinations and passes bounded waveform round trips, but its frequencies are arbitrary; it does not decode native Ech’ta’reen signals, authenticate adversarial audio, or establish semantic grounding. Run `py -3 -m unittest discover -s tests -p test_experimental_resonance_packet.py -v` to test it.

The separate [semantic composition proposal](proposals/SEMANTIC_COMPOSITION_V4.md) analyzes **source-verified author interlinear glosses** into tentative, typed roles, evidentiality, consent loci and partial scope trees. Its `research/semantic_ir_proposal.py` implementation abstains on conflicting sources, unlicensed operator stacks, and protected notation; it rejects spoofed string subclasses at its public parsing boundaries. It does not parse novel Num’ta’reen text or prove productive language; test it with `py -3 -m unittest discover -s tests -p test_semantic_ir_proposal.py -v`.

The [semantic/acoustic alignment falsification audit](docs/SEMANTIC_ACOUSTIC_ALIGNMENT_AUDIT.md) quantifies what the original 3,072-state synthetic packet **loses**: 27 accepted authored source observations project to only 16 packet values, including collisions in predicate identity, question, focus, and consent scope. The `research/alignment_projection.py` reference projection is explicitly lossy and refuses any lossless-qualification claim. Run `py -3 -m unittest discover -s tests -p test_alignment_projection.py -v`; `py -3 -m research.census_alignment` reproduces the counts. This is a negative control, not canonical native encoding.

The [typed semantic observation channel](proposals/TYPED_SEMANTIC_CHANNEL_V1.md) addresses that measured loss at the **symbolic research layer**: it preserves all 27 eligible source-observed predicate, ordered role, focus/question and distinct consent arrangements in reversible framed records, verifies provenance on every public decoded-object export, and abstains on unknown/conflicted/protected inputs. Run `py -3 -m unittest discover -s tests -p test_typed_channel.py -v`. It does **not** teach the translator new sentences, establish native frequency assignments, or prove the language's mathematical semantics.

## Development

### Governed Universal Translator reference bridge

The opt-in `python -m numtareen.interop` command accepts UTF-8 JSONL requests
and returns source-bound reference records for the public UNVTRSLR validator.
For example, submit `{"direction":"nt-en","text":"Nûm ta=en ech."}` as one
line on stdin. The result is **author-provided reference evidence**, not a
learned semantic association; it is always ineligible for grounding
qualification and withheld true-name chord material is never synthesized.

The source texts and corpus are visible in this public repository. See
[`docs/UNVTRSLR_INTEROP_V1.md`](docs/UNVTRSLR_INTEROP_V1.md) for the JSONL
protocol, provenance boundaries, and PowerShell encoding requirements. The
[`historical integration design guide`](docs/UNVTRSLR_INTEROP_GUIDE.md) records
the original proposal; it is not the implemented protocol. The test matrix pins the
public validator to an exact commit for cross-repository verification.

```powershell
py -3 -m unittest discover -s tests -v
```

The tool needs only local, checked-in JSON. The CI workflow runs the test suite on Windows and Linux. No production service, host agent, or external database is required.

The current implementation performs source-attested sentence lookup and approximate lexicon lookup, **not unrestricted compositional or native-resonance translation**. See `proposals/RESONANCE_AND_EVERYDAY_COVERAGE_V0.md` for a noncanonical research direction and `docs/DISPATCH3_ENGINEERING_REPORT.md` for this iteration's execution evidence and remaining platform checks.

## Provenance and rights

The language reference originates with the supplied *Wreckforge Chronicles* documents, not machine inference. See [`sources/SOURCES.md`](sources/SOURCES.md) for document identities, hashes, and amendment priority. Public GitHub visibility does not imply open-source licensing of the worldbuilding, underlying creative material, or larger manuscript.
