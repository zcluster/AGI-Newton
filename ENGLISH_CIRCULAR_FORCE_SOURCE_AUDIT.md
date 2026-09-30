# English circular-force premise: reviewed candidate, gate still open

## Candidate located

*An Accompt of Some Books*, *Philosophical Transactions*, volume 8, number 95 (1673), pp. 6068–6074, DOI [10.1098/rstl.1673.0030](https://doi.org/10.1098/rstl.1673.0030), contains an English review of Huygens's *Horologium Oscillatorium*. The [original-volume contents](https://www.jstor.org/stable/i206873) independently identify its page range and JSTOR record [101361](https://www.jstor.org/stable/101361).

The publisher's PDF endpoint returned HTTP 403. The same seven-page historical article was obtained through [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Philosophical_Transactions_-_Volume_8_p6068-6074.pdf), using its Special:FilePath download. The downloaded PDF SHA-256 is `e430d1b1d2d54e37acee3826d8765e04f83ec816da786b9a7c9baf87d16f6ad5`. It is a scan with JSTOR/Royal Society digitization markings, not a modern explanatory translation. The original article pages were rendered and all seven inspected visually; ordinary PDF text extraction returned almost no article text, so an empty search result was **not** used as evidence of absence.

## Actual content, not inferred from the title

| Printed pages | Inspected content |
| --- | --- |
| 6068 | End of an unrelated fruit-tree item, then the Huygens review begins; five-part structure and pendulum-clock description |
| 6069 | Falling bodies, cycloid, curve development, centre of vibration; identifies Part V as a circular pendulum and centrifugal-force theorems |
| 6070–start of 6071 | Further discussion of curves, compound pendulums, clock design, trials at sea, and a universal length measure |
| Rest of 6071–6073 | Review of Jonas Moore's fortification book |
| 6073–6074 | Review of Kersey's algebra book, then an unrelated medical addendum |

**Decision:** this review is a historical English witness that Huygens's book contained centrifugal-force theorems. It does not state the quantitative radius/period or velocity/radius scaling needed by our evaluation. No `C ∝ R/T²` equivalent was identified in the visually inspected review. Consequently it does **not** pass the second-premise gate, and has not been inserted into the strict training corpus.

The later Hutton/Shaw/Pearson abridgment found in search results is outside the cutoff and must not substitute for the original 1673 review. Neither an original publication year attached to a later abridgment nor a journal's start date establishes that the actual training text is pre-1687.

## What remains

The original 1673 Latin Huygens pages already support the quantitative premise (see `PREMISE_ACCESS_AUDIT.md`). A strict English-only route still needs a dated English text explicitly expressing it. A multilingual route instead needs demonstrated Latin premise access; a modern English translation would be a separately labelled capability control. The failure to find the relation in **this review** is not evidence that no pre-1687 English witness exists.

No GPU run, training corpus, model weight, or historical-admission policy changed during this source check.
