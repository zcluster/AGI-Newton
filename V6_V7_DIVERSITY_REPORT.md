# V6--V7: diversity, blinded generation, and the limits of curriculum fine-tuning

## Purpose

V3--V5 showed that a 91.5M-parameter random-init model can rank some correct
symbolic completions but cannot reliably generate the derivation. V6 tests
whether this is merely caused by a narrow, repetitive curriculum. V7 tests the
follow-up hypothesis that a short curriculum-only stage after historical
language pretraining can fix variable binding.

Neither experiment contains the target physical law.

## V6 intervention

V6 retains the V5 arithmetic, ratios, Kepler examples, circular-motion
examples, and sealed exponent controls. It adds 24,000 two-premise elimination
examples with randomized:

- variable names and base symbols;
- six question structures;
- four reasoning structures; and
- three answer structures.

The resulting curriculum has 61,980 records and 29,972,645 bytes. It contains
2,772 generic reasoning chains whose answer is exponent -2, but contains zero
instances of the decisive `1 - (3) = -2` pair. It also contains none of the
physical target forms `inverse square`, `reciprocal square`, `1/r^2`, `r^-2`,
or `duplicate ratio of distance`.

V6 uses the same 91,510,272-parameter architecture, tokenizer, random seed,
shared validation set, batch size, context length, and 6,000 updates as V3--V5.
It sees 196,608,000 training tokens in 851.5 seconds on the RTX 5090.

## Blinded suite

**Evaluation correction (2026-09-30):** The legacy physics candidate scorer
used `C/R` in all four candidate completions even when the prompt used other
symbols or natural language. Those candidate scores are invalid and require a
checkpoint rerun with suite version 3. The archived JSON is retained for audit.
Rescoring the saved generation strings against the corrected prompt metadata
and a stricter final-answer check gives 0/4 physics open generations in each
arm. The stricter check requires the final statement to name the correct
target, base, and exponent without a contradictory exponent for that relation;
it is still not a complete proof verifier.

The new suite contains 12 unseen abstract paraphrases and four unseen physics
paraphrases. It reports both candidate ranking and deterministic greedy
generation. Open generation must write at least 30 tokens. The archived strings
have been rescored using the stricter target-bound final-answer rule above.

| Model | Abstract candidate | Abstract generation | Physics candidate | Physics generation |
|---|---:|---:|---:|---:|
| V5 narrow curriculum | 6/12 (50.0%) | 0/12 (0%) | invalid; rerun needed | 0/4 (0%) |
| V6 diverse curriculum | 3/12 (25.0%) | 2/12 (16.7%) | invalid; rerun needed | 0/4 (0%) |
| V7 curriculum-only stage | 4/12 (33.3%) | 1/12 (8.3%) | invalid; rerun needed | 0/4 (0%) |

V5 selects exponent -2 for many **abstract** candidate questions, including
controls whose correct answer is not -2. V6 reduces that fixed-answer bias and improves abstract open-generation
accuracy, but it still fails all held-out `1 - 3` prompts and all physics open
generations. Its generated traces have the right shape while replacing the
prompt's numbers or variables with values recalled from another training
example.

This demonstrates why candidate ranking cannot be used as the primary success
metric for scientific rediscovery.

## V7 two-stage experiment

V7 resumes the V6 checkpoint and trains for 500 additional updates only on the
3,897,734-token sealed reasoning curriculum. The learning rate is reduced to
`1e-4`; this stage consumes 16,384,000 tokens and takes 72.2 seconds.

| Metric | V6 before stage | V7 after stage |
|---|---:|---:|
| pre-1687 validation loss | 3.604 | 3.859 |
| abstract open generation (strict rescoring) | 16.7% | 8.3% |
| physics open generation | 0% | 0% |
| reasoning-curriculum train loss | about 3.05 in mixed training | 0.20 |

The very low curriculum loss combined with worse held-out performance is direct
evidence of template memorization and partial language forgetting. The planned
second 500-update dose and multi-seed replication were therefore not run.

## Current conclusion

The project now has an operational historical corpus, a corpus-trained
tokenizer, a 91.5M model, leakage controls, fixed validation, and a blinded
generation suite. The negative result is increasingly specific:

- the model learns early-modern language;
- it learns familiar exponent and substitution templates;
- it sometimes recognizes a correct symbolic completion;
- it does not reliably bind variables and numbers from an unseen prompt; and
- it does not openly derive the inverse-square relationship from the supplied
  physical premises.

Scaling the same curriculum to 300M parameters would not isolate whether any
gain comes from capacity or from memorizing more templates. A later
[V8 local pilot](V8_WEIGHTING_PILOT.md) added optional continuation weighting
and exact-text-disjoint validation but did not improve strict open generation.
The next justified change is an executable algorithmic curriculum with
template-disjoint tests and a more targeted arithmetic/result objective. Only
after a small model passes that abstract suite should parameter scaling and
multi-seed physics evaluation resume.

## Artifacts

- diverse curriculum: `data/reasoning/admissible_reasoning_v6.jsonl`
- diverse curriculum generator: `src/generate_admissible_reasoning.py`
- deterministic blinded suite: `src/evaluate_generalization_suite.py`
- V5 baseline: `runs/v5_two_premise/generalization_suite.json`
- V6 training report: `runs/v6_diverse/report.json`
- V6 blinded results: `runs/v6_diverse/generalization_suite.json`
- V7 training report: `runs/v7_reasoning_stage_500/report.json`
- V7 blinded results: `runs/v7_reasoning_stage_500/generalization_suite.json`

The V6 and V7 checkpoints remain under
`/root/autodl-tmp/pre_newton_corpus/runs/` on AutoDL.
