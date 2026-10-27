# V176 equal-duration synthetic acoustic challenge — research only

**Conclusion:** Within one frozen fixed-seed synthetic trial of 128 shaped
malformed 480 ms inputs, **two repeated V138 240 ms packets with consensus
accepted 0/128**, whereas the newer V158 eight-slot 480 ms code **accepted
1/128**. Both achieved 96/96 correct classifications on separately rendered
in-contract positives. V158 still accepted 8/8 publicly forged inputs.

This falsifies any categorical claim that V158 must outperform simple
repetition at equal **airtime**; it does **not** prove general superiority of
repetition. There was only one discordant negative, with two-sided exact
paired p=1.0. Equal duration does not ensure equal energy, channel capacity,
number of carrier bands, synchronization cues, throughput, or noise/channel
realism. The negative generator uses an already-disclosed artificial waveform
family; no humans or actual Ech’ta’reen/Num’ta’reen speech were involved.

## Frozen material

The four copied source artifacts below are byte-identical to the original
independent V176 run (SHA-256 enforced by `tests/test_acoustic_v176.py`):

| File | SHA-256 | Role |
| --- | --- | --- |
| `PROTOCOL.md` | `a08bcbb0378014806b5e9b38a655aa83acb39b038a186892a87ec17c159795fc` | Frozen-before-run internal protocol, append-only outcomes |
| `equal_duration_probe.py` | `81a2e40abdc8855617e218c3c8212276c8ba7943ff5da906369b11a162838896` | Deterministic evaluator |
| `test_equal_duration_probe.py` | `5c884ff81dd7d1b4a33365b0fb1c8abb6436a8cd0673c1ad2c60a84568faf65a` | Original local path-dependent regression tests, archive only |
| `RESULT.json` | `f7f5816eabc8914ef8107d58923cf3f4026a82cbef87c85f1a78e0f60f9ec4fe` | Single frozen confirmatory output |

The original evaluator has an obsolete scratch-directory **default** source
path. Use explicit `--source-dir` when invoking it in this repository:

```bash
python research/acoustic_v176/equal_duration_probe.py --source-dir research/acoustic_v158
python -m unittest discover -s tests -p test_acoustic_v176.py -v
```

The first reproduces the original seeds and prints the JSON result; the
second uses a portable repository-root path, verifies the byte hashes, and
tests both correct and abstaining/error cases. Re-running either is a
**reproducibility check**, not an independent held-out replication.
The archived original `test_equal_duration_probe.py` is retained for source
custody but contains an old scratch-specific path; use the root-discoverable
adapter for CI. The older V138/V158 frozen implementations and their SHA-256
custody remain in [`../acoustic_v158/`](../acoustic_v158/).

The V176 protocol was timestamped only by the project's internal log. It is
not independently time-attested. Neither decoder authenticates a sender;
public forgeries, replay, and simultaneous-source mixtures remain unresolved.

No production translator, canonical vocabulary, source corpus, user-facing
audio renderer, or protected E26 input is changed here. A new code design
requires prospective fixed-budget hypotheses and fresh seeds, not retuning
against this disclosed result.
