# Publication evidence map and next decision

## Scientific question, unchanged

Can a randomly initialized language model, trained on auditable pre-1687
mathematical and scientific material without the target law, generate a valid
derivation of inverse-square attraction from historical knowledge? Longer-term
scientific-discovery transfer is a motivation, not an outcome established here.

The direct Earth–Moon question remains unsolved. A circular-orbit exponent
calculation alone would not establish universal attraction, its mass dependence,
or a correct extension to the Moon. Those must be distinguished in scoring.

## Evidence available now

| Observation | Authoritative report | Permitted conclusion |
|---|---|---|
| V11 historical bootstrap, roughly 92M parameters and 197M training tokens; direct derivation fails | `V11_BOOTSTRAP_RESULTS.md` | This small, limited-budget implementation fails; not a general impossibility result |
| Answer-only vs continuation supervision, three matched fine-tuning seeds: 94/80/81 versus 48/47/49 exact relation answers out of 96 | `ANSWER_ONLY_PROTOCOL.md`, `audit/objective_replication/` | Objective choice improves this synthetic reading task; initial pretraining is shared, not independently replicated |
| All six above models give zero exact long-form physics answers out of four | same report | Reading improvement does not establish physics transfer on these probes |
| Balanced arithmetic sampling: 537/544 train, 4/30 validation | `MATH_CALIBRATION_PROTOCOL.md`, `audit/balanced_math/` | Strong familiar-task fitting with weak held-out accuracy, one seed |
| Prospective transfer: balanced model 46/48 familiar prompts, 4/48 new wording, 2/48 new operands with familiar answers, 0/48 new operands and answers | `audit/arithmetic_transfer/` | Narrow transfer; synthetic answer novelty is not historical-pretraining novelty |
| Actual mathematical passages contain lost layouts and corrupted numerals | `PREMISE_ACCESS_AUDIT.md`, `audit/historical_arithmetic_recorde/REVIEW.md` | Book inclusion and keyword counts cannot certify accessible premises |

These are separate experiments at different scales. Do not pool their prompts as
independent trials or conflate synthetic calibration with historical discovery.
Existing negative results are useful diagnostics, not yet a paper establishing
the project's main claim. A methods paper is possible only after a stable,
replicable benchmark and meaningful controls are added.

## Next experiment: repair premise accessibility before scaling training

Do not repeat arithmetic training merely because an earlier training score rose.
The immediate dependency is a small, source-verified historical premise pack:

1. Kepler period–distance relation: original English Streete pp. 39–40 already
   inspected; prepare literal transcription with page provenance and independent
   review. Admit only the reviewed passage and sufficient context, not the whole
   unchecked book. Check for target-law disclosure in that context.
2. Circular-motion relation: original Huygens Latin pp. 159–160 already inspected.
   Use a checked Latin transcription in the strict arm. An English translation is
   a separately labeled access control, never silently historical English.
   A [provisional I–V transcription](audit/source_pages/HUYGENS_TRANSCRIPTION_REVIEW.md)
   is now available for review; theorem V retains the original string-tension and
   weight comparison, without treating it as a universal attraction law.
3. Audit mathematical prerequisites by skill, not by book title. Recorde is a
   candidate; its incomplete worked examples remain quarantined. A missing image
   need not block review of the already retained physics-page images.

Freeze source hashes, admissible passages, excluded target-law material and test
prompts before training. Keep evaluation answers and modern translations out of
strict training. A modern pretrained reference is a contaminated capability
baseline only, not evidence of historical rediscovery.

On the existing V11 checkpoint first evaluate three **separate** endpoints:
historical passage reading in its own language, algebraic composition with given
premises, and unassisted direct Earth–Moon derivation. Report free generations,
reversed/counterfactual premises and all failures. Teacher-forced loss and ranking
are diagnostics, not primary discovery scores. If source-language reading fails,
do not interpret an English derivation failure as isolated scientific reasoning
failure. If composition fails with clean premises, source cleanup alone cannot
explain the failure either.

Only after this pack is frozen should matched-budget source-cleanup training be
submitted to the isolated AGI-Newton HPC directory. Compare unchanged historical
text against reviewed original-language text with the same initialization and
budget; hold translation assistance in a separate arm. Replicate promising
effects across independent pretraining seeds when feasible. No job is launched
by this document, and source approval remains unfinished.

## Publication gates still open

- Independently reviewed historical passages and leakage boundaries.
- A predeclared semantic/derivation benchmark, not only four physics questions.
- Meaningful retrieval, symbolic-composition and constant-answer controls.
- Source-level held-out tasks and multiple pretraining seeds; distinguish seed
  uncertainty from correlated prompt variants.
- Checked intermediate reasoning and physical assumptions, not merely exponent
  matching; blind expert review for any candidate discovery.
- Complete reproducibility bundle, synchronized repository and checkpoint access.

No success claim is made until these requirements have evidence. Scaling or RL
is not excluded, but neither is the next default action before the training
information and evaluation targets are made interpretable.
