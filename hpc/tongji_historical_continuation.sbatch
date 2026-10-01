#!/bin/bash
#SBATCH --job-name=agi-newton-historical-continue
#SBATCH --partition=L40
#SBATCH --gres=gpu:l40:1
#SBATCH --cpus-per-task=2
#SBATCH --time=00:50:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
RUN=runs/hpc_v11_historical_continue_seed1692
test ! -e "$RUN/model.pt"
echo '10deb0e421e963ce2e715afa37601d6d0bd9a3bc15dbcc624e24fe8d0ab2a480  runs/hpc_v11_bootstrap_seed1686/model.pt' | sha256sum -c -
echo '6d9bef7d45138291679b0eff11f62c97e0f93129b8831f3265aa1503d023cb8c  data/tokenized_v11_bootstrap/train.bin' | sha256sum -c -
sha256sum data/tokenized_v11_bootstrap/train.bin data/real_pilot_v11/validation.bin data/tokenizer_v11/pre1687_bpe.model
"$PY" src/train_bpe_gpt.py --resume runs/hpc_v11_bootstrap_seed1686/model.pt \
  --train data/tokenized_v11_bootstrap/train.bin --validation data/real_pilot_v11/validation.bin \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model --output-dir "$RUN" \
  --steps 12000 --batch-size 32 --context 512 --width 768 --heads 12 --layers 12 \
  --learning-rate 1e-4 --warmup-steps 500 --log-every 500 --seed 1692 \
  --label historical_continuation_reset_optimizer_not_english_only
"$PY" src/evaluate_generalization_suite.py --checkpoint "$RUN/model.pt" \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model --output "$RUN/generalization_suite.json"
"$PY" src/evaluate_premise_access.py --checkpoint "$RUN/model.pt" \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model --probes audit/streete_clean_reading_probes.json \
  --output "$RUN/streete_reading.json"
sha256sum "$RUN/model.pt"
