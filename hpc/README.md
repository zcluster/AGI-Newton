# Tongji HPC: AGI-Newton

Use the project-only directory `~/data/AGI-Newton` and the project-only
Python environment `~/apps/agi-newton-py312`.
Do not use or modify the separate SSNS project or its environment. Submit GPU
work with `sbatch`; do not train on a login node.

Create `logs/`, then submit `sbatch hpc/tongji_l40_smoke.sbatch` from the
AGI-Newton directory. It
requests one L40, two CPU cores, and at most ten minutes. Logs and results
stay under `logs/` and `hpc_smoke/`. Its training and validation
streams deliberately overlap: **this tests infrastructure only**, not
generalization or scientific discovery.

On 2026-09-30, the L40 partition exposed a 48 GB L40 with driver 580.65.06
and CUDA 13.0. Job 2859908 completed 30 steps; job 2859932 completed 300
steps in 70 seconds total, including startup, evaluation, and checkpointing.
The latter's training loop took 21.3 seconds and allocated at most 4.99 GB
of GPU memory (PyTorch's measurement). Both used a 91,510,272-parameter model.
The posted rates are ¥2 per L40 GPU-hour and ¥4 per A800 GPU-hour, plus
CPU-core charges. Use L40 for current ~91.5M-parameter runs;
consider A800 only if a future run exceeds 48 GB or measured throughput
justifies its higher price. Corpus review, split design, and audits belong on
the Mac or CPU nodes. Longer GPU training should wait for a predeclared
semantic holdout and approved historical sources.

The V11 primary-scan raw-text-only baseline and separate evaluation completed
as jobs 2861419 and 2861442. Results and input hashes are in
[`V11_PRIMARY_SCAN_CORPUS.md`](../V11_PRIMARY_SCAN_CORPUS.md). It failed the
free-generation and transfer tests; the checkpoint is retained on HPC. Both
jobs ran only in `~/data/AGI-Newton`, not the SSNS project.

The separate V11 historical-English bootstrap run is documented in
[`V11_BOOTSTRAP_RESULTS.md`](../V11_BOOTSTRAP_RESULTS.md). Its CPU download,
rebuild, and encoding jobs gated L40 job 2861975; all work remained in the
AGI-Newton directory. Language validation improved, but free mathematical
and physics derivations still failed.
