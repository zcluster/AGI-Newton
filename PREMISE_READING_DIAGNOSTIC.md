# V11 premise-reading diagnostic

Protocol frozen before this diagnostic's outputs, 2026-10-01.

Purpose: identify whether the existing random-initialized historical language model
can read a relevant English source, rather than equating an unsuccessful gravity
answer with failure of scientific reasoning. No training or tokenizer change.

Checkpoint: `runs/hpc_v11_bootstrap_seed1686/model.pt`; tokenizer:
`data/tokenizer_v11/pre1687_bpe.model`. Greedy generation, at most 60 new tokens,
and existing mean-token-NLL candidate scoring. Save every prompt and output.

Eight probes:

- Streete (1661), printed p39: original OCR numeric-example paragraph,
  asked which power of the periods it compares; two prompt formats.
- A modern English paraphrase of that relation; the same two formats.
- An explicitly synthetic counterfactual swapping square and cube; two formats.
- Two arithmetic controls, `1 - 3` and `3 - 1`.

The original OCR is extracted verbatim from the previously acquired book and its
SHA256 is recorded. The modern paraphrase and counterfactual are evaluation-only,
not historical documents or training material. Streete is not in this checkpoint's
training corpus, so source-given results concern reading, not trained recall.

Primary evidence is the saved free generation, reviewed for answering the actual
question. Ranking is a secondary diagnostic: a constant square choice scores 4/6
on reading probes and does not establish sensitivity to the input. Report paired
true/counterfactual behavior, not only aggregate accuracy. Two formats are correlated,
not independent replications. Short candidate differences can reflect lexical priors.

All prompt-plus-candidate sequences must fit the model's context without cropping.
No discovery success claim, causal attribution, or model-family generalization is
allowed from this single-checkpoint, post-hoc probe. This does not replace direct
Earth–Moon evaluation, source admission review, or independent training seeds.

Run the dependency-free fixture check:

```sh
python3 src/evaluate_premise_access.py --self-check
```

## Observed results

Tongji L40 job `2862873`: completed, exit `0:0`, elapsed 32 seconds.
An earlier job `2862869` failed because the remote raw-source directory was absent;
the source was copied, checked, and the completed job was then submitted.
No checkpoint was retrained or modified. Full outputs: `audit/premise_reading_v11.json`.
Source SHA256: `1f9d37d233dd32d2e1c2dc15786bbbdabd0d9bbb5626489a65335da4efcf4585`.
All prompts plus candidates fit within the 512-token context; prompts use 17–147 tokens.

| Probe | Expected | Ranking winner | Free-generation answer |
| --- | --- | --- | --- |
| Original OCR, question | square | cube | unrelated repetitive Earth/centre prose |
| Original OCR, continuation | square | square | unrelated repetitive Earth/centre prose |
| Modern paraphrase, question | square | square | math placeholders |
| Modern paraphrase, continuation | square | square | no substantive continuation |
| Swapped paraphrase, question | cube | square | math placeholders |
| Swapped paraphrase, continuation | cube | square | no substantive continuation |
| 1 minus 3 | −2 | −2 | math placeholders |
| 3 minus 1 | 2 | −2 | math placeholders |

Manual inspection finds zero responsive correct free-generated answers out of eight.
This is a descriptive count on correlated post-hoc probes, not an estimated success
rate with eight independent trials. Ranking is 4/8 overall: 3/6 reading, 1/2 arithmetic.
A constant-square reading baseline is 4/6, exceeding the observed reading ranking.
Neither modern-paraphrase pair changes its winner when the relation is reversed;
arithmetic ranking likewise stays at −2. Thus the ranking successes cannot establish
input-conditioned reasoning. Candidates have unequal token lengths, another reason
not to interpret mean-NLL comparisons as proof of understanding.

The evidence rules out neither better historical-language training nor future
discovery. It shows that removing Latin and OCR from these particular prompts is
insufficient for this checkpoint. Reliable English relation extraction and elementary
instruction-following remain unproven; source quality alone is not the only plausible
bottleneck. The checkpoint was trained for next-token continuation, not general
instruction-following. Changing both data and training objective would require a new,
explicitly labelled experiment rather than a causal claim about this diagnosis.

Next experimental gate: demonstrate input-sensitive extraction on a held-out relation
reading set before spending another large historical-only training run. An optional
instruction/calibration arm must avoid gravity target answers, be paired with a
historical-only control, and be reported separately from a strictly historical-data
discovery claim. Direct no-premise Earth–Moon testing remains the final target.
