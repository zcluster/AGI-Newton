#!/usr/bin/env python3
"""Conservative, reproducible descriptive audit of the fixed-boundary outputs."""
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
    assert len(probes) == 32 and len(pairs) == 16 and all(len(pair) == 2 for pair in pairs.values())
    return {"cases": len(probes), "exact_answers": sum(exact(p) for p in probes),
            "rank_correct": sum(p["winner"] == p["target"] for p in probes),
            "both_counterfactual_answers_correct": sum(all(pair) for pair in pairs.values()),
            "constant_square_rank_baseline": sum(p["target"] == "square" for p in probes)}


if __name__ == "__main__":
    fixture = {"prompt": "Answer: ", "generation": "Answer: square of the lengths.",
               "target": "square", "candidates": {"square": "square of the lengths."}}
    assert exact(fixture)
    assert not exact({**fixture, "generation": "Answer: square of the widths."})
    root = Path(__file__).resolve().parents[1] / "audit/reading_calibration"
    result = {"historical_baseline": summarise(root / "heldout_reading_boundary_fixed.json"),
              "synthetic_calibrated": summarise(root / "calibrated/heldout_reading_boundary_fixed.json")}
    aligned = root / "aligned/heldout_reading.json"
    if aligned.exists():
        result["synthetic_calibrated_aligned"] = summarise(aligned)
    (root / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
