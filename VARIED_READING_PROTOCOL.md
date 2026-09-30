# Varied reading calibration pilot

Frozen before this run, 2026-10-01. This follows the tiny calibration pilot and
uses the corrected, regression-checked SentencePiece boundaries. It is a modern
synthetic instruction arm, never labelled purely historical training or discovery.

Starting model: the unchanged historical V11 bootstrap checkpoint. Train on 7,728
records with 24 quantity nouns, both queried sides, swapped square/cube relations,
question and continuation formats, and distractor relations both before and after
the queried relation. Distractor nouns are never the queried nouns. No gravitational
answer, orbital period, distance, inverse-square law, or algebraic combination is
taught. The objective is reading supplied premises, not predicting physical laws.

Use the same architecture/tokenizer and continuation weighting. Reset optimizer
as in the prior pilot; seed 1686, 1,000 steps, batch 16, context 512, bf16, learning
rate 3e-5, warmup 30. Exposure: 8,192,000 tokens. No model selection or early stopping.
Single training seed and shared pretrained checkpoint are exploratory limitations.

72 held-out probes, equally divided into:

- Familiar prompt format, six nouns unseen in calibration training.
- Familiar nouns, an unseen question template.
- Both unseen calibration nouns and unseen question template.

The nouns may occur in historical pretraining: this is not a lifetime-vocabulary
holdout. Relations are semantically close to training; no semantic-family
generalization claim is allowed. The new test does not include distractors, so
success would not prove robust multi-relation retrieval. Exactly identical prompts
must not cross train/test; targets and counterfactual reversals are balanced.

Save greedy free generation and candidate NLL for the original and calibrated
model. Primary audit: exact power-and-queried-noun answer, plus both answers correct
in each reversed-relation pair. Report all three groups. A constant-square ranking
baseline is 36/72. Exact match is conservative; archive raw answers for manual review.
Validation uses these synthetic test cases but never selects a checkpoint, so this
is a fixed pilot evaluation rather than a repeatedly tuned blind benchmark.

Also run the unchanged eight source/arithmetic probes, the physics/abstract suite,
and the separate direct Earth–Moon checkpoint evaluator. Synthetic reading gains
cannot count as physics discovery. A reading improvement is a prerequisite for
later explicitly separated algebraic/historical interventions, not goal completion.

Retention endpoint added before observing the calibrated outputs: evaluate original
and calibrated models on the unchanged `data/real_pilot_v11/validation.bin` scientific
text, 16 batches of 8 × 512-token windows sampled with seed 1686. This measures
language-model retention, not physics reasoning. Report both losses rather than
assuming that synthetic instruction gains preserve historical-language capability.
Use the existing direct evaluator's optional `--validation` argument; no retraining.

## Observed results

Tongji L40 training/evaluation job `2862938`: completed, exit `0:0`, elapsed 2m21s.
Training took 71.98s. The 431,296-token stream was revisited approximately 19 times.
Synthetic validation loss changed from 1.6825 to 1.1317; train loss ended at 0.0235.
The paired retention job `2862944` completed in 15s, exit `0:0`.

| Endpoint | Original historical model | Varied synthetic calibration |
| --- | ---: | ---: |
| Exact power-and-noun answers | 0/72 | 25/72 |
| New nouns, familiar question | 0/24 | 7/24 |
| Familiar nouns, new question | 0/24 | 12/24 |
| Both new nouns and new question | 0/24 | 6/24 |
| Both reversed-relation answers correct | 0/36 | 3/36 |
| Candidate ranking | 36/72 | 59/72 |
| Scientific-text mean loss, fixed matched windows | 4.9096 | 4.9956 |

The calibrated model produces square answers on 62/72 cases; 39/72 answers name
the wrong queried noun. All outputs were inspected and retained. Its unseen-template
group contains no correct cube answer: 12/24 matches the constant-square power
baseline, so that subgroup is not evidence of reliable template transfer. Candidate
ranking forces the correct noun into both alternatives; its much higher accuracy
does not measure open-vocabulary noun binding or autonomous reasoning.

The scientific-language loss worsens by 0.0860 on this fixed window sample. This is
a measured retention cost, not a statistical claim about all scientific text. The
eight original source/arithmetic prompts still have no fully responsive correct
answer. The model sometimes switches square/cube in the question-format modern
paraphrases, but calls the periods `roots`, so this is not successful source reading.
Abstract compositional free answers remain 0/12; premise-given physics remains 0/4.
The separate direct evaluator's Earth–Moon output says `the squares of the parts`
and appends an unrelated training-style question; it does not derive inverse-square
attraction. This evaluator's direct output is sampled, not a multi-draw success-rate
estimate. Physics suite generation is greedy and its full outputs are retained.

Reproduce descriptive reading counts with:

```sh
python3 src/summarise_reading_calibration.py --root audit/reading_varied
```

Files: `audit/reading_varied/summary.json`, original-model outputs at that directory's
top level, calibrated outputs under `calibrated/`; the generator and hashed dataset
are under `src/build_reading_calibration.py` and `data/reading_varied/`.
Checkpoint stays on HPC at `runs/hpc_reading_varied_seed1686/model.pt`, SHA256
`92d28784de17be0d023b6a06a6adc83de1637e5676e5be4239f6edb05bb175ab`.

Conclusion: increasing curriculum variation improves some exact reading answers,
but fails the input-sensitive generalization gate. The observed gains are not
scientific discovery or proof that a larger model will solve it. Next intervention
should address explicit entity copying/binding, with independent noun and question
holdouts and a historical-text retention control, before adding algebraic discovery
training. Extending the same template training indefinitely is not justified.
