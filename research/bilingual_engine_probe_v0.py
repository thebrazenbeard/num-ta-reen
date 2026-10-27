"""Exploratory, in-memory leave-one-out probe of the existing Translator.

Does not mutate source files, and never treats a lexical gloss as a complete
translation of a held-out sentence.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from research import bilingual_eval_v0 as benchmark
import numtareen
from numtareen import Translator


def evaluate_engine(root: Path) -> dict:
    root = root.resolve()
    actual_engine_root = Path(numtareen.__file__).resolve().parents[1]
    if actual_engine_root != root:
        raise ValueError("translator engine and authored data must share one repository root")
    # Fail closed if the source dataset changes independently of the baseline.
    benchmark.load_source(root)

    translator = Translator(root / "data")
    rows = [row for row in translator.corpus if row["id"] not in benchmark.PROTECTED_IDS]
    results = {}
    for direction in ("nt-en", "en-nt"):
        in_sample = Counter()
        held_out = Counter()
        negative = Counter()
        for row in rows:
            source, _ = benchmark.fields(row, direction)
            in_sample[translator.translate(source, direction)["status"]] += 1

            # Suppress *every* source attestation at the tested key while
            # retaining source lexemes and the rest of the authored corpus.
            key = benchmark.normalize(source)
            saved = translator.sentences[direction].pop(key, None)
            try:
                held_out[translator.translate(source, direction)["status"]] += 1
            finally:
                if saved is not None:
                    translator.sentences[direction][key] = saved

            negative[translator.translate(source + " " + benchmark._NEGATIVE_SENTINEL,
                                          direction)["status"]] += 1
        results[direction] = {
            "source_known": dict(in_sample),
            "held_out_sentence": dict(held_out),
            "attested_with_unknown_suffix": negative.get("attested", 0),
            "negative_statuses": dict(negative),
        }
    return {"root": str(root.resolve()), "evaluation_rows": len(rows),
            "engine_status_evidence": results,
            "interpretation": "Lexical and ambiguous mean dictionary matches only; neither scores as correct unseen-sentence translation."}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path, nargs="?", default=benchmark.DEFAULT_ROOT)
    args = ap.parse_args()
    print(json.dumps(evaluate_engine(args.root), indent=2))
