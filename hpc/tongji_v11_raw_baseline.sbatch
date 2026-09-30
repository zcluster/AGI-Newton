#!/bin/bash
#SBATCH --job-name=agi-newton-v11-raw
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"

# Raw historical-text baseline only: no synthetic target-premise curriculum.
"$PY" src/train_bpe_gpt.py \
  --train data/real_pilot_v11/train.bin \
  --validation data/real_pilot_v11/validation.bin \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --output-dir runs/hpc_v11_raw_seed1686 \
  --steps 1500 --batch-size 16 --context 512 \
  --width 768 --heads 12 --layers 12 \
  --warmup-steps 100 --log-every 100 \
  --seed 1686 --label hpc_v11_primary_scan_raw_only
