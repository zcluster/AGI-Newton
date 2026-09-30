# A pre-1687 English witness to the period–distance premise

## Finding and scope

Thomas Streete's *Astronomia Carolina* (London, 1661), printed pp. 39–40, explicitly compares squared orbital periods with cubed mean distances. This provides an English-language candidate witness to the Kepler premise currently available in the V11 core only through difficult Latin OCR. It does **not** state or prove universal inverse-square attraction, and does not establish that a model can derive it.

The [Wellcome catalogue](https://identity.wellcomecollection.org/works/cnv8jz6q) independently identifies the English 1661 edition, London printer/publisher Lodowick Lloyd, and Wing S5953. An [original-edition microfilm scan](https://archive.org/details/bim_early-english-books-1641-1700_astronomia-carolina-a-n_streete-thomas_1661) is publicly accessible. The archive page-number mapping identifies printed p. 39 as image n38 and printed p. 40 as n39; these addresses must be checked visually rather than inferred from offsets.

## Downloaded evidence

The original-scan OCR is saved in `raw/streete_astronomia_carolina_1661.txt`, SHA-256 `1f9d37d233dd32d2e1c2dc15786bbbdabd0d9bbb5626489a65335da4efcf4585`. Lines 2363–2448 contain the relevant heading, planetary table, Earth–Mars ratio example, and its continuation. OCR corrupts fractions and individual digits; it is not a verified clean transcription.

Separately, [Lund University's download page](https://www.particle-nuclear.lu.se/lars-gislen/downloads) supplies a modern electronic rendering of the 1661 text, tables, and a separate modern commentary. The ZIP SHA-256 is `374ab874a08b34af53bea5c9953fa99e1ee4617b03063e01511d1c457588594e`; the text PDF SHA-256 is `a89c8dea04c4adb8795dc41d3054c5f8f8adc8f3afeeaf652a777430d2bdee07`. Its p. 39 was extracted and visually inspected. This is a **modern typesetting**, not an original-page facsimile; neither it nor its commentary has been added to training or redistributed here.

The modern rendering of p. 39 gives Earth period 525968 1/2 minutes, Mars period 989247 1/2 minutes, Earth mean distance 100000, and Mars mean distance 152369. The text explicitly says to compare the square of the first pair with the cube of the second pair. A numerical check gives:

```text
(989247.5 / 525968.5)^2 = 3.5374511587658968
(152369 / 100000)^3    = 3.537446267659409
relative difference   = 1.3826659453577172e-6
```

The original printed pages were then visually inspected. [Printed p. 39 / n38](https://archive.org/download/bim_early-english-books-1641-1700_astronomia-carolina-a-n_streete-thomas_1661/page/n38.jpg) visibly contains the same squared-period/cubed-distance comparison and the four numerical values above. [Printed p. 40 / n39](https://archive.org/download/bim_early-english-books-1641-1700_astronomia-carolina-a-n_streete-thomas_1661/page/n39.jpg) continues its logarithmic calculation and applies the relation to Jupiter's satellites. Thus the decisive premise is supported by an original-page witness, not merely by the modern rendering. The mathematical interpretation is our reading, not an expert-approved transcription.

The source-page images are retained as `audit/source_pages/streete_1661_n38.jpg` (SHA-256 `7c2ef45ff1910f6db57b070d0119159bd6b1903ee9542ce4301ca6d7cc48c9af`) and `streete_1661_n39.jpg` (SHA-256 `7c8b017dcfa7d3bc0674f849e37bf6b655670a5a3cc2b4a68d235332656fae6f`). This check also avoids relying on the potentially confusing direction of the prose's “sesquialter” formulation.

The unchanged repository leakage scan returned no hard/modern/review terms for this OCR. That is **not** an admission certificate: manual search found several references to Bullialdus, including *Astronomia Philolaica* near line 2775. OCR spelling variants can evade the current policy. The cited passages and surrounding context must be checked for precursor-law leakage before admitting the book. No existing policy or old audit has been silently changed.

## Experimental consequence

### Preliminary review of named precursor references

The original OCR search locates Bullialdus spelling variants at lines 820, 2307, 2775, 5330, 5691, 6753 and 6970. Reading the surrounding passages indicates solar parallax, lunar nodes, inner-planet eccentricity/elongation geometry, and eclipse observations/tables. In particular, the citation around line 2775 (printed p. 45) discusses Morin's construction from three greatest elongations, not an attraction law. Merely naming Boulliau therefore does not demonstrate target-answer leakage.

A second search over the entire 120-page modern electronic rendering, used only as an audit aid, also finds observational citations on pp. 31, 96, 101, 105, 108, 111, 112 and 115. The natural magnetic attraction discussion on p. 11 is qualitative. No inverse-square attraction statement was found in these search-selected contexts. This is a preliminary negative finding, **not** a complete original-page clearance: OCR and typesetting differences can hide terms, and a lack of keyword matches does not prove absence. The whole book remains outside training until the historical and leakage review is complete.

1. Keep the original OCR unchanged and the modern rendering outside the strict arm.
2. The decisive original pages have been visually checked. Expert-review any corrected transcription and target-leakage screening of the **whole** book next. A passage-level finding does not approve the whole book.
3. Locate a comparably dated English witness to circular-force scaling. This source supplies only one of the two required premises; it cannot silently substitute for the second. The [1673 English Huygens book review](ENGLISH_CIRCULAR_FORCE_SOURCE_AUDIT.md) has now been checked and does not express the needed quantitative relation.
4. Once both gates pass, compare premise identification, premise-given algebraic composition, and the direct Earth–Moon derivation separately. Never count a supplied modern paraphrase as historical rediscovery.

This is source-acquisition progress, not a new training result. No existing tokenizer, corpus, checkpoint, or GPU job was changed.
