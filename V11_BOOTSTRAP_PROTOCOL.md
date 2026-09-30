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
set to see 196.6M tokens. Any change therefore **cannot** be attributed to
the corpus addition alone. This comparison asks whether the combined regime
works, not for an isolated treatment effect. A matched-compute ablation would
be needed before making a causal claim.

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

The dependent Slurm jobs are download **2861664**, CPU preparation
**2861705**, and L40 training/evaluation **2861706**. They use only
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
