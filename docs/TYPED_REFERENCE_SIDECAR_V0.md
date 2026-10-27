# Num’ta’reen ⇄ Universal Translator: typed reference sidecar V0

**Status:** opt-in research proposal; `SOURCE_BOUND_NONCANONICAL`. This is
not a Num’ta’reen grammar ratification, a learned semantic claim, or a
Universal Translator qualification path.

## Verified sources and compatibility

- Num’ta’reen authored corpus inspected with Git blob pin
  `53d9f27d03579a1a3fc700c3394b56f834da784e`; the implementation
  is additive and independent of the current main commit.
- Universal Translator (`thebrazenbeard/unvtrslr`) main inspected at
  `d113df8b72385300c570ccb9d1c8a36f20ddb738`.
- The existing `unvtrslr-reference-evidence-v1` parser accepts a strict
  author-reference schema with `semantic_atoms: null`. This research sidecar
  does **not** change that schema, production APIs, or parser/training code.
- Num’ta’reen's source attestation expects the Git blob SHA-1
  `53d9f27d03579a1a3fc700c3394b56f834da784e` for the author corpus.
  This is a reproducibility checksum, **not** a cryptographic signature of
  author identity or a claim of independent evidence.

## Frame/envelope contract

`research.typed_reference_bridge_v0.build_sidecar("E01", repo_root=...)`
first requires
the source-verified author row and asks two existing Num’ta’reen adapters for:

1. A real V1 author-reference record, with the exact attested orthography and
   corresponding English rendering, parsed by Universal Translator's actual
   V1 implementation.
2. A typed semantic research frame from the corpus-ID encoder, then decoded
   against the same pinned source. Its wire format remains the existing
   `NTSP1` magic, big-endian 32-bit payload length, SHA-256 digest, and
   canonical JSON. The checksum guards accidental corruption, not authorship.

Those travel **alongside one another** in canonical UTF-8 JSON:

| Field | Required value / rule |
| --- | --- |
| `schema` | `numtareen-unvtrslr-typed-reference-sidecar-v0` |
| `status` | `SOURCE_BOUND_NONCANONICAL` |
| `origin_repo` | `thebrazenbeard/num-ta-reen` |
| `corpus_id` | Exact source-verified corpus identifier |
| `source_git_blob_sha1` | `53d9f27d03579a1a3fc700c3394b56f834da784e` |
| `reference_evidence_v1` | Unmodified strictly validated V1 reference record |
| `typed_frame_base64` | Canonical base64 of verified typed frame |
| `qualification_eligible`, `learner_visible` | Both `false` |
| `source_independence` | `SINGLE_AUTHOR_REFERENCE` |

The parser strictly checks field names, duplicate JSON members, canonical
serialization, UTF-8, 64 KiB envelope ceiling, base64 integrity, both
existing validators, corpus identifier consistency, and **complete
byte-for-byte regeneration** of the packet from trusted source files. A
valid-looking altered translation, recomputed frame checksum, forged source
identifier, inserted semantic atoms, or stronger independence claim still
fails. No API converts this envelope to training examples.

Of 30 source corpus identifiers, 27 presently qualify for this limited
source-bound research envelope. E13/E23 abstain because their source
interpretations conflict; E26 abstains because its content is protected.
Unsupported/unknown records also abstain; no fabricated lexemes are supplied.

## Local, offline verification against actual checkouts

From a Num’ta’reen repository checkout containing the module and peer test,
with the exact public Universal Translator peer checked out at
`.unvtrslr_current_peer` and installed into Python >=3.11:

```shell
NUMTAREEN_ROOT=. UNVTRSLR_ROOT=.unvtrslr_current_peer \
  python -m unittest discover -s tests \
  -p 'peer_typed_reference_sidecar_v0.py' -v
```

The peer workflow runs this command on Ubuntu and Windows, Python 3.11/3.13.
Its test filename intentionally is not selected by generic `test_*.py`
discovery: standalone Python 3.10 jobs need not install an incompatible
public peer. The module itself defers that dependency until it is invoked,
at which point a missing validator fails closed.

The nine independent V0 tests cover 27/30 source-bound acceptance, hostile
semantic and provenance forgery, V1 strict-schema compatibility, V1 CLI
subprocess acceptance/rejection, packet damage, duplicate members, an
otherwise valid but corrupted V1 translation, deeply nested JSON resource
exhaustion, and honest replay behavior.

To re-run the original Num’ta’reen ↔ Universal Translator V1 tests using the
**real** Universal Translator checkout:

```shell
UNVTRSLR_ROOT=.unvtrslr_current_peer \
  python -m unittest discover -s tests -p test_unvtrslr_interop.py -v
```

## Known limits and decisions before adoption

> A typed frame may provide a well-formed description of what the author
> thinks an utterance means. It does **not** demonstrate that a listener,
> another speaker, or an independently observed signal expresses that meaning.

- This V0 research envelope must remain explicitly opt-in, noncanonical,
  learner-invisible, and ineligible for held-out qualification. Do not upgrade
  its evidence labels based on model agreement.
- Replaying the identical source reference is accepted; the interface makes
  **no freshness or anti-replay guarantee**. Such a replay is still one
  author-supplied reference, never independent corroboration.
- The decoded typed atoms are constrained by the existing author-attested
  corpus; they are not a productive grammar, complete dictionary, or measured
  acoustic frequency/resonance mapping.
- A future governed V1 semantic link requires owner-approved vocabulary and
  grammar, source attribution, a separate empirical evidence lane, negative
  controls, and explicit learning/qualification authorization. Do not silently
  let downstream applications interpret these sidecars as observations.
- The sidecar module does not change production APIs, train models, write to
  GitHub, or modify either repository's source data when invoked.
