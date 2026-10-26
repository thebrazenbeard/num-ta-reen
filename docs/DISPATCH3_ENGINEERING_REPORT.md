# BT2 third native dispatch: Nûm’ta’reen offline translator

**Date:** 2026-10-26. **Baseline `main` commit:** `35ff3adf3e9ff6dc91b92cec2b29f6c7919a1bed`.

## Dispatch record

Seven native child agents were requested. The runtime offered seven total slots including the lead, so six real children were successfully spawned and observed concurrently in the native roster. The lead took the seventh specialty (language expansion/UX). Exact native worker receipts:

| Worker | Assignment | Outcome |
| --- | --- | --- |
| `/root/linguistics` | Source precedence and linguistic architecture | Independent read-only audit; contradictions left unresolved in canon |
| `/root/translation` | Python offline translation engine | Implemented corpus and lexicon lookups with uncertainty; focused tests |
| `/root/powershell` | Windows entrypoint | Implemented UTF-8 Base64 transport and interactive invocation |
| `/root/corpus` | Lexicon/corpus provenance | Five new data-lineage regressions, no canon changes |
| `/root/security` | Hostile review | Reproduced and retested regex DoS and terminal-control escapes |
| `/root/verification` | CI and independent contract tests | Black-box CLI tests and expanded Windows/Linux workflows |

The dispatch experiment confirms *six native child workers plus a lead*, not seven children; no roleplaying or simulated agents were counted. Worker reports themselves are review evidence, not substitutes for integration tests.

## Source and canon boundary

The amended `UPDATED_lphoneme` reference grammar and dictionary take precedence. The checked-in lexicon retains 500 entries and 30 source-attested utterances. Source identifiers and text-line provenance were checked against repository exports; original OneDrive DOCX hashes were **not** independently reauthenticated. The supplied `Num'ta'reen.zip` contains the end of a saved ChatGPT HTML conversation with a design discussion, not the original five Word documents. Its ideas inform `proposals/` only.

Linguistic ambiguities intentionally left for authorial review include an incomplete compact phoneme/coda inventory, the E24 `keth` IPA disagreement, and the derived E01–E30 source-order labels. No speculative forms, frequencies, or grammatical repairs were introduced into canonical data.

## Behavior and verification

Implementation supports offline `python -m numtareen` lookup in both directions, full-source-utterance priority, nonfluent lexical glosses, ambiguity, unknown policies, source/register/taboo indicators, and interactive direction switching. The PowerShell wrapper uses UTF-8 Base64 to preserve Windows PowerShell 5.1 argument text. E26 true-name chord notation remains unspoken with an explicit warning.

Integration commands on Linux/Python 3.12:

```text
python3 -m unittest discover -s tests -q
Ran 38 tests — OK (exit 0; current integrated suite)

python3 -m numtareen --direction nt-en --text 'Nûm ta=en ech.'
source-attested E01 → You are aligned (I witness it).

python3 -m numtareen --direction en-nt --text 'Stop. Do not proceed.'
source-attested E17 → Ta’qesh.

python3 -m numtareen --direction nt-en --text 'Nûm veyl'
approximate lexical gloss only (not a fluent or attested sentence)
```

Independent hostile probing reproduced an exponential-time slash-gloss regex and terminal control/bidi output injection in earlier drafts. The final engine bounded slash matching and visibly escapes terminal controls; adversarial regressions are included.

**CI corrective iteration:** Initial GitHub Actions run `40321596682` exposed two genuine portability gaps: a Windows redirected `cp1252` stdout `UnicodeEncodeError` on IPA/symbols, and a PowerShell syntax error from typographic apostrophes inside single-quoted CI script literals. The CLI now explicitly configures UTF-8 output and has a legacy-code-page regression test; the workflow now constructs the curly apostrophe with `[char]0x2019` and uses ASCII-only diagnostic literals. These corrections require a fresh Windows/Linux CI run on their exact published commit.

Follow-up run `40322144943` passed all Ubuntu jobs and Windows Python/PowerShell 7 steps, but uncovered a Windows PowerShell 5.1 native-argument quoting defect in the Python interpreter probe (`py -3 -c ...`). The launcher now uses a quote-free `--version` probe and parses Python's major/minor version, with guarded fallback. The Windows 5.1 CI test also checks that an embedded double quote and a non-BMP character survive the Base64 transport. This change requires a third, exact-head CI readback before merge.

**Qualification boundaries:** The 38-test result is local Linux behavior. Windows PowerShell 5.1/7 runtime behavior and the *corrected* published branch's GitHub Actions are separate, pending effects until observed. Main integration requires PR review, CI, and an explicit decision; this report does not itself authorize merging.

