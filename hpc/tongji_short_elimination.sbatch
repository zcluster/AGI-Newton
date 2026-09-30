#!/bin/bash
#SBATCH --job-name=agi-newton-short-elimination
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
for RUN in hpc_v11_bootstrap_seed1686 hpc_reading_binding_seed1686 hpc_answer_only_seed1686; do
  "$PY" src/evaluate_premise_access.py --checkpoint "runs/$RUN/model.pt" \
    --tokenizer data/tokenizer_v11/pre1687_bpe.model \
    --probes tests/fixtures/short_elimination_probes.json \
    --output "runs/$RUN/short_elimination.json"
done
