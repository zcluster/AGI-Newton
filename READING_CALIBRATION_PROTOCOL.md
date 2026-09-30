# Reading calibration pilot (not the historical-only discovery arm)

Frozen before running this pilot, 2026-10-01. V11 premise-reading failures motivate
this intervention; its outcomes cannot retroactively validate that diagnostic.

Starting checkpoint: V11 historical bootstrap, 91.5M parameters, seed 1686.
Same tokenizer and architecture; initialize weights from that checkpoint and reset
the AdamW optimizer, as the existing trainer's `--resume` implements. Original
checkpoint remains untouched. Fine-tune 300 steps, batch 16, context 512, bf16,
learning rate 3e-5, warmup 30; seed 1686. This is an exploratory single-seed pilot,
not a replicated causal comparison or a choice among multiple reported best runs.

Synthetic, evaluation-informed instruction data: 120 records on extracting square
or cube from a supplied relation. Six generic training nouns; four distinct test
nouns. The 32 test cases include a held-out question template as well as familiar
wording with held-out nouns. They remain semantically close, not a semantic-family
holdout. No gravity, orbital period, distance, inverse-square target, or algebraic
composition answers occur in calibration training. The data are modern generated
instruction examples, not newly found pre-1687 documents.

Reuse the existing tokenizer's continuation weighting (4 versus 1) and unmodified
trainer. This is continuation-weighted next-token training, not strictly answer-only
SFT: random windows can cross document boundaries. 2,457,600 training tokens seen.
Synthetic validation loss is monitored but no early stopping or model selection.

Evaluate the original and calibrated checkpoints on the exact same 32 held-out
cases, saving greedy generations and rankings. Primary descriptive endpoint: free
answers explicitly naming the correct power without giving a conflicting power.
Report prompt subgroups and counterfactual pairs. A constant square answer reaches
16/32; correlated cases and shared initialization prohibit population-level claims.
Human review is required for nonresponsive or ambiguous outputs; raw outputs remain
available. Candidate NLL is secondary, not evidence of discovered knowledge.

Then rerun the frozen eight source-reading/arithmetic probes, the existing
generalization suite, and the separate direct Earth–Moon checkpoint evaluator. Improvement on
synthetic reading alone is only calibration success. A successful physics answer
would still require independent seeds, provenance/leakage audits, and stronger
controls before a discovery claim. This arm is never labelled historical-only.

## Execution and an evaluation defect

Calibration job `2862895` completed in 1m35s, exit `0:0`; training took 23.19s.
Training loss reached 0.0140; held-out synthetic validation loss changed from
1.5860 to 1.1612. These do not demonstrate free-answer generalization.

The first evaluation exposed a common prompt-boundary defect: the tokenizer
encodes the trailing blank in `Answer: ` as a separate `▁` token, while the same
blank inside training text is incorporated in the next word's leading-space piece.
For example, the correct full-text segmentation proceeds from `:` to `▁s`, whereas
the old evaluation inserted `▁` before `▁s`. The resulting inference prefix was
not the prefix on which answers were trained. The model often chose immediate EOS.

Both shared helpers (`generate` and `score`) now strip trailing horizontal blanks
before encoding the prompt. Generation preserves the original prompt verbatim in
its returned text, so downstream correctness checks do not change their prefix
contract. A real-tokenizer regression check verifies full-text segmentation,
generation/scoring input IDs, exact prompt preservation, and immediate-EOS handling.
The protocol did not anticipate this defect; the correction and retest are explicit
post-hoc implementation changes, not a quietly substituted favourable result.

Retest job `2862901` completed in 59s, exit `0:0`, without retraining either model.
Raw original outputs remain under `audit/reading_calibration/`; authoritative retests
have the suffix `boundary_fixed.json`, with calibrated retests in `calibrated/`.

| Corrected held-out endpoint | Historical baseline | Synthetic calibrated |
| --- | ---: | ---: |
| Exact correct answer, including queried noun | 0/32 | 4/32 |
| Candidate ranking | 16/32 | 17/32 |
| Both members of a reversed-relation pair exactly correct | 0/16 | 0/16 |
| Constant-square ranking baseline | 16/32 | 16/32 |
| Abstract compositional free answers | 0/12 | 0/12 |
| Premise-given physics free answers | 0/4 | 0/4 |

