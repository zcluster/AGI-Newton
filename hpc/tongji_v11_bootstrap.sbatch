#!/bin/bash
#SBATCH --job-name=agi-newton-v11-bootstrap
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:45:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
RUN=runs/hpc_v11_bootstrap_seed1686

# Same tokenizer and scientific validation as the V11 raw-only baseline.
# The only new training material is screened pre-1687 general English.
"$PY" src/train_bpe_gpt.py \
  --train data/tokenized_v11_bootstrap/train.bin \
  --validation data/real_pilot_v11/validation.bin \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --output-dir "$RUN" \
  --steps 12000 --batch-size 32 --context 512 \
  --width 768 --heads 12 --layers 12 \
  --warmup-steps 500 --log-every 500 \
  --seed 1686 --label hpc_v11_primary_scan_plus_general_english
"$PY" src/evaluate_generalization_suite.py \
  --checkpoint "$RUN/model.pt" \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --output "$RUN/generalization_suite.json" > /dev/null
sha256sum "$RUN/model.pt" "$RUN/report.json" "$RUN/generalization_suite.json"
