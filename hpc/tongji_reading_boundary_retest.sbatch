#!/bin/bash
#SBATCH --job-name=agi-newton-reading-retest
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
TOK=data/tokenizer_v11/pre1687_bpe.model
"$PY" tests/test_bpe_prompt_boundary.py
for ARM in hpc_v11_bootstrap_seed1686 hpc_reading_calibration_seed1686; do
  RUN=runs/$ARM
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --probes data/reading_calibration/probes.json --output "$RUN/heldout_reading_boundary_fixed.json"
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --output "$RUN/premise_reading_boundary_fixed.json"
  "$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --output "$RUN/generalization_suite_boundary_fixed.json" > /dev/null
done
