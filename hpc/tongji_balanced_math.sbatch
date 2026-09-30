#!/bin/bash
#SBATCH --job-name=agi-newton-balanced
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
TOK=data/tokenizer_v11/pre1687_bpe.model
DATA=data/math_calibration
RUN=runs/hpc_math_balanced_seed1686
test ! -e "$RUN/model.pt"
"$PY" src/build_balanced_math.py
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/balanced_train.jsonl" \
  --output "$DATA/balanced.bin" --loss-weights-output "$DATA/balanced_weights.bin" --answer-only
"$PY" src/train_bpe_gpt.py --resume runs/hpc_v11_bootstrap_seed1686/model.pt \
  --train "$DATA/balanced.bin" --loss-weights "$DATA/balanced_weights.bin" \
  --validation "$DATA/validation.bin" --tokenizer "$TOK" --output-dir "$RUN" \
  --steps 1000 --batch-size 16 --context 512 --width 768 --heads 12 --layers 12 \
  --learning-rate 3e-5 --warmup-steps 30 --seed 1686 --log-every 250 \
  --label synthetic_math_balanced_not_historical_only
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes "$DATA/subtraction_grid.json" --output "$RUN/subtraction_grid.json"
"$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --output "$RUN/generalization_suite.json" > /dev/null
"$PY" src/evaluate_composition_grid.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --output "$RUN/composition_grid.json"
"$PY" src/audit_composition_grid.py "$RUN/composition_grid.json" > "$RUN/composition_audit.json"
"$PY" src/evaluate_bpe_checkpoint.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --validation data/real_pilot_v11/validation.bin --output "$RUN/direct_retention.json" > /dev/null
