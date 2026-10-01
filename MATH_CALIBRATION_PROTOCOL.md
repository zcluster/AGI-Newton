# Mathematical calibration and sealed exponent transfer

This pilot tests the next bottleneck in AGI-Newton after repeated relation-reading
improvements failed to transfer to arithmetic or physics. It does not train on
new historical sources and cannot establish historical-only rediscovery.
Settings are fixed on 2026-10-01 before running either new model.

## Dataset and exclusions

`src/build_math_calibration.py` reuses the existing diverse elimination generator,
with structured metadata rather than reconstructing exponents from prose. It emits
three answer styles per question: a worked explanation, a short power expression,
and a complete proportionality statement. Small signed subtraction questions are
added. All answer styles of a question share a split; subtraction paraphrases share
the split for their numerical operands. Exact records are deduplicated.

There are 29,033 training and 1,504 validation records, containing 1,909,406 and
99,323 tokens. The validation set is an internal formatting/data check, not unseen
numerical-combination evidence. The decisive numerator 1 / denominator exponent 3
combination is excluded from every record. Direct subtraction 1 minus 3 and its
reverse are also excluded. Other abstract -2 results are admitted: this seals a
combination, not a target value. No period, distance, gravity, Newton or inverse
terminology is included. Modern notation and instruction construction remain
explicit experimental interventions, not authentic pre-1687 documents.

## Matched objective comparison

Start both models from the same historical V11 checkpoint, not from the best
reading model. Reset optimizers and use seed 1686, 1,000 steps, batch 16, context
512, learning rate 3e-5, warmup 30 and bf16, on one L40 sequentially. Each run sees
8,192,000 input tokens. Compare existing continuation-weighted training with
prompt-masked continuation supervision. For worked answers, the supplied prompt
stops after the question: the model must generate the reasoning, not receive it
as input. For short answers, the prompt includes only the answer delimiter.
Check identical token bytes before training. Objective normalization also changes;
the comparison does not isolate masking alone.

Rebuild with `python src/build_math_calibration.py --output-dir data/math_calibration`.
The small committed audit records hashes; generated JSONL and binaries need not
be committed. Run `hpc/tongji_math_calibration.sbatch` on Tongji after inspecting
the user queue. Each checkpoint gets its own output directory.

## Evaluation and decision

Run the unchanged eight short-answer probes, twelve abstract and four physics
long-form cases, source-reading diagnostic, 96 relation-reading probes, direct
Earth–Moon generation and fixed-window scientific-text retention. Preserve raw
outputs including failures. Exact answers and valid generated final relations
are primary; candidate likelihoods alone never establish success. A correct
physical answer must also respond correctly to changed premises. All these suites
are previously inspected diagnostics, not a fresh blind benchmark.

If basic subtraction still fails, first inspect memorization and answer formats.
If arithmetic succeeds but elimination fails, focus on composition. If abstract
elimination succeeds but physical transfer fails, investigate vocabulary/premise
binding. Even correct supplied-premise physics would not prove retrieval of the
historical premises, universal attraction or a direct Earth–Moon discovery.
One fine-tuning seed and one historical initialization limit inference; successful
effects require replication and fresh held-out tasks before publication claims.

## Execution status

Tongji job 2863142 completed with exit 0, elapsed 4m08s. The grid job 2863144
completed with exit 0, elapsed 1m20s. Both use separate model directories on a
single L40 sequentially. Execution and checkpoint hashes are recorded under
`audit/math_calibration/execution_evidence.json`.

## Additional composition coverage

Before inspecting new model outputs, also specify the existing 204-case composition
grid, including six sealed-pair cases and 198 controls, for both models. Its exact
question wording is disjoint from the new training corpus. It reports a valid final
relation separately from a correct arithmetic trace plus relation, and the existing
audit checks one-input counterfactual consistency. Preserve its original decoding
conditions (100 tokens, minimum length 30), unlike the short-answer diagnostic.
The relation grader is narrow and does not credit a bare numeric answer; report raw
outputs so format failures are distinguishable from arithmetic errors. This is an
existing, previously inspected diagnostic, not a fresh blind evaluation. Run
`hpc/tongji_math_grid.sbatch` only after the training job completes successfully.

