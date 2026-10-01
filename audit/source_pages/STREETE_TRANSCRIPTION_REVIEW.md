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
