"""Attested-sentence lookup and explicitly non-fluent lexical glossing.

Canonical lexical and corpus data live in data/*.json. This module never
generates new words or infers fluent syntax from interlinear glosses.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_APOSTROPHE_TRANSLATION = str.maketrans({"'": "’", "‘": "’", "ʼ": "’"})
_WHITESPACE = re.compile(r"\s+")
_WORD_EDGES = " \t\r\n.,!?;:\"“”«»()[]{}"
_SIMPLE_ALTERNATIVES = re.compile(r"^[^\s/.,;:()]+(?:/[^\s/.,;:()]+)+\.?$")


class DataError(ValueError):
    """Checked-in data is absent or malformed."""


class UnknownTermError(ValueError):
    """The requested phrase cannot be translated under strict unknown policy."""


def normalize(value: str) -> str:
    """Normalize presentation variants, never erase phonemic accents or /ʔ/."""
    if not isinstance(value, str):
        raise TypeError("text must be a string")
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


def _load_document(directory: Path, name: str, key: str, count_key: str) -> list[dict]:
    path = directory / name
    try:
        with path.open("r", encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DataError(f"Unable to read canonical {name}: {exc}") from exc
    if not isinstance(document, dict) or document.get("schema_version") != 1:
        raise DataError(f"Unsupported or malformed schema in {name}")
    records = document.get(key)
    if not isinstance(records, list) or document.get(count_key) != len(records):
        raise DataError(f"Canonical count mismatch in {name}")
    if any(not isinstance(row, dict) for row in records):
        raise DataError(f"Malformed record in {name}")
    return records


class Translator:
    """Bounded lookup engine whose results carry provenance and uncertainty."""

    def __init__(self, data_dir: Path | None = None):
        directory = Path(data_dir) if data_dir is not None else DATA_DIR
        self.lexicon = _load_document(directory, "lexicon.json", "entries", "entry_count")
        self.corpus = _load_document(directory, "corpus.json", "records", "record_count")
        self.words: dict[str, list[dict]] = defaultdict(list)
        self.glosses: dict[str, list[dict]] = defaultdict(list)
        self.sentences = {"nt-en": defaultdict(list), "en-nt": defaultdict(list)}

        for entry in self.lexicon:
            required = ("headword", "gloss", "category", "register", "taboo", "ipa", "source_line")
            if any(not isinstance(entry.get(k), str) if k != "source_line" else not isinstance(entry.get(k), int) for k in required):
                raise DataError("Malformed lexicon entry")
            clean = _record(entry)
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

    @staticmethod
    def _candidate(entry: dict) -> dict:
        return dict(entry)

    def _lexical_nt(self, token: str) -> list[dict]:
        direct = self.words.get(normalize(token), [])
        if direct:
            return [self._candidate(e) for e in direct]
        # Conservative tokenization of *attested clitics*. A bare stem not in
        # the dictionary remains unknown; no grammatical reading is inferred.
        if "=" in token and not token.startswith("="):
            pieces = token.split("=")
            if any(not piece for piece in pieces):
                return []
            stem = self.words.get(normalize(pieces[0]), [])
            clitics = [self.words.get(normalize("=" + piece), []) for piece in pieces[1:]]
            if stem and all(clitics):
                return [{"segmentation": [self._candidate(e) for e in stem]
                         + [self._candidate(e) for choices in clitics for e in choices],
                         "note": "Lexical segmentation only; not a grammatical parse"}]
        return []

    def translate(self, text: str, direction: str = "nt-en", unknown: str = "mark") -> dict:
        if direction not in self.sentences:
            raise ValueError("direction must be nt-en or en-nt")
        if unknown not in {"mark", "keep", "error"}:
            raise ValueError("unknown policy must be mark, keep, or error")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be nonempty")
        query = normalize(text)
        attested = self.sentences[direction].get(query, [])
        if attested:
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
            return {"direction": direction, "input": text, "status": "attested", "matches": matches,
                    "note": "Exact source-attested utterance; not a general grammatical generation"}

        if direction == "nt-en":
            tokens = [part.strip(_WORD_EDGES) for part in _WHITESPACE.split(text.strip())]
            lookups = [(part, self._lexical_nt(part)) for part in tokens if part]
        else:
            whole = self.glosses.get(query, [])
            if whole:
                lookups = [(text.strip(), [self._candidate(e) for e in whole])]
            else:
                tokens = [part.strip(_WORD_EDGES) for part in _WHITESPACE.split(text.strip())]
                lookups = [(part, [self._candidate(e) for e in self.glosses.get(normalize(part), [])])
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
        return {"direction": direction, "input": text, "status": status, "parts": parts,
                "unknown_count": unknown_count, "ambiguous_count": ambiguous_count,
                "note": "Approximate dictionary glosses only; no new canonical sentence or fluent translation"}


def format_translation(result: dict) -> str:
    """Human-readable output with an explicit evidence grade."""
    if result["status"] == "attested":
        lines = ["Status: source-attested translation"]
        for match in result["matches"]:
            lines.append(f"{match['translation']} [corpus {match['id']}]")
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
    return "\n".join(escape_invisible(line) for line in lines)
