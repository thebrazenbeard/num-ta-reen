# Nûm’ta’reen

> Fictional language and state-sharing communication system of the Ech’ta’reen, from *The Wreckforge Chronicles*.

This repository turns Patrick A. Sims’s existing worldbuilding documents into a versioned language reference, a 500-entry digital dictionary, a 30-utterance attested bilingual corpus, and a **PowerShell-friendly, offline Num’ta’reen ⇄ English interface**.

The original OneDrive folder and documents remain untouched. The repository is private and contains text extracts, searchable data, and code—not the manuscript. The two `UPDATED_lphoneme` sources take precedence over older drafts.

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

## Repository contents

| Path | Purpose |
| --- | --- |
| `sources/` | Text extractions of all five provided Word documents, plus source precedence and original file hashes |
| `data/lexicon.json` | 500 canonical dictionary entries with IPA, category, register, taboo, and line-level provenance |
| `data/corpus.json` | 30 source-attested bilingual utterances with IPA, interlinear glosses and field notes |
| `numtareen/` | Python standard-library-only translator and terminal interface |
| `scripts/` | PowerShell launcher |
| `docs/LANGUAGE_OVERVIEW.md` | Grammar summary, linguistic constraints and examples |
| `docs/SOURCE_PARSE_REPORT.md` | Source extraction checks and unresolved internal inconsistencies |
| `proposals/` | Proposed extensions for Patrick’s editorial approval; **not** canon by default |
| `tests/` | Offline source, translation and safety regressions |

## Growing the language

The supplied dictionary is substantial but does not fully define everyday communication. Additions therefore use a visible two-stage workflow:

1. **Proposal** — identify an unmet semantic domain, describe native state/resonance distinctions, propose forms and example usages, and check against the existing dictionary and phonology.
2. **Canonization** — Patrick reviews/changes/accepts proposals. Only explicitly accepted entries move into canonical datasets. Proposed meanings remain excluded from default translation.

See `proposals/` for the first extension tranche and the open linguistic design questions. We do not overwrite or silently reinterpret the supplied documents.

## Development

### Governed Universal Translator reference bridge

The opt-in `python -m numtareen.interop` command accepts UTF-8 JSONL requests
and returns source-bound reference records for the public UNVTRSLR validator.
For example, submit `{"direction":"nt-en","text":"Nûm ta=en ech."}` as one
line on stdin. The result is **author-provided reference evidence**, not a
learned semantic association; it is always ineligible for grounding
qualification and withheld true-name chord material is never synthesized.

The source texts and corpus stay private. See
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

The language reference originates with the supplied *Wreckforge Chronicles* documents, not machine inference. See [`sources/SOURCES.md`](sources/SOURCES.md) for document identities, hashes, and amendment priority. This is a private working copy of original creative material; no open-source licensing of the worldbuilding or larger manuscript is implied.
