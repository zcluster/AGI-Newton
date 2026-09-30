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
