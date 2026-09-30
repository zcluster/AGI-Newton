#!/bin/bash
#SBATCH --job-name=agi-newton-math-grid
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:20:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
for OBJECTIVE in continuation answer_only; do
  RUN="runs/hpc_math_${OBJECTIVE}_seed1686"
  "$PY" src/evaluate_composition_grid.py --checkpoint "$RUN/model.pt" \
    --tokenizer data/tokenizer_v11/pre1687_bpe.model --output "$RUN/composition_grid.json"
  "$PY" src/audit_composition_grid.py "$RUN/composition_grid.json" > "$RUN/composition_audit.json"
done
