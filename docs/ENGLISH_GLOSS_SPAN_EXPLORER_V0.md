# English gloss-span exploration (V0, experimental)

This supplements the strict source-attested sentence lookup. Dictionary
glosses are often multiword (`ech’nûm` is glossed `witnessed alignment.`),
so a whitespace-only English fallback can miss an existing lexical entry
inside a longer English utterance. V0 reports **all** overlapping source
dictionary spans at deterministic zero-based, half-open token offsets.

It does **not** infer word order, align sentence roles, select a segmentation,
assert consent, synthesize Num’ta’reen text, or qualify machine translation.
The `spans[].candidates` entries preserve source dictionary line/category/
register/taboo provenance. `uncovered` lists every token with no matching
dictionary span. `overlapping_span_pairs` explicitly represents competing
source gloss spans without declaring one correct.

The output describes **loaded dictionary candidates**, not an independent
attestation check. With the default checked-in lexicon they retain the
authored dictionary metadata; when a caller constructs `Translator` with a
custom dataset, `source_line` and other metadata are assertions of that
dataset, not proof of author provenance. Exact source integrity must be
established separately before an entry can be described as source-attested.

## PowerShell

```powershell
.\scripts\Translate-Numtareen.ps1 -Direction en-nt -Text 'I noticed witnessed alignment yesterday' -GlossSpans
```

The JSON response is intended for investigation, not fluent translation.
The existing `-Text` mode, default direction, and attested phrase results
remain unchanged. Python 3.10+ and the complete checked-in repository are
required. PowerShell 5.1 and 7 UTF-8/Base64 handling follows the existing
wrapper; live PowerShell host qualification remains outstanding.

## Direct Python

```shell
python -m numtareen --direction en-nt --text 'a shared state' --gloss-spans
```

Inputs are bounded at 4096 characters and 32 whitespace tokens. A source
dictionary with more than 512 matching spans fails explicitly, without
partial output masquerading as complete. Full authored sentence alignment
should still use the original default exact-corpus `translate` operation.

## Adversarial considerations

- Competing glosses with overlapping spans remain simultaneous possibilities.
- A phrase spanning punctuation is matched only when the normalized source
  dictionary index has that exact spelling; missing punctuation is not used
  to invent a gloss.
- Prosody, grammatical scope and speaker consent cannot be established from
  English gloss spans. Source `CONS` affix semantics must come from authored
  grammar/corpus, not from lexical English paraphrase.
- Complete token coverage **does not** mean a grammatical translation exists.
- The JSON/CLI escapes Unicode control characters; the PowerShell executable
  path is resolved using the existing Python 3.10+ probe.

Event: `linguistics_live_coordination`. Independent hostile v147 rejected the
first input/provenance implementation; v152 corrected both defects and fresh
v156/v161 reviews passed the source-bounded implementation. This remains a
research-only dictionary explorer; exact-head Windows PowerShell 5.1/7 CI
qualification is required before release.
