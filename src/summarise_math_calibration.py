#!/usr/bin/env python3
"""Recompute matched mathematical pilot metrics from saved generations."""
import json
from pathlib import Path

from evaluate_composition_grid import equation_and_answer_correct
from evaluate_generalization_suite import generation_is_correct
from summarise_reading_calibration import exact, summarise


def main():
    root = Path(__file__).resolve().parents[1] / "audit/math_calibration"
    result, signatures = {}, []
    for objective in ("continuation", "answer_only"):
        directory = root / objective
        load = lambda name: json.loads((directory / f"{name}.json").read_text())
        training = load("report")
        assert training["tokens_seen"] == 8192000 and training["args"]["seed"] == 1686
        assert training["args"]["steps"] == 1000
        short, seen, grid = load("short_elimination"), load("seen_subtraction"), load("composition_grid")
        signatures.append({
            "short": [(p["id"], p["prompt"], p["target"], p["candidates"]) for p in short["probes"]],
            "seen": [(p["id"], p["prompt"], p["target"], p["candidates"]) for p in seen["probes"]],
            "grid": [(p["id"], p["prompt"], p["expected"]) for p in grid["cases"]],
            "settings": {k: training["args"][k] for k in
                         ("resume", "context", "batch_size", "width", "heads", "layers",
                          "learning_rate", "warmup_steps", "precision")}})
        assert len(short["probes"]) == 8 and len(seen["probes"]) == 14
        assert len(grid["cases"]) == 204 and sum(r["sealed_pair"] for r in grid["cases"]) == 6
        for row in grid["cases"]:
            assert row["expected"] == row["numerator"] - row["known"]
            assert row["answer_correct"] == generation_is_correct(
                row["generation"], row["prompt"], row["target"], row["base"], row["expected"])
            assert row["equation_and_answer_correct"] == equation_and_answer_correct(row["generation"], row)
        suite = load("generalization_suite")
        result[objective] = {
            "short_exact": sum(exact(p) for p in short["probes"]),
            "seen_subtraction_exact": sum(exact(p) for p in seen["probes"]),
            "abstract": suite["abstract_metrics"], "physics": suite["physics_metrics"],
            "grid": grid["all"], "sealed_grid": grid["sealed_pair"],
            "reading": summarise(directory / "reading.json"),
            "scientific_mean_loss": load("direct_retention")["scientific_retention"]["mean_loss"]}
    assert signatures[0] == signatures[1]
    (root / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
