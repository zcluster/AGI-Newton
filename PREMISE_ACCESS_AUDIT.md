# Premise-access audit (2026-09-30)

This audit asks a narrower question than whether the model can discover gravity:
does the **actual training text** expose the two relations that the current
physics prompts hand to the model? The corpus is still `machine_reviewed`, not
human-approved. These observations are not a claim of historical rediscovery.

The source audit now distinguishes byte-level `raw_sha256` from
`normalized_sha256`. Previously the field named `raw_sha256` actually held the
normalized-text digest. Rebuilding after that correction left all four
training/quarantine JSONL files byte-for-byte unchanged; only audit metadata
changed.

| Premise | Evidence in the sealed text | What is still uncertain |
|---|---|---|
| Kepler's period–distance relation | The 1619 *Harmonices Mundi* OCR has the relevant Book V, chapter III passage around printed pages 189–190: [`raw/kepler_harmonices_1619.txt`](raw/kepler_harmonices_1619.txt), lines 19799–19821; strict-corpus chunk 92, SHA-256 `183e7a97226abe80f87d30b07989d60ed98b02828f0e2dce88fb40b76a4d45cc`. | The decisive `sesquialtera proportionis mediarum distantiarum` wording is badly corrupted by OCR. Merely including this book does **not** establish that a text-only learner can recover `T² ∝ R³`. The [1619 carrier](https://archive.org/details/ioanniskepplerih00kepl) and page must be visually checked before using a corrected transcription. |
| Huygens's circular-force relations | The 1673 *Horologium Oscillatorium*, Part V, Theorems I–IV, occurs in [`raw/huygens_horologium_1673.txt`](raw/huygens_horologium_1673.txt), lines 8289–8327; strict-corpus chunk 39, SHA-256 `6e37bab8bf290732527e5302b54750f144434f13a3146381f7ced9a3aac13543`. The OCR is appreciably more legible. | The text gives ratio theorems for *centrifugal* force under controlled time, speed, and diameter conditions. Reading them as the modern `C ∝ R/T²` relation, then identifying the required inward tendency or attraction, requires additional interpretation. Check the [1673 carrier](https://archive.org/details/bub_gb_e_VXcl87u6AC) and its diagrams. |

The existing `src/generate_admissible_reasoning.py` explicitly teaches Kepler
period examples and the numerical rule “divide radius by period squared.” The
existing `src/evaluate_generalization_suite.py` physics prompts explicitly
**supply both relations**. Therefore performance on those prompts measures
composition **given premises**, not finding the premises in historical books.
The direct Earth–Moon question is a separate, harder endpoint and remains
unsolved. A centrifugal-to-attractive-force inference and an extrapolation
beyond measured orbits must also be stated, not silently credited.

## Next controlled comparison, fixed before training

1. Visually verify the two original-edition pages, record page-image locators,
   and have a human check any transcription. Keep raw OCR and corrected
   original-language passages as separately hashed inputs; never overwrite
   the OCR. Do not import a modern explanatory translation into the strict arm.
2. With matched tokenizer, model initialization, token budget, and at least
   three paired seeds, compare: raw OCR only; raw OCR plus the verified
   original-language passage; and an explicitly labelled synthetic-premise
   teaching arm. The synthetic arm is a capability control, not historical
   evidence. Keep Boulliau/Hooke target precursors excluded from all strict
   arms.
3. Report three endpoints separately: direct question with no supplied
   premises; retrieval/identification of the historical premises with source
   locators; and algebraic composition when the two premises are supplied.
   Score free generation and a checked derivation as primary outcomes.
   Candidate-answer likelihood and validation loss are diagnostics only.
   Include non-`-2` control exponents and answer-prior baselines so a fixed
   inverse-square preference cannot count as success.

This is a preregistration of **conditions**, not a completed experiment. The
historical-source and holdout gates must pass before a long GPU sweep or a
publication claim.
