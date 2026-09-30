#!/bin/bash
#SBATCH --job-name=agi-newton-answer-only
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
DATA=data/reading_binding
RUN=runs/hpc_answer_only_seed1686
TOK=data/tokenizer_v11/pre1687_bpe.model
"$PY" src/tokenize_corpus.py --tokenizer "$TOK" --data "$DATA/train.jsonl" \
  --output "$DATA/answer_only.bin" --loss-weights-output "$DATA/answer_only_weights.bin" --answer-only
cmp "$DATA/train.bin" "$DATA/answer_only.bin"
"$PY" src/train_bpe_gpt.py --resume runs/hpc_v11_bootstrap_seed1686/model.pt \
  --train "$DATA/answer_only.bin" --loss-weights "$DATA/answer_only_weights.bin" \
  --validation "$DATA/validation.bin" --tokenizer "$TOK" --output-dir "$RUN" \
  --steps 1000 --batch-size 16 --context 512 --width 768 --heads 12 --layers 12 \
  --learning-rate 3e-5 --warmup-steps 30 --seed 1686 --log-every 250 \
  --label synthetic_answer_only_not_historical_only
for TYPE in probes copy_probes seen_probes; do
  "$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
    --probes "$DATA/$TYPE.json" --output "$RUN/$TYPE.json"
done
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --probes data/reading_varied/probes.json --output "$RUN/old_reading.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" --output "$RUN/premise_reading.json"
"$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" --output "$RUN/generalization_suite.json" > /dev/null
"$PY" src/evaluate_bpe_checkpoint.py --checkpoint "$RUN/model.pt" --tokenizer "$TOK" \
  --validation data/real_pilot_v11/validation.bin --output "$RUN/direct_retention.json" > /dev/null
