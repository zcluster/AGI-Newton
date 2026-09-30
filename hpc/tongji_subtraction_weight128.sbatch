#!/bin/bash
#SBATCH --job-name=agi-newton-subtraction128
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:20:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
DATA=data/math_calibration
TOK=data/tokenizer_v11/pre1687_bpe.model
RUN=runs/hpc_math_subtraction128_seed1686
test ! -e "$RUN/model.pt"
"$PY" src/build_math_calibration.py --output-dir "$DATA"
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/train.jsonl" \
  --output "$DATA/subtraction128.bin" --loss-weights-output "$DATA/subtraction128_weights.bin" \
  --answer-only --subtraction-weight 128
cmp "$DATA/answer_only.bin" "$DATA/subtraction128.bin"
"$PY" src/train_bpe_gpt.py --resume runs/hpc_v11_bootstrap_seed1686/model.pt \
  --train "$DATA/subtraction128.bin" --loss-weights "$DATA/subtraction128_weights.bin" \
  --validation "$DATA/validation.bin" --tokenizer "$TOK" --output-dir "$RUN" \
  --steps 1000 --batch-size 16 --context 512 --width 768 --heads 12 --layers 12 \
  --learning-rate 3e-5 --warmup-steps 30 --seed 1686 --log-every 250 \
  --label synthetic_math_subtraction128_not_historical_only
for MODEL in runs/hpc_math_answer_only_seed1686 "$RUN"; do
  "$PY" src/evaluate_premise_access.py --checkpoint "$MODEL/model.pt" --tokenizer "$TOK" \
    --probes "$DATA/subtraction_grid.json" --output "$MODEL/subtraction_grid.json"
done
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes tests/fixtures/short_elimination_probes.json --output "$RUN/short_elimination.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes "$DATA/seen_subtraction.json" --output "$RUN/seen_subtraction.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes data/reading_binding/probes.json --output "$RUN/reading.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" --output "$RUN/premise_reading.json"
"$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --output "$RUN/generalization_suite.json" > /dev/null
"$PY" src/evaluate_composition_grid.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --output "$RUN/composition_grid.json"
"$PY" src/audit_composition_grid.py "$RUN/composition_grid.json" > "$RUN/composition_audit.json"
"$PY" src/evaluate_bpe_checkpoint.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --validation data/real_pilot_v11/validation.bin --output "$RUN/direct_retention.json" > /dev/null
