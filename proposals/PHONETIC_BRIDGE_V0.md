# Human phonetic bridge — experimental proposal v0

**Status:** NONCANONICAL teaching/interface proposal. Nothing in this folder
amends a Wreckforge word, meaning, pronunciation, or Ech’ta’reen physiology.
**Reviewed source subject:** `thebrazenbeard/num-ta-reen@ed9a94d53d17db6415de172858773714644e01ba`.

## What the author material actually establishes

The amended `sources/reference_grammar_v2_updated_lphoneme.txt` takes source
priority over the original according to `sources/SOURCES.md:17`.

| Topic | Author-supplied rule | Exact amended-grammar line(s) |
|---|---|---|
| Human transliteration versus native signal | Transliteration is an analytic phonemic layer, not the physical Ech’ta’reen signal. | 18–23 |
| Lateral consonant | `/l/` is a phoneme; `[ɫ]` is an attested low-frequency formal allophone. | 25–26 |
| Laryngeal interruption | Orthographic apostrophe `’` represents phonemic `/ʔ/`, potentially creaky `/ʔ̞/` in rapid field speech. | 11, 28, 32 |
| Restricted consonant | `/q/` is associated with ritual/taboo registers. | 27 |
| Other allophones | `[ɾ]` and `[r]` vary with register/emphasis; `/x/` may surface `[χ]`. | 33–34 |
| Phonemic length | Long vowels contrast with short vowels; length may contribute coherence/scope. | 35, 61–63 |
| Syllables | `(C)(C)V(ː)(C)`, with listed formal clusters `/ʃr, xr, kw, sw/` and codas `/n ŋ k t ʃ x/`. | 36–41 |
| Stress | Default initial, unless vowel length attracts stress. | 47–50 |
| Timing hypotheses in the fictional field grammar | Long nuclei, compressed interword timing, or doubled interruptions may signal scope/status/caution. | 51–55 |

These are **author-source attestations**, not physical measurements of a
real-world speaker, and therefore are not independent scientific validation.

### Critical extraction limitation

In the repository's current *plain-text extraction*, the headings `Consonants`
and `Vowels` appear near lines 25–30, while their flattened table contents
appear out of sequence at lines 517–550. The original source DOCX needs a
layout-aware reading to confirm table alignment. Even this amended table
omits segments found in the amended dictionary (for example `/v/`, `/θ/`,
`/t͡ʃ/`). That contradiction requires author review; do **not** reconstruct
an inventory by guessing which published IPA entries are wrong.

## Minimal teaching format

Teach a source-matched example as three distinct columns:

1. **Printed human approximation** — source orthography; `=` marks a clitic
   boundary, not a spoken character.
2. **Sourced IPA** — either a complete attested corpus transcription or an
   *isolated dictionary* entry. Never concatenate dictionary IPAs to invent
   an utterance IPA. For E01, `Nûm ta=en ech.` has the complete attested
   `/ˈnuːm tɑʔˈɛn ɛt͡ʃ/` (amended grammar lines 162–163).
3. **Resonance/channel description** — explicit `unassigned`, until acoustic
   parameters and semantic mappings have separate justification. No guessed
   fundamental frequency, harmony, phase, or timing constant is represented
   as canon.

The opt-in `numtareen/phonetic_bridge.py` implements exactly this source lookup.
It returns `ATTESTED_UTTERANCE`, `ATTESTED_LEXEME`, `UNKNOWN`, or `WITHHELD`,
with pronunciation, source locator, Unicode-safe lookup and cautious feature
flags. It does not transcribe new words or synthesize audio.

## Three source-grounded drills

- **Length:** `nûm /nuːm/` versus `num /num/` (amended grammar 61–63).
  Both are distinct; ASCII accent stripping would erase a phonemic contrast.
- **Laryngeal boundary:** corpus E01 `ta=en` is transcribed `/tɑʔˈɛn/`,
  whereas isolated dictionary `=en` has `/ɛn/` (amended dictionary line 20).
  That is why a dictionary IPA lookup is not a connected-speech generator.
- **Lateral:** dictionary `veyl /vejl/` (amended dictionary line 51) contains
  `/l/`; current amended grammar line 26 accepts it. Original-only inventory
  restrictions are superseded.

## Blocking source disagreement

Corpus E13 (`Veyl sekh së nûm reen.`) carries IPA
`/ˈvejl sɛx sɛn ˈnuːm riːn/` (amended grammar lines 250–251), even though
the written token `së` and dictionary source analyze a separate `sën`.
The guide flags the conflict instead of choosing an IPA correction.

Protected E26 is unspoken chord notation rather than a pronounceable utterance.
The guide never emits its symbolic numeric values or asserts a spoken IPA.
The original field text is already present in the public author-source
repository; this interface's withholding is a speech-output policy, **not**
a confidentiality guarantee or a retroactive redaction of the original.

## Proposed experimental bridge (not author canon)

Represent every training prompt as:

```json
{
  "human_orthography": "Nûm ta=en ech.",
  "attested_human_ipa": "/ˈnuːm tɑʔˈɛn ɛt͡ʃ/",
  "resonance_descriptor": null,
  "resonance_frequency_hz": null,
  "semantic_scope_encoding": null,
  "evidence": "AUTHOR_ATTESTED_CORPUS:E01"
}
```

Future math/acoustic experiments can populate a **different**, versioned
`EXPERIMENTAL_RESONANCE` layer. Only after randomized blind discrimination,
noise/channel tests, inversion tests, controlled semantic-feature recovery,
and author review could a rule be considered for canon.

## Falsifiers and open decisions

1. Recover and inspect the original amended DOCX table cells; determine
   whether the missing phoneme inventory is extraction loss.
2. Collate all attested IPA/orthography alignments; flag exceptions rather
   than forcing character-to-IPA mappings (`së`/`sën` is already one).
3. Decide whether register-specific syllable timing is measurable or merely
   fictional analytical notation. No physical microphone records exist here.
4. Test human intelligibility of length versus short-vowel pairs before
   prescribing durations. Neither milliseconds nor Hertz thresholds are
   supplied by the source.
5. Confirm with Patrick whether human speech is meant to be imperfect
   *translation* of higher-dimensional resonance; the existing source
   suggests this but does not determine the math.

### Execution

From an ordinary repository checkout after this experimental module and its
test are integrated:

```bash
python -m unittest discover -s tests -p 'test_phonetic_bridge.py' -v
python -m numtareen.phonetic_bridge --repo-root . 'Nûm ta=en ech.'
```

The bridge verifies exact SHA-256 source fingerprints before returning any
`AUTHOR_ATTESTED_*` label: both checked-in normalized JSON files and the two
amended source extracts. Otherwise it fails closed, including for a forged
same-length corpus. The JSON files are pinned to LF by `.gitattributes`; the
source TXT hashes normalize only Git's possible CRLF checkout conversion.
After a legitimate author revision, reviewers must advance these pins and
tests in a new proposal version, not silently accept arbitrary source roots.

