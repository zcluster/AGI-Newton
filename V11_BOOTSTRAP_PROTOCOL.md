# V11 historical-language bootstrap: frozen pilot protocol

Frozen before seeing the bootstrap model's outputs on 2026-09-30. This is an
engineering comparison, not a preregistered causal study or a rediscovery
claim.

## Question and arms

Does adding screened, pre-1687 ordinary English to the V11 primary-scan
scientific core improve the model's ability to answer the held-out physics
questions by **free generation**? The completed raw-only arm is recorded in
[`V11_PRIMARY_SCAN_CORPUS.md`](V11_PRIMARY_SCAN_CORPUS.md). The new arm uses
the same 8,000-piece V11 tokenizer, 91.5M-parameter architecture, scientific
validation stream, and random seed 1686. Its training stream concatenates
the reconstructed 200 MB PYCCLE EEBO Phase-I training subset with the V11
strict scientific training chunks. No synthetic math or target-answer text is
added. The EEBO ingestion quarantines Newton references and policy-detected
target/modern terms.

The training budgets differ: raw-only saw 12.3M tokens; the bootstrap job is
set to see 196.6M tokens. Given uniform random windows in a 70.1M-token
mixture containing 4.29M scientific tokens, its *expected* scientific-token
exposure is about 12.0M, close to raw-only's 12.3M. This does **not** equalize
total compute, optimization trajectory, or sample order. Any change therefore
cannot be attributed to the corpus addition alone. This comparison asks
whether the combined regime works, not for an isolated treatment effect. A
matched-compute ablation would be needed before making a causal claim.

## Fail-closed data and execution gates

1. Download the public 1,175,523,327-byte archive and require SHA-256
   `51d28b97fa8ea8801d5d16df3251c7d6fbd7fe056274ddf1676795f1b5c5a5a5`.
2. Extract its date CSV, re-run [`src/ingest_pyccle_eebo.py`](src/ingest_pyccle_eebo.py),
   and require the new audit JSON to equal the earlier committed
   [`general_audit.json`](data/eebo_pre1687/general_audit.json) exactly.
3. Encode only the accepted EEBO training documents plus the V11 strict
   training split with the existing V11 tokenizer. Keep the already frozen
   V11 scientific validation stream separate.
4. Only if steps 1–3 succeed, train on one Tongji L40 using
   [`hpc/tongji_v11_bootstrap.sbatch`](hpc/tongji_v11_bootstrap.sbatch): 12,000
   steps, batch 32, context 512, bf16, seed 1686. Evaluate with the existing
   12 abstract and four premise-given physics cases. Checkpoints stay on HPC;
   reports, hashes, and logs will be committed.

Steps 1–3 passed. The rebuilt EEBO audit is byte-identical to the earlier
committed audit (SHA-256
`4d884454d325e640d8b3ff11132b304cda7b5a165a105fbf178356e05e2a393c`):
1,179 training documents, 18 validation documents, 1,112 quarantined
documents, and 200,033,084 training-text bytes. The rebuilt general training
JSONL hashes to
`8ff8e4fdc64b36df1dac2f2863b38d3f7c95c3f1b26379240210cfa8a6676bde`.
The combined token stream has **70,125,444 tokens** and SHA-256
`6d9bef7d45138291679b0eff11f62c97e0f93129b8831f3265aa1503d023cb8c`.
The L40 job completed. Its [result and limitations](V11_BOOTSTRAP_RESULTS.md)
are recorded separately from this frozen protocol.

Download **2861859** passed the archive hash; CPU job **2861860** rebuilt the
EEBO audit exactly but failed during encoding because the V11 `train.jsonl`
had not been copied to HPC. That file was transferred and verified against
its committed SHA-256. The current dependent jobs are CPU encoding
**2861974** and L40 training/evaluation **2861975**. The earlier download
chain (2861664, 2861705, 2861706) was cancelled after S3 stalled; its 770 MB
of partial ranges were retained for the successful resumed transfer. The jobs
use only
`~/data/AGI-Newton` and its Python environment. Other project directories
and environments are outside their paths.

## Interpretation rule

Lower validation loss and fluent historical prose show language learning,
not physical discovery. Candidate ranking is diagnostic only. A positive
physics result would require an explicit, correct, non-copied free derivation
from the two premises and consistent answers across distinct wording and
non-`-2` controls. The direct Earth–Moon question must also be reported
separately; success when the decisive premises are supplied is weaker than
independent rediscovery. The fixed four physics cases are too few for a
publication-level success claim, even if all four pass.
