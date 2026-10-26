"""Source-constrained field-orthography observations, never a grammar parser.

Dictionary lines and corpus examples support recognition of *markers*, but do
not authorize generation of new grammar or a grammaticality/meaning verdict.
The historical field transliteration loses native timing and resonance scope.
"""

from __future__ import annotations

from pathlib import Path

from .engine import DATA_DIR, MAX_SEGMENTED_PIECES, DataError, Translator, normalize
from .interop import verify_source_snapshot

SCHEMA = "numtareen.grammar_diagnostic.v0"
MAX_TEXT_CHARACTERS = 4096
MAX_TOKENS = 128

# These labels describe observed dictionary markers. They are not inferred
# grammatical relations or a complete parse of an utterance.
_ROLE_MARKERS = {"=ka", "=en", "=ru", "=va", "=shi"}
_CONSENT_MARKER = "=uth"
_FOCUS_MARKERS = {"=tra", "=sha"}
_EVIDENTIALS = {"ech", "reen"}
_ECHO_OPERATORS = {"qir", "ruun", "na’vyr"}
_SIMPLE_FUNCTIONS = {
    "hë": "question_marker",
    "vu": "negation",
    "ta’qesh": "prohibition",
    "ke": "complementizer",
}
_GRAMMAR_SECTIONS = {
    "role": "II.4",
    "consent": "IV.3",
    "topic_focus": "II.4",
    "evidential": "IV.1–IV.2",
    "echo_operator": "II.5, IV.1",
    "question_marker": "III.6",
    "negation": "III.7",
    "prohibition": "III.7, IV.2",
    "complementizer": "III.8",
    "lexical_source": "II.3",
}
_FIELD_EDGES = ".,!?;:\"“”"
_ATTESTED_ARGUMENT_HOSTS = {"ta": "E02/E03", "na": "E02/E03"}


def _classification(marker: str) -> str:
    if marker in _ROLE_MARKERS:
        return "role"
    if marker == _CONSENT_MARKER:
        return "consent"
    if marker in _FOCUS_MARKERS:
        return "topic_focus"
    if marker in _EVIDENTIALS:
        return "evidential"
    if marker in _ECHO_OPERATORS:
        return "echo_operator"
    return _SIMPLE_FUNCTIONS.get(marker, "lexical_source")


def _observation(translator: Translator, *, index: int, marker: str, host: str) -> dict:
    marker_key = normalize(marker)
    rows = translator.words.get(marker_key, [])
    source_lines = sorted({row["source_line"] for row in rows})
    kind = _classification(marker_key)
    source_authority = "AUTHOR_DICTIONARY_AND_GRAMMAR_NOT_INDEPENDENT"
    if marker_key in _ATTESTED_ARGUMENT_HOSTS and not rows:
        kind = "attested_argument_host"
        source_authority = "AUTHOR_ATTESTED_CORPUS_E02_E03"
    return {
        "token_index": index,
        "host": host,
        "marker": normalize(marker),
        "kind": kind,
        "dictionary_source_lines": source_lines,
        "grammar_section": _GRAMMAR_SECTIONS.get(kind),
        "source_authority": source_authority,
    }


def _conflicts(seen: set[str]) -> list[dict]:
    conflicts: list[dict] = []
    if seen.intersection({"së", "sën"}):
        conflicts.append({
            "code": "RELATIVIZER_FORM_CONFLICT",
            "forms": ["së", "sën"],
            "claims": [
                {"source": "amended grammar III.8", "claim": "sën is REL"},
                {"source": "amended lexicon lines 34, 59",
                 "claim": "së is REL; sën is WH.MANNER"},
                {"source": "corpus E13", "claim": "së used as REL"},
            ],
            "resolution": None,
        })
    if "rhel" in seen:
        conflicts.append({
            "code": "RHEL_FUNCTION_CONFLICT",
            "forms": ["rhel"],
            "claims": [
                {"source": "amended grammar III.8", "claim": "rhel is concessive"},
                {"source": "amended lexicon line 53",
                 "claim": "rhel is restore balance/coherence"},
                {"source": "corpus E23", "claim": "rhel used as restore.balance"},
            ],
            "resolution": None,
        })
    return conflicts


