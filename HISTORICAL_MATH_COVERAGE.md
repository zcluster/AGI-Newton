# Historical mathematics coverage audit — 2026-10-01

## Finding

The V11 scientific training stream contains 1,600,825 tokens from five sources
whose existing manifest role is `core_math`. That is 37.34% of the scientific
stream, but only 2.28% of the 70,125,444-token combined historical bootstrap.
The latter is the contribution of these curated sources, **not the total
mathematical content of the combined corpus**: the EEBO English stream has not
been passage-level subject classified. Physics and astronomy works also contain
mathematics. Conversely, a mathematical book's entire OCR is not usable mathematics.

The current evidence therefore supports a coverage and usability concern, not
a proven causal explanation of the failed Newton derivations.

## Exact source accounting

Counts include each record's BOS and EOS, using the original V11 tokenizer.

| Source | Edition | Language | Training tokens | Combined stream share |
| --- | ---: | --- | ---: | ---: |
| Euclid, Billingsley's *Elements of Geometrie* | 1570 | English | 923,192 | 1.316% |
| Descartes, *La Géométrie* | 1637 | French | 255,333 | 0.364% |
| Wallis, *Operum mathematicorum*, part II | 1656 | Latin | 221,338 | 0.316% |
| Napier, *Mirifici logarithmorum canonis descriptio* | 1614 | Latin | 102,609 | 0.146% |
| Barrow, *Lectiones geometricae* | 1670 | Latin | 98,353 | 0.140% |
| **Math-role source total** | | | **1,600,825** | **2.283%** |

The scientific stream totals 4,287,350 tokens: mathematics-role sources
1,600,825; physics 1,527,523; astronomy 915,541; observation 243,461.
Across all scientific sources, language totals are English 1,856,621, Latin
1,587,801, Italian 587,595, and French 255,333. These are source metadata
languages, not automatic language-detection results.

## What is missing from this evidence

There is no dedicated elementary arithmetic source among these five math-role
sources. This does **not** establish that arithmetic is absent from their text
or the EEBO collection. There is also no measured count of clean worked examples
for signed arithmetic, ratios, powers, substitution, or elimination. No
passage-level formula fidelity or expert-approval percentage has been established.
The English math-role source is primarily geometrical; the other listed sources
require Latin or French access. Training a mostly English bootstrap does not
demonstrate the ability to transfer their mathematical content into English answers.

Whole-source automated historical screening is not human certification. This
audit counts what was actually tokenized, not whether each passage is historically
clean, legible, correctly interpreted, or sufficient for the Newton task.

## Training implications and a falsifiable next step

The later synthetic calibration is a separate capability arm, not historical
evidence. It contains 29,033 mathematical training records, but signed subtraction
has only 1,394/575,730 supervised target tokens (0.24%). Raising their weight to
128 at fixed inputs and budget did not improve subtraction; see
[the paired results](MATH_CALIBRATION_PROTOCOL.md#subtraction-weighting-results-and-next-checks).
More mathematical text or a larger loss multiplier cannot yet be claimed to solve
the problem.

Before another training run:

1. Test BOS/no-BOS inference with unchanged saved checkpoints and prompts; do not
   silently change legacy evaluation defaults.
2. Measure the sampled exposure of the sparse arithmetic tail under the actual
   batchwise loss normalization.
3. Build a skill-level inventory of **already available** historical passages,
   starting with arithmetic, proportions, and algebra. Record edition, page,
   original wording, legibility, and target-law leakage status. Add sources only
   for demonstrated gaps; modern explanations remain in a separate calibration arm.

Prior to a new experiment, freeze basic arithmetic and proportional-reasoning
generation gates and a matched-budget comparison. Do not treat candidate ranking,
memorized worked examples, or synthetic success as historical Newton discovery.

## Reproduction

From the repository root with the existing local data and dependencies:

```sh
python src/audit_historical_math_coverage.py
```

The script asserts the source chunk and token totals against the saved tokenizer
audit, reconstructs the complete scientific token stream, and verifies its SHA-256
against the actual training binary. The verified stream SHA-256 is
`8192ba313b8a4b408c48743d4ed6e72a3d793ecb7915683e49d9790d1461d46e`.
The JSON result retains source totals and input/tokenizer hashes at
`audit/historical_math_coverage.json`. It does not download or reclassify Hla.
