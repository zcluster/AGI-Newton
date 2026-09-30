#!/bin/bash
#SBATCH --job-name=agi-newton-pyccle-ranges
#SBATCH --partition=intel
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
cd "$HOME/data/AGI-Newton"
mkdir -p data/eebo/parts
url=https://s3.amazonaws.com/pyccle/pyccle-eebo.tgz
total=1175523327
segments=8
size=$(( (total + segments - 1) / segments ))
pids=()
for i in $(seq 0 $((segments - 1))); do
  start=$((i * size))
  end=$((start + size - 1))
  if ((end >= total)); then end=$((total - 1)); fi
  part=$(printf 'data/eebo/parts/%02d' "$i")
  expected=$((end - start + 1))
  if [[ -f "$part" && $(stat -c %s "$part") -eq $expected ]]; then continue; fi
  (curl -fL --retry 3 --silent --show-error --range "$start-$end" \
    --output "$part" "$url" && \
    [[ $(stat -c %s "$part") -eq $expected ]]) &
  pids+=("$!")
done
for pid in "${pids[@]}"; do wait "$pid"; done
cat data/eebo/parts/{00,01,02,03,04,05,06,07} > data/eebo/pyccle-eebo.tgz.tmp
echo '51d28b97fa8ea8801d5d16df3251c7d6fbd7fe056274ddf1676795f1b5c5a5a5  data/eebo/pyccle-eebo.tgz.tmp' | sha256sum -c -
mv data/eebo/pyccle-eebo.tgz.tmp data/eebo/pyccle-eebo.tgz
tar -tzf data/eebo/pyccle-eebo.tgz | grep -E 'dates-eebo\.csv$'
