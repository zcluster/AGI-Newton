# AGI-Newton

Research code, corpus audit, training settings, and results for a historical
rediscovery test of Newton's inverse-square law. The latest Chinese progress
summary is [`AI_NEWTON_PROGRESS_2026-09-29.md`](AI_NEWTON_PROGRESS_2026-09-29.md).
The latest Tongji HPC baseline and historical-language comparison are in
[`V11_BOOTSTRAP_RESULTS.md`](V11_BOOTSTRAP_RESULTS.md); language modeling
improved, but free derivation and the direct Earth–Moon test still failed.

Latest diagnostic: [`READING_CALIBRATION_PROTOCOL.md`](READING_CALIBRATION_PROTOCOL.md).
A shared SentencePiece prompt-boundary defect was fixed and both baseline and
synthetic-calibrated models retested. The calibration improves answer formatting,
not reliable relation transfer or physics discovery. Earlier BPE generation/ranking
results must be treated as legacy measurements until retested with the corrected
helper; the original output files are retained for traceability.

The subsequent [`varied reading pilot`](VARIED_READING_PROTOCOL.md) increases
curriculum diversity and reaches 25/72 exact held-out answers, but only 3/36 complete
counterfactual pairs. Physics remains unsuccessful; this synthetic calibration arm
is explicitly separate from historical-only training. Scientific-text loss worsens
slightly on matched validation windows, so language retention is also tracked.

The [`copy/binding augmentation`](BINDING_CALIBRATION_PROTOCOL.md) then achieves
23/24 exact copying answers but defaults to square on all 96 new-label relation
cases, with 0/48 complete counterfactual pairs. A small exact-training-prompt audit
also exposes this failure. Low whole-stream loss must not be equated with learning
the answer-relevant relation.

The matched-input [`answer-only comparison`](ANSWER_ONLY_PROTOCOL.md) subsequently
reaches 94/96 exact answers and 46/48 complete reversal pairs, versus 48/96 and
0/48 for that control. This is a single-seed synthetic reading result, not Newton
rediscovery: original OCR reading, algebraic transfer and physics remain unsuccessful.
Scientific-text prediction also deteriorates. Paired fine-tuning-seed replication
is specified before further scaling or capability claims.

The repository includes the pilot OCR text, source manifests, generated
reasoning curricula, tokenizer, scripts, tests, and JSON evaluation results.
The full EEBO language archive and large V2--V7 model checkpoints are not in
Git; see the acquisition and experiment reports below for their provenance
and exact training settings. The pilot OCR editions are machine reviewed,
not yet certified as publication-grade historical inputs. No run so far
demonstrates autonomous rediscovery.

A [separate synthetic RL engineering demo](rl_demo/README.md) records code,
Mac MPS / RTX 5090 runs, and mixed outcomes. It has **not** been applied to
the historical Newton model.

For a local setup, use Python 3.12 or newer and install the core dependencies:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

`datasets` and `duckdb` are needed only for the optional Hla ingestion paths.
CUDA training used PyTorch 2.8.0 with CUDA 12.8 on one RTX 5090; the
platform-specific PyTorch build must match the machine used for reproduction.

## Original corpus project notes

This directory implements the corpus boundary for the first scientific-
rediscovery experiment: train a language model from random initialization on
knowledge available before Newton's *Principia*, then test whether it can infer
an inverse-square interaction from observations and admissible mathematics.

The cutoff is **31 December 1686**. A date cutoff alone is not sufficient:
Boulliau and Hooke discussed inverse-square gravitational hypotheses before
1687. The build therefore produces three auditable data arms:

1. `strict_clean.jsonl` — approved pre-cutoff sources with target-bearing
   passages excluded. This is the default training corpus.
2. `precursor_only.jsonl` — deliberately isolated target precursors. Never mix
   this file into the strict experiment.
3. `date_only_all.jsonl` — the date-only baseline, including precursors. This
   measures how much apparent rediscovery is explainable by historical leakage.

`quarantine.jsonl` contains rejected documents and reasons. `audit.json`
contains counts, hashes, and every leakage match.

## Corpus layers

- **Language bootstrap:** general English printed no later than 1686. It gives
  the model syntax and ordinary vocabulary, not modern scientific answers.
- **Curated core:** primary mathematics, astronomy, mechanics, instruments,
  observations, and failed theories. Every edition must be reviewed by a
  human and linked to a scan or diplomatic transcription.
- **Target precursors:** Boulliau, Hooke, and any other source that states or
  strongly implies the held-out law. These are an experimental treatment, not
  default training data.

Modern translations are not accepted in the strict arm. They can introduce
modern notation and interpretation even when the underlying work is ancient.
Digitization date is harmless only when the digital text faithfully represents
a verified pre-cutoff edition.

## Quick validation

From this directory:

```bash
python3 -m unittest discover -s tests -v
python3 src/build_corpus.py \
  --manifest tests/fixtures/manifest.jsonl \
  --raw-dir tests/fixtures/raw \
  --output-dir /tmp/pre_newton_demo
```

The fixture must yield two strict documents, one isolated precursor, and two
quarantined documents. This is deliberately small: it tests the epistemic
boundary before any expensive download or model training.

## Adding real sources

1. Add a record to `manifest/curated_sources.jsonl`.
2. Locate the exact historical edition. Record both `work_year` and
   `edition_year`; never substitute a modern translation silently.
3. Download OCR/transcription to `raw/<id>.txt` and record its `source_url`.
4. Change `review_status` to `approved` only after checking title page,
   edition, completeness, and OCR quality.
5. Build the corpus. Inspect `audit.json` and every quarantine decision.

The candidate-discovery script queries Internet Archive metadata only; it does
not auto-approve a result:

