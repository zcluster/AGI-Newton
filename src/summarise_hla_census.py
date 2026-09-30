#!/usr/bin/env python3
"""Export a reproducible title-level triage of the cached, fully read catalogue.

This is not a content classifier: the exceptions below encode human title review.
"""
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "audit/hla_before1687"
EXCEPTIONS = {
    "A summarie of the antiquities": ("science_candidate", "Pliny digest; natural history, not quantitative mechanics"),
    "The wonderfull woorkmanship": ("science_candidate", "Christian natural philosophy; contents and provenance need review"),
    "A new and short defense of tabacco": ("science_candidate", "Medicine/tobacco tract; not mathematical physics"),
    "Philosophical transactions.": ("science_candidate", "Science journal; actual volume date needs review"),
    "The voyages and travels": ("science_adjacent", "Travel/geography, not a mechanics treatise"),
    "The Liberties and Customes of the Lead-mines": ("science_adjacent", "Mining customs/law in verse; technical content uncertain"),
    "The Works of Mr Abraham Cowley": ("mixed_literary", "Literary collected works; incidental scientific content possible"),
    "[Tabacco]": ("ambiguous", "Short title; inspect text before assigning subject"),
    "revised and refined": ("ambiguous", "Incomplete title"),
    "revised, etc": ("ambiguous", "Incomplete title"),
    "with additions": ("ambiguous", "Incomplete title"),
}


def category(title):
    matches = [value for prefix, value in EXCEPTIONS.items() if title.startswith(prefix)]
    assert len(matches) <= 1, title
    return matches[0] if matches else ("other_by_title", "Title review: literature/history/religion/politics; not evidence of no science in body")


def main():
    coverage = json.loads((ROOT / "coverage.json").read_text())
    assert coverage["complete"] and coverage["shards_read"] == 42
    rows = []
    for path in sorted(ROOT.glob("shard_*.json")):
        cache = json.loads(path.read_text())
        assert cache["base_url"] == coverage["base_url"]
        for row in cache["rows"]:
            label, note = category(row["title"])
            rows.append({"shard": cache["shard"], **row, "category": label, "review_note": note})
    assert len(rows) == coverage["pre1687_rows"]
    unique = {(r["year"], r["title"]): r for r in rows}
    summary = {"method": "Manual review of every distinct year/title pair; title-level triage, not full-text validation",
               "rows": len(rows), "year_title_pairs": len(unique),
               "row_categories": dict(Counter(r["category"] for r in rows)),
               "year_title_categories": dict(Counter(r["category"] for r in unique.values()))}
    with (ROOT / "catalogue.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["year"], r["title"], r["shard"])))
    (ROOT / "subject_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    assert category("The Alchemist [A comedy, in five acts and in verse.]")[0] == "other_by_title"
    assert category("Philosophical transactions.")[0] == "science_candidate"


if __name__ == "__main__":
    main()
