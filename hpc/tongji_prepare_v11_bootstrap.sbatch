#!/bin/bash
#SBATCH --job-name=agi-newton-v11-prepare
#SBATCH --partition=intel
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=01:00:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
PY="$HOME/apps/agi-newton-py312/bin/python"
archive=data/eebo/pyccle-eebo.tgz
mapfile -t dates < <(tar -tzf "$archive" | grep -E '(^|/)dates-eebo\.csv$')
[[ ${#dates[@]} -eq 1 ]]
tar -xOzf "$archive" "${dates[0]}" > data/eebo/dates-eebo.csv
"$PY" src/ingest_pyccle_eebo.py \
  --archive "$archive" --dates data/eebo/dates-eebo.csv \
  --output-dir data/eebo_v11_bootstrap \
  --sample-documents 5000 --max-train-bytes 200000000
"$PY" -c 'import json; from pathlib import Path; old=json.loads(Path("data/eebo_pre1687/general_audit.json").read_text()); new=json.loads(Path("data/eebo_v11_bootstrap/general_audit.json").read_text()); assert old==new, "EEBO rebuild differs from prior audit"'
"$PY" src/tokenize_corpus.py \
  --tokenizer data/tokenizer_v11/pre1687_bpe.model \
  --data data/eebo_v11_bootstrap/general_train.jsonl data/real_pilot_v11/train.jsonl \
  --output data/tokenized_v11_bootstrap/train.bin
sha256sum data/eebo_v11_bootstrap/general_train.jsonl data/tokenized_v11_bootstrap/train.bin
