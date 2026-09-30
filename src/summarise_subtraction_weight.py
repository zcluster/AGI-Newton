#!/usr/bin/env python3
"""Matched subtraction generations, grouped by training status and operand pair."""
import json
import re
from pathlib import Path

from summarise_reading_calibration import exact


def numeric_correct(probe):
    assert probe["generation"].startswith(probe["prompt"])
    answer = probe["generation"][len(probe["prompt"]):].strip()
    match = re.fullmatch(r"(-?\d+)\.?", answer)
    return bool(match and int(match.group(1)) == probe["expected"])


def main():
    root = Path(__file__).resolve().parents[1] / "audit/subtraction_weight128"
    result, signatures = {}, []
    for name in ("baseline", "weighted"):
        report = json.loads((root / name / "subtraction_grid.json").read_text())
        rows = report["probes"]
        assert len(rows) == 578
        signatures.append([(p["id"], p["prompt"], p["group"], p["expected"], p["candidates"]) for p in rows])
        groups = {}
        for group in ("train", "validation", "sealed_newton", "sealed_reverse"):
            subset = [p for p in rows if p["group"] == group]
            pairs = {}
            for p in subset:
                assert p["expected"] == p["a"] - p["b"]
                pairs.setdefault((p["a"], p["b"]), []).append(numeric_correct(p))
            assert pairs and all(len(pair) == 2 for pair in pairs.values())
            groups[group] = {"cases": len(subset), "format_exact": sum(exact(p) for p in subset),
                             "numeric_correct": sum(numeric_correct(p) for p in subset),
                             "operand_pairs": len(pairs), "both_formats_correct": sum(all(pair) for pair in pairs.values())}
        assert [groups[g]["cases"] for g in groups] == [544, 30, 2, 2]
        result[name] = groups
    assert signatures[0] == signatures[1]
    (root / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
