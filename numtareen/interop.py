"""Quarantined source-reference bridge for universal-translation experiments.

This is deliberately NOT a learned semantic grounder. Every successful output
is an operator-authored reference, and every record is unqualified for semantic
learning or grounding claims. No private corpus is written to another repo.

Protocol: one UTF-8 JSON request per stdin line, one JSON response per stdout
line. The receiving implementation must treat this process as an *oracle* and
exclude its answers from no-shared-language discovery evaluations.
"""

from __future__ import annotations

import base64
import binascii
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from .engine import AmbiguityOverflowError, DATA_DIR, DataError, Translator, UnknownTermError


SCHEMA = "unvtrslr-reference-evidence-v1"
SOURCE_BASELINE_COMMIT = "cdfbea09cc8b4a1648cde733953986c7d694d496"
ORIGIN_REPO = "thebrazenbeard/num-ta-reen"
MAX_REQUEST_BYTES = 65536
MAX_TEXT_BYTES = 16384
MAX_BASE64_CHARS = 4 * ((MAX_TEXT_BYTES + 2) // 3)
DATA_SHA256 = {
    "corpus.json": "5bc4c939e728e9e5bce1875eafcba9e71609570281bebb87dc7e64e2e9a6d229",
    "lexicon.json": "208d5daa5953383cccbac6a145df795531691ec60248256dc2e18a5651c6ba08",
}
_CHORD_NOTATION = re.compile(r"⟦[0-9]+(?:·[0-9]+)+⟧")


def _reject_duplicate_json_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    record: dict[str, Any] = {}
    for key, value in pairs:
        if key in record:
            raise ValueError("duplicate JSON member")
        record[key] = value
    return record


def _reject_non_json_constant(value: str) -> None:
    raise ValueError("non-JSON numeric constant")


def verify_source_snapshot(directory: Path = DATA_DIR) -> None:
    """Fail closed if checked-in source data differs from the pinned baseline.

    The commit identifies *these data files*, not the current program revision.
    Updating source data requires independently reviewing and repinning both
    digests and the baseline commit, never an automatic hash refresh.
    """
    for name, expected in DATA_SHA256.items():
        try:
            actual = hashlib.sha256((directory / name).read_bytes()).hexdigest()
        except OSError as exc:
            raise DataError(f"Missing source-bound {name}") from exc
        if actual != expected:
            raise DataError(f"Source-bound {name} digest mismatch")


def _origin(source: dict[str, Any] | None, record_id: str | None = None) -> dict[str, Any]:
    return {
        "repo": ORIGIN_REPO,
        "commit": SOURCE_BASELINE_COMMIT,
        "source_group": "single-author-wreckforge",
        "source_document": source.get("title") if source else None,
        "source_sha256": source.get("source_sha256") if source else None,
        "record_id": record_id,
    }


def _source_metadata(translator: Translator, kind: str) -> dict[str, Any]:
    """Use the package's source metadata in CLI and direct Python calls."""
    directory = getattr(translator, "data_dir", DATA_DIR)
    document = json.loads((directory / f"{kind}.json").read_text(encoding="utf-8"))
    return document["source"]


def _lexical_alternatives(result: dict[str, Any], direction: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for part in result["parts"]:
        if part["kind"] != "lexical":
            continue
        for match in part["matches"]:
            if "segmentation" in match:
                # A clitic segmentation is a dictionary lookup, not a phrase
                # translation. Preserve its constituent provenance verbatim.
                candidates.append({
                    "kind": "lexical_segmentation",
                    "token": part["token"],
                    "segmentation": match["segmentation"],
                    "value": None,
                    "note": "Unparsed lexical segmentation",
                })
            else:
                candidates.append({
                    "kind": "lexeme",
                    "token": part["token"],
                    "value": match["gloss"] if direction == "nt-en" else match["headword"],
                    "headword": match["headword"],
                    "gloss": match["gloss"],
                    "category": match["category"],
                    "register": match["register"],
                    "taboo": match["taboo"],
                    "ipa": match["ipa"],
                    "source_line": match["source_line"],
                    "note": "Lexical candidate only; not a fluent translation",
                })
    return candidates


def to_reference_record(
    translator: Translator, text: str, direction: str = "nt-en", unknown: str = "mark"
) -> dict[str, Any]:
    """Translate with explicit operator-oracle and no-grounding boundaries.

    Every output has ``semantic_atoms: null`` and
    ``qualification_eligible: false``. English glosses are not UNVTRSLR
    ground-truth semantic atoms. The true-name chord is never rendered.
    """
    # Caller-supplied Translator instances may be pointed at unrelated or
    # mutated data. Never attribute that output to the pinned source commit.
    directory = translator.data_dir
    verify_source_snapshot(directory)
    checked = Translator(directory)
    if translator.lexicon != checked.lexicon or translator.corpus != checked.corpus:
        raise DataError("Translator in-memory source differs from pinned files")
    verify_source_snapshot(directory)
    result = checked.translate(text, direction=direction, unknown=unknown)
    source: dict[str, Any] | None = None
    record_id: str | None = None
    target: str | None = None
    alternatives: list[dict[str, Any]] = []
    evidence_class = "UNKNOWN"
    warnings = ["OPERATOR_SUPPLIED_REFERENCE_NOT_GROUNDED", "NOT_INDEPENDENT_GROUNDING_SOURCE"]
    withheld = _CHORD_NOTATION.search(text) is not None

    if result["status"] == "attested":
        source = _source_metadata(translator, "corpus")
        evidence_class = "AUTHOR_ATTESTED_CORPUS"
        matches = result["matches"]
        if len(matches) == 1:
            record_id = matches[0]["id"]
            target = matches[0]["translation"]
        else:
            alternatives = [
                {"kind": "corpus", "record_id": m["id"], "value": m["translation"]}
                for m in matches
            ]
            warnings.append("MULTIPLE_ATTESTED_MATCHES_NOT_DISAMBIGUATED")
        if any(match["id"] == "E26" for match in matches):
            withheld = True
    else:
        source = _source_metadata(translator, "lexicon")
        alternatives = _lexical_alternatives(result, direction)
        if result["status"] in {"lexical", "ambiguous"}:
            evidence_class = "AUTHOR_LEXICON_GLOSS"
            warnings.append("LEXICAL_CANDIDATES_NOT_FLUENT_TRANSLATION")
        elif alternatives:
            # The phrase is not translatable, but the recognized fragments
            # retain dictionary provenance. Never construct a fluent target.
            evidence_class = "AUTHOR_PARTIAL_LEXICAL"
            warnings.append("UNKNOWN_SEGMENTS_PRESENT")
            warnings.append("LEXICAL_CANDIDATES_NOT_FLUENT_TRANSLATION")
        else:
            warnings.append("UNKNOWN_OR_PARTIAL_INPUT")

    if withheld:
        # E26 is the attested statement *about* an unspoken true name. Its
        # numeric chord is not a spellable/speakable target signal. Even on
        # English->Num translation, do not emit that chord as target text.
        target = None
        alternatives = []
        warnings.append("TRUE_NAME_CHORD_WITHHELD")

    return {
        "schema": SCHEMA,
        "origin": _origin(source, record_id),
        "direction": direction,
        "evidence_class": evidence_class,
        "source_text": None if withheld else text,
        "target_text": target,
        "alternatives": alternatives,
        "register": None,
        "taboo": None,
        "semantic_atoms": None,
        "qualification_eligible": False,
        "learner_visible": False,
        "source_independence": "SINGLE_AUTHOR_REFERENCE",
        "withheld": withheld,
        "warnings": warnings,
    }


def _error(code: str, message: str, request_id: str | None = None) -> dict[str, Any]:
    return {
        "ok": False,
        "request_id": request_id,
        "error": {"code": code, "message": message},
    }


def handle_request(translator: Translator, request: Any) -> dict[str, Any]:
    if not isinstance(request, dict):
        return _error("INVALID_REQUEST", "JSON request must be an object")
    request_id = request.get("request_id")
    if request_id is not None and (not isinstance(request_id, str) or len(request_id) > 128):
        return _error("INVALID_REQUEST", "request_id must be a string of at most 128 characters")
    if set(request) - {"direction", "text", "text_base64", "unknown", "request_id"}:
        return _error("INVALID_REQUEST", "Unsupported request fields", request_id)
    direction = request.get("direction")
    unknown = request.get("unknown", "mark")
    if ("text" in request) == ("text_base64" in request):
        return _error("INVALID_REQUEST", "Exactly one of text or text_base64 is required", request_id)
    if "text_base64" in request:
        encoded = request["text_base64"]
        if not isinstance(encoded, str) or not encoded or len(encoded) > MAX_BASE64_CHARS:
            return _error("INVALID_TEXT_ENCODING", "text_base64 must be bounded Base64 text", request_id)
        try:
            encoded_bytes = base64.b64decode(encoded, validate=True)
            if len(encoded_bytes) > MAX_TEXT_BYTES:
                raise ValueError("decoded text exceeds byte limit")
            phrase = encoded_bytes.decode("utf-8", errors="strict")
        except (binascii.Error, UnicodeError, ValueError):
            return _error("INVALID_TEXT_ENCODING", "text_base64 must decode to bounded UTF-8", request_id)
    else:
        phrase = request["text"]
    if (direction not in ("nt-en", "en-nt") or not isinstance(phrase, str)
            or not phrase.strip() or len(phrase) > 4096):
        return _error("INVALID_REQUEST", "direction and nonempty text up to 4096 characters are required", request_id)
    if unknown not in ("mark", "keep", "error"):
        return _error("INVALID_REQUEST", "unknown must be mark, keep, or error", request_id)
    try:
        response = to_reference_record(translator, phrase, direction=direction, unknown=unknown)
    except UnknownTermError:
        return _error("UNKNOWN_SEGMENT", "Unknown segment with strict unknown policy", request_id)
    except AmbiguityOverflowError:
        return _error("AMBIGUITY_LIMIT", "Lexical segmentation exceeds safe analysis limits", request_id)
    except (DataError, OSError, KeyError):
        return _error("SOURCE_DATA_ERROR", "Pinned reference data could not be verified", request_id)
    except ValueError:
        return _error("INVALID_TEXT", "Input has no translatable segments", request_id)
    envelope = {"ok": True, "request_id": request_id, "record": response}
    if len(json.dumps(envelope, ensure_ascii=True, separators=(",", ":")).encode("utf-8")) > MAX_REQUEST_BYTES:
        return _error("RESPONSE_TOO_LARGE", "Reference evidence exceeds 65536 bytes", request_id)
    return envelope


def main() -> int:
    try:
        verify_source_snapshot()
        translator = Translator()
        # Metadata is loaded on demand from verified package data, not from
        # host git state or ambient credentials.
    except (DataError, OSError, ValueError, KeyError) as exc:
        print(json.dumps(_error("SOURCE_DATA_ERROR", str(exc)), ensure_ascii=True))
        return 1

    input_stream = sys.stdin.buffer
    while True:
        line = input_stream.readline(MAX_REQUEST_BYTES + 2)
        if not line:
            return 0
        if len(line.rstrip(b"\r\n")) > MAX_REQUEST_BYTES or not line.endswith(b"\n"):
            # Drain a long line before processing the next request. This keeps
            # memory bounded and synchronization unambiguous.
            if not line.endswith(b"\n"):
                while True:
                    fragment = input_stream.readline(MAX_REQUEST_BYTES + 2)
                    if not fragment or fragment.endswith(b"\n"):
                        break
            response = _error("REQUEST_TOO_LARGE", "JSONL request exceeds 65536 bytes")
        else:
            try:
                request = json.loads(
                    # utf-8-sig consumes precisely one BOM at byte zero of
                    # this frame. Interior/double BOMs and invalid UTF-8
                    # remain malformed JSON; JSON guards still apply.
                    line.decode("utf-8-sig"),
                    object_pairs_hook=_reject_duplicate_json_keys,
                    parse_constant=_reject_non_json_constant,
                )
            except (UnicodeError, ValueError, RecursionError):
                response = _error("MALFORMED_JSON", "Request must be UTF-8 JSON")
            else:
                response = handle_request(translator, request)
        print(json.dumps(response, ensure_ascii=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
