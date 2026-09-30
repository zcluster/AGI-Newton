#!/bin/bash
#SBATCH --job-name=agi-newton-varied-reading
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
DATA=data/reading_varied
RUN=runs/hpc_reading_varied_seed1686
BASE=runs/hpc_v11_bootstrap_seed1686/model.pt
TOK=data/tokenizer_v11/pre1687_bpe.model
"$PY" src/build_reading_calibration.py --varied --output-dir "$DATA"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/train.jsonl" \
  --output "$DATA/train.bin" --loss-weights-output "$DATA/weights.bin"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/validation.jsonl" --output "$DATA/validation.bin"
"$PY" src/evaluate_premise_access.py --checkpoint "$BASE" --tokenizer "$TOK" \
  --probes "$DATA/probes.json" --output "$DATA/baseline_evaluation.json"
"$PY" src/train_bpe_gpt.py --resume "$BASE" --train "$DATA/train.bin" \
  --loss-weights "$DATA/weights.bin" --validation "$DATA/validation.bin" \
  --tokenizer "$TOK" --output-dir "$RUN" --steps 1000 --batch-size 16 \
  --context 512 --width 768 --heads 12 --layers 12 --precision bf16 \
  --learning-rate 3e-5 --warmup-steps 30 --seed 1686 --log-every 250 \
  --label synthetic_varied_reading_not_historical_only
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes "$DATA/probes.json" --output "$RUN/heldout_reading_boundary_fixed.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" --output "$RUN/premise_reading.json"
"$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" --output "$RUN/generalization_suite.json" > /dev/null
"$PY" src/evaluate_bpe_checkpoint.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" --output "$RUN/direct_evaluation.json" > /dev/null
