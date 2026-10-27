"""Bounded English gloss-span discovery over the loaded dictionary.

No segmentation is selected, no English sentence is converted into a
Num'ta'reen sentence, and overlapping candidates are not silently resolved.
This is a research aid for finding multiword entries *inside* longer English
queries, complementing the strict exact-corpus translator.
"""

from __future__ import annotations

from .engine import Translator, normalize


MAX_QUERY_CHARACTERS = 4096
MAX_QUERY_TOKENS = 32
MAX_CANDIDATE_SPANS = 512
# A closing parenthesis can be a meaningful part of an English dictionary
# gloss such as "home-realm (endonym)." Keep balanced gloss delimiters.
_SENTENCE_EDGES = " \t\r\n.,!?;:\"“”«»…。，！？．；："


def discover_english_gloss_spans(translator: Translator, text: str) -> dict:
    """Report every source-dictionary matching span, preserving overlaps.

    Token indexes are half-open and refer to Unicode-whitespace tokenization
    of the raw English query. Candidates have no compositional grammar claim.
    """
    if not isinstance(text, str):
        raise ValueError("text must be nonempty")
    # Only operate on the actual built-in string value. A caller-controlled
    # str subclass may override split()/strip() and otherwise substitute words
    # that were never present in the reported original input.
    text = str.__str__(text)
    if not text.strip():
        raise ValueError("text must be nonempty")
    if len(text) > MAX_QUERY_CHARACTERS:
        raise ValueError("English query character bound exceeded")
    words = text.split()
    if len(words) > MAX_QUERY_TOKENS:
        raise ValueError("English query token bound exceeded")

    # Translator.glosses is the checked-in lexicon index. Longest possible
    # gloss span comes from source, not from an untrusted user-supplied size.
    max_length = max((len(key.split()) for key in translator.glosses), default=0)
    spans = []
    covered = set()
    for start in range(len(words)):
        for end in range(start + 1, min(len(words), start + max_length) + 1):
            # Trim sentence punctuation but retain source parentheticals:
            # "home-realm (endonym)," must still match the dictionary gloss.
            phrase = " ".join(words[start:end]).strip(_SENTENCE_EDGES)
            candidates = translator.glosses.get(normalize(phrase), ())
            if not candidates:
                continue
            spans.append({
                "start": start,
                "end": end,
                "english_span": phrase,
                "candidates": [dict(item) for item in candidates],
            })
            covered.update(range(start, end))
            if len(spans) > MAX_CANDIDATE_SPANS:
                raise ValueError("English gloss-span candidate bound exceeded")

    return {
        "schema": "numtareen.experimental.english_gloss_spans.v0",
        "input": text,
        "status": "none" if not spans else "partial" if len(covered) < len(words) else "candidates",
        "token_count": len(words),
        "spans": spans,
        "uncovered": [{"index": index, "token": word}
                      for index, word in enumerate(words) if index not in covered],
        "overlapping_span_pairs": [
            [i, j] for i, left in enumerate(spans) for j in range(i + 1, len(spans))
            if left["start"] < spans[j]["end"] and spans[j]["start"] < left["end"]
        ],
        "note": "Loaded dictionary candidate spans only; overlaps and "
                "dictionary alternatives are not resolved, no sentence generated.",
    }