## Verified results

| Diagnostic | Continuation weighted | Prompt masked |
| --- | ---: | ---: |
| Exact short answers | 0/8 | 1/8 |
| Abstract final relations | 3/12 | 6/12 |
| Physics final relations | 0/4 | 0/4 |
| Grid final relations | 89/204 | 136/204 |
| Grid correct arithmetic trace and relation | 62/204 | 61/204 |
| Grid sealed combination final relations | 0/6 | 0/6 |
| Unique relation coverage | 143/204 | 177/204 |
| Counterfactual consistent pairs among observed pairs | 233/594 | 469/732 |
| Scientific text mean loss | 5.20994 | 5.17364 |

This is partial abstract mathematical competence, not sealed-combination or
physics success. The prompt-masked model can generate -2 for another combination
in the abstract suite, but not the Newton combination. In an inspected sealed grid
case it correctly substitutes `z^1/z^3` but incorrectly simplifies to `z^-1`.
The control also sometimes copies the wrong denominator. The single short-answer
success is the reversed abstract case, not the sealed case. Direct Earth–Moon
sampling remains irrelevant; an incidental -2 attached to an arbitrary abstract
variable is not a gravitational prediction.
Both models also score 0/96 on the earlier relation-reading diagnostic. They start
from historical V11, not the trained reading model, so this is not a measured loss
of the latter's 94/96 capability; the two isolated calibration branches have not
yet been combined into one model.

The counterfactual audit's permutation null is a within-template diagnostic of
output association, not evidence of independent discoveries or a population
significance claim. Consistent differences can also coexist with wrong absolute
answers. The trace metric is slightly lower under masking despite higher final
relation accuracy. All scientific-text losses remain worse than the historical
checkpoint's fixed-window 4.90960. Whole-stream synthetic validation loss is
0.11900 versus 2.81993, again not directly comparable to the masked training loss.

## Post hoc subtraction check

After seeing sealed subtraction failures, select 14 exact training subtraction
prompts, two for each result -3 through 3, and verify every complete answer occurs
in the training file (two paraphrases for each of seven operand pairs). The
deterministic builder writes `seen_subtraction.json`;
this is a memorization diagnostic, not held-out evaluation. Job 2863150 runs both
models on these prompts without changing either model or the training data.
It completed with exit 0, elapsed 21s. Exact generation is 1/14 for the control
and 0/14 for prompt masking; both rank the correct answer in 4/14 cases. Even
training-prompt subtraction is largely unlearned, so this test cannot attribute
the sealed failures solely to a failure of mathematical generalization.

An objective coverage audit finds subtraction accounts for 10,882/1,909,406 input
tokens (0.57%) and only 1,394/575,730 masked target tokens (0.24%). This imbalance
is a plausible explanation to test, not a demonstrated cause. A subsequent
intervention should compare mathematical family balancing before assuming model
size is the limiting factor, while keeping the sealed pair excluded.

Run `python src/summarise_math_calibration.py` to recompute the paired summary.
The script checks matched short probes, budgets and grid arithmetic, and recomputes
the saved grid grading flags from the actual generated text.

## Fixed input subtraction weighting experiment

On 2026-10-01, before new outcomes, fix subtraction target weight at 128 (including
EOS) and leave other masked target weights at one. Keep every prompt masked, every
input token unchanged, the same historical initialization, seed 1686 and 1,000-step
budget. Compare with the existing masked mathematical checkpoint. This tests loss
allocation without resampling or adding examples. Static weighted target mass for
subtraction rises from 0.24% to 23.70%; this is not measured gradient contribution
because the trainer normalizes within each minibatch. The factor is a single planned
pilot, not a tuned optimum. Changing relative loss can affect clipping and retention.

