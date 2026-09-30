#!/bin/bash
#SBATCH --job-name=agi-newton-math-calibration
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
DATA=data/math_calibration
TOK=data/tokenizer_v11/pre1687_bpe.model
"$PY" src/build_math_calibration.py --output-dir "$DATA"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/train.jsonl" \
  --output "$DATA/train.bin" --loss-weights-output "$DATA/weights.bin"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/train.jsonl" \
  --output "$DATA/answer_only.bin" --loss-weights-output "$DATA/answer_only_weights.bin" --answer-only
cmp "$DATA/train.bin" "$DATA/answer_only.bin"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/validation.jsonl" --output "$DATA/validation.bin"
for OBJECTIVE in continuation answer_only; do
  RUN="runs/hpc_math_${OBJECTIVE}_seed1686"
  test ! -e "$RUN/model.pt"
  TRAIN="$DATA/train.bin"
  WEIGHTS="$DATA/weights.bin"
  if [ "$OBJECTIVE" = answer_only ]; then
    TRAIN="$DATA/answer_only.bin"
    WEIGHTS="$DATA/answer_only_weights.bin"
  fi
  "$PY" src/train_bpe_gpt.py --resume runs/hpc_v11_bootstrap_seed1686/model.pt \
    --train "$TRAIN" --loss-weights "$WEIGHTS" --validation "$DATA/validation.bin" \
    --tokenizer "$TOK" --output-dir "$RUN" --steps 1000 --batch-size 16 \
    --context 512 --width 768 --heads 12 --layers 12 --learning-rate 3e-5 \
    --warmup-steps 30 --seed 1686 --log-every 250 \
    --label "synthetic_math_${OBJECTIVE}_not_historical_only"
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --probes tests/fixtures/short_elimination_probes.json --output "$RUN/short_elimination.json"
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --probes data/reading_binding/probes.json --output "$RUN/reading.json"
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --output "$RUN/premise_reading.json"
  "$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --output "$RUN/generalization_suite.json" > /dev/null
  "$PY" src/evaluate_bpe_checkpoint.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --validation data/real_pilot_v11/validation.bin --output "$RUN/direct_retention.json" > /dev/null
done
