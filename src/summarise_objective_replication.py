#!/usr/bin/env python3
"""Matched-probe, per-seed objective comparison; missing runs fail explicitly."""
import json
from pathlib import Path

from summarise_reading_calibration import exact, summarise


def main():
    root = Path(__file__).resolve().parents[1]
    destination = root / "audit/objective_replication"
    comparison, signatures = {}, []
    for seed in (1686, 1687, 1688):
        comparison[str(seed)] = {}
        for objective in ("continuation", "answer_only"):
            if seed == 1686:
                directory = root / ("audit/reading_binding/calibrated" if objective == "continuation"
                                    else "audit/answer_only/calibrated")
                reading = directory / "heldout_reading_boundary_fixed.json"
                copy = directory / "copy_evaluation.json"
            else:
                directory = destination / f"{objective}_seed{seed}"
                reading, copy = directory / "probes.json", directory / "copy_probes.json"
            report = json.loads(reading.read_text())
            training = json.loads((directory / "report.json").read_text())
            args = training["args"]
            assert args["seed"] == seed and args["steps"] == 1000
            assert args["batch_size"] == 16 and args["context"] == 512
            assert args["learning_rate"] == 3e-5 and args["warmup_steps"] == 30
            assert args["resume"] == "runs/hpc_v11_bootstrap_seed1686/model.pt"
            assert training["tokens_seen"] == 8192000
            signatures.append([(p["id"], p["prompt"], p["target"], p["candidates"])
                               for p in report["probes"]])
            result = summarise(reading)
            assert result["cases"] == 96
            copied = json.loads(copy.read_text())["probes"]
            assert len(copied) == 24
            result["copy_exact"] = sum(exact(p) for p in copied)
            suite = json.loads((directory / "generalization_suite.json").read_text())
            result["abstract"] = suite["abstract_metrics"]
            result["physics"] = suite["physics_metrics"]
            retention = json.loads((directory / "direct_retention.json").read_text())["scientific_retention"]
            assert retention["sampling_seed"] == 1686 and retention["rounds"] == 16
            result["scientific_mean_loss"] = retention["mean_loss"]
            result["checkpoint"] = report["checkpoint"]
            comparison[str(seed)][objective] = result
    assert all(signature == signatures[0] for signature in signatures), "Probe sets differ"
    output = {"scope": "Three fine-tuning seeds, one historical initialization; repeated fixed test set",
              "matched_probes_verified": True, "by_seed": comparison}
    destination.mkdir(exist_ok=True)
    (destination / "summary.json").write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