The deterministic full subtraction grid has 578 prompts: 544 training prompts
(272 operand pairs), 30 internal-validation prompts (15 pairs), and two wording
variants each for 1 minus 3 and 3 minus 1. The former is the sealed Newton combination;
the reverse is excluded only from direct subtraction, not from abstract elimination.
Report format-exact answers and full-suffix integer accuracy, allowing a missing final
period but rejecting explanations, expressions and multiple answers. Also report both
wordings correct per operand pair. Repeated wordings are not independent examples.
Use the same grid on the old baseline and new model. This is new diagnostic coverage
of the same task, not an independently sourced scientific benchmark.

The operational next-stage gate is at least 90% correct training subtraction and
80% correct internal-validation subtraction, plus reporting all four sealed outputs.
These thresholds decide what to investigate next, not publication sufficiency. If
training performance remains poor, inspect learning before blaming generalization;
if arithmetic improves but the sealed algebra and physical transfer still fail,
focus on composition and binding. Retest the unchanged abstract/physical grid,
direct Earth–Moon sample and scientific text retention. Do not certify discovery
from the presence of -2 anywhere in a response. One seed remains insufficient for
general claims. Run `hpc/tongji_subtraction_weight128.sbatch` on one L40 and reproduce
the primary comparison with `src/summarise_subtraction_weight.py`.

Submitted as job 2863237. Another user-owned project was already running at
submission; it was left untouched. The new job requests only one scheduler-managed
L40 and writes exclusively under the AGI-Newton project. Local checks confirm exactly
1,394 target positions change from weight one to 128, no other weights change, and
the input bytes remain identical. Submission does not establish an outcome.

## Subtraction weighting results and next checks

Job 2863237 completed with exit 0, elapsed 3m35s. Runtime weight files on HPC
confirm exactly 1,394 changed target positions and weighted mass 752,768.
The initializer, seed, architecture, learning rate, warmup, precision and
8,192,000-token budget match the old masked model. Raw artifacts and checkpoint
hashes are under `audit/subtraction_weight128/`.

| Metric | Original masked model | Subtraction weight 128 |
| --- | ---: | ---: |
| Training subtraction numeric answers | 32/544 | 13/544 |
| Training operand pairs correct in both wordings | 9/272 | 6/272 |
| Internal validation numeric answers | 3/30 | 3/30 |
| Internal validation pairs correct in both wordings | 1/15 | 1/15 |
| Sealed Newton arithmetic prompts | 0/2 | 0/2 |
| Sealed reverse arithmetic prompts | 0/2 | 0/2 |
| Abstract suite final relations | 6/12 | 2/12 |
| Composition grid final relations | 136/204 | 99/204 |
| Correct grid arithmetic trace and relation | 61/204 | 54/204 |
| Sealed grid final relations | 0/6 | 0/6 |
| Physics final relations | 0/4 | 0/4 |
| Scientific text mean loss | 5.17364 | 5.15677 |

All full-grid numeric successes also satisfy format-exact grading in this run.
Neither model passes the operational subtraction gate. The specific weighting
intervention fails to improve the desired abilities in this paired seed; this is
not a general refutation of underexposure, balancing, or other weight factors.
The direct Earth–Moon sample is still an unrelated abstract formula, not a law.

Before further training, inspect two concrete possibilities. First, tokenization
inserts a BOS marker for each record, whereas current inference starts from the
raw prompt without explicitly prepending BOS. Random-window training also starts
inside records, so this discrepancy is a hypothesis to test, not a proven bug.
Use a labeled BOS/no-BOS inference ablation on identical saved checkpoints and
prompts before changing defaults. Second, arithmetic records occupy a contiguous
small tail of the token stream. Static target mass is not the mean per-minibatch
arithmetic contribution under batchwise normalization; audit sampled exposure
before deciding between resampling and a larger training budget. Do not launch
a weight search or model scaling on the basis of these unverified explanations.

