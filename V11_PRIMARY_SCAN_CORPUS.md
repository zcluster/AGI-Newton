# V11 primary-scan pilot corpus (2026-09-30)

This is a **new, machine-reviewed pilot**, not a human-approved historical
corpus and not a discovery result. It leaves V3–V10 inputs and reports
unchanged. The reason for rebuilding is concrete: the earlier strict JSONL
contains obvious modern scanning or transcription material in 61 chunks
(55 Wallis, 4 Hooke, 1 Copernicus, 1 Galileo) under the search terms below.

| Source | V11 change | Raw-source SHA-256 |
|---|---|---|
| Wallis, 1656 | Replace the Google-scanned *Arithmetica* OCR, including repeated Google watermarks, with a [1656 original-edition scan](https://archive.org/details/bim_early-english-books-1641-1700_johannis-wallisii-_wallis-john_1656) of *Operum mathematicorum, pars altera*, which includes *Arithmetica infinitorum*. | `ac2892be22226485bd42257a2b7351ac1e21ec3243cc7abe6a1bd23fd596d813` |
| Hooke, 1665 | Replace the Project Gutenberg transcription and its modern license/front matter with [original-edition scan OCR](https://archive.org/details/mobot31753000817897). | `f89e5def4a42a9e12e3141728bbb09fba3a7269d25f6f99b9361ca41607f84bb` |
| Copernicus, 1543 | Keep the original raw OCR but skip its first 22 lines of modern digitization front matter when building V11. | `0432dab6f35f0cef191c419d5abee7ce4addf44a725a004d1fe696bd60ad4634` |
| Galileo, 1638 | Keep the original raw OCR but skip its first 30 lines of library and digitization front matter when building V11. | `b57e4290f9cb9ef95e4e16ab0de19f716c78257d9216a1caab584b64966fb41e` |

The source-selection and cut instructions are in
[`manifest/pilot_primary_scans_v11.jsonl`](manifest/pilot_primary_scans_v11.jsonl).
`raw_sha256` still hashes the **unaltered** source file; `normalized_sha256`
hashes what enters the model. The 11 unaffected strict sources have identical
chunk-hash sequences across V10 and V11.

V11 has 1,819 strict chunks and 0 policy-quarantined documents. A diagnostic
case-insensitive search for `internet archive|project gutenberg|google book
search|digitized by|copyright|in 20[0-9][0-9]|https?://` now finds **zero**
strict chunks, versus 61 in V10. This is only a targeted marker audit: it
does not prove the absence of all anachronisms, OCR errors, edition mixtures,
or target leakage. The existing inverse-square/modern-concept policy found
zero hard and modern matches in the four changed sources. Human historical
review is still required.

## Frozen first baseline input

The deterministic text-identity split has 1,727 training and 92 validation
chunks. Kepler chunk 92 and Huygens chunk 39, whose source-page locations are
in [`PREMISE_ACCESS_AUDIT.md`](PREMISE_ACCESS_AUDIT.md), are explicitly pinned
to training; the default hash split would have withheld Huygens's passage.
The 8,000-piece tokenizer is trained **only on V11 training chunks**, from
random initialization. Encoded streams contain 4,287,350 training and
230,842 validation tokens. This is a small, multilingual, OCR-noisy corpus;
a model trained on it alone is a feasibility baseline, not a realistic
language-competent discovery system.

| Artifact | SHA-256 |
|---|---|
| `strict_clean.jsonl` | `acabe8e1d90116c6f25cebb7d6c140440930df890e885d48ff91ead23473549b` |
| `train.jsonl` | `250f1148d3d77132e21f4c5dbecc240d1eac91daf900c34db8481a2c4076f83c` |
| `validation.jsonl` | `2d6b84ca4ab69da46c8ae93de172466527f56c2233ca7f7f4d7d38fc9a24411b` |
| tokenizer `.model` | `3464f65b26010ca6788f00b4b344e0834c26d2a194e24c27ecb65eb1a7833cc0` |
| `train.bin` | `8192ba313b8a4b408c48743d4ed6e72a3d793ecb7915683e49d9790d1461d46e` |
| `validation.bin` | `33533c201026e67bede464481ed2fd6ddf8c9bec4c1c3e73657e8e4eaeccc2de` |

The L40 job in [`hpc/tongji_v11_raw_baseline.sbatch`](hpc/tongji_v11_raw_baseline.sbatch)
is prepared but **not yet submitted**: campus/VPN routing was unavailable at
preparation time. It requests one L40 for at most 15 minutes, uses only the
AGI-Newton directory, and never accesses the separate SSNS project. The
generated `train.bin` and `validation.bin` are intentionally Git-ignored and
must be transferred or regenerated before submission. Its validation stream
is separate from training, unlike the earlier infrastructure smoke test.
Even if its validation loss improves, only free generation with checked
physics reasoning and strong answer-prior controls could support discovery.

A three-step, 1.43M-parameter local Mac smoke test completed on the V11
token streams (validation loss 9.007 to 8.925). This checks the new data path,
not language acquisition or physics performance; its temporary checkpoint is
not a research result.
