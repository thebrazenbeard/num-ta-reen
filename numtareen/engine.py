"""Attested-sentence lookup and explicitly non-fluent lexical glossing.

Canonical lexical and corpus data live in data/*.json. This module never
generates new words or infers fluent syntax from interlinear glosses.
"""

from __future__ import annotations

import json
import hashlib
import re
import unicodedata
from collections import defaultdict
from itertools import product
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
# Exact checked-in source record export, with enforced LF in .gitattributes.
# Updating the authored corpus requires an explicit, reviewed provenance bump;
# caller-supplied datasets can still be queried but are not source-attested.
ATTESTED_CORPUS_SHA256 = "5bc4c939e728e9e5bce1875eafcba9e71609570281bebb87dc7e64e2e9a6d229"
ATTESTED_LEXICON_SHA256 = "208d5daa5953383cccbac6a145df795531691ec60248256dc2e18a5651c6ba08"
_APOSTROPHE_TRANSLATION = str.maketrans({"'": "’", "‘": "’", "ʼ": "’"})
_WHITESPACE = re.compile(r"\s+")
# Recognize common Unicode sentence punctuation at lexical token boundaries.
# This affects dictionary fallback only: exact corpus matching still uses
# normalize(), and phonemic apostrophes / true-name brackets are untouched.
_WORD_EDGES = " \t\r\n.,!?;:\"“”«»()[]{}…。，！？．；："
_SIMPLE_ALTERNATIVES = re.compile(r"^[^\s/.,;:()]+(?:/[^\s/.,;:()]+)+\.?$")
MAX_SEGMENTED_PIECES = 16
MAX_SEGMENTATION_ANALYSES = 64


class DataError(ValueError):
    """Checked-in data is absent or malformed."""


class UnknownTermError(ValueError):
    """The requested phrase cannot be translated under strict unknown policy."""


class AmbiguityOverflowError(ValueError):
    """Bounded lexical segmentation would omit valid dictionary analyses."""


def normalize(value: str) -> str:
    """Normalize presentation variants, never erase phonemic accents or /ʔ/."""
    if not isinstance(value, str):
        raise TypeError("text must be a string")
    # A str subclass may override .translate(), .strip(), or .casefold() and
    # thereby turn an unrelated input into an apparently attested sentence.
    value = str.__str__(value)
    value = unicodedata.normalize("NFC", value.translate(_APOSTROPHE_TRANSLATION))
    value = _WHITESPACE.sub(" ", value.strip())
    # A period is a sentence terminator, not a lexical contrast. Question
    # marks and exclamation marks are deliberately preserved.
    return value.removesuffix(".").casefold()


def escape_invisible(value: str) -> str:
    """Render terminal controls and bidi format controls visibly, not actively.

    Used only for human-readable presentation; lookup keeps the raw Unicode
    intact so an altered input cannot accidentally match an attested phrase.
    """
    return "".join(f"\\u{ord(ch):04x}" if unicodedata.category(ch).startswith("C")
                   or unicodedata.category(ch) in {"Zl", "Zp"} else ch for ch in value)


def _record(entry: dict) -> dict:
    return {
        "headword": entry["headword"],
        "gloss": entry["gloss"],
        "category": entry["category"],
        "register": entry["register"],
        "taboo": entry["taboo"],
        "ipa": entry["ipa"],
        "source_line": entry["source_line"],
    }


