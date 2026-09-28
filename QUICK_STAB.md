# Real quick stab: sealed pre-Newton language model

## Question

Can a language model initialized from random weights, trained only on admitted
pre-Newton text, assign unusually high probability to an inverse-square Earth--
Moon attraction law? This pilot asks the question without geometry images,
modern pretrained weights, a modern tokenizer, or instruction tuning.

This is a signal-detection experiment, not yet a faithful reconstruction of a
human scientific derivation. The open-ended generation is recorded, but the
primary quick diagnostic is blinded candidate-completion likelihood because a
small model trained on roughly 15 MB of OCR is not expected to be conversational.

## Two controlled arms

| Arm | Training text | Meaning |
|---|---|---|
| `strict` | 15 strict-clean works | The uncontaminated pilot |
| `precursor` | the same 15 works plus isolated Boulliau and Hooke works | Positive-control / historical-leakage arm |

Both models have identical random initialization, architecture, optimizer,
training steps, and evaluation prompts. The only changed variable is precursor
exposure. Neither arm starts from a modern model.

## Evaluation

The harness records:

1. held-out next-byte loss, to verify that actual language learning occurred;
2. free generation after a direct Earth--Moon attraction question;
3. conditional likelihoods for constant, inverse, inverse-square, and inverse-
   cube completions under three prompt styles.

The completion test is not a substitute for derivation. It is a cheap check
that the training and leakage controls are sensitive enough to justify a more
expensive run.

## Run on the RTX 5090

From the project directory, run the strict arm:

```bash
python src/train_random_init_smoke.py \
  --data data/real_pilot/strict_clean.jsonl \
  --output-dir runs/quick_stab_strict \
  --label strict \
  --device cuda --precision bf16 \
  --steps 1500 --batch-size 32 \
  --context 256 --width 384 --heads 6 --layers 6
```

Then run the precursor-exposed positive control:

```bash
python src/train_random_init_smoke.py \
  --data data/real_pilot/strict_clean.jsonl data/real_pilot/precursor_only.jsonl \
  --output-dir runs/quick_stab_precursor \
  --label strict_plus_precursors \
  --device cuda --precision bf16 \
  --steps 1500 --batch-size 32 \
  --context 256 --width 384 --heads 6 --layers 6
```

Create the comparison:

```bash
python src/compare_quick_stab.py \
  --strict runs/quick_stab_strict/report.json \
  --precursor runs/quick_stab_precursor/report.json \
  --output runs/QUICK_STAB_RESULTS.md
```

The two arms each see 12.3 million training bytes (tokens) at 1,500 steps. This
is roughly one pass over the pilot corpus. Increase steps only after checking
that the positive-control arm responds in the expected direction.

## Decision rule

- Neither arm selects inverse-square: a useful null result. The present
  corpus/model/evaluation is not sensitive enough.
- Only the precursor arm selects inverse-square: the harness detects target
  exposure; this is leakage detection, not rediscovery.
- The strict arm selects inverse-square: repeat across seeds and paraphrases,
  audit its nearest training passages, and scale the corpus before claiming
  anything stronger.

## Known limitations

- The 17 editions have machine review, not final named human approval.
- OCR quality and multilingual mixing are poor.
- The corpus is much too small for a capable general-purpose language model.
- The candidate choices reveal the hypothesis class at evaluation time.
- A genuine second-stage experiment must demand an explicit derivation from
  Keplerian periods, orbital geometry, and centripetal acceleration, with those
  premises provided in historically admissible form.
