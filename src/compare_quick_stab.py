#!/usr/bin/env python3
"""Compare strict and precursor-exposed quick-stab reports."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", type=Path, required=True)
    parser.add_argument("--precursor", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    strict = json.loads(args.strict.read_text())
    precursor = json.loads(args.precursor.read_text())
    strict_probes = {
        probe["id"]: probe for probe in strict["law_evaluation"]["probes"]
    }
    precursor_probes = {
        probe["id"]: probe for probe in precursor["law_evaluation"]["probes"]
    }

    lines = [
        "# Pre-Newton random-init quick stab",
        "",
        "This is an engineering and signal-detection run, not a claim that Newton's law was rediscovered.",
        "Both arms start from the same seed and architecture. The only treatment is adding the isolated",
        "Boulliau/Hooke precursor corpus to the second arm.",
        "",
        "| Arm | Parameters | Training bytes | Tokens seen | Final validation loss | Training time |",
        "|---|---:|---:|---:|---:|---:|",
        f"| Strict | {strict['parameters']:,} | {strict['bytes']:,} | {strict['tokens_seen']:,} | {strict['final_validation_loss']:.4f} | {strict['training_seconds']/60:.1f} min |",
        f"| + precursors | {precursor['parameters']:,} | {precursor['bytes']:,} | {precursor['tokens_seen']:,} | {precursor['final_validation_loss']:.4f} | {precursor['training_seconds']/60:.1f} min |",
        "",
        "Lower mean NLL is preferred. The key diagnostic is whether precursor exposure selectively lowers",
        "the inverse-square completion relative to the other laws.",
        "",
        "| Probe | Strict winner | +precursor winner | Strict target margin | +precursor target margin | Treatment effect |",
        "|---|---|---|---:|---:|---:|",
    ]
    deltas = []
    for probe_id, left in strict_probes.items():
        right = precursor_probes[probe_id]
        left_nll = left["scores"]["inverse_square"]["mean_nll"]
        right_nll = right["scores"]["inverse_square"]["mean_nll"]
        left_best_other = min(
            score["mean_nll"]
            for name, score in left["scores"].items()
            if name != "inverse_square"
        )
        right_best_other = min(
            score["mean_nll"]
            for name, score in right["scores"].items()
            if name != "inverse_square"
        )
        left_margin = left_nll - left_best_other
        right_margin = right_nll - right_best_other
        delta = right_margin - left_margin
        deltas.append(delta)
        lines.append(
            f"| {probe_id} | {left['winner']} | {right['winner']} | "
            f"{left_margin:+.4f} | {right_margin:+.4f} | {delta:+.4f} |"
        )
    lines += [
        "",
        "Target margin is inverse-square mean NLL minus the best non-target NLL; negative means inverse-square wins.",
        f"Mean treatment effect on that margin: **{sum(deltas)/len(deltas):+.4f}**.",
        "A negative treatment effect is the expected direction. Mixed signs across probes are a failed sensitivity check,",
        "not evidence for or against physical rediscovery.",
        "",
        "## Free generations",
        "",
        "### Strict",
        "",
        "```text",
        strict["free_generation"],
        "```",
        "",
        "### With precursors",
        "",
        "```text",
        precursor["free_generation"],
        "```",
        "",
        "## Interpretation rule",
        "",
        "- If neither arm prefers inverse-square, record a clean negative result: the present corpus/model is insufficient.",
        "- If only the precursor arm prefers it, the harness detects historical leakage but not rediscovery.",
        "- If the strict arm prefers it reproducibly across seeds and adversarial paraphrases, scale before making a stronger claim.",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
