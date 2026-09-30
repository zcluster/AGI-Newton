# Answer-only objective comparison

Frozen before outputs, 2026-10-01. The copying/binding augmentation returned square
on all 96 held-out relation cases and all 16 inspected training cases. This pilot
tests whether supervising answers alone changes that behavior; it adds no data.

Dataset: unchanged `data/reading_binding/train.jsonl`, 17,880 records, SHA256
`75031726a1b03aa3883fec8842ff3f5ff865a1962c0b9da2687f37020a1a4c9b`.
Whole-text tokenization is unchanged. Assert byte-for-byte equality between the
old and new token streams before training. Prompt target weights become zero;
answer and EOS target weights become one. Prompt is an explicit proper text prefix
or, for copy records, the prefix through the final `\nAnswer: ` delimiter. Unicode
offset and teacher-forcing alignment tests are required. A zero-target batch must
fail explicitly, never silently create NaN or change the effective step budget.

Start at the same original V11 historical checkpoint, seed 1686, 1,000 steps,
batch 16, context 512, learning rate 3e-5, warmup 30, bf16. Optimizer is reset, as
in the existing trainer. Same 8,192,000 input tokens seen. Compared control is the
previous continuation-weighted augmentation checkpoint, not the varied-only model.
The objective also changes normalization and the effective gradient contribution;
this is an objective comparison, not a claim about masking in isolation. One seed,
shared initialization and post-hoc motivated design remain limitations.

Run identical 96 held-out label-relation probes, 24 copy probes, 16 seen training
probes, old 72-word probes, eight original source/arithmetic probes and abstract /
physics suites. Report exact answers, both members of reversal pairs and constant
square baselines, not ranking alone. Candidate NLL is secondary. The seen probes
and old test are diagnostics, not fresh blind evaluation sets.

Validation loss reported by the existing trainer still covers all validation tokens;
it is not the answer-only loss and must not be compared directly with the training
loss. The instruction dataset contains modern synthetic task construction, but no
Newton target answer. This is never called a historical-only rediscovery success.
Audit unchanged scientific-text retention with the fixed windows, and direct
Earth–Moon generation using the existing evaluator. Preserve every old checkpoint.

## Verified pilot results

Tongji job 2863086 completed with exit 0, elapsed 2m23s; training took 70.73s.
Both input streams have SHA256
`873276486f4da8ac0a5d741ddc4d92d02bb219ba9b7689d4a1313001ccf9b8dc`.
The answer-only checkpoint SHA256 is
`edd25e3da54170fcd97e5a9c5ffd3650f53ebd87dd646fb3466c72f36ac73c51`.
Raw outputs and the comparison are in `audit/answer_only/`.

| Metric | Continuation-weighted control | Answer-only |
| --- | ---: | ---: |
| Exact held-out label answers | 48/96 | 94/96 |
| Both members of reversal pairs correct | 0/48 | 46/48 |
| Familiar template, new labels | 24/48 | 48/48 |
| New template and new labels | 24/48 | 46/48 |
| Candidate ranking correct (secondary) | 51/96 | 93/96 |
| Copy probes | 23/24 | 24/24 |
| Inspected training prompts, exact | 8/16 | 16/16 |
| Old 72-probe diagnostic, exact | 31/72 | 51/72 |
| Old diagnostic, complete reversal pairs | 0/36 | 19/36 |

The control answered square in every held-out relation case. The two answer-only
errors are one wrong power and one wrong entity. Thus the apparent constant-answer
collapse is not an unavoidable capability limit at this model size on this task.
This does not establish which component of the objective change caused the gain.

Only 3/8 source/arithmetic probes are correct: the modern paraphrase question and
continuation, and the swapped-relation question. Both members of that question pair
are now correct, but the original OCR prompts and arithmetic prompts still fail.
The deterministic suite remains 0/12 abstract derivations and 0/4 physics generations.
The direct Earth–Moon sampled output remains incoherent. These are not rediscovery
results; favorable candidate likelihoods in some legacy probes do not override them.

