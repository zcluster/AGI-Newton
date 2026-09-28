# V2: pre-1687 language bootstrap plus admissible reasoning

## Objective

This run is the first end-to-end test of the intended experiment rather than a
toy regression task.  A transformer is initialized from random weights, learns
ordinary pre-1687 English, then receives mathematical and astronomical
exercises that do **not** state the inverse-square law.  It is finally asked
whether it can combine two supplied premises:

1. orbital period squared varies as mean distance cubed; and
2. circular turning tendency varies as distance divided by period squared.

Algebraically those premises imply a dependence proportional to the reciprocal
square of distance.  Candidate ranking and open generation are both recorded;
candidate ranking alone is not counted as a rediscovery.

## Data

### General-language bootstrap

- Source: public PYCCLE release of EEBO Phase I.
- Historical cutoff: 31 December 1686.
- Deterministic document sample: seed 1686.
- Accepted: 1,197 documents (1,179 training, 18 validation).
- Training text: 200,033,084 UTF-8 bytes in 25,464 chunks.
- Quarantined: 1,112 documents, including 46 Newton/Principia references and
  one target-adjacent document requiring review.
- The release's word/POS lines were converted back to plain text.  No modern
  pretrained tokenizer or model weight was used.

The exact archive hash and all accepted source identifiers are stored in
`data/eebo_pre1687/general_audit.json`.  This automated filtering is suitable
for an engineering pilot, not yet a publication-grade contamination guarantee.

### Scientific core

The small manually selected pilot contains pre-cutoff mathematics, astronomy,
mechanics, instruments, observations, and competing theories.  Passages
containing target precursors are separated into `precursor_only.jsonl`.

### Target-free reasoning curriculum

The generated curriculum contains 25,980 examples (11.1 MB):

| Family | Examples | Purpose |
|---|---:|---|
| arithmetic | 6,000 | elementary numerical competence |
| ratio composition | 7,980 | compose direct and reciprocal powers; result exponent -2 is excluded |
| Kepler harmonic rule | 6,000 | calculate examples of period-squared/distance-cubed scaling |
| circular tendency | 6,000 | calculate distance divided by period squared |

Generation fails closed if it finds `inverse square`, `reciprocal square`,
`1/r^2`, `r^-2`, `duplicate ratio of distance`, or `square of distance` in a
target-bearing form.  This removes the answer while preserving the two pieces
of reasoning needed to derive it.

## Controlled arms

| Arm | Mixture | Meaning |
|---|---|---|
| strict | 200 MB general English + strict scientific core + reasoning curriculum twice | actual sealed test |
| precursor-exposed | strict mixture + isolated precursor file repeated eight times | deliberately amplified positive control |

Repeating the precursor file is intentionally artificial: it asks whether this
small model and evaluation harness can react to target exposure.  It is not a
historically natural training mixture.

Both arms used the same seed and a 25,482,752-parameter byte-level transformer
(8 layers, width 512, 8 heads, context 256), bf16 on one RTX 5090, batch 64,
and 15,000 updates.  Each saw 245,760,000 byte tokens.  Runtime was 10.7 minutes
for strict and 9.4 minutes for the exposed control.

## Results

Lower mean negative log-likelihood (NLL) is better.  Target margin is the
inverse-square NLL minus the best non-target NLL; a negative value means the
inverse-square candidate wins.

| Probe | Strict winner | Strict target margin | Exposed winner | Exposed target margin |
|---|---|---:|---|---:|
| supplied-premise derivation | inverse-square | -0.0119 | inverse-square | -0.0699 |
| direct modern Earth--Moon question | constant | +0.0288 | inverse | +0.2539 |
| period-style historical wording | constant | +0.3476 | inverse-square | -0.0937 |
| modern symbolic notation | constant | +1.4479 | inverse | +0.6758 |

The strict model therefore shows only a **very weak compositional signal** when
both required premises are explicitly supplied: square beats cube by just
0.0119 NLL.  It fails the direct question and the other two phrasings.  The
exposed control improves from one to two candidate wins, but also fails the
direct question.  Its mixed response means the current model is not yet a
strong positive-control detector.

Open generation is a clean failure in both arms.  For example, the strict
model continues the direct Earth--Moon prompt with unrelated early-modern
prose rather than a physical law.  It does not articulate the algebraic chain
`r/T^2`, `T^2 proportional to r^3`, therefore `r/r^3 = 1/r^2`.

The reported validation losses should not be compared between arms.  The
current byte loader concatenates input files before taking its final 5% as the
validation split; repeated precursor files therefore change the validation
distribution.  This does not affect the fixed law probes, but the next run
should use a separately constructed, identical validation set.

## Verdict

This V2 run successfully validates the full local-Mac-to-AutoDL workflow,
random initialization, historical bootstrap ingestion, leakage quarantine,
reasoning-curriculum generation, training, checkpointing, and fixed evaluation.
It does **not** demonstrate autonomous rediscovery of Newton's inverse-square
law.  The most defensible conclusion is that a 25.5M byte-level model can show
a fragile likelihood preference after the decisive premises are supplied, but
cannot yet express or robustly generalize the derivation.

## Next experiment justified by this result

1. Train a 100M--300M parameter model with a learned tokenizer on the same
   sealed corpus.
2. Replace templated answer exposure with multi-step, target-free algebra and
   dimensional-reasoning curricula.
3. Use one fixed, source-stratified validation set for both arms.
4. Pre-register many unseen prompt paraphrases and require an explicit
   derivation, not only candidate ranking.
5. Repeat at least five seeds and keep the direct Earth--Moon question fully
   held out until final evaluation.

## Reproducibility artifacts

- corpus ingestion: `src/ingest_pyccle_eebo.py`
- curriculum generation: `src/generate_admissible_reasoning.py`
- training: `src/train_random_init_smoke.py`
- checkpoint-only evaluation: `src/evaluate_checkpoint.py`
- strict report: `runs/v2_strict/report.json`
- exposed-control report: `runs/v2_precursor/report.json`
- all open generations: `runs/v2_strict/evaluation_all.json` and
  `runs/v2_precursor/evaluation_all.json`
- compact numeric comparison: `runs/V2_BOOTSTRAP_RESULTS.md`
