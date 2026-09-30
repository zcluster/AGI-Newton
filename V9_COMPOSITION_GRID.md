# V9 local pilot: compositional grid and answer-token weighting

## Decision

Do **not** promote final-exponent weighting to the historical 91.5M model.
On a new 204-case abstract elimination grid, the same-token-stream control
answered 20 cases correctly; the arm weighting the final exponent answered
one. Neither solved any of the six `1 - 3 = -2` sealed-pair cases or any of
the four physics open-generation cases. This is a single-seed, 1.85M-parameter,
synthetic-only diagnostic, not a Newton rediscovery experiment or a general
claim that answer weighting cannot work.

| Metric | No loss weights | Continuation 4×, final exponent 16× |
|---|---:|---:|
| Exact-text-disjoint synthetic validation loss | 0.8182 | 0.7843 |
| New grid: correct final relation | 20/204 | 1/204 |
| New grid: matching subtraction, final relation, no explicit wrong quotient | 6/204 | 1/204 |
| New grid: sealed `1 - 3` pair, final relation | 0/6 | 0/6 |
| Old suite v3: abstract strict open generation | 0/12 | 0/12 |
| Old suite v3: physics strict open generation | 0/4 | 0/4 |

The lower validation loss did **not** predict better novel-prompt generation.
Candidate ranking on the old abstract suite was 1/12 versus 3/12, but neither
arm produced a correct open answer there. The control's new-grid successes are
concentrated in one of two prompt wordings, not evenly distributed. These are
failure diagnostics, not evidence of robust algebraic reasoning.

## What was tested

`src/evaluate_composition_grid.py` generates two new prompt wordings, three
symbol sets, and 34 admissible `(known, numerator)` exponent pairs per symbol
set: 204 cases total. Every oracle is `numerator - known`; six cases have the
target pair `(1, 3)`. The two prompt wordings are absent from the full V6
reasoning corpus. This is **exact-wording disjoint**, not semantically
template-disjoint: the training curriculum contains closely related
elimination exercises. Numbers and symbol roles are varied, but many values
are seen elsewhere during training. The sealed pair was checked for the
literal `1 - (3) = -2` solution string; this is not a comprehensive semantic
leakage proof.

The `answer_correct` checker requires a target-bound final relation and
rejects contradictory exponents on that same relation. The narrower
`equation_and_answer_correct` checker additionally requires an arithmetically
valid subtraction using the prompt's exponents and rejects any explicit
same-base quotient with mismatched operands. It does **not** parse every
intermediate verbal statement, so neither metric certifies a formal proof.
An earlier exploratory checker counted 12 control traces but accepted wrong
intermediate quotients; that figure is superseded by the audited 6/204.

## Reproduction boundary

Both arms started from random initialization, shared seed 1686, the same
3,775,795-token training stream and 197,472-token validation stream, and
trained for 2,000 updates on the local Mac MPS (4 layers, width 128, 4 heads,
context 256, batch 8, fp32, learning rate `3e-4`, 30 warmup steps; 1,845,504
parameters). The source is V8's SHA-256-of-text split of
`data/reasoning/admissible_reasoning_v6.jsonl` (58,761 train rows and 3,219
validation rows, zero exact-text overlap). Both arms used the V9 train-token
stream because independently tokenizing the emphasized final exponent changes
its segmentation; **V8 and V9 losses are not directly comparable**.

The V9 training token SHA-256 is
`839bb036ad463fc5938fd988857358d4281fd9161b828eaff51a68369dae3335`;
the weight-file SHA-256 is
`5ac0dd41e4cc230347abfcd5fc4b67c52e555efd97c4a472669cf1fe35dcd0c6`.
The weights are 1 for ordinary material (2,147,611 tokens), 4 for procedural
continuations (1,587,823), and 16 for final exponent tokens (40,361). The
control reads the same token stream without a weight file; the intervention
uses that file. The validation token SHA-256 is
`acae5e0d7573c9159fb2b24360dc42e7bfa6f6d57871fbdb049bf0871cc2bdf7`.

From the repository root, with the dependencies in `requirements.txt`:

```bash
python src/split_curriculum.py --input data/reasoning/admissible_reasoning_v6.jsonl --train /tmp/v9-train.jsonl --validation /tmp/v9-validation.jsonl
python src/tokenize_corpus.py --tokenizer data/tokenizer_v3/pre1687_bpe.model --data /tmp/v9-train.jsonl --output /tmp/v9-train.bin --loss-weights-output /tmp/v9-train.weights --focus-final-exponent
python src/tokenize_corpus.py --tokenizer data/tokenizer_v3/pre1687_bpe.model --data /tmp/v9-validation.jsonl --output /tmp/v9-validation.bin
```

Train twice with `src/train_bpe_gpt.py`, using the architecture and optimizer
above and the same `/tmp/v9-train.bin`. Pass `--loss-weights
/tmp/v9-train.weights` only to the intervention arm. Then run
`src/evaluate_composition_grid.py` on both checkpoints with greedy decoding
and `src/evaluate_generalization_suite.py` for the old suite. Checkpoints and
token binaries are omitted from Git; the saved reports retain full training
arguments and every generated response:

- [Control training](runs/v9_composition_grid/control_train.json),
  [grid](runs/v9_composition_grid/control_grid.json),
  [old suite](runs/v9_composition_grid/control_suite.json).
- [Weighted training](runs/v9_composition_grid/targeted_train.json),
  [grid](runs/v9_composition_grid/targeted_grid.json),
  [old suite](runs/v9_composition_grid/targeted_suite.json).

## Next gate

Do not spend the rented RTX 5090 on scaling this weighting intervention yet.
The useful next experiment is to improve *held-out semantic structure* and
trace verification, then require stable open derivations across several
seeds. Only after that would a historical-language-plus-physics run be
interpretable. The original direct Earth--Moon question remains unsolved.