## Frozen BOS inference diagnostic (2026-10-01, before outcomes)

Use both saved masked-math checkpoints (original and subtraction-weight-128),
the identical 578-case subtraction grid, greedy decoding, at most 60 tokens,
and no forced minimum generation length. For each checkpoint rerun legacy
inference and explicit BOS inference. No weights, prompts, candidates, or
training inputs change. The default evaluation remains legacy; the explicit
`--prepend-bos` flag affects both generation and candidate scoring.

Primary outcomes are numeric free-generation correctness by train, internal
validation, and both sealed operand groups, with paired prompt comparison.
Preserve the existing operational gates (90% training and 80% internal validation).
Ranking is secondary. A small improvement does not establish the cause of failure;
even a passed arithmetic gate is not historical scientific discovery. Record
checkpoint and probe hashes and verify legacy outputs reproduce the saved results.
Run `hpc/tongji_bos_ablation.sbatch` on one isolated L40 allocation; no training.

### BOS diagnostic outcome

Tongji job 2863283 completed with exit 0 in 1m31s. Both checkpoints and probe
hashes match across their two modes; all 1,156 legacy generations reproduce the
previous saved outputs exactly. `src/summarise_bos_ablation.py` checks those
invariants and grades free generation using the existing numeric grader.

| Checkpoint / group | Legacy | Explicit BOS |
| --- | ---: | ---: |
| Original masked model / training | 32/544 | 29/544 |
| Original masked model / validation | 3/30 | 2/30 |
| Weight-128 model / training | 13/544 | 19/544 |
| Weight-128 model / validation | 3/30 | 4/30 |
| Either model / sealed Newton operands | 0/2 | 0/2 |
| Either model / sealed reverse operands | 0/2 | 0/2 |

In the original training group BOS rescues four prompts and regresses seven;
in the weighted training group it rescues six and regresses none. Neither
checkpoint approaches the frozen 90% training / 80% validation gates. The missing
explicit BOS is therefore not a sufficient explanation or a working fix for this
arithmetic failure. This does not rule out other input-format or training issues.
Keep legacy inference defaults unchanged. These are two related synthetic
capability checkpoints, one training seed, not evidence of historical discovery.

Raw reports and paired summary are at `audit/bos_ablation/`. Reproduce with
`python src/summarise_bos_ablation.py` after obtaining those four reports and the
previous subtraction audit. Next inspect actual sampled arithmetic exposure
before another training intervention; historical skill coverage remains a separate
source-quality problem, documented in `HISTORICAL_MATH_COVERAGE.md`.

## Arithmetic exposure reconstruction (before outcomes)

Run a CPU-only job using the training host's Python environment and the saved
weight-128 report. Reconstruct seed 1686, CPU model-initialization RNG consumption,
16 initial validation batches, and 1,000 training draws of 16 windows of length
512. Use the original `torch.randint` bounds and shifted next-token target indices.
Only sampling is replayed: no model forward, optimizer, or gradient measurement.
The trainer has no CPU-random operation between training draws in its current
implementation; still, there are no original sampled-index logs to certify an
exact historical replay. Record the runtime, report, weight, and sampled-start hashes.

Measure batches with no arithmetic targets, target-position coverage and exposure
counts, and the mean per-batch normalized arithmetic loss-coefficient mass for
weights one versus 128. Do not mistake global static target mass for this mean,
or either quantity for a measured gradient contribution. A weighting change cannot
increase the number of batches that encounter arithmetic. This diagnostic must
precede selecting another training intervention.

### Exposure result and interpretation

CPU job 2863299 completed with exit 0 in 38s, using PyTorch 2.8.0+cu128. The
reconstructed 1,000 training draws contain arithmetic target tokens in only
74 batches; **926 batches (92.6%) contain none**. Across the 1,394 arithmetic
target positions there are 4,738 sampled exposures, median four per position
(minimum zero, maximum seven); 67 positions are never encountered. These count
next-token targets, not full examples or guaranteed intact question context.

