#!/bin/bash
#SBATCH --job-name=agi-newton-streete-objective
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
for SEED in 1686 1687 1688; do
  for OBJECTIVE in continuation answer_only; do
    RUN="runs/hpc_objective_replication_${OBJECTIVE}_seed${SEED}"
    if [ "$SEED" = 1686 ]; then
      RUN=runs/hpc_reading_binding_seed1686
      if [ "$OBJECTIVE" = answer_only ]; then RUN=runs/hpc_answer_only_seed1686; fi
    fi
    OUTPUT="audit/streete_${OBJECTIVE}_${SEED}.json"
    test -f "$RUN/model.pt"
    test ! -e "$OUTPUT"
    "$HOME/apps/agi-newton-py312/bin/python" src/evaluate_premise_access.py \
      --checkpoint "$RUN/model.pt" --tokenizer data/tokenizer_v11/pre1687_bpe.model \
      --probes audit/streete_clean_reading_probes.json --output "$OUTPUT"
  done
done
