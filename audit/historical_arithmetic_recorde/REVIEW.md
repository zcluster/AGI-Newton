# Recorde subtraction: contextual review, not training approval

Source: retained A10530 TEI, edition 1582, pinned commit and SHA-256 in
`summary.json`. Paragraph indices refer to the body-only inventory, not printed
page numbers. This review uses the transcription, not verified source images.

## What the actual lesson supplies

Paragraphs 309–318 form a teacher–learner dialogue. They introduce subtraction as
removing one sum from another, define the remainder, and instruct the learner to
align place values, work from right to left, and write zero when digits are equal.
Paragraph 315 explicitly gives 18 minus 14 equals 4. This is genuine procedural
historical material, unlike merely counting a book as “mathematics.”

The procedure in paragraph 318 is not a complete general algorithm by itself:
borrowing is discussed later. Extracting just this paragraph would omit a crucial
condition when a lower digit exceeds the upper digit. The lesson must be reviewed
as a contextual block, including diagrams and later exceptions.

## A concrete integrity failure

Paragraphs 319–321 discuss subtracting 36 from 48. Their prose states that units
give two and tens give one, but their displayed calculations contain math gaps.
Paragraph 322 reads, verbatim:

> Whereby it appeareth, that if I withdraw 36, out of 48, there remaineth 2.

The transcription therefore contradicts the preceding prose and ordinary
arithmetic: the expected result is 12, not 2. **Do not silently replace 2 with
12.** Until the corresponding source image is checked, we cannot distinguish an
original printing error from a transcription omission. Neither “keyboarded” nor
“no gap tag in this paragraph” certifies semantic accuracy.

Paragraph 323 also omits a laid-out multi-digit example. Paragraph 336 has missing
numerals in the borrowing explanation. These are material gaps, not harmless
formatting differences.

## Admission decision

- Entire chapter: withheld pending layout and numeral verification.
- Paragraphs 309–318: promising partial instructional context, not approved as a
  self-contained complete subtraction lesson.
- Paragraph 322: quarantined factual inconsistency; retain original text and
  record any later source-verified correction separately.
- Signed subtraction: not established by this excerpt; no claim that it fixes
  the existing negative-integer calibration failure.

No text from this review is added to the historical training corpus. No synthetic
questions or modern worked answers have been generated from it. A minimal next
check is the handful of source images around this worked example and borrowing,
not an indiscriminate new OCR pass over the book.