```bash
python3 src/discover_internet_archive.py \
  --manifest manifest/curated_sources.jsonl \
  --output candidates/internet_archive.jsonl
```

Internet Archive, Wikisource, and Project Gutenberg are carriers. Their files
must still be checked against the bibliographic edition in the manifest.

Download OCR only for the explicitly selected candidates:

```bash
python3 src/fetch_internet_archive.py \
  --manifest manifest/curated_sources.jsonl \
  --selection manifest/selected_ia.jsonl \
  --raw-dir raw \
  --audit audit/ia_downloads.jsonl
```

Downloaded files retain `pending_review` status. Inspect their catalogue title,
date, title-page OCR, and representative interior passages before copying
records into an approved pilot manifest.

For engineering validation only, the preliminary machine-reviewed manifest can
be built explicitly:

```bash
python3 src/prepare_machine_review.py \
  --manifest manifest/curated_sources.jsonl \
  --audit audit/ia_downloads.jsonl \
  --output manifest/pilot_machine_reviewed.jsonl
python3 src/build_corpus.py \
  --manifest manifest/pilot_machine_reviewed.jsonl \
  --raw-dir raw \
  --output-dir data/real_pilot \
  --allow-machine-reviewed
```

The flag is intentionally conspicuous. A publication-grade strict build must
replace `machine_reviewed` with a named human approval and omit the flag.

Finally, verify that the real strict corpus can update a randomly initialized
model. This tiny byte-level GPT is a pipeline test, not a rediscovery claim:

```bash
python src/train_random_init_smoke.py \
  --data data/real_pilot/strict_clean.jsonl \
  --output-dir runs/random_init_smoke \
  --steps 100
```

A successful run must save a checkpoint and reduce held-out next-byte loss.
Later experiments add a corpus-trained tokenizer, a 91.5M model, a general
pre-1687 language layer, and a separate physics evaluation harness.

For the first real controlled run (strict corpus versus deliberately exposed
historical precursors), see [`QUICK_STAB.md`](QUICK_STAB.md). Unlike the earlier
pipeline-only check, it records free generation and blinded law-completion
scores for both randomly initialized models.

The first complete language-bootstrap experiment is documented in
[`V2_BOOTSTRAP_EXPERIMENT.md`](V2_BOOTSTRAP_EXPERIMENT.md). It uses PYCCLE's
public EEBO Phase I release. A complete, revision-pinned metadata census of
Hla's public corpus found 395 records dated before 1687 (357 distinct
year/title pairs). Manual title triage found four science candidates, not
four verified pre-Newtonian scientific works. See the cached
[`Hla census`](audit/hla_before1687/README.md) and its per-record catalogue.
Full-text date/provenance validation and usable-token counts remain unfinished;
its suitability for a 200 MB bootstrap is not yet established.

For a newly verified original-page English witness to Kepler's
period–distance premise, see the [Streete source audit](STREETE_ENGLISH_PREMISE_AUDIT.md).
This source remains outside the training corpus pending whole-book review.

The next controlled series, including the learned tokenizer and the V3--V5
reasoning interventions, is documented in
[`V3_V5_CONTROLLED_CURRICULUM.md`](V3_V5_CONTROLLED_CURRICULUM.md).

The V6 diversity experiment, blinded deterministic-generation suite, and V7
curriculum-only stopping result are documented in
[`V6_V7_DIVERSITY_REPORT.md`](V6_V7_DIVERSITY_REPORT.md).
The local V8 continuation-weighting ablation and stricter generation audit are
documented in [`V8_WEIGHTING_PILOT.md`](V8_WEIGHTING_PILOT.md).
The V9 compositional grid and final-exponent weighting ablation are documented
in [`V9_COMPOSITION_GRID.md`](V9_COMPOSITION_GRID.md).
The three-seed replication and counterfactual audit, which overturns a
single-seed weighting conclusion, are in
[`V10_MULTISEED_AUDIT.md`](V10_MULTISEED_AUDIT.md).
The historical-premise accessibility gap and the next controlled comparison
are documented in [`PREMISE_ACCESS_AUDIT.md`](PREMISE_ACCESS_AUDIT.md).
The source-corrected V11 pilot corpus and its separate raw-text baseline
are documented in [`V11_PRIMARY_SCAN_CORPUS.md`](V11_PRIMARY_SCAN_CORPUS.md).
Tongji L40 deployment and the infrastructure-only benchmark are in
[`hpc/README.md`](hpc/README.md).

Build the pre-1687 EEBO layer from an already downloaded PYCCLE archive:

```bash
python3 src/ingest_pyccle_eebo.py \
  --archive data/eebo/pyccle-eebo.tgz \
  --dates data/eebo/dates-eebo.csv \
  --output-dir data/eebo_pre1687 \
  --sample-documents 5000 \
  --max-train-bytes 200000000
```

Generate the target-free arithmetic, ratios, Kepler, and circular-motion
curriculum:

```bash
python3 src/generate_admissible_reasoning.py \
  --output data/reasoning/admissible_reasoning.jsonl \
  --examples-per-family 6000
```

Hla remains available as a secondary corpus experiment.  Stream it only with
the stricter 1686 cutoff and this project's target-specific exclusions:

```bash
pip install datasets
python3 src/ingest_hla.py --output-dir data/hla_pre1687 --max-records 10000
```

Remove `--max-records` only after inspecting the pilot audit. Documents with a
hard answer, a modern term, or even a target-adjacent review flag are withheld;
they are not silently admitted to the strict language layer.

## What this version intentionally does not do

- It does not claim that a title match is the correct edition.
- It does not silently translate Latin, Greek, French, or Italian into modern
  English.
- It does not download millions of documents before the exclusion policy has
  been tested.
- It does not treat keyword filtering as proof of zero contamination.
