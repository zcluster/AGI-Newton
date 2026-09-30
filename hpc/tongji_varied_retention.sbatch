#!/bin/bash
#SBATCH --job-name=agi-newton-varied-retention
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
for ARM in hpc_v11_bootstrap_seed1686 hpc_reading_varied_seed1686; do
  "$HOME/apps/agi-newton-py312/bin/python" src/evaluate_bpe_checkpoint.py \
    --checkpoint "runs/$ARM/model.pt" --tokenizer data/tokenizer_v11/pre1687_bpe.model \
    --validation data/real_pilot_v11/validation.bin \
    --output "runs/$ARM/varied_retention.json" > /dev/null
done
