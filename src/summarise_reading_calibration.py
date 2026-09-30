#!/usr/bin/env python3
"""Conservative, reproducible descriptive audit of the fixed-boundary outputs."""
import argparse
import json
from pathlib import Path


def exact(probe):
    assert probe["generation"].startswith(probe["prompt"])
    return probe["generation"][len(probe["prompt"]):].strip() == probe["candidates"][probe["target"]]


def summarise(path):
    probes = json.loads(path.read_text())["probes"]
    pairs = {}
    for p in probes:
        key = p["id"].replace("_square_", "_POWER_").replace("_cube_", "_POWER_")
        pairs.setdefault(key, []).append(exact(p))
    assert len(probes) == 2 * len(pairs) and all(len(pair) == 2 for pair in pairs.values())
    result = {"cases": len(probes), "exact_answers": sum(exact(p) for p in probes),
            "rank_correct": sum(p["winner"] == p["target"] for p in probes),
            "both_counterfactual_answers_correct": sum(all(pair) for pair in pairs.values()),
            "constant_square_rank_baseline": sum(p["target"] == "square" for p in probes)}
    if any("group" in p for p in probes):
        result["groups"] = {group: {"cases": sum(p["group"] == group for p in probes),
                            "exact_answers": sum(exact(p) for p in probes if p["group"] == group)}
                            for group in sorted({p["group"] for p in probes})}
    return result


if __name__ == "__main__":
    fixture = {"prompt": "Answer: ", "generation": "Answer: square of the lengths.",
               "target": "square", "candidates": {"square": "square of the lengths."}}
    assert exact(fixture)
    assert not exact({**fixture, "generation": "Answer: square of the widths."})
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "audit/reading_calibration")
    parser.add_argument("--baseline-label", default="historical_baseline")
    args = parser.parse_args()
    root = args.root
    result = {args.baseline_label: summarise(root / "heldout_reading_boundary_fixed.json"),
              "synthetic_calibrated": summarise(root / "calibrated/heldout_reading_boundary_fixed.json")}
    aligned = root / "aligned/heldout_reading.json"
    if aligned.exists():
        result["synthetic_calibrated_aligned"] = summarise(aligned)
    for name, path in ((args.baseline_label, root / "copy_evaluation.json"),
                       ("synthetic_calibrated", root / "calibrated/copy_evaluation.json")):
        if path.exists():
            probes = json.loads(path.read_text())["probes"]
            assert len(probes) == 24 and all(p["group"].startswith("copy_") for p in probes)
            result[name]["copy"] = {"cases": len(probes), "exact_answers": sum(exact(p) for p in probes)}
            result[name]["copy"]["groups"] = {group: sum(exact(p) for p in probes if p["group"] == group)
                                              for group in sorted({p["group"] for p in probes})}
    seen = root / "calibrated/seen_reading.json"
    if seen.exists():
        result["synthetic_calibrated"]["seen_training_diagnostic"] = summarise(seen)
    (root / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
