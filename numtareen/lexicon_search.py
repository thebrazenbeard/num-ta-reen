"""Source-constrained dictionary discovery, separate from translation.

Every returned entry is an existing author-supplied lexeme. Glosses may be
explanatory definitions, not context-independent English synonyms.
"""

from __future__ import annotations

from typing import Any

from .engine import DataError, Translator, escape_invisible, normalize
from .interop import verify_source_snapshot


_FIELDS = ("headword", "gloss", "category", "register", "taboo", "ipa", "source_line")
_SEARCH_FIELDS = ("headword", "gloss", "both")
_MATCH_MODES = ("exact", "contains")
MAX_QUERY_CHARS = 256
MAX_RESULTS = 100
# ``source_line`` is inherited from this amended authorial dictionary,
# not the normalized JSON projection used for offline lookup.
SOURCE_LINE_DOCUMENT = "sources/dictionary_v2_updated_lphoneme.txt"
NORMALIZED_DATA_FILE = "data/lexicon.json"


def search_lexicon(
    translator: Translator,
    query: str,
    *,
    match: str = "contains",
    field: str = "both",
    category: str | None = None,
    register: str | None = None,
    taboo: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    """Return bounded, provenance-preserving lexical search results.

    This function neither composes sentences nor calls the translation
    engine. Matching is literal after the same NFC/apostrophe normalization
    as source lookup, and phonemic accent distinctions remain significant.
    """
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY_CHARS:
        raise ValueError("Search query must contain 1..256 characters")
    if match not in _MATCH_MODES:
        raise ValueError("Search match must be exact or contains")
    if field not in _SEARCH_FIELDS:
        raise ValueError("Search field must be headword, gloss, or both")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_RESULTS:
        raise ValueError("Search limit must be an integer from 1 to 100")
    for label, selected in (("category", category), ("register", register), ("taboo", taboo)):
        if selected is not None and (not isinstance(selected, str) or not selected.strip()
                                     or len(selected) > 128):
            raise ValueError(f"Search {label} filter must be nonempty text up to 128 characters")

    # The result is labeled AUTHOR_LEXICON_REFERENCE. Do not let a caller
    # relabel arbitrary or in-memory-mutated dictionary data as Patrick's
    # checked-in language material.
    directory = translator.data_dir
    verify_source_snapshot(directory)
    checked = Translator(directory)
    if translator.lexicon != checked.lexicon or translator.corpus != checked.corpus:
        raise DataError("Translator in-memory source differs from pinned files")
    verify_source_snapshot(directory)

    needle = normalize(query)
    if not needle:
        raise ValueError("Search query must contain lexical characters")
    search_fields = ("headword", "gloss") if field == "both" else (field,)
    filters = {"category": category, "register": register, "taboo": taboo}
    ranked: list[tuple[int, int, dict[str, Any]]] = []
    for entry in checked.lexicon:
        if any(selected is not None and entry[name].casefold() != selected.strip().casefold()
               for name, selected in filters.items()):
            continue
        values = tuple(normalize(entry[name]) for name in search_fields)
        exact = any(value == needle for value in values)
        if match == "exact":
            if not exact:
                continue
        elif not any(needle in value for value in values):
            continue
        ranked.append((0 if exact else 1, entry["source_line"],
                       {**{name: entry[name] for name in _FIELDS},
                        "source_line_document": SOURCE_LINE_DOCUMENT}))

    ranked.sort(key=lambda ranked_entry: (ranked_entry[0], ranked_entry[1],
                                         normalize(ranked_entry[2]["headword"])))
    total = len(ranked)
    entries = [row[2] for row in ranked[:limit]]
    return {
        "mode": "lexicon_search",
        "normalized_data_file": NORMALIZED_DATA_FILE,
        "source_line_document": SOURCE_LINE_DOCUMENT,
        "evidence_class": "AUTHOR_LEXICON_REFERENCE",
        "source_independence": "SINGLE_AUTHOR_REFERENCE",
        "qualification_eligible": False,
        "learner_visible": False,
        "semantic_atoms": None,
        "fluent_translation": False,
        "query": query,
        "match": match,
        "field": field,
        "filters": filters,
        "limit": limit,
        "total_matches": total,
        "returned": len(entries),
        "truncated": total > limit,
        "entries": entries,
        "note": "Source-author lexical references only; no sentence meaning inferred",
    }


def format_search(result: dict[str, Any]) -> str:
    """Make user-facing results safe for terminals with control characters."""
    count = result["total_matches"]
    label = f"Lexicon reference search: {count} match(es)"
    if result["truncated"]:
        label += f" (showing {result['returned']})"
    lines = [label, "Dictionary glosses are not fluent translations."]
    for entry in result["entries"]:
        headword = escape_invisible(entry["headword"])
        gloss = escape_invisible(entry["gloss"])
        category = escape_invisible(entry["category"])
        register = escape_invisible(entry["register"])
        taboo = escape_invisible(entry["taboo"])
        lines.append(
            f"{headword} — {gloss} "
            f"[{category}; register={register}; taboo={taboo}; "
            f"source={entry['source_line_document']}:{entry['source_line']}]"
        )
    return "\n".join(lines)