| Arithmetic loss-coefficient mass | Original weight | Weight 128 |
| --- | ---: | ---: |
| Global static stream fraction | 0.242% | 23.703% |
| Mean normalized fraction over reconstructed batches | 0.199% | 5.632% |

The difference follows from batchwise normalization and sparse, clustered
arithmetic targets: a multiplier cannot affect the 926 batches without them.
This is evidence of underexposure in the reconstructed sampling schedule and
explains why the static mass overstates average per-update arithmetic weighting.
It does **not** prove the original training draws exactly matched the reconstruction
(no original index logs), that gradients have these fractions, or that correcting
sampling will solve generation or historical discovery.

The next justified capability intervention is a separately labeled, fixed-budget
balanced curriculum that changes arithmetic exposure rather than another weight
search. Preserve the historical initializer, sealed operands, train/validation
split, optimization settings, and generation gates. Freeze the concrete sampling
construction and comparisons before outcomes, and measure achieved exposure.
Do not substitute this synthetic control for an improved historical math corpus.

Result hashes, runtime and counts are in `audit/arithmetic_exposure.json`; the job
output is `audit/arithmetic_exposure_job2863299.out`. Reproduce using
`python src/audit_arithmetic_exposure.py` on the training host with the saved
report and streams. Source and language coverage remain a separate audit.

## Frozen resampling pilot (before outcomes)

Repeat each of the 544 existing training subtraction records 128 times, retain
each elimination record once, and shuffle with Python seed 1686. No new strings
or answers are authored; the existing validation file and sealed operands remain
unchanged. All answer weights are one and prompts remain masked. The constructor
checks exact multiplicities and split/leakage invariants. This yields 69,632
subtraction records and 28,489 elimination records (98,121 total).

Start from the same V11 historical initializer, training seed 1686, 1,000 steps,
batch 16, context 512, learning rate 3e-5, warmup 30, bf16: 8,192,000 tokens seen.
Keep legacy no-BOS greedy arithmetic evaluation with maximum 60 tokens and no
minimum. Compare all 578 outputs to the old masked and weight-128 checkpoints;
retain 90% training and 80% internal-validation gates. Also measure abstract and
physics generation, the 204-case composition grid including its sealed cases,
and scientific-text retention. Candidate ranking cannot substitute for generation.

This intervention changes token distribution and ordering, not only weight.
At fixed total training budget, arithmetic exposure increases at the expense of
elimination exposure. One seed is exploratory; passing would require replicated
seeds and fresh tests before a research claim. Synthetic capability gains do not
establish historical-only Newton discovery. Record achieved source-token and
target-token proportions; do not assume the repeat factor equals either share.

### Resampling result

L40 job 2863304 completed with exit 0 in 3m04s. The constructor reproduced
the frozen input hash and unchanged validation hash. Saved reports verify
matching initializer path, seed, architecture, optimizer settings and 8,192,000
tokens seen. The checkpoint SHA-256 is
`a270638321e841743f5a1a089d52f3ba7ec0776106cd272f430942a196827faa`.

| Free-generation measure | Original masked model | Resampled |
| --- | ---: | ---: |
| Training subtraction | 32/544 | **537/544** |
| Internal-validation subtraction | 3/30 | **4/30** |
| Sealed 1 minus 3 (two wordings) | 0/2 | **2/2** |
| Sealed 3 minus 1 (two wordings) | 0/2 | **0/2** |
| Abstract final relations | 6/12 | 5/12 |
| Physics final relations | 0/4 | 0/4 |
| Composition-grid final relations | 136/204 | 132/204 |
| Correct grid arithmetic trace and relation | 61/204 | 80/204 |
| Sealed composition-grid relations | 0/6 | 0/6 |

The training-generation gate passes (98.7%), but internal validation fails
(13.3% versus the frozen 80% gate). The sharp train/validation gap is consistent
with overfitting or insufficient algorithmic generalization; it is not proof of
memorization as the sole mechanism. Answering the two standalone `1 - 3` prompts
is not the same as applying that arithmetic inside elimination, much less
deriving a gravitational law from historical sources. The sealed composition
and physics failures remain the decisive boundary.

