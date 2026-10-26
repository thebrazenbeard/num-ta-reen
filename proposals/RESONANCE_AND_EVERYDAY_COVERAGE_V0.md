# Proposed work: resonance encoding and everyday communication

**Status:** proposal / noncanonical. **Owner approval required before any rule, form, or meaning is added to the lexicon or corpus.** This file contains research questions and engineering design suggestions, not attested Nûm’ta’reen expressions.

## Context and authorial intent

A saved ChatGPT conversation page, titled *Dispatch and security audit* and packaged as `Num'ta'reen.zip`, records Patrick's stated interest in variable resonance/frequency patterns and an algorithmic or mathematical route from Ech’ta’reen communication to English semantics. The page also contains an assistant's hypotheses about harmonic relations, phase, interference, semantic intermediate representations, and possibly interactive co-created states. **Patrick's stated interest is design direction; the assistant's hypotheses are not canon or evidence that a specific native encoding already exists.** The saved page shows only its visible end-of-chat segment and is not treated as a complete structured transcript.

## Existing constraints to respect

The current amended grammar and dictionary describe Ech’ta’reen communication as multimodal resonance-based **state-sharing**. The written orthography is a field transliteration, not a lossless representation. The attested grammar distinguishes role/consent clitics and echo-status/evidential operators; ritual, contact, and true-name material carry restrictions. Any algorithm should preserve those distinctions or disclose exactly what it loses.

## Signal model to investigate (not a canon claim)

Treat a native utterance as a structured temporal state packet with *separate, typed channels*, rather than assigning an arbitrary musical note to each English word:

| Proposed channel | Possible modeled data | Unresolved authorial questions |
| --- | --- | --- |
| State contour | Sequence of state transitions, duration, overlap | What changes count as linguistic contrasts? |
| Resonance | Relative frequency bands, phase, harmonics, modulation | Are values absolute, listener-relative, or contextual? |
| Participant roles | Agent, patient, source, goal, means | Can multiple roles overlap in one packet? |
| Consent | Explicit permission state and scope | How is withdrawal represented during an ongoing event? |
| Echo/evidence | Witnessed, verified, looped, returned, collapsed | Which combinations are grammatical? |
| Register | Formal, clipped, ritual, contact | Are some channels unavailable in certain registers? |

No frequency in hertz, waveform, algorithmic encoding, or invented morpheme is stipulated here. These require Patrick's authorial choice and checks against the amended source documents.

## Translation architecture proposal

1. **Attested text ⇄ English:** exact Nûm’ta’reen corpus matches return their recorded free translations and provenance. Reverse English lookup may return multiple attested choices or none; it must never silently select an ambiguous inverse.
2. **Lexical lookup:** dictionary matches return glosses, class, register/taboo labels, and ambiguity—not fabricated fluent output.
3. **Future structured representation:** if the author specifies the native signal, add a versioned, typed intermediate representation. Include source provenance, evidential status, and a lossiness report when converting into either written language.
4. **Future renderer:** only produce sound or frequency-based output after the encoding is canonically specified and tested. Do not render or pronounce true-name chord notation in the ordinary CLI; any exceptional mechanism requires a separate explicit authorial canon and safety rule.

A round-trip test should compare *semantic constraints* and report information lost; `English → packet → English` is not expected to reproduce exact wording. Test cases must explicitly distinguish `nûm` from `num`, direct witness (`ech`) from cross-echo verification (`reen`), each participant role including the source/origin role (`=ru`), and consent-present from consent-absent utterances.

## Everyday-language gap assessment (candidate categories)

Before proposing words, use the current 500-entry lexicon and 30 utterances to score whether these functions are directly expressible, compositional but unattested, ambiguous, or absent:

- introductions and participant identity without true-name revelation;
- basic requests, refusal, consent, withdrawal, and repair of misunderstanding;
- time ordering without importing ordinary past/future tense;
- place, direction, distance, and navigation;
- quantities and measurement, including whether numeric magnitudes fit resonance constraints;
- care, injury, urgency, reassurance, and safety signals;
- social coordination and truthful reporting of uncertainty.

Record each gap with a stable identifier, the attempted communicative intent, all candidate attested entries, and the missing semantic distinction. No invented examples belong in the attested corpus. Prioritize high-frequency communication acts and explicit consent over untested vocabulary volume.

## Learner-interface proposal

For future CLI work, keep **attested**, **lexical gloss**, **ambiguous**, and **unknown** visibly distinct. A learning mode could display IPA, register/taboo notes, provenance, a constrained practice prompt, and the exact reason a translation is approximate. Examples used for quizzes should be drawn from the attested 30-utterance corpus until new examples are approved.

## Decision gates

1. Patrick selects whether resonance is physically acoustic, field-mediated, perceptual, or a hybrid in the fictional setting.
2. Patrick defines the minimum native state packet and its meaningful channel contrasts.
3. A test corpus of *author-approved* packets is created, including collisions and ambiguous readings.
4. Only then should a reversible encoder/decoder or synthesizer be proposed for canonical use.

## External implementation references (not linguistic authorities)

- [Unicode Standard Annex #15](https://www.unicode.org/reports/tr15/) documents canonical Unicode normalization; a text pipeline can use NFC while still preserving meaning-bearing diacritics.
- [Leipzig Glossing Rules](https://www.eva.mpg.de/lingua/resources/glossing-rules.php) offer established alignment notation for learner-facing interlinear displays.
- [W3C SSML 1.1](https://www.w3.org/TR/speech-synthesis/) describes pitch and timing controls for ordinary speech synthesis; it is only an engineering comparison, **not** a representation of Ech’ta’reen native resonance.

