"""Research-only clause-boundary observations from a pinned authored corpus.

The boundary table is *not* a generative grammar or a native signal decoder.
It preserves human-authored sentence punctuation and interlinear-gloss order
for five identified source utterances. No unlisted utterance is segmented.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re


CORPUS_GIT_BLOB_SHA1 = "53d9f27d03579a1a3fc700c3394b56f834da784e"
EVIDENCE = "SOURCE_VERIFIED_AUTHOR_IGT_WITH_BOUNDARY_AUDIT"
OPERATORS = frozenset({"PROH", "NEG", "EVID.WIT", "EVID.VRF"})
_MAX_CORPUS_BYTES = 100_000

# Source-specific pair counts and complete orthographic segments. These were
# manually reconciled against the authored IGT, NOT generalized to new prose.
# The actual data bytes must also match the pinned Git object on every read.
_SOURCE_SPANS = {
    "E11": (("Ta’qesh kesh ech.", 3),),
    "E17": (("Ta’qesh.", 1),),
    "E19": (("Threnn’vahl vu ech.", 3),),
    "E27": (("Threnn’vahl reen.", 2), ("Uth’se’run.", 1)),
    "E30": (("Ta’qesh.", 1), ("Veyl’sekh ech.", 2), ("Kesh vu.", 2)),
}


class SourceBoundaryUnavailable(ValueError):
    """Source missing/changed, protected, or unsupported segmentation."""


@dataclass(frozen=True)
class OperatorObservation:
    atom_index: int
    form: str
    gloss: str


@dataclass(frozen=True)
class ClauseObservation:
    source_id: str
    source_git_blob_sha1: str
    evidence: str
    clause_index: int
    orthography: str
    atom_start: int
    atom_end_exclusive: int
    atoms: tuple[tuple[str, str], ...]
    operators: tuple[OperatorObservation, ...]
    qualification_eligible: bool = False


def _repo_root(repo_root: str | Path | None) -> Path:
    return Path(repo_root) if repo_root is not None else Path(__file__).resolve().parents[1]


def _verified_source(repo_root: str | Path | None) -> dict:
    path = _repo_root(repo_root) / "data" / "corpus.json"
    content = path.read_bytes()
    if not 0 < len(content) <= _MAX_CORPUS_BYTES:
        raise SourceBoundaryUnavailable("source size outside audited bound")
    sha = hashlib.sha1(b"blob " + str(len(content)).encode("ascii") + b"\0" + content).hexdigest()
    if sha != CORPUS_GIT_BLOB_SHA1:
        raise SourceBoundaryUnavailable("source Git blob mismatch")
    try:
        rows = json.loads(content)["records"]
    except (ValueError, TypeError, KeyError) as exc:
        raise SourceBoundaryUnavailable("invalid source records") from exc
    if len(rows) != 30 or {row["id"] for row in rows} != {f"E{i:02d}" for i in range(1, 31)}:
        raise SourceBoundaryUnavailable("unexpected source record set")
    return {row["id"]: row for row in rows}


def attested_clause_observations(source_id: str, *, repo_root: str | Path | None = None) -> tuple[ClauseObservation, ...]:
    """Return only explicitly source-pinned clause groupings, or fail closed.

    Physical timing, global negation scope, native prosody, and the pragmatic
    equivalence of unattested variants remain unresolved.
    """
    if type(source_id) is not str or source_id not in _SOURCE_SPANS:
        raise SourceBoundaryUnavailable("no bounded source clause mapping")
    try:
        row = _verified_source(repo_root)[source_id]
        orthography = row["orthography"]
        igt = row["igt"]
    except (OSError, TypeError, KeyError) as exc:
        raise SourceBoundaryUnavailable("source attestation unavailable") from exc
    if type(orthography) is not str or type(igt) is not str:
        raise SourceBoundaryUnavailable("source fields are not text")
    if "⟦" in orthography or "⟧" in orthography or "⟦" in igt or "⟧" in igt:
        raise SourceBoundaryUnavailable("protected source")
    orthographic_sentences = tuple(re.split(r"(?<=[.!?])\s+", orthography.strip()))
    specification = _SOURCE_SPANS[source_id]
    if orthographic_sentences != tuple(part for part, _ in specification):
        raise SourceBoundaryUnavailable("orthographic sentence source drift")
    fields = igt.split()
    if len(fields) % 2:
        raise SourceBoundaryUnavailable("source IGT is not paired")
    pairs = tuple(zip(fields[::2], fields[1::2]))
    if len(pairs) != sum(count for _, count in specification):
        raise SourceBoundaryUnavailable("source IGT span count mismatch")
    observations = []
    start = 0
    for index, (sentence, count) in enumerate(specification):
        slice_ = pairs[start:start + count]
        operators = tuple(OperatorObservation(start + offset, form, gloss)
                          for offset, (form, gloss) in enumerate(slice_)
                          if gloss in OPERATORS)
        observations.append(ClauseObservation(source_id, CORPUS_GIT_BLOB_SHA1,
                                              EVIDENCE, index, sentence,
                                              start, start + count, slice_, operators))
        start += count
    return tuple(observations)
