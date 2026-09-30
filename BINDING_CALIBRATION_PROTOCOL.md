# Copying and binding augmentation pilot

Frozen before outputs, 2026-10-01. The varied curriculum improved format and some
answers but often substituted a training noun for the queried noun. This pilot
tests an augmentation, not physics discovery or historical-only learning.

Augmented training: the unchanged 7,728 varied examples plus 1,128 explicit label
copy exercises and 9,024 square/cube relation-reading exercises with artificial
two-syllable labels. Total 17,880 records. Of 400 generated labels, 24 are reserved
and absent as substrings from all training text. Their letters are represented in
training. Labels are invented task symbols; no claim is made that their strings
never occurred accidentally in historical pretraining. No target physics is added.

Start from the original V11 historical bootstrap, not the varied-calibrated model.
Use the same seed 1686, 1,000 steps, batch 16, context 512, learning rate 3e-5, warmup
30 and continuation weighting as the earlier varied run. Same 8,192,000-token
budget, tokenizer, architecture and initial weights. Reuse that run's checkpoint
as the budget-matched varied-only control; do not retrain or select a better seed.
This is an exploratory sequentially designed comparison: augmentation includes
both copying and extra binding examples, so it does not isolate copying alone.

New test: twelve reserved labels in 96 balanced relation-reading cases, split
equally between familiar questions and the previously withheld question template.
All 48 reversal pairs must be reported. Additional 24 copy probes split familiar
and unseen copy instructions. The task family and component characters are familiar;
this is neither an entirely new reasoning family nor independent trial replication.

Save both models' greedy generations and ranking scores. Exact power-and-label
answers and complete reversal pairs are primary; forced-choice ranking is secondary.
For copying, exact free answers are primary (candidate keys are labels, not powers).
Both models also face the old 72-word reading set. That set is no longer a blind
benchmark: its errors motivated this experiment. No reserved-label training is
allowed; generator assertions enforce the split and target-physics exclusion.

Then rerun the frozen source/arithmetic probes, abstract/physics suite and direct
Earth–Moon evaluator. Audit scientific retention on the same fixed 16 batches of
8 × 512 tokens from `data/real_pilot_v11/validation.bin`, seed 1686. The prior control
retention result is cached. The initial model, old varied model and augmented model
all remain separate checkpoints. Do not infer discovery from copying improvements.

Post-hoc diagnostic added after observing the held-out results: evaluate the first
16 balanced binding records whose left entity is the first training label (`babe`).
These are exact training prompts, not a test of generalization. They represent two
partner labels, both square/cube assignments and both query/continuation formats.
Freeze this deterministic slice before inspecting its outputs. Use it only to
distinguish training-task failure from held-out generalization failure; it cannot
replace the 96 held-out cases or be used for checkpoint selection.

## Observed results

Job `2862981` completed, exit `0:0`, elapsed 2m32s; actual training took 72.23s.
The augmented stream has 873,604 tokens, approximately 9.4 passes at the fixed token
budget. Scientific retention and direct evaluation were included in this job.
The initial upload attempt failed during a transient SSH timeout; its eventual
submission command reported a missing script, so no job was submitted then. Files
were re-uploaded and validated before the single successful training submission.
No other project was altered. Mac's real-tokenizer check and 24 unit tests pass.

| New-label endpoint | Budget-matched varied-only control | Copy/binding augmentation |
| --- | ---: | ---: |
| Exact relation answers | 18/96 | 48/96 |
| Familiar question, new labels | 9/48 | 24/48 |
| Unseen question, new labels | 9/48 | 24/48 |
| Both reversed-relation answers correct | 4/48 | 0/48 |
| Forced-choice ranking | 67/96 | 51/96 |
| Exact label copying | 0/24 | 23/24 |
| Scientific-text loss on matched fixed windows | 4.9956 | 5.0518 |

The augmented model outputs `square` on **all 96** relation cases. Its 48/96 exact
answers equal the constant-square baseline; the aggregate gain is not relation
understanding. It copies the queried label correctly in 86/96 relation outputs but
never solves both members of a reversed pair. On isolated copying, familiar prompts
are 12/12 and novel prompts 11/12; the lone failure changes `dabi` to `dabu`.
Candidate copy ranking is 24/24, despite that generation error: forcing alternatives
can conceal an incorrect freely generated third label. Full outputs are retained.

On the old, non-blind 72-word set, exact answers increase from 25/72 to 31/72, but
complete reversal pairs drop from 3/36 to 0/36. Therefore the augmentation is not
promoted as a generally better reading model. The frozen eight source/arithmetic
probes produce one responsive correct answer on the original modern paraphrase
(`square of the periods`), but its swapped counterpart is wrong. This isolated
answer cannot demonstrate input-sensitive source acquisition. Original OCR reading
remains unsuccessful; abstract free answers remain 0/12 and physics free answers
0/4. Direct Earth–Moon generation produces an unrelated `number of the numbers`
statement and a training-style question, not inverse-square attraction.

The post-hoc seen-prompt diagnostic job `2863032` completed in 16s, exit `0:0`.
The augmented model answers square on all 16 exact training prompts: 8/16 exact,
0/8 complete pairs, 9/16 ranking. This small deterministic slice does not cover the
whole training corpus, but shows that held-out vocabulary cannot alone explain the
failure. Train loss 0.0286 and synthetic validation loss 1.0153 do not establish
learning of the answer-relevant relation; predictable template tokens contribute
heavily to these whole-stream losses. Do not infer memorization from low loss alone.

Next controlled intervention: on exactly this dataset and initial historical model,
compare answer-only supervision with the current continuation-weighted objective,
keeping input token IDs, seed, learning rate and token budget fixed. This tests the
loss objective rather than adding physics answers, scaling the model, or prematurely
attributing failure to lack of an RL stage. It is a proposal, not a completed run.

Reproduce the descriptive audit:

```sh
python3 src/summarise_reading_calibration.py --root audit/reading_binding --baseline-label varied_control
```

Raw outputs: `audit/reading_binding/`, with augmented results under `calibrated/`.
The training/test generator and hashed fixtures are in `src/build_reading_calibration.py`
and `data/reading_binding/`; the 16 seen fixtures were added after training and did
not change its hash. HPC checkpoint: `runs/hpc_reading_binding_seed1686/model.pt`,
SHA256 `9dc1d7042a8ccdcd5a85d54927c520f1c6bdf90de516fc60299b7ff0eb19a197`.
This is one shared-initialization, one-seed exploratory comparison, not a replicated
effect estimate or a scientific-discovery success.
