#!/bin/bash
#SBATCH --job-name=agi-newton-premise-reading
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
"$HOME/apps/agi-newton-py312/bin/python" src/evaluate_premise_access.py \
  --checkpoint runs/hpc_v11_bootstrap_seed1686/model.pt \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --output runs/hpc_v11_bootstrap_seed1686/premise_reading.json
