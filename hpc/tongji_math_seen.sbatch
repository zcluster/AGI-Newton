#!/bin/bash
#SBATCH --job-name=agi-newton-math-seen
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
for OBJECTIVE in continuation answer_only; do
  RUN="runs/hpc_math_${OBJECTIVE}_seed1686"
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" \
    --tokenizer data/tokenizer_v11/pre1687_bpe.model \
    --probes data/math_calibration/seen_subtraction.json --output "$RUN/seen_subtraction.json"
done
