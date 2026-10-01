# Streete (1661): provisional English premise transcription

Status: assistant visual transcription, pending independent review; **not admitted
to training**. Source: *Astronomia Carolina*, printed pp. 39–40, original-edition
scan. See `STREETE_ENGLISH_PREMISE_AUDIT.md` for bibliographic provenance.

Image n38 SHA-256:
`7c2ef45ff1910f6db57b070d0119159bd6b1903ee9542ce4301ca6d7cc48c9af`.
Image n39 SHA-256:
`7c8b017dcfa7d3bc0674f849e37bf6b655670a5a3cc2b4a68d235332656fae6f`.
Both hashes were rechecked against retained images before this transcription.

## Transcription convention

This is a selected prose excerpt, not a diplomatic transcription of both pages.
Long s is rendered as s, line breaks and line-end word division are joined, and
stacked halves are rendered as `1/2`. Spelling and numerical values are retained.
These transformations do not supply a modern physical explanation. The planetary
table and logarithmic calculation are **not transcribed** here; omissions are
explicit, and this document must not be serialized as uninterrupted book text.

## Printed page 39: heading and worked-example prose

> Of the Primary Planets,
>
> The Proportion of their Orbes to the Periods of their Revolutions.

[Opening discussion and planetary table omitted from this selected excerpt.]

> For Example, The Period of the Revolution of the Earth reduced into
> minutes of time, being 525968. 1/2. and of Mars. 989247. 1/2. I say, as the
> square of. 525968. 1/2. to the square of. 989247. 1/2. so the Cube of 100000.
> the mean distance of the Earth, to the Cube of 152369.the Mean distance of
> Mars. or by artificiall numbers,

[Logarithmic calculation begins at the bottom and continues on printed p. 40;
not transcribed in this excerpt.]

## Printed page 40: continuation prose

> And so of the rest. The like proportion is upon good grounds assigned to
> the four Satellites about Jupiter, in their secondary Revolutions and distances
> from him.

[Following paragraph and next section omitted.]

## Review questions and limits

1. Verify every numeral and the half fractions against the retained images.
2. Decide whether the excerpt plus heading and explicit omission boundaries is
   sufficient context for an experimental passage-level admission. No whole-book
   approval follows from it.
3. Confirm target-law leakage screening of the selected context. The excerpt
   states an orbital proportion, not an inverse-square attraction law.
4. Keep modern symbolic interpretation and answer keys in evaluation metadata,
   not appended to the strict source text. The Jupiter statement does not itself
   justify extrapolation to Earth's Moon or universal attraction.

No new tokenizer, corpus binary, model weight or training job is created here.
This material is a review artifact; its headings and editorial notes are modern
metadata and are not historical training prose.

## Frozen checkpoint-only reading diagnostic

`streete_clean_reading_probes.json` contains four probes: question/continuation
interfaces for the selected clean excerpt, and corresponding square/cube-swapped
counterfactuals. The latter are modern interventions, not historical sources.
They reuse the existing premise evaluator and candidate answers. This is a
post-hoc diagnostic chosen after earlier reading failures, not a blind benchmark.
Only the period-power endpoint is tested; force derivation and source retrieval
are not tested. The numeric values in counterfactuals are deliberately unchanged,
so these cases test textual reading rather than numerical physical consistency.
Evaluate the unchanged V11 checkpoint, legacy no-BOS interface; inspect full
generations and both members of each pair. A constant-square answer would get
2/4 individually but 0/2 pairs. No training or checkpoint selection is authorized
by this fixture; source text remains pending independent admission review.

## Observed checkpoint-only diagnostic

Job `2864262` completed with exit `0:0` in 25 seconds. The retrieved report is
`streete_clean_reading_result.json`. Its fixture SHA-256 is
`cd270a121c8ee40e9d9104c60c8833af31fdd7dcb0019b4aeb539ee8e9e32a7d`;
checkpoint SHA-256 is
`10deb0e421e963ce2e715afa37601d6d0bd9a3bc15dbcc624e24fe8d0ab2a480`.
All four IDs, prompts, targets and candidate strings were checked against the
frozen local fixture; legacy no-BOS inference was verified. No training occurred.

