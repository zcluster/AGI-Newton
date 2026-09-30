#!/bin/bash
#SBATCH --job-name=agi-newton-v11-eval
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:08:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
RUN=runs/hpc_v11_raw_seed1686
sha256sum "$RUN/model.pt"
"$PY" src/evaluate_generalization_suite.py \
  --checkpoint "$RUN/model.pt" \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --output "$RUN/generalization_suite.json" > /dev/null
echo "evaluation written to $RUN/generalization_suite.json"
