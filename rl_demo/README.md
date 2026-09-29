# Synthetic RL engineering demo

This is a **separate toy experiment**, not RL training of the historical
pre-Newtonian language model. A 69,065-parameter randomly initialized
Transformer reads eight numerical observations and emits three coefficients
of a quadratic equation. It receives a supervised warm-start from exhaustive
search, then 25 policy-gradient updates. Reward uses only observed points;
extrapolation points remain hidden until evaluation.

## Recorded results

Extrapolation normalized mean squared error (NMSE; lower is better) on 64
held-out quadratic coefficient combinations:

| Run | SFT only | SFT + RL | Exhaustive search |
|---|---:|---:|---:|
| [Mac MPS](results/mac_mps_verified/report.md) | 2.4444 | 0.6954 | 0.0000 |
| [RTX 5090 CUDA](results/cuda_verified/report.md) | 2.4444 | 2.6516 | 0.0000 |

The independent Mac run improved; the CUDA run did not. These are single-seed
results and **do not establish a reliable RL generalization gain**. The model
also performs poorly on out-of-grammar sine worlds. The [Mac plot](results/mac_mps_verified/results.png)
and [CUDA plot](results/cuda_verified/results.png) show the recorded curves and
baselines. The corresponding `report.json` files contain raw metrics, training
history, environment, hashes, and sample predictions.

The same Mac checkpoint and saved evaluation worlds were evaluated on both
devices: [Mac](results/mac_shared_eval/report.json) and
[CUDA](results/mac_on_cuda_shared/report.json) give held-out NMSE
`0.6953793764`, with maximum aggregate metric difference `5.96e-8`.
[CUDA resume](results/resume_cuda/report.json) verified loading the Mac
optimizer state and updating weights. Model checkpoints and test tensors are
not committed here.

**Provenance caveat:** the initial training and resume reports record source
SHA-256 `080759…dad6b`; the current `run_demo.py` and both cross-device
reevaluation reports record `265c91…e24`. The original training-source revision
is not archived in this repository, so those initial trajectories are not
byte-for-byte reproducible from this commit. The reported outcomes are kept
as historical records, not presented as a new rerun.

## Run a fresh experiment

From the repository root, install `requirements.txt` and run:

```bash
python rl_demo/test_demo.py
python rl_demo/run_demo.py --device auto --sft-steps 100 --rl-steps 25 --out runs/rl_demo_local
```

Use a fresh `--out` directory each time. `--device auto` selects CUDA, then
MPS, then CPU; specify a device explicitly to forbid fallback. To render a
plot, install optional `matplotlib` and run
`python rl_demo/plot_results.py runs/rl_demo_local/report.json`.

This validates a Mac-to-GPU RL workflow and evaluation boundaries. It does
not demonstrate Newtonian rediscovery or open-ended scientific discovery.
