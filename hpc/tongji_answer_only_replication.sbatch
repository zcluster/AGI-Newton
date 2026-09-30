#!/bin/bash
#SBATCH --job-name=agi-newton-objective-replication
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:20:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
DATA=data/reading_binding
TOK=data/tokenizer_v11/pre1687_bpe.model
cmp "$DATA/train.bin" "$DATA/answer_only.bin"
for SEED in 1687 1688; do
  for OBJECTIVE in continuation answer_only; do
    RUN="runs/hpc_objective_replication_${OBJECTIVE}_seed${SEED}"
    test ! -e "$RUN/model.pt"
    TRAIN="$DATA/train.bin"
    WEIGHTS="$DATA/weights.bin"
    if [ "$OBJECTIVE" = answer_only ]; then
      TRAIN="$DATA/answer_only.bin"
      WEIGHTS="$DATA/answer_only_weights.bin"
    fi
    "$PY" src/train_bpe_gpt.py --resume runs/hpc_v11_bootstrap_seed1686/model.pt \
      --train "$TRAIN" --loss-weights "$WEIGHTS" \
      --validation "$DATA/validation.bin" --tokenizer "$TOK" --output-dir "$RUN" \
      --steps 1000 --batch-size 16 --context 512 --width 768 --heads 12 --layers 12 \
      --learning-rate 3e-5 --warmup-steps 30 --seed "$SEED" --log-every 250 \
      --label "synthetic_objective_replication_${OBJECTIVE}_not_historical_only"
    for TYPE in probes copy_probes; do
      "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
        --probes "$DATA/$TYPE.json" --output "$RUN/$TYPE.json"
    done
    "$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
      --output "$RUN/generalization_suite.json" > /dev/null
    "$PY" src/evaluate_bpe_checkpoint.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
      --validation data/real_pilot_v11/validation.bin --output "$RUN/direct_retention.json" > /dev/null
  done
done
