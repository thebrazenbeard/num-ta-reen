"""Noncanonical, read-only pronunciation evidence for Nûm’ta’reen.

This is a source lookup and human-learning aid, NOT a grapheme-to-phoneme
model, acoustic reconstruction, or claim about native Ech’ta’reen signals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


# Frozen author-supplied Wreckforge source snapshot; this is evidence custody,
# not an assertion that these texts exhaust the possible language.
SOURCE_SHA256 = {
    "data/corpus.json": "5bc4c939e728e9e5bce1875eafcba9e71609570281bebb87dc7e64e2e9a6d229",
    "data/lexicon.json": "208d5daa5953383cccbac6a145df795531691ec60248256dc2e18a5651c6ba08",
    "sources/reference_grammar_v2_updated_lphoneme.txt": "2771ccd4456aa8340479daf76f9e3953c4f04eedb2cb1ff9270f3b9f9c02d1b3",
    "sources/dictionary_v2_updated_lphoneme.txt": "612c1326293af1e6606da7ce72b13eb08b13c51bc435fc677591a8acbdbd290c",
}


@dataclass(frozen=True)
class PronunciationEvidence:
    status: str
    ipa: str | None
    evidence_class: str
    source_document: str | None
    source_locator: str | None
    register: str | None
    laryngeal_interruptions_attested: bool | None
    phonemic_length_attested: bool | None
    scope_or_resonance_frequency_hz: None
    caution: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def _key(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("lookup text must be a string")
    value = value.replace("\r\n", "\n")
    # The attested E27 corpus item comprises two lines. Permit that exact
    # separator without accepting other terminal control characters.
    if len(value) > 8192 or not value.strip() or any(
        unicodedata.category(c) == "Cs" or (ord(c) < 32 and c != "\n")
        for c in value
    ):
        raise ValueError("lookup text contains unsupported characters")
    return unicodedata.normalize("NFC", value).casefold()


def _verify_bytes(root: Path, path: str) -> bytes:
    """Fail closed when the caller supplies a forged or outdated source tree.

    Hash and deserialize the *same bytes* so a second ordinary read does not
    turn the hash check into a content-independent endorsement of source text.
    Any later author amendment requires explicitly reviewing and updating the
    pins; an arbitrary caller cannot produce AUTHOR_ATTESTED_* evidence.
    """
    actual = (root / path).read_bytes()
    # Git fixes the normalized JSON to LF via .gitattributes. The extracted
    # source .txt files have no such rule and Windows may check out CRLF;
    # normalize *only* that Git line-ending conversion for provenance.
    stable = actual.replace(b"\r\n", b"\n") if path.startswith("sources/") else actual
    if hashlib.sha256(stable).hexdigest() != SOURCE_SHA256[path]:
        raise ValueError(f"source snapshot mismatch: {path}")
    return actual


def _read_json_verified(root: Path, path: str) -> dict[str, Any]:
    return json.loads(_verify_bytes(root, path).decode("utf-8"))


def _evidence(
    *,
    status: str,
    ipa: str | None = None,
    evidence_class: str = "UNKNOWN",
    source_document: str | None = None,
    source_locator: str | None = None,
    register: str | None = None,
    cautions: tuple[str, ...] = (),
) -> PronunciationEvidence:
    # Only source-written IPA licenses feature observations. Never synthesize
    # formant values, acoustic bands, prosody, or phonetic strings from spelling.
    return PronunciationEvidence(
        status=status,
        ipa=ipa,
        evidence_class=evidence_class,
        source_document=source_document,
        source_locator=source_locator,
        register=register,
        laryngeal_interruptions_attested=("ʔ" in ipa) if ipa else None,
        phonemic_length_attested=("ː" in ipa) if ipa else None,
        scope_or_resonance_frequency_hz=None,
        caution=cautions,
    )


class AttestedPronunciationGuide:
    """Look up attested complete utterances or separately attested lexemes.

    The consumer supplies an explicit checked-out Num’ta’reen repository root;
    no fallback to network sources or invented grapheme conversion exists.
    """

    def __init__(self, repo_root: Path | str) -> None:
        root = Path(repo_root)
        corpus = _read_json_verified(root, "data/corpus.json")
        lexicon = _read_json_verified(root, "data/lexicon.json")
        _verify_bytes(root, "sources/reference_grammar_v2_updated_lphoneme.txt")
        _verify_bytes(root, "sources/dictionary_v2_updated_lphoneme.txt")
        if corpus.get("record_count") != len(corpus.get("records", [])):
            raise ValueError("corpus count does not match records")
        if lexicon.get("entry_count") != len(lexicon.get("entries", [])):
            raise ValueError("dictionary count does not match entries")
        self._corpus: dict[str, dict[str, Any]] = {}
        self._lexicon: dict[str, dict[str, Any]] = {}
        for record in corpus["records"]:
            if record["id"] == "E26":
                continue  # Deliberately withhold the protected chord notation.
            key = _key(record["orthography"])
            if key in self._corpus:
                raise ValueError("colliding corpus orthography")
            self._corpus[key] = record
        for entry in lexicon["entries"]:
            key = _key(entry["headword"])
            if key in self._lexicon:
                raise ValueError("colliding dictionary headword")
            self._lexicon[key] = entry

    def lookup(self, text: str) -> PronunciationEvidence:
        key = _key(text)
        if key == "e26" or "⟦" in key or "⟧" in key:
            return _evidence(
                status="WITHHELD",
                cautions=("Protected unspoken true-name chord; no phonetic realization is supplied.",),
            )
        record = self._corpus.get(key)
        if record:
            ipa = record.get("ipa")
            if not isinstance(ipa, str) or not ipa.startswith("/"):
                return _evidence(status="UNKNOWN", cautions=("Attested utterance has no speakable IPA.",))
            cautions = [
                "Corpus IPA is an attested field transcription, not measured native resonance.",
                "Whole-utterance IPA cannot be generalized to unattested new sentences.",
            ]
            if record["id"] == "E13":
                cautions.append(
                    "Source conflict: së orthography and /sɛn/ in E13 remain unresolved."
                )
            return _evidence(
                status="ATTESTED_UTTERANCE",
                ipa=ipa,
                evidence_class="AUTHOR_ATTESTED_CORPUS",
                source_document="sources/reference_grammar_v2_updated_lphoneme.txt",
                source_locator=record["id"],
                cautions=tuple(cautions),
            )
        entry = self._lexicon.get(key)
        if entry:
            ipa = entry.get("ipa")
            if not isinstance(ipa, str) or not ipa.strip():
                return _evidence(status="UNKNOWN", cautions=("No lexical IPA was supplied.",))
            return _evidence(
                status="ATTESTED_LEXEME",
                ipa="/" + ipa.strip("/") + "/",
                evidence_class="AUTHOR_LEXICON_REFERENCE",
                source_document="sources/dictionary_v2_updated_lphoneme.txt",
                source_locator=f"line:{entry['source_line']}",
                register=entry.get("register"),
                cautions=(
                    "Isolated lexical IPA does not establish pronunciation after clitic attachment.",
                    "Native Ech’ta’reen resonance is not reconstructed from this symbol string.",
                ),
            )
        return _evidence(
            status="UNKNOWN",
            cautions=("No attested IPA. Do not infer pronunciation from spelling.",),
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Noncanonical source-attested Num’ta’reen pronunciation lookup"
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("text", help="whole attested utterance or dictionary headword")
    args = parser.parse_args()
    guide = AttestedPronunciationGuide(args.repo_root)
    result = guide.lookup(args.text)
    print(json.dumps(result.as_dict(), ensure_ascii=False, sort_keys=True))
    return 0 if result.status.startswith("ATTESTED") else 2


if __name__ == "__main__":
    raise SystemExit(main())

