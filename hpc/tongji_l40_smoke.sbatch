#!/bin/bash
#SBATCH --job-name=agi-newton-l40-smoke
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:10:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
mkdir -p hpc_smoke

# Infrastructure check only: these data are not a blinded discovery evaluation.
"$PY" src/tokenize_corpus.py \
  --tokenizer data/tokenizer_v3/pre1687_bpe.model \
  --data data/real_pilot/strict_clean.jsonl \
  --output hpc_smoke/train.bin
cp hpc_smoke/train.bin hpc_smoke/validation.bin
"$PY" src/train_bpe_gpt.py \
  --train hpc_smoke/train.bin \
  --validation hpc_smoke/validation.bin \
  --tokenizer data/tokenizer_v3/pre1687_bpe.model \
  --output-dir "hpc_smoke/run_${SLURM_JOB_ID}" \
  --steps 300 --batch-size 16 --context 512 \
  --width 768 --heads 12 --layers 12 \
  --warmup-steps 30 --log-every 50 \
  --label tongji_l40_smoke