This single-seed pilot establishes that the earlier inability to reproduce even
training arithmetic was not an unavoidable property of the initializer/model:
a fixed-budget training-distribution intervention substantially changes that
outcome. It does not isolate repetition from shuffling or reduced algebra exposure,
and does not establish robust unseen arithmetic or scientific discovery.
Before further scale-up, investigate held-out arithmetic generalization and
premise binding, and strengthen the audited historical skill inventory. Do not
optimize against the two sealed arithmetic examples or present them as a discovery.

Raw generations, construction audit, matched-settings checks and summary live
under `audit/balanced_math/`; reproduce the comparison with
`python src/summarise_balanced_math.py`.

Local retokenization independently verifies 3,291,420 input tokens and the
98,121-record count. Arithmetic accounts for 1,392,896 input tokens (42.32%)
and 178,432 answer targets; all 752,768 answer targets have weight one, so the
static arithmetic supervision share is 23.70%. The new stream's weight-file hash
is `e745b461b38cfa6d43210443c0466904377025dbae0ed4e4338055c4d9309b7b`.

At the initial result recording, exposure verification was pending. Initial CPU job
2863307 completed, but inspection found that the audit's *hypothetical global
weight-128* fraction reused the actual weight-one array in the generalized
records branch. That counterfactual statistic was wrong; the primary weight-one
statistic was unaffected. The code now explicitly constructs counterfactual
weights, with a mixed-family regression test. A fresh verification submission
lost its SSH response before acknowledgment: inspect the scheduler and
`audit/balanced_exposure_verified.json` before retrying; do not resubmit training.
Do not use the initial counterfactual statistic or claim final exposure verification
until the corrected output is retrieved. `hpc/tongji_balanced_exposure.sbatch`
only audits on CPUs and protects the corrected output from overwrite.

### Corrected exposure verification and post-hoc error analysis

The disconnected verification submission was **job 2863312**, now confirmed
COMPLETED with exit 0 in 44s. Its corrected output and logs have been retrieved
at `audit/balanced_exposure_verified.json` and
`audit/balanced_exposure_job2863312.out`. Report, record, and weight hashes match
the local archived artifacts. The sampling reconstruction encounters arithmetic
targets in all 1,000 batches, with a mean normalized arithmetic loss-coefficient
mass of **24.106%** at the actual weight one, versus 0.199% in the original
sampling reconstruction. The 178,432 repeated target positions receive 446,766
exposures. These are token-copy exposures, not counts of unique mathematical
examples or exact logged training indices. The hypothetical weight-128 figures
in this corrected report are not settings used in the balanced training run.

The primary exact-generation verdict is unchanged: training passes, validation
fails. A separately labeled **post-hoc** analysis of the same validation prompts
finds that all 30 resampled-model outputs are parseable integers. Four are exact;
the other 26 differ from ground truth by precisely one (16 too high, 10 too low).
The original model has 29 parseable outputs, three exact and no off-by-one errors.
Mean absolute error on parseable outputs is 5.931 for the original (29 answers)
and 0.867 for the resampled model (30 answers). Denominators differ; this is not
a frozen primary comparison or a significance claim. Counts and exclusions are
preserved in the updated `audit/balanced_math/summary.json`.

The finding rules out output formatting as the main explanation on these
validation cases and cautions against describing the model as *only* memorizing.
It is consistent with partial numerical generalization, local interpolation, or
other answer priors, not proof of an exact subtraction algorithm. It does not
justify rounding corrections, consulting ground truth at inference, or tuning
against the sealed Newton operands. Next use newly frozen operand-range and
wording tests to distinguish these possibilities before changing the curriculum.
Keep basic arithmetic precision, algebraic composition, historical premise access,
and actual discovery as separate requirements.
