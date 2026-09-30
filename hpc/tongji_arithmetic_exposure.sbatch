#!/bin/bash
#SBATCH --job-name=agi-newton-exposure
#SBATCH --partition=amd
#SBATCH --cpus-per-task=2
#SBATCH --time=00:05:00
#SBATCH --output=logs/%x-%j.out
set -euo pipefail
cd "$HOME/data/AGI-Newton"
test ! -e audit/arithmetic_exposure.json
"$HOME/apps/agi-newton-py312/bin/python" src/audit_arithmetic_exposure.py
