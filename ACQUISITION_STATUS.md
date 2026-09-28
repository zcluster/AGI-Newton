# Acquisition status — 2026-09-13

## Current real pilot

- 17 exact Internet Archive items downloaded as OCR: 15 strict-source books
  and 2 isolated target precursors.
- Raw OCR size: approximately 16 MB.
- Strict build: 1,800 chunks, 13,503,824 characters, 15 source documents.
- Precursor-only build: 166 chunks, 1,290,940 characters, 2 documents.
- Strict language composition: 873 English, 103 French, 241 Italian, and
  583 Latin chunks.
- The 1570 Billingsley English Euclid and Boyle's 1660 air-pump experiments
  were found in a second, broader catalogue search and added to the pilot.
- Six automated tests pass, including regression tests for Latin `quantum`
  and non-gravitational duplicate-ratio false positives.

The pilot manifest is marked `machine_reviewed`, not human-approved. It can be
used for engineering tests only through the explicit
`--allow-machine-reviewed` flag.

## Completed

- Defined a 19-work seed bibliography spanning geometry, calculus precursors,
  astronomy, mechanics, instruments, observations, and explicit target
  precursors.
- Queried Internet Archive for up to three candidates per work.
- Retrieved 36 candidate records covering 15 of the 19 seed entries.
- Kept every candidate unreviewed: search rank is not bibliographic approval.
- Implemented strict, precursor-only, date-only, and quarantine outputs.
- Added deterministic hashes, leakage contexts, and rejection reasons.
- Verified the boundary with an executable five-document fixture.

## Important findings from candidate discovery

The search found plausible original-edition records for Copernicus (1543),
Napier (1614), Kepler (1609 and 1619), Galileo (1632 and 1638), Salusbury
(1661), Descartes (1637), Barrow (1670), Huygens (1673), Gilbert (1600),
Hooke's *Micrographia* (1665), Boulliau (1645), and Hooke's 1674 tract.

It also demonstrated why year and edition must be checked separately:

- the Descartes search returned two 1886 editions beside a 1637 candidate;
- the Copernicus search returned a 1943 record beside 1543 records;
- the Galileo search returned a 2000 edition beside 1632 records;
- the Gilbert search returned a 1903 edition beside 1600 records.

Those later editions are not admissible merely because their underlying works
are old.

## Still requiring bibliographic resolution

The expanded search still did not return a satisfactory candidate for:

- Cavalieri, *Geometria indivisibilibus* (1635);
- Hooke–Newton correspondence (1679).

These require broader catalogue queries or another carrier such as EEBO,
Wikisource, a university special-collections scan, or a scholarly manuscript
edition. They must remain pending until the exact source is verified.

## Next gate before training

For each selected item, inspect the title page and representative OCR pages,
record the exact edition and carrier URL, then mark it `approved`. Only after
that gate should the large Hla pre-1687 language layer be streamed and combined
with the curated core. The strict experiment must never consume
`precursor_only.jsonl` or `date_only_all.jsonl`.