Candidate ranking selects `square` in all four cases: 2/4 individually and 0/2
complete counterfactual pairs, equal to a constant-square baseline. Full generated
answers are repetitive: the original question produces “The square of the whole
Numbers is 100000” repeatedly; the original continuation repeats “square of the
square”; both altered passages still produce repetitive Square statements.
None supplies the complete requested period-power relation. Recognizing a first
word is not credited as a valid full answer or derivation. The report includes
the prompt within `generation`; inspect only its generated suffix when grading.

This diagnostic does not isolate a causal OCR effect: it changes surface text
and has no matched training intervention. It does establish that damaged OCR is
not necessary for failure on this specific supplied clean excerpt. It is also
not source retrieval, historical premise learning, or force-law discovery.

Next decision: do not launch physics-source fine-tuning on the assumption that
text cleanup alone solves the access problem. Establish basic input-sensitive
English reading on held-out historical passages, retaining the existing
answer-only control results and counterfactual pair scoring. The English-first
main line remains distinct from any optional Latin source-access diagnostic.

### Prospective existing-checkpoint transfer comparison

Before viewing new outputs, evaluate the same frozen four prompts on all six
saved objective-comparison models (continuation and answer-only, fine-tuning
seeds 1686–1688), using the unchanged evaluator and no-BOS setting. Do not retrain,
change candidates, or choose a seed. These models share V11 pretraining and use
synthetic calibration, so this compares transfer of that calibration, not six
independent historical models. The pilot baseline outputs are already known:
this extension is exploratory, not an independent blind benchmark. Report full
generated suffixes, candidate ranking and both complete reversal pairs per model.
The runnable job is `hpc/tongji_streete_objective_transfer.sbatch`; it refuses
to overwrite existing results or proceed without a checkpoint.

### Six-model transfer results

Job `2864308` completed, exit `0:0`, elapsed 1m15s. All six reports are retained
as `streete_{continuation,answer_only}_{1686,1687,1688}.json`. Each report's fixture
hash, all four prompt/target/candidate identities and no-BOS setting were checked.
Checkpoint hashes are retained in the raw reports; seed-1686 hashes match the
previous objective experiment. These are evaluation runs, not new training.

| Objective | Fine-tuning seed | Ranking correct /4 | Exact candidate-text generated suffix /4 |
|---|---:|---:|---:|
| continuation | 1686 | 2 | 0 |
| continuation | 1687 | 2 | 1 |
| continuation | 1688 | 2 | 1 |
| answer-only | 1686 | 2 | 0 |
| answer-only | 1687 | 2 | 1 |
| answer-only | 1688 | 2 | 1 |

Exact candidate-text matching is a descriptive check, not a universal semantic
grader. In particular, singular `period` is not a substantive reasoning error.
Inspection of all generated suffixes supplies an important qualification:

- Continuation seed 1686 produces `square of the period.` and `cube of the period.`
  on the original/counterfactual **question** pair. This is a semantically correct
  paired response despite zero exact candidate-string matches. Its continuation
  pair substitutes `sides` and `totals`, so the complete four-case task still fails.
- Continuation seeds 1687–1688 answer the original question correctly but substitute
  `products` in the counterfactual question. Their continuation answers contain
  truncated `Revolu` labels and, for the original, repeated squares.
- All three answer-only seeds answer both questions with `cube`: wrong on the
  original, right on the counterfactual (seed 1686 uses singular `period`). Seeds
  1687–1688 track the changed power in continuations but bind it to `Earth`, not
  periods; seed 1686 repeats squares in both continuations.

Thus a post-hoc semantic reading identifies one complete question reversal pair
in continuation seed 1686 and none in the other five models. This interpretation
is explicitly manual and not independent blind adjudication. None of the six
has both interfaces' complete pairs correct. Ranking always gives 2/4 with 0/2
complete ranking pairs: continuation ranks square everywhere, while answer-only
ranks cube for questions and square for continuations.

The replicated synthetic reading advantage does **not** transfer as a consistent
advantage on this four-case historical prose diagnostic. Conversely, calling all
generations complete failures would overlook the valid seed-1686 question pair.
The result motivates a broader, predeclared historical reading suite with semantic
entity binding and independent adjudication, not selecting this seed as a success
or pooling repeated prompts into an inflated sample size. Force-law discovery
has not been tested by these four reading questions.
