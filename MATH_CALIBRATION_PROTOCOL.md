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

Submitted as Tongji job 2863142 on 2026-10-01 after confirming the user queue was
empty. Submission does not establish completion; verify scheduler state and both
output directories before reporting outcomes.
