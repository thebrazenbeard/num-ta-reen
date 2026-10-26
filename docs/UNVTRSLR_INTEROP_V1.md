# UNVTRSLR ↔ Nûm’ta’reen reference bridge (v1)

This private repository exposes its already attested material to UNVTRSLR as
**operator-supplied reference evidence**. It does not confer learned semantics,
signal discovery, independent-source corroboration, or R1/R2 qualification.

## Boundary and source binding

- `numtareen.interop` has no network, SDK, model, or external service dependency.
- `data/corpus.json` and `data/lexicon.json` are checked against pinned SHA-256
  digests; the direct Python API also checks the in-memory translator against
  fresh data loaded from those files. The provenance `origin.commit` identifies
  the canonical data baseline `cdfbea09cc8b4a1648cde733953986c7d694d496`,
  **not** the current implementation commit or a newly authenticated DOCX file.
- Every record uses `origin.source_group: single-author-wreckforge` and
  `source_independence: SINGLE_AUTHOR_REFERENCE`. Repeated utterances do not
  count as independent experimental sources.
- `qualification_eligible` and `learner_visible` are always false, and
  `semantic_atoms` is always null. The English free translations remain author
  reference text, not discovered learner ontology or semantics.
- The true-name chord represented in corpus E26 is withheld (`withheld:true`,
  null source/target text) when exposed through this bridge. Ordinary lexical
  ambiguity, unknown tokens, register, taboo and line-level provenance are
  retained rather than promoted to fluent target utterances.
- **Do not commit or publish** exported Num’ta’reen utterances, lexicon entries,
  original document metadata or derived test fixtures to public UNVTRSLR.
  UNVTRSLR's public parser tests must use unrelated synthetic strings.

## Process contract

From the private repository root on Linux, macOS, or a UTF-8 Windows host:

```sh
python -m numtareen.interop
```

Send one UTF-8 JSON request per line on stdin, with a maximum of 65,536 bytes
per line (excluding CR/LF). The process returns one JSON object per line,
without banners or logging on stdout.

```json
{"request_id":"r1","direction":"nt-en","text":"Nûm ta=en ech.","unknown":"mark"}
```

For callers with unreliable Unicode JSON serialization (especially Windows
PowerShell 5.1), a request may instead contain the **mutually exclusive**
`text_base64` field. Its value must be standard padded Base64 of strict UTF-8
text, not a lossy code-page conversion. This is an ASCII-only request shape:

```json
{"direction":"nt-en","text_base64":"BASE64_OF_UTF8_TEXT"}
```

`BASE64_OF_UTF8_TEXT` is a placeholder, not a valid encoded utterance.
Exactly one of `text` or `text_base64` is required. The decoded text follows
the same 4,096-character limit; invalid Base64, invalid UTF-8, and excessive
decoded bytes yield `INVALID_TEXT_ENCODING`, without stopping later frames.
This transport changes no meaning, source precedence or qualification grade.

Directions are `nt-en` and `en-nt`; unknown policies are `mark`, `keep` and
`error`, defaulting to `mark`. Unsupported fields, oversized requests, bad
UTF-8, malformed JSON, and invalid options produce a structured error without
halting later requests. Strict unknown policy produces `UNKNOWN_SEGMENT`.

Success is a **transport envelope**:

```text
{"ok":true,"request_id":"r1","record":<reference-evidence-v1 object>}
```

Errors are `{ "ok": false, "request_id": null|string,
"error": { "code": string, "message": string } }`. Consumer validators should
parse `record` with the public `unvtrslr-reference-evidence-v1` schema rather
than treating the transport envelope as a source observation.

The evidence record fields include:

| Field | Meaning |
| --- | --- |
| `schema` | `unvtrslr-reference-evidence-v1` |
| `origin` | private repository, pinned baseline commit, single source group, original document title/hash, corpus ID when uniquely attested |
| `direction` | Requested lookup direction |
| `evidence_class` | `AUTHOR_ATTESTED_CORPUS`, `AUTHOR_LEXICON_GLOSS`, `AUTHOR_PARTIAL_LEXICAL`, or `UNKNOWN` |
| `source_text`, `target_text` | Input and uniquely attested target, or null if protected/inapplicable |
| `alternatives` | Typed, source-labeled lexical candidates or corpus alternatives; not a fluent inferred sentence |
| `register`, `taboo` | Nullable at utterance level; attested lexicon categories retained on individual alternatives |
| `withheld` | True when true-name chord material is suppressed |
| `semantic_atoms`, `qualification_eligible`, `learner_visible` | Always null, false, false respectively |
| `source_independence` | Always `SINGLE_AUTHOR_REFERENCE` |
| `warnings` | Explicit oracle, limitation, ambiguity and withholding labels |

Windows PowerShell 5.1 may recode piped Unicode input under legacy code pages.
For ordinary interactive Windows translation, use the existing
`scripts/Translate-Numtareen.ps1` Base64 transport. For JSONL automation, the
private `tests/Test-NumtareenInterop.ps1` demonstrates building a fixed ASCII
JSON request containing `text_base64` and writing exact ASCII bytes to the
Python process. Avoid implicit PowerShell 5.1 string-pipeline encoding.

## Qualification rule

Using this bridge as a **human-reference renderer or evaluator fixture** is
permitted within the user's private workspace. Injecting these authored pairs
as hidden learner labels, target-grounding episodes, independent `source_id`
trials, or claims of mathematically discovered Num’ta’reen semantics is a
bridge-oracle leakage failure. A later resonance/frequency model needs its own
authorial specification and independent interventions; no frequencies,
waveforms, semantic atoms, or new canonical words are created here.
