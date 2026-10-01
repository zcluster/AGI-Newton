#!/bin/bash
#SBATCH --job-name=agi-newton-transfer
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
for ARM in answer_only balanced; do
  test ! -e "audit/arithmetic_transfer/${ARM}.json"
  "$PY" src/evaluate_premise_access.py --checkpoint "runs/hpc_math_${ARM}_seed1686/model.pt" \
    --tokenizer data/tokenizer_v11/pre1687_bpe.model --probes audit/arithmetic_transfer/probes.json \
    --output "audit/arithmetic_transfer/${ARM}.json"
done
