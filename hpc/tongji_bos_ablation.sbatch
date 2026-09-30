#!/bin/bash
#SBATCH --job-name=agi-newton-bos-audit
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
TOK=data/tokenizer_v11/pre1687_bpe.model
OUT=audit/bos_ablation
test ! -e "$OUT"
mkdir -p "$OUT"
for ARM in answer_only subtraction128; do
  MODEL="runs/hpc_math_${ARM}_seed1686/model.pt"
  for MODE in legacy bos; do
    FLAGS=()
    if [ "$MODE" = bos ]; then FLAGS=(--prepend-bos); fi
    "$PY" src/evaluate_premise_access.py --checkpoint "$MODEL" --tokenizer "$TOK" \
      --probes data/math_calibration/subtraction_grid.json \
      --output "$OUT/${ARM}_${MODE}.json" "${FLAGS[@]}"
  done
done
