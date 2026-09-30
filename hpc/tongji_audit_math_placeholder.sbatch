#!/bin/bash
#SBATCH --job-name=agi-newton-math-placeholder
#SBATCH --partition=intel
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
for file in data/eebo_v11_bootstrap/general_train.jsonl data/real_pilot_v11/train.jsonl; do
  printf '%s chunks=' "$file"
  wc -l < "$file"
  printf '%s chunks_with_placeholder=' "$file"
  (grep -cF '〈 math 〉' "$file" || true)
  printf '%s placeholder_occurrences=' "$file"
  (grep -oF '〈 math 〉' "$file" || true) | wc -l
done
