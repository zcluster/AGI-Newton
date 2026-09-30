# Hla pre-1687 metadata census

Dataset: https://huggingface.co/datasets/mhla/pre1900-corpus

Pinned revision: `ff332ef64f896c8d44672b4d1d0c752029e32f29`.

All 42 shards were queried using `year < 1687`. The cached JSON files contain the matching metadata and original shard row numbers; they do not contain book text or images.

| Measure | Count |
| --- | ---: |
| Total dataset rows | 2,074,160 |
| Rows with year < 1687 | 395 |
| Distinct (year, title) pairs | 357 |
| Distinct title strings | 337 |
| institutional-books matching rows | 111 |
| blbooks matching rows | 284 |

The matching rows comprise 0.01904% of dataset rows. These are metadata counts, not verified distinct historical works, token counts, or scientifically usable training examples. Date fields can describe series start dates or original works reproduced in later editions. Subject classification and provenance validation remain unfinished.

Title-level candidates include *Philosophical transactions.* (1666), *The wonderfull woorkmanship of the world* (1578), and a Pliny digest (1566). These candidates have not yet been validated by inspecting their text and publication provenance. Do not infer that all their contents predate 1687.

## Subject triage

All 357 distinct year/title pairs were read for title-level triage. The reproducible exceptions are encoded in `src/summarise_hla_census.py`; `catalogue.csv` retains all 395 rows, including shard/row addresses and classification notes.

| Title-level category | Year/title pairs | Dataset rows |
| --- | ---: | ---: |
| Science candidates | 4 | 4 |
| Science-adjacent: travel/geography and mining customs | 2 | 2 |
| Mixed literary collection: Cowley | 1 | 1 |
| Ambiguous/incomplete titles | 4 | 4 |
| Other by title: chiefly literature, plus history/religion/politics | 346 | 384 |

The fourth science candidate is *A new and short defense of tabacco* (1602), a medicine/tobacco tract. No dedicated mathematical, astronomical, or mechanical treatise was identified from these titles. This is not an exhaustive full-text subject assertion: incidental scientific passages can occur in otherwise literary works. *The Alchemist*, *The Virtuoso*, *The mock astrologer*, and *The Farriar made Physician* are dramatic works, not science manuals. *Ars adulandi* is the art of flattery, not a scientific textbook.

The categories are deliberately conservative and not verified training-admission decisions. The ambiguous titles are *[Tabacco]* (1595), *revised and refined* (1638), *revised, etc* (1650), and *with additions* (1661). Date concerns also appear outside the scientific candidates: a title explicitly describes a Cornmarket Press facsimile, and serial titles may carry start dates instead of individual volume dates.

Run `python3 src/summarise_hla_census.py` to regenerate the catalogue and counts entirely offline, including consistency checks. `src/inspect_hla_candidates.py` retrieves only the 11 candidate rows' text and caches each completed result; it does not repeat the full date scan.

## Reuse rather than repeat

The earlier geometry/schema discussion did not leave a retrievable full date-and-subject census in the local project or in the inspected HPC AGI-Newton directory. That does not establish that no earlier inspection happened. This census makes the scope and evidence explicit. Future subject analysis should use these cached records; a full scan is unnecessary unless the dataset revision or cutoff changes.

Reproduce or reuse the cached census:

```sh
uv run --with duckdb python src/audit_hla_before1687.py \
  --output-dir audit/hla_before1687 \
  --base-url https://huggingface.co/datasets/mhla/pre1900-corpus/resolve/ff332ef64f896c8d44672b4d1d0c752029e32f29
```

The script reuses per-shard caches for the same revision. Optional text retrieval is separate and is not needed to recompute these metadata counts.