Run `python3 src/summarise_reading_calibration.py` to regenerate the exact-answer,
ranking and paired counts. Exact matching is an additional conservative audit:
the protocol's power-only endpoint is 15/32 for calibrated output, still below the
constant-square 16/32. Many responses name a training noun instead of the queried
held-out noun. All 32 calibrated outputs produce a short `square/cube of ...` answer;
31 choose square, showing format acquisition without reliable relational transfer.
The 4 exact answers comprise three familiar-question cases and one unseen-question
case. No pair is solved in both directions. These are descriptive, correlated counts.

The original eight reading/arithmetic probes remain without a fully responsive
correct answer after either calibration or boundary correction. Some calibrated
answers use the right power but the wrong subject (`square of the lengths` when
asked about periods); this is not credited as successful source reading.

Interpretation: the pilot learns an answer format and heavily overfits its tiny
instruction set; it does not establish historical premise acquisition, compositional
reasoning, or gravity discovery. A larger varied calibration dataset may help, but
that is a hypothesis, not an observed outcome. Do not launch a larger historical
pretraining run on the strength of this pilot. Earlier BPE evaluation reports must
be treated as legacy until their checkpoints are retested with the corrected helper.

### Training serialization correction and aligned rerun

Before interpreting the calibration failure, a second boundary defect was verified:
`tokenize_corpus.encode_record` encoded procedural text segments separately, inserting
a dummy-prefix space after a newline. Actual weighted training text decoded as
`\n Question:`, while the plain text decoded as `\nQuestion:`. Thus weighted and
unweighted token streams differed, confounding prior loss-weight comparisons.
The helper now encodes the whole text once and assigns weights using native
SentencePiece character offset mappings (0.2.2 or later). Real-tokenizer checks verify identical token IDs
for weighted/unweighted encoding, including Unicode text and final-exponent weights.

The first calibration run and both evaluation retests remain archived. An aligned
rerun uses the same 120 training records, 300 steps, learning rate and initial model,
but corrected serialization; its output directory is
`runs/hpc_reading_calibration_aligned_seed1686`, leaving both old checkpoints intact.
This is an explicit implementation-correction rerun, not best-of-seeds selection.
Its results must be reported separately. Earlier synthetic weighted experiments
also require retesting before claims about the effect of loss weighting.

Aligned rerun job `2862932` completed, exit `0:0`, elapsed 1m18s; training took
22.41s. Job `2862919` had first failed at tokenization because SentencePiece 0.2.2
removed the deprecated immutable-proto API; the native offset-mapping API avoids
adding protobuf and was verified before submitting the successful rerun.
The new dependency minimum reflects that API. The real-tokenizer regression check
and all 23 existing unit tests pass on the HPC environment. A separate initial
full-test failure was due to missing remote source fixtures and an outdated remote
build helper; both were synchronized before the successful tests, without changing
the local test's intended assertions.

| Aligned rerun endpoint | Result |
| --- | ---: |
| Exact held-out answers (power and queried noun) | 6/32 |
| Power-only answer audit | 17/32 |
| Candidate ranking | 21/32 |
| Both reversed-relation answers exactly correct | 1/16 |
| Abstract compositional free answers | 0/12 |
| Premise-given physics free answers | 0/4 |

Aligned validation loss reaches 1.0261, with train loss 0.0140. The training stream
contains only 5,600 tokens, revisited many times; reliable generalization is not
established. Its source-reading/arithmetic diagnostic still contains no complete
correct response. Direct Earth–Moon generation recorded by the trainer (sampled,
not the greedy suite) says `It varies as the square of the subsides`, followed by
an unrelated calibration answer. This is not the inverse-square law. The earlier
uncalibrated/calibrated direct retest job `2862904` likewise completed and its
outputs are archived; neither gave a valid direct answer.

Aligned checkpoint SHA256:
`3040d2b4a966987119a65268e35507ce0236a34713ab3d4824c5359d3390aa36`.
Weights remain on HPC, not Git; all three checkpoints are separate. No project GPU
jobs remain running after these pilots. Current inference: correct serialization
is necessary, but this tiny reading curriculum is insufficient. The next experiment
must test richer, varied relation reading with input-sensitive holdouts; extra
training on the same 120 records alone is not supported by these results.