Scientific-text mean loss on identical fixed validation windows is 5.07719, versus
5.05184 for the control and 4.90960 for the historical starting model. No population
significance is inferred from these windows. Whole-stream synthetic validation loss
is 3.00430 versus the control's 1.01529; answer-only training loss is 0.03395.
These losses measure different targets and must not be conflated. Improved answer
behavior coexists with degraded full-text prediction.

## Frozen replication plan

Repeat both objectives with fine-tuning seeds 1687 and 1688, starting from the same
historical V11 checkpoint, unchanged data and 1,000-step budget. Use existing masked
and control token streams, checking byte equality first. Primary outcomes are exact
96-case generation and all 48 complete reversal pairs, reported for each seed,
including failures; copying and physics are secondary. Do not select the best seed
or tune on these outcomes. `hpc/tongji_answer_only_replication.sbatch` runs the four
jobs sequentially on one L40 and uses separate output directories. Historical
pretraining remains a single seed, and this repeated test set is not a new blind
benchmark. Broader discovery claims require new tasks and audited source material.

Replication submitted as Tongji job 2863128 on 2026-10-01. Submission is not evidence
of completion; inspect scheduler state and all four output directories before
reporting results.

## Short-answer interface diagnostic

While replication is running, a post-hoc eight-case diagnostic is fixed in
`tests/fixtures/short_elimination_probes.json`: two each for subtraction, abstract
elimination, symbolic orbital premises and verbal orbital premises. Within each
group the exponents are reversed, changing the correct answer from -2 to +2.
Greedy generation permits immediate EOS, uses 60 tokens and no minimum length,
matching the reading evaluator rather than demanding a long reasoning trace.
Run on historical V11, continuation-weighted control and answer-only seed 1686.
Exact full suffix is the primary diagnostic; ranking is secondary. All prompts
provide their premises: even success would not demonstrate retrieval of historical
knowledge or autonomous discovery. Counterfactual physics cases are deliberately
not claims about the real world. The old long-form suite is retained unchanged.
Tongji job 2863130 is submitted with `afterok:2863128`, so it will not run concurrently
with the replication on another GPU. No diagnostic outcomes are claimed yet.

## Completed replication and interface diagnostic

Job 2863128 completed, exit 0, elapsed 7m58s. Job 2863130 completed, exit 0,
elapsed 19s. The full per-run outputs are under `audit/objective_replication/`
and `audit/short_elimination/`. Run `python src/summarise_objective_replication.py`
to reproduce all seed-level counts; it asserts identical probe identities,
prompts, targets and candidate texts across all six runs and fails on missing runs.

| Fine-tuning seed | Control exact /96 | Answer-only exact /96 | Control complete pairs /48 | Answer-only complete pairs /48 |
| --- | ---: | ---: | ---: | ---: |
| 1686 | 48 | 94 | 0 | 46 |
| 1687 | 47 | 80 | 11 | 33 |
| 1688 | 49 | 81 | 2 | 33 |

The objective advantage repeats in both additional seeds but the first seed
overstates typical performance. The control is not always constant-square:
seed 1687 gets 11 complete pairs. All six models still score 0/12 abstract and
0/4 physics generations in the unchanged long-form suite. Scientific loss for
control/answer-only respectively is 5.05184/5.07719, 5.05206/5.06689 and
5.05144/5.05299. Retention worsens in each paired seed, by differing amounts.
No significance claim or independent-test-set confidence interval is made.

In the eight short-answer probes, historical V11, continuation seed 1686 and
answer-only seed 1686 each produce **0/8 exact answers**, including both arithmetic
questions. Candidate ranking is 4/8, 4/8 and 3/8 respectively; these do not establish
derivation. Answer-only outputs are dominated by its learned square/cube answer
style even for arithmetic and symbolic questions. Thus a short-answer interface
does not rescue transfer. The next capability intervention must address arithmetic
and elimination rather than extend relation-reading training. Such modern synthetic
mathematical calibration must remain explicitly separate from the historical-only
arm, with the Newton exponent combination sealed and counterfactual tests retained.
