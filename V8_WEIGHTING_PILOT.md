# V8 local pilot: weighting generated reasoning continuations

## Question and result

V5--V7 often copied a derivation template but substituted the wrong variables
or exponents. V8 tests a narrower intervention: give the reasoning and answer
continuation of each **procedural** example four times the next-token loss
weight of its question. Historical text stays at weight one. The token stream
is identical between arms; only the loss weights differ.

This local, synthetic-only pilot **did not produce an open-derivation gain**.
The 1.85M-parameter unweighted and weighted models scored 2/12 and 1/12 on
strict abstract open generation, respectively; both scored 0/4 on physics
open generation. The weighted arm's ordinary validation loss was slightly
lower, but its open-generation result was worse. Neither arm answered any of
the four sealed `1 - 3` cases.

| Metric | Unweighted | Continuation weight 4 |
|---|---:|---:|
| Exact-text-disjoint synthetic validation loss | 0.6559 | 0.6463 |
| Abstract candidate ranking | 4/12 | 5/12 |
| Abstract strict open generation | 2/12 | 1/12 |
| Physics candidate ranking | 4/4 | 0/4 |
| Physics strict open generation | 0/4 | 0/4 |

The unweighted arm's 4/4 physics **candidate** score is not evidence of
discovery: it generated no correct physical derivation and showed the same
fixed-answer warning seen in earlier experiments. This small, single-seed
pilot cannot establish whether weighting is beneficial or harmful at 91.5M.

The earlier generation scorer counted any occurrence of the expected exponent,
even if the final answer contradicted it or used another variable. Suite
version 3 requires a target-bound final statement and rejects contradictory
exponents for that relation. This remains a conservative surface-form check,
not a formal proof verifier. The saved V5--V7 generations were rescored under
the same rule; see [`V6_V7_DIVERSITY_REPORT.md`](V6_V7_DIVERSITY_REPORT.md).

## Exact pilot setup

- Source: `data/reasoning/admissible_reasoning_v6.jsonl`, SHA-256
  `d9f9dcb0c9347d7360d6aeef0564f35520b969a4097f2f52d5ea3c18e4d3a6ba`.
- SHA-256-of-text modulo 20 assigns identical questions to the same split:
  58,761 train rows (3,711,401 BPE tokens) and 3,219 validation rows
  (197,472 tokens). The sets have **zero exact-text overlap**, but this does
  not eliminate semantically near-duplicate templates.
- Corpus-trained 8,000-piece tokenizer SHA-256:
  `88e085b1a1aee58a6c94fd3ae7d68e1ba692cd9b5a9b880ab244111fcf65a4ca`.
- MPS on the local Mac; 4 layers, width 128, 4 heads, context 256,
  1,845,504 parameters; seed 1686; batch 8; 2,000 updates; 4,096,000
  sampled training tokens; learning rate `3e-4`, 30 warmup steps, fp32.
- Both arms train from random initialization. Neither sees historical prose in
  this pilot; it is an isolated algorithmic-skills diagnostic, **not** a
  pre-Newtonian rediscovery experiment.

Rebuild the data from the repository root (substitute your Python executable):

```bash
python src/split_curriculum.py --input data/reasoning/admissible_reasoning_v6.jsonl --train /tmp/v8-train.jsonl --validation /tmp/v8-validation.jsonl
python src/tokenize_corpus.py --tokenizer data/tokenizer_v3/pre1687_bpe.model --data /tmp/v8-train.jsonl --output /tmp/v8-train.bin --loss-weights-output /tmp/v8-train.weights
python src/tokenize_corpus.py --tokenizer data/tokenizer_v3/pre1687_bpe.model --data /tmp/v8-validation.jsonl --output /tmp/v8-validation.bin
```

The train weight file has exactly one byte per token: 2,147,611 at weight 1
and 1,563,790 at weight 4. It is aligned with the token stream by target
position. Pass `--loss-weights /tmp/v8-train.weights` only to the weighted arm
of `src/train_bpe_gpt.py`. Both arms otherwise use the fixed setup above and
the corrected suite version 3. The source split SHA-256 hashes are
`082b45b9c7424b80d6dabec6408f76d43579a36d6c816ebb331001618bb309d8`
(train) and `535d57e3103635e6a7a583424b3d103aae41a93c1b62c95aa23900f6ddf16423`
(validation).

Raw reports: [unweighted training](runs/v8_weighting_pilot/unweighted_train.json),
[weighted training](runs/v8_weighting_pilot/weighted_train.json),
[unweighted blind suite](runs/v8_weighting_pilot/unweighted_suite.json), and
[weighted blind suite](runs/v8_weighting_pilot/weighted_suite.json). Checkpoints
are not committed.

## Decision

Do **not** promote continuation weighting alone to the 91.5M historical
model on these data. The first row-based split had 596 exact train--validation
overlaps and was discarded; the results above come only from the repaired
text-hash split. The next experiment needs a larger, template-disjoint
benchmark and several seeds. It should weight the *actual arithmetic and
final result tokens*, not merely all continuation prose, before spending GPU
time on the historical model.
