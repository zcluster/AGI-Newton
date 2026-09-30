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
| Kepler's period–distance relation | The 1619 *Harmonices Mundi* OCR has the relevant Book V, chapter III passage around printed pages 189–190: [`raw/kepler_harmonices_1619.txt`](raw/kepler_harmonices_1619.txt), lines 19799–19821; strict-corpus chunk 92, SHA-256 `183e7a97226abe80f87d30b07989d60ed98b02828f0e2dce88fb40b76a4d45cc`. | The decisive `sesquialtera proportionis mediarum distantiarum` wording is badly corrupted by OCR. Merely including this book does **not** establish that a text-only learner can recover `T² ∝ R³`. |
| Huygens's circular-force relations | The 1673 *Horologium Oscillatorium*, Part V, Theorems I–IV, occurs in [`raw/huygens_horologium_1673.txt`](raw/huygens_horologium_1673.txt), lines 8289–8327; strict-corpus chunk 39, SHA-256 `6e37bab8bf290732527e5302b54750f144434f13a3146381f7ced9a3aac13543`. The OCR is appreciably more legible. | The text gives ratio theorems for *centrifugal* force under controlled time, speed, and diameter conditions. Reading them as the modern `C ∝ R/T²` relation, then identifying the required inward tendency or attraction, requires additional interpretation. |

## Original-page visual check (2026-10-01 correction)

I inspected the **original-edition scans**, not just their OCR. Kepler's
relevant statement begins near the bottom of printed page 189 and continues
at the top of page 190 ([printed p. 189 / image n280](https://archive.org/download/ioanniskepplerih00kepl/page/n280.jpg),
[printed p. 190 / image n281](https://archive.org/download/ioanniskepplerih00kepl/page/n281.jpg); local copies:
[`n280`](audit/source_pages/kepler_1619_n280.jpg), [`n281`](audit/source_pages/kepler_1619_n281.jpg)).
The earlier PDF citation said “scan pages 281–282”; that was one page late.
The separately downloaded PDF SHA-256 is
`fe23e48c1a43f27875415755ca63b554889f78a0c449c76fafac960ed694dc35`.
The print clearly states a sesquialterate proportion between planetary
periods and mean distances; the following page discusses taking cube roots
of periods and squaring them. This supports the **historical presence** of
the relation, but not its recoverability from our damaged OCR.

Huygens's heading and Theorem I begin on printed page 159; Theorems I–IV
continue on page 160 ([printed p. 159 / image n176](https://archive.org/download/bub_gb_e_VXcl87u6AC/page/n176.jpg),
[printed p. 160 / image n177](https://archive.org/download/bub_gb_e_VXcl87u6AC/page/n177.jpg); local copies:
[`n176`](audit/source_pages/huygens_1673_n176.jpg), [`n177`](audit/source_pages/huygens_1673_n177.jpg)).
The earlier PDF citation said “scan pages 177–178”; that too was one page late.
The separately downloaded PDF SHA-256 is
`0c6fff9868252f75c2bb5bafd1379645de655d423424edac9158309960c292cf`.
For equal bodies, the text separately relates centrifugal force to diameter
at equal period (I), inversely to diameter at equal speed (II), and to squared
speed at equal circumference (III); IV relates period to square-root diameter
at equal force. The combination implies the magnitude scaling
`C ∝ R/T²` for circular motion, but the book does **not** thereby state a
universal Earth–Moon *attractive* force law. A subject-matter expert should
check this reading and any proposed transcription before either enters a
training arm. The two PDF hashes identify the exact scans inspected; neither
PDF nor an edited transcription has been inserted into the model corpus.

The four page-image SHA-256 digests, in the same order as the links above, are
`b7003d30828b353318b5273c6037073a86882b87f6eee3c444de616c38833b56`,
`fff2a1c0f2a422c0dc4ae1d00b6d65ba8448859af7bae979c7893e47e7442ba9`,
`40db464047214820a27f3c0bccdd6147b36b2db67ea362d5f96bc17a8be15db0`, and
`251a7ebf041eceb86d70f83eebfa46d28bfd8e03f0104a3b657f46f9f9b54d93`.
These are **source evidence, not training examples**. The decisive Kepler
phrase on p. 189 reads “*sit praecise sesquialtera proportionis mediarum
distantiarum*”; the Huygens heading explicitly says “*De vi centrifuga ex
motu circulari*.” Both are provisional visual readings, not a checked
machine-readable edition. In particular, no modern paraphrase of either
passage is admissible to the strict historical training arm.

## Language-access gate

**Both decisive pages are Latin, not English.** In the V11 scientific
training split, 575 Latin chunks contain 4,346,018 characters, versus 824
English chunks containing 6,181,578 characters (counting JSONL `text`
characters). The two relevant books account for 114 Kepler chunks (862,088
characters) and 37 Huygens chunks (285,909 characters). The later bootstrap
adds 200,033,084 bytes of ordinary pre-1687 English, while the physics
evaluation asks its questions in English. These are different units and are
not a token-frequency estimate, but they establish that the bootstrap is
strongly English-dominant. A random-initialized model cannot be assumed to
understand the two Latin premises merely because their books are included.

Thus the current negative result cannot isolate scientific reasoning failure
from damaged OCR, insufficient Latin acquisition, or Latin-to-English
transfer failure. Any strict English-only arm needs an independently dated
pre-1687 English witness to **each** required premise; none has yet been
verified here. A modern English translation, if used, belongs in a separately
labelled translation/capability control, not in the historically sealed arm.
Alternatively, a multilingual historical arm must test Latin premise
identification before crediting an English derivation.

The existing `src/generate_admissible_reasoning.py` explicitly teaches Kepler
period examples and the numerical rule “divide radius by period squared.” The
existing `src/evaluate_generalization_suite.py` physics prompts explicitly
**supply both relations**. Therefore performance on those prompts measures
composition **given premises**, not finding the premises in historical books.
The direct Earth–Moon question is a separate, harder endpoint and remains
unsolved. A centrifugal-to-attractive-force inference and an extrapolation
beyond measured orbits must also be stated, not silently credited.

## Planned controlled comparison (not yet run)

1. Have a human check the scanned passages and any transcription. Keep raw OCR and corrected
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

This records proposed **conditions**, not a completed or formally registered experiment. The
historical-source and holdout gates must pass before a long GPU sweep or a
publication claim.
