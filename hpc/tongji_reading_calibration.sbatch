#!/bin/bash
#SBATCH --job-name=agi-newton-reading-calibration
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
DATA=data/reading_calibration
BASE=runs/hpc_v11_bootstrap_seed1686/model.pt
RUN=runs/hpc_reading_calibration_aligned_seed1686
TOK=data/tokenizer_v11/pre1687_bpe.model
"$PY" src/build_reading_calibration.py --output-dir "$DATA"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/train.jsonl" \
  --output "$DATA/train.bin" --loss-weights-output "$DATA/weights.bin"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/validation.jsonl" --output "$DATA/validation.bin"
"$PY" src/evaluate_premise_access.py --checkpoint "$BASE" --tokenizer "$TOK" \
  --probes "$DATA/probes.json" --output "$DATA/baseline_evaluation.json"
"$PY" src/train_bpe_gpt.py --resume "$BASE" --train "$DATA/train.bin" \
  --loss-weights "$DATA/weights.bin" --validation "$DATA/validation.bin" \
  --tokenizer "$TOK" --output-dir "$RUN" --steps 300 --batch-size 16 \
  --context 512 --width 768 --heads 12 --layers 12 --precision bf16 \
  --learning-rate 3e-5 --warmup-steps 30 --seed 1686 --log-every 100 \
  --label synthetic_reading_calibration_not_historical_only
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes "$DATA/probes.json" --output "$RUN/heldout_reading.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --output "$RUN/premise_reading.json"
"$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" \
  --tokenizer "$TOK" --output "$RUN/generalization_suite.json"