def _verified_translator(supplied: Translator | None) -> Translator:
    """Load canonical, hash-pinned data; never trust mutable caller indexes.

    A caller may pass a Translator for API compatibility, but its in-memory
    lexicon, corpus and lookup indexes must agree with an independently loaded
    snapshot. Every observation is made from that newly checked snapshot.
    """
    if supplied is not None and not isinstance(supplied, Translator):
        raise DataError("Diagnostic translator must be a Translator instance")
    try:
        directory = Path(supplied.data_dir if supplied is not None else DATA_DIR)
    except (TypeError, ValueError) as exc:
        raise DataError("Invalid source-bound data directory") from exc
    verify_source_snapshot(directory)
    checked = Translator(directory)
    if supplied is not None and any(
        getattr(supplied, field) != getattr(checked, field)
        for field in ("lexicon", "corpus", "words", "glosses", "sentences")
    ):
        raise DataError("Diagnostic translator differs from pinned source")
    verify_source_snapshot(directory)
    return checked


def diagnose(text: str, *, translator: Translator | None = None) -> dict:
    """Observe supported field markers with explicit uncertainty.

    This does not infer full syntax, consent, a true-name signal, or English
    meaning. An author-attested corpus ID identifies the *source example*,
    not an independent semantic qualification.
    """
    if not isinstance(text, str) or not text.strip():
        raise ValueError("diagnostic text must be a nonempty string")
    if len(text) > MAX_TEXT_CHARACTERS:
        raise ValueError("diagnostic text length exceeds 4096 characters")
    translator = _verified_translator(translator)
    query = normalize(text)

    # The E26 chord is documented only as an intentionally unspoken true-name
    # placeholder. No fragment of its notation may enter diagnostics.
    protected = any(row["id"] == "E26" and query in
                    {normalize(row["orthography_index"]), normalize(row["english"])}
                    for row in translator.corpus)
    if "⟦" in text or "⟧" in text or protected:
        return {
            "schema": SCHEMA,
            "source_text": None,
            "withheld": True,
            "attested_corpus_ids": [],
            "observations": [],
            "unknown_tokens": [],
            "source_conflicts": [],
            "warnings": ["TRUE_NAME_CHORD_WITHHELD"],
            "limitations": ["NO_FULL_PARSE", "NO_NATIVE_RESONANCE_OR_TIMING_RECOVERY"],
            "grammar_verdict": None,
            "semantic_atoms": None,
            "qualification_eligible": False,
        }

    tokens = text.split()
    if len(tokens) > MAX_TOKENS:
        raise ValueError("diagnostic token count exceeds 128")
    observations: list[dict] = []
    unknown: list[dict] = []
    seen: set[str] = set()
    has_consent = False
    contains_vahl = False
    for index, literal in enumerate(tokens):
        token = literal.strip(_FIELD_EDGES)
        parts = token.split("=")
        if len(parts) > MAX_SEGMENTED_PIECES:
            raise ValueError("diagnostic segment count exceeds 16")
        base = parts[0]
        base_key = normalize(base)
        seen.add(base_key)
        contains_vahl |= base_key == "vahl"
        if base_key:
            if base_key.startswith("‹") and base_key.endswith("›"):
                unknown.append({"token_index": index, "token": base, "kind": "marked_loan"})
            elif base_key not in translator.words and base_key not in _ATTESTED_ARGUMENT_HOSTS:
                unknown.append({"token_index": index, "token": base, "kind": "unknown"})
            else:
                observations.append(_observation(
                    translator, index=index, marker=base, host=base,
                ))
        for clitic in parts[1:]:
            marker = "=" + clitic
            marker_key = normalize(marker)
            seen.add(marker_key)
            if marker_key not in translator.words:
                unknown.append({"token_index": index, "token": marker, "kind": "unknown_clitic"})
            else:
                observations.append(_observation(
                    translator, index=index, marker=marker, host=base,
                ))
                if marker_key == _CONSENT_MARKER:
                    has_consent = True
    warnings: list[str] = []
    if contains_vahl and not has_consent:
        # The grammar says this *may* implicate coercion, never proves it.
        warnings.append("POSSIBLE_COERCION_IMPLICATURE")
    if unknown:
        warnings.append("UNRECOGNIZED_OR_MARKED_CONTACT_MATERIAL")
    return {
        "schema": SCHEMA,
        "source_text": text,
        "withheld": False,
        "attested_corpus_ids": [
            row["id"] for row in translator.corpus
            if normalize(row["orthography_index"]) == query
        ],
        "observations": observations,
        "unknown_tokens": unknown,
        "source_conflicts": _conflicts(seen),
        "warnings": warnings,
        "limitations": ["NO_FULL_PARSE", "NO_NATIVE_RESONANCE_OR_TIMING_RECOVERY"],
        "grammar_verdict": None,
        "semantic_atoms": None,
        "qualification_eligible": False,
    }
