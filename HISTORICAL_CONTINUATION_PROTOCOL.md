# Frozen historical continuation pilot

Before training outputs: resume the unchanged historical V11 weights, SHA-256
`10deb0e421e963ce2e715afa37601d6d0bd9a3bc15dbcc624e24fe8d0ab2a480`.
Use the same 70,125,444-token historical bootstrap stream, tokenizer, architecture
and scientific validation. No synthetic calibration, corrected excerpt, modern
translation or target answer is added. This preserves existing machine-reviewed
corpus limitations; it does not certify purity or create an English-only model.

Add 12,000 updates at batch 32/context 512: 196,608,000 further token exposures,
393,216,000 cumulative exposures (repeated data, not new unique tokens). Fixed
learning rate 1e-4 after 500-step warmup, seed 1692, bf16, one L40. Save in a new
directory; do not overwrite or select among intermediate checkpoints. The trainer
loads weights only, resets optimizer state and uses a new sampling seed. Thus
this is an exploratory continued-pretraining intervention, not an isolated test
of duration or a replicated scaling-law experiment.

Primary descriptive endpoints: the unchanged 12 abstract and four physics free
generation cases, direct Earth–Moon output, and the four already exposed Streete
reading/counterfactual cases. Report all, including retention loss and repetitions.
All endpoints are existing diagnostics, not blind new scientific benchmarks.
Candidate ranking cannot substitute for valid free derivation. No early-stop
selection based on these answers. A positive result needs separate held-out tests
and replication before any discovery claim; a negative result cannot prove that
more training or larger models will fail.

`hpc/tongji_historical_continuation.sbatch` checks the starting checkpoint hash,
logs input hashes and refuses to overwrite the new model. Inspect input hashes
against original encoding artifacts when retrieving results. The anticipated
runtime is roughly the prior 32-minute training plus evaluation, not guaranteed.
Only the isolated AGI-Newton directory is used; no other project is altered.
