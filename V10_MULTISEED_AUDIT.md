# V10: three-seed replication and counterfactual audit

## Finding

V9's single-seed result does **not** establish that weighting final answer
tokens helps or hurts. With identical data and matched seeds, the weighted
arm scored worse at seed 1686, better at 1687, and slightly worse at 1688.
The large between-seed spread is itself the main result of this local pilot.
None of the six models solved a sealed `1 - 3 = -2` case (0/6 each), and none
answered an old-suite physics question by open generation (0/4 each). This
remains a synthetic-only, 1.85M-parameter diagnostic, **not** an experiment
showing Newtonian rediscovery.

| Seed | Arm | New-grid final relation | Narrow equation + answer | Old abstract open | Old physics open |
|---|---|---:|---:|---:|---:|
| 1686 | no weights | 20/204 | 6/204 | 0/12 | 0/4 |
| 1686 | final exponent 16× | 1/204 | 1/204 | 0/12 | 0/4 |
| 1687 | no weights | 32/204 | 16/204 | 1/12 | 0/4 |
| 1687 | final exponent 16× | 42/204 | 25/204 | 1/12 | 0/4 |
| 1688 | no weights | 3/204 | 1/204 | 0/12 | 0/4 |
| 1688 | final exponent 16× | 2/204 | 0/204 | 0/12 | 0/4 |

The two arms for each seed use **the same** training-token stream and initial
random seed; only next-token loss weights differ. Both start from random
initialization, train for 2,000 updates, and use 4 layers, width 128, 4
attention heads, context 256, batch 8, fp32, learning rate `3e-4` and 30
warmup steps on local Mac MPS. The V9 report records the source split,
tokenizer, token and weight hashes, and exact data construction. The control
does not read the weight file. The three paired score differences on 204
cases are `-19`, `+10`, and `-1`; three seeds are insufficient for a stable
population-level treatment effect estimate.

## Post-hoc trivial baselines

The fixed 204-case grid also exposes a simpler failure. A rule that **always
answers exponent 0** is right on 36/204 cases; a rule that always answers
`-2` is right on 24/204. Both require no reading of the premises. Across the
same grid repeated for three seeds, the unweighted models achieve 55/612 and
the weighted models 45/612 exact final relations, versus 108/612 for constant
0. Five of the six individual models are below the constant-0 baseline; the
weighted seed-1687 model is the exception at 42/204.

The sealed `1 - 3` subset has six cases. Constant `-2` would score 6/6 there
while scoring only 18/198 on the other cases. Thus even a future 6/6 sealed
score would not establish composition without strong non-`-2` controls and a
checked derivation. These baselines were added **after** seeing V10 outcomes;
they are descriptive diagnostics, not a preregistered treatment comparison.
The 612 counts repeat one fixed grid across seeds, not 612 independent test
problems. The saved per-case reports support the counts directly.

## Counterfactual sensitivity

`src/audit_composition_grid.py` groups cases with the same prompt wording and
symbol set, then pairs cases differing in exactly one input exponent. It
extracts a unique stated target exponent when possible and asks whether the
change in that exponent equals the oracle change. Each 204-case grid contains
960 eligible **correlated** pairs. This tests local input sensitivity, not
correct scientific reasoning or independent trial accuracy.

| Seed | Arm | Unique relation parsed | Counterfactual pairs consistent / observed |
|---|---|---:|---:|
| 1686 | no weights | 204/204 | 70/960 |
| 1686 | weighted | 178/204 | 91/775 |
| 1687 | no weights | 144/204 | 74/574 |
| 1687 | weighted | 204/204 | 147/960 |
| 1688 | no weights | 121/204 | 15/399 |
| 1688 | weighted | 118/204 | 17/405 |

To calibrate this descriptive metric, the audit shuffles predicted exponents
1,000 times *within each wording × symbol stratum*, preserving the model's
answer distribution and missing-answer pattern. The saved audit JSON contains
the conditional null means, intervals and upper-tail permutation values.
Four of six models show above-null sensitivity on this fixed grid; both seed
1688 models do not. The permutation values are post-hoc diagnostics on a
fixed, non-random grid, **not** inferential evidence of general scientific
discovery or a treatment-effect test. Notably, seed 1686's unweighted model
scored 0/102 under the first wording and 20/102 under the second, whereas
seed 1687 scored 15/102 and 17/102. A single wording split is unstable.

## Reproduce and inspect

Train seeds 1687 and 1688 using the V9 token files and training settings,
passing `--loss-weights /tmp/agi-newton-v9-train.weights` only to the weighted
arm. The training reports below retain all command arguments. Evaluate each
checkpoint with `src/evaluate_composition_grid.py` and
`src/evaluate_generalization_suite.py`, then run:

```bash
python src/audit_composition_grid.py runs/v10_multiseed/seed1687_control_grid.json
```

Reports are in [`runs/v10_multiseed/`](runs/v10_multiseed/): the four new
models each have a `train`, `grid`, and `suite` JSON; audit JSONs cover all six
models, including seed 1686 from V9. Every grid JSON retains all 204 prompts
and generated responses. Checkpoints and token binaries are not committed.
The archived 1686 grid and training reports remain in
[`runs/v9_composition_grid/`](runs/v9_composition_grid/).

## Publication gate

This result corrects a potentially misleading one-seed conclusion, but is
not yet a publishable answer to the project's scientific question. A stronger
study needs a predeclared **semantic-structure** holdout (the current grid
only holds out exact wording), more random seeds or paired confidence
analysis, a verifier of *all* intermediate relations or human trace audit,
and a historical-corpus-trained model tested against meaningful baselines.
The direct Earth--Moon question remains unsolved.
