# V3--V5: learned tokenizer, 91.5M model, and controlled reasoning curricula

## Outcome

These experiments improve the V2 engineering prototype in three ways:

1. the 8,000-piece BPE tokenizer is learned from the sealed corpus rather than
   inherited from a modern model;
2. all arms use the same separately encoded pre-1687 validation set; and
3. the model grows from 25.5M byte-level parameters to 91.5M BPE parameters.

The result is a useful but negative scientific finding. The model learns seen
exponent transformations and acquires some constrained preferences for the
correct symbolic result. It still cannot freely derive the inverse-square law
or answer the direct Earth--Moon question.

## Fixed training configuration

| Item | Value |
|---|---:|
| parameters | 91,510,272 |
| tokenizer | random-from-corpus BPE, 8,000 pieces |
| transformer | 12 layers, width 768, 12 heads |
| context | 512 tokens |
| batch | 64 sequences |
| updates | 6,000 |
| tokens seen per arm | 196,608,000 |
| precision/device | bf16, one RTX 5090 |
| peak allocated GPU memory | 14.99 GB |
| runtime per arm | approximately 14.2 minutes |
| shared validation tokens | 689,061 |

The tokenizer was trained on the admitted pre-1687 English, strict scientific
core, and target-screened reasoning curriculum. It used identity normalization
and byte fallback. It did not load a pretrained vocabulary.

## Curriculum intervention

All physical target statements remain excluded. The three arms differ only in
which abstract mathematical competence is made available.

| Arm | Additional admissible knowledge | Deliberately held out |
|---|---|---|
| V3 | arithmetic, ratios, Kepler examples, circular-motion examples, exponent operations except result -2 | every abstract result `x^-2`; all physical target associations |
| V4 | V3 plus 570 generic, nonphysical `x^-2` examples | exact quotient `x^1/x^3`; two-premise substitution; all physical target associations |
| V5 | V4 plus 6,000 generic two-premise substitution examples, including 554 with result -2 | the decisive exponent pair `1-(3)` within that family; all physical target associations |

V5 contains no `inverse square`, `reciprocal square`, `1/r^2`, `r^-2`, or
gravity/distance answer statement. The model is taught mathematical tools, not
the target physical law.

## Language learning

The identical validation set makes the losses directly comparable.

| Arm | Training tokens in stream | Final validation loss | Perplexity |
|---|---:|---:|---:|
| V3 | 60,432,013 | 3.5847 | 36.04 |
| V4 | 60,433,735 | 3.5893 | 36.21 |
| V5 | 61,417,053 | 3.5934 | 36.36 |

The near-identical language losses show that the interventions did not simply
make one model globally better or worse.

## Capability ladder

`Pass` below means that the correct completion has the lowest mean token NLL.
It is a constrained diagnostic, not an open-ended discovery.

| Diagnostic | V3 | V4 | V5 |
|---|---|---|---|
| seen `x^3/x^1 = x^2` control | Pass | Pass | Pass |
| held-out simple `x^1/x^3 = x^-2` | Fail | Pass | Near-tie fail |
| neutral two-premise substitution | Fail | Fail | Pass |
| physics premises, symbolic `distance^-2` answer | Fail | Pass | Pass |
| original verbal inverse-square candidates | Fail | Fail | Fail |
| free derivation | Fail | Fail | Fail |
| direct Earth--Moon answer | Fail | Fail | Fail |

The V5 symbolic physics bridge prefers the correct answer by only 0.053 NLL
over the best alternative. V5's simple held-out division misses by only 0.004
NLL. These small margins are unstable and require multiple seeds.

## Why forced generation matters

The first open-generation evaluator allowed an immediate end-of-sequence token.
The final evaluator therefore requires at least 30 new tokens. This exposes the
difference between recognition and derivation:

- V4 substitutes the wrong indices and produces `2 - 3 = -1`;
- V5 copies the learned template but changes the variables and produces an
  unrelated relation such as `1 - 0 = 1`;
- historical-language continuations remain syntactically plausible in places
  but do not form a valid proof.

Accordingly, the candidate-ranking passes cannot be described as rediscovery.
They show that useful internal associations are beginning to form, while the
model still lacks robust algorithmic execution and physical-to-symbolic
composition.

## Scientific interpretation

The progression localizes the bottleneck:

1. V3 demonstrates that withholding all abstract `-2` results makes the task
   unnecessarily impossible.
2. V4 shows that generic negative-exponent knowledge is legitimate prerequisite
   mathematics rather than target leakage.
3. V5 shows that generic two-premise substitution improves the matching neutral
   diagnostic, yet does not produce a stable free derivation.

The next justified experiment is not another copy of the same template. It
should use a substantially more diverse algorithmic curriculum, multiple
random seeds, and blinded prompt families. A 300M model is reasonable only
after the 91.5M model passes the open abstract derivation tests; otherwise scale
would obscure a curriculum/evaluation problem.

## Reproducibility artifacts

- tokenizer training: `src/train_tokenizer.py`
- corpus encoding: `src/tokenize_corpus.py`
- 91.5M GPT training: `src/train_bpe_gpt.py`
- transfer evaluation: `src/evaluate_bpe_checkpoint.py`
- curriculum generator: `src/generate_admissible_reasoning.py`
- tokenizer audit: `data/tokenizer_v3/tokenizer_audit.json`
- V3 report: `runs/v3_strict/report.json`
- V4 report: `runs/v4_abstract_bridge/report.json`
- V5 report: `runs/v5_two_premise/report.json`
- final candidate evaluations: each run's `evaluation_final.json`
- forced-generation evaluations: each run's `evaluation_min_generation.json`

Large checkpoints remain on AutoDL under
`/root/autodl-tmp/pre_newton_corpus/runs/<run>/model.pt`.
