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

The original encoding job `2861974` records training-stream SHA-256
`6d9bef7d45138291679b0eff11f62c97e0f93129b8831f3265aa1503d023cb8c`
in `runs/hpc_v11_bootstrap_seed1686/agi-newton-v11-encode-2861974.out`.
The submission script now requires this exact digest, rather than merely logging
the current file's hash. Checkpoint and training-stream mismatch stop before
training. Remote upload/submission attempts have not yielded any job ID; the
latest diagnostic connection closes during key exchange, before authentication.
Reconcile the remote script and scheduler state before retrying submission.