def _load_document(directory: Path, name: str, key: str, count_key: str) -> tuple[list[dict], str]:
    path = directory / name
    try:
        raw = path.read_bytes()
        document = json.loads(raw.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataError(f"Unable to read canonical {name}: {exc}") from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise DataError(f"Unsupported or malformed schema in {name}")
    records = document.get(key)
    if not isinstance(records, list) or document.get(count_key) != len(records):
        raise DataError(f"Canonical count mismatch in {name}")
    if any(not isinstance(row, dict) for row in records):
        raise DataError(f"Malformed record in {name}")
    # Hash the *same bytes* that were parsed, avoiding a read/verify race.
    return records, hashlib.sha256(raw).hexdigest()


class Translator:
    """Bounded lookup engine whose results carry provenance and uncertainty."""

    def __init__(self, data_dir: Path | None = None):
        directory = Path(data_dir) if data_dir is not None else DATA_DIR
        self.data_dir = directory
        self.lexicon, lexicon_sha256 = _load_document(directory, "lexicon.json", "entries", "entry_count")
        self.corpus, corpus_sha256 = _load_document(directory, "corpus.json", "records", "record_count")
        self._source_attested_corpus = corpus_sha256 == ATTESTED_CORPUS_SHA256
        # File-level grade only; individual lexical candidates are approximate
        # glosses, never fluent or sentence-attested translations.
        self._source_verified_lexicon_file = lexicon_sha256 == ATTESTED_LEXICON_SHA256
        # The API exposes mutable records to existing consumers. Preserve a
        # private content snapshot so mutations and reindexed references
        # cannot silently acquire an authored evidence grade later.
        self._loaded_corpus_rows = {
            id(row): json.dumps(row, sort_keys=True, ensure_ascii=False)
            for row in self.corpus
        }
        self.words: dict[str, list[dict]] = defaultdict(list)
        self.glosses: dict[str, list[dict]] = defaultdict(list)
        self.sentences = {"nt-en": defaultdict(list), "en-nt": defaultdict(list)}
        # Lookup dictionaries remain mutable for compatibility. Keep a private
        # snapshot of each emitted lexical record so later API-level edits do
        # not inherit the integrity grade of the original on-disk export.
        self._loaded_lexical_records: dict[int, str] = {}

        for entry in self.lexicon:
            required = ("headword", "gloss", "category", "register", "taboo", "ipa", "source_line")
            if any(not isinstance(entry.get(k), str) if k != "source_line" else not isinstance(entry.get(k), int) for k in required):
                raise DataError("Malformed lexicon entry")
            clean = _record(entry)
            self._loaded_lexical_records[id(clean)] = json.dumps(
                clean, sort_keys=True, ensure_ascii=False)
            self.words[normalize(entry["headword"])].append(clean)
            gloss = entry["gloss"].strip().removesuffix(".")
            self.glosses[normalize(gloss)].append(clean)
            # Only a single explicitly slash-separated gloss is split into
            # *candidate* alternatives. These are not fluent translations.
            if _SIMPLE_ALTERNATIVES.fullmatch(entry["gloss"].strip()):
                for alternative in gloss.split("/"):
                    if normalize(alternative) != normalize(gloss):
                        self.glosses[normalize(alternative)].append(clean)

        for row in self.corpus:
            fields = ("id", "orthography_index", "english", "ipa", "igt")
            if any(not isinstance(row.get(k), str) for k in fields):
                raise DataError("Malformed corpus record")
            self.sentences["nt-en"][normalize(row["orthography_index"])].append(row)
            self.sentences["en-nt"][normalize(row["english"])].append(row)

    def _candidate(self, entry: dict, *, lookup_key: str, reverse: bool = False) -> dict:
        candidate = dict(entry)
        try:
            snapshot_unchanged = (self._loaded_lexical_records.get(id(entry)) ==
                                  json.dumps(entry, sort_keys=True, ensure_ascii=False))
            if reverse:
                gloss = entry["gloss"].strip()
                normalized = gloss.removesuffix(".")
                allowed = {normalize(normalized)}
                if _SIMPLE_ALTERNATIVES.fullmatch(gloss):
                    allowed.update(normalize(part) for part in normalized.split("/"))
                key_matches = normalize(lookup_key) in allowed
            else:
                key_matches = normalize(lookup_key) == normalize(entry["headword"])
        except (TypeError, ValueError, KeyError, AttributeError, RecursionError):
            snapshot_unchanged = key_matches = False
        candidate["source_candidate_verified"] = bool(
            self._source_verified_lexicon_file and snapshot_unchanged and key_matches)
        return candidate

    def _lexical_nt(self, token: str) -> list[dict]:
        direct = self.words.get(normalize(token), [])
        if direct:
            return [self._candidate(e, lookup_key=token) for e in direct]
        # Conservative tokenization of *attested clitics*. A bare stem not in
        # the dictionary remains unknown; no grammatical reading is inferred.
        if "=" in token and not token.startswith("="):
            pieces = token.split("=")
            if len(pieces) > MAX_SEGMENTED_PIECES:
                raise AmbiguityOverflowError("segmentation depth limit exceeded")
            if any(not piece for piece in pieces):
                return []
            stem = self.words.get(normalize(pieces[0]), [])
            clitics = [self.words.get(normalize("=" + piece), []) for piece in pieces[1:]]
            if stem and all(clitics):
                candidate_count = len(stem)
                for choices in clitics:
                    if candidate_count > MAX_SEGMENTATION_ANALYSES // len(choices):
                        raise AmbiguityOverflowError("segmentation analysis limit exceeded")
                    candidate_count *= len(choices)
                keys = [pieces[0]] + ["=" + piece for piece in pieces[1:]]
                return [{"segmentation": [self._candidate(e, lookup_key=key)
                                          for e, key in zip(analysis, keys)],
                         "note": "Lexical segmentation only; not a grammatical parse"}
                        for analysis in product(stem, *clitics)]
        return []

    def translate(self, text: str, direction: str = "nt-en", unknown: str = "mark") -> dict:
        if direction not in self.sentences:
            raise ValueError("direction must be nt-en or en-nt")
        if unknown not in {"mark", "keep", "error"}:
            raise ValueError("unknown policy must be mark, keep, or error")
        if not isinstance(text, str):
            raise ValueError("text must be nonempty")
        text = str.__str__(text)
        if not text.strip():
            raise ValueError("text must be nonempty")
        query = normalize(text)
        attested = self.sentences[direction].get(query, [])
        if attested:
            field = "orthography_index" if direction == "nt-en" else "english"
            verified = self._source_attested_corpus and all(
                self._loaded_corpus_rows.get(id(row)) ==
                json.dumps(row, sort_keys=True, ensure_ascii=False)
                and normalize(row[field]) == query
                for row in attested
            )
            matches = [{
                "id": row["id"],
                "translation": row["english"] if direction == "nt-en" else row["orthography"],
                "orthography": row["orthography"],
                "english": row["english"],
                "ipa": row["ipa"],
                "igt": row["igt"],
                "source_note": row.get("notes", ""),
                "source_section": row.get("source_section"),
            } for row in attested]
            return {"direction": direction, "input": text,
                    "status": "attested" if verified else "unverified",
                    "matches": matches,
                    "note": ("Exact source-attested utterance; not a general grammatical generation"
                             if verified else
                             "Exact match in loaded corpus; source attestation is UNVERIFIED")}

        if direction == "nt-en":
            tokens = [part.strip(_WORD_EDGES) for part in _WHITESPACE.split(text.strip())]
            lookups = [(part, self._lexical_nt(part)) for part in tokens if part]
        else:
            whole = self.glosses.get(query, [])
            if whole:
                lookups = [(text.strip(), [self._candidate(e, lookup_key=query, reverse=True)
                                          for e in whole])]
            else:
                tokens = [part.strip(_WORD_EDGES) for part in _WHITESPACE.split(text.strip())]
                lookups = [(part, [self._candidate(e, lookup_key=part, reverse=True)
                                   for e in self.glosses.get(normalize(part), [])])
                           for part in tokens if part]

        parts = []
        for token, matches in lookups:
            if matches:
                parts.append({"token": token, "kind": "lexical", "matches": matches})
            else:
                if unknown == "error":
                    raise UnknownTermError(f"Unknown {direction} segment: {token}")
                parts.append({"token": token, "kind": "unknown", "display": token if unknown == "keep"
                              else f"⟦unknown: {token}⟧", "matches": []})
        if not parts:
            raise ValueError("text does not contain a translatable segment")
        unknown_count = sum(part["kind"] == "unknown" for part in parts)
        ambiguous_count = sum(len(part["matches"]) > 1 for part in parts)
        status = ("incomplete" if unknown_count else "ambiguous" if ambiguous_count
                  else "lexical")
        candidate_flags = [
            bool(atom.get("source_candidate_verified", False))
            for part in parts for match in part["matches"]
            for atom in (match.get("segmentation") or [match])
        ]
        return {"direction": direction, "input": text, "status": status, "parts": parts,
                "unknown_count": unknown_count, "ambiguous_count": ambiguous_count,
                "lexicon_file_verified": self._source_verified_lexicon_file,
                "lexicon_candidate_verified": all(candidate_flags) if candidate_flags else None,
                "note": "Approximate dictionary glosses only; no new canonical sentence or fluent translation"}


def format_translation(result: dict) -> str:
    """Human-readable output with an explicit evidence grade."""
    if result["status"] in {"attested", "unverified"}:
        verified = result["status"] == "attested"
        lines = ["Status: source-attested translation" if verified else
                 "Status: unverified loaded corpus match (authored origin not established)"]
        for match in result["matches"]:
            source = "corpus" if verified else "unverified loaded corpus"
            lines.append(f"{match['translation']} [{source} {match['id']}]")
            lines.append(f"  IPA: {match['ipa']}")
            if match["source_note"]:
                lines.append(f"  Source note: {match['source_note']}")
        return "\n".join(escape_invisible(line) for line in lines)

    grade = {"lexical": "approximate lexical gloss", "ambiguous": "ambiguous lexical lookup",
             "incomplete": "incomplete lexical gloss (unknown segments)"}[result["status"]]
    lines = [f"Status: {grade}"]
    for part in result["parts"]:
        if part["kind"] == "unknown":
            lines.append(part["display"] + " [untranslated]")
            continue
        for match in part["matches"]:
            if "segmentation" in match:
                pieces = "; ".join(f"{x['headword']}={x['gloss']}" for x in match["segmentation"])
                lines.append(f"{part['token']}: {pieces} [segmented; not a parse]")
                continue
            target = match["gloss"] if result["direction"] == "nt-en" else match["headword"]
            lines.append(f"{part['token']} → {target} [category={match['category']}; "
                         f"register={match['register']}; taboo={match['taboo']}; "
                         f"dictionary line={match['source_line']}]")
    lines.append("Note: " + result["note"])
    if result.get("lexicon_file_verified") is False:
        lines.append("Provenance: loaded lexicon file unverified against the authored export")
    elif result.get("lexicon_candidate_verified") is False:
        lines.append("Provenance: loaded dictionary candidate unverified after mutation or replacement")
    return "\n".join(escape_invisible(line) for line in lines)
