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

```powershell
py -3 -m unittest discover -s tests -v
```

The tool needs only local, checked-in JSON. The CI workflow runs the test suite on Windows and Linux. No production service, host agent, or external database is required.

## Provenance and rights

The language reference originates with the supplied *Wreckforge Chronicles* documents, not machine inference. See [`sources/SOURCES.md`](sources/SOURCES.md) for document identities, hashes, and amendment priority. This is a private working copy of original creative material; no open-source licensing of the worldbuilding or larger manuscript is implied.
