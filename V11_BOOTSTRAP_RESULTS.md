# V11 historical-language bootstrap: result (2026-10-01)

**Verdict: improved historical-text modeling, no demonstrated mathematical
composition or Newtonian discovery.** The [frozen pilot protocol](V11_BOOTSTRAP_PROTOCOL.md)
specified free generation as the primary diagnostic. The new model failed
all 12 abstract and all four premise-given physics generation cases, and did
not answer the direct Earth–Moon question. A few candidate-ranking wins must
not be reported as discovery.

## Data and execution

The public [PYCCLE EEBO Phase-I release](https://github.com/uoy-linguistics/pyccle)
was re-downloaded and verified against the old archive SHA-256. Re-ingestion
reproduced the earlier audit **byte for byte**: 1,179 accepted training
documents, 18 validation documents, 1,112 quarantined documents, and
200,033,084 accepted training-text bytes. These metadata dates are
automatically scraped by PYCCLE and may contain errors; the accepted texts
have not received human historical approval.

The combined stream has 70,125,444 tokens (SHA-256
`6d9bef7d45138291679b0eff11f62c97e0f93129b8831f3265aa1503d023cb8c`)
under the **same** V11 tokenizer as the raw-only arm. No modern pretrained
weights, synthetic reasoning examples, or target-answer examples were added.
Tongji L40 job **2861975** completed with exit code 0 in 33m09s: 91,510,272
random-initialized parameters, seed 1686, context 512, batch 32, 12,000
updates, bf16, 196,608,000 tokens seen, and 8.41 GB peak allocated GPU
memory. The checkpoint remains at
`~/data/AGI-Newton/runs/hpc_v11_bootstrap_seed1686/model.pt` (SHA-256
`10deb0e421e963ce2e715afa37601d6d0bd9a3bc15dbcc624e24fe8d0ab2a480`).
The prior raw-only checkpoint and both runs' reports use the same scientific
validation stream (230,842 tokens).

| Measure | V11 raw-only | V11 + pre-1687 English |
|---|---:|---:|
| Training-stream tokens | 4,287,350 | 70,125,444 |
| Tokens seen in training | 12,288,000 | 196,608,000 |
| Scientific validation loss (lower better) | 5.3599 | 4.7924 |
| Scientific validation perplexity | 212.7 | 120.6 |
| Abstract candidate ranking | 1/12 | 2/12 |
| Abstract correct free generation | 0/12 | 0/12 |
| Premise-given physics candidate ranking | 0/4 | 0/4 |
| Premise-given physics correct free generation | 0/4 | 0/4 |
| Direct Earth–Moon answer | failed | failed |

The 2/12 abstract ranking is **exactly** the constant-`2` baseline: the
bootstrap model selected exponent `2` for every one of the 12 abstract cases,
including all five whose correct exponent was `-2`, and for all four physics
cases. Its fixed law-phrase probes ranked “inverse square” first in three of
four styles, but that conflicts with the controlled exponent tests and the
absence of a derivation. These rankings are consistent with prompt/answer priors, not
evidence of physical reasoning.

In deterministic generation, the model repeatedly produced `〈 math 〉`
instead of a calculation. A one-core source audit found this literal
placeholder 280 times in 49 of the 25,464 EEBO training chunks and zero
times in the 1,727 V11 scientific training chunks. This identifies one
source of the emitted string; its modest frequency does **not** by itself
prove why the model repeats it. The result does show that simply adding
historical English does not supply the missing algebraic skill.

## Interpretation and boundary

The lower validation loss is a real improvement on the fixed scientific
validation stream. It does **not** establish a causal effect of English
bootstrap alone: the arms have different total training budgets, although
the larger stream's expected scientific-token exposure is about 12.0M,
close to raw-only's 12.3M. This is one seed and a small fixed prompt suite.
Neither Kepler's damaged OCR nor Huygens's historically nuanced centrifugal
force statements have been converted into expert-checked training premises.
There is no basis here for saying the model rediscovered inverse-square
attraction or that historical-only rediscovery is impossible.

The next informative intervention is **not** a larger GPU run on the same
inputs. First obtain expert-checked original-language transcriptions of the
two premise passages, with source-page hashes and explicit exclusion of
target-law precursors; then test premise identification and algebraic
composition separately, with counterfactual non-`-2` cases and multiple
seeds. A synthetic target-free algebra curriculum may be a separately
labelled capability control, never historical evidence.

The [training report](runs/hpc_v11_bootstrap_seed1686/report.json),
[generalization report](runs/hpc_v11_bootstrap_seed1686/generalization_suite.json),
and [HPC logs](runs/hpc_v11_bootstrap_seed1686/) preserve the exact outputs.
The archive, 200 MB training JSONL, 140 MB token stream, and checkpoint are
kept off GitHub; their hashes and rebuild scripts are committed.
