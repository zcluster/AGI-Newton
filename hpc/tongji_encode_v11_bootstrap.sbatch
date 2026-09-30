#!/bin/bash
#SBATCH --job-name=agi-newton-v11-encode
#SBATCH --partition=intel
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
echo '250f1148d3d77132e21f4c5dbecc240d1eac91daf900c34db8481a2c4076f83c  data/real_pilot_v11/train.jsonl' | sha256sum -c -
"$PY" -c 'import json; from pathlib import Path; old=json.loads(Path("data/eebo_pre1687/general_audit.json").read_text()); new=json.loads(Path("data/eebo_v11_bootstrap/general_audit.json").read_text()); assert old==new, "EEBO rebuild differs from prior audit"'
"$PY" src/tokenize_corpus.py \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --data data/eebo_v11_bootstrap/general_train.jsonl data/real_pilot_v11/train.jsonl \
  --output data/tokenized_v11_bootstrap/train.bin
sha256sum data/eebo_v11_bootstrap/general_train.jsonl data/tokenized_v11_bootstrap/train.bin
