#!/usr/bin/env python3
"""Re-evaluate a saved random-init model, including open generation for every probe."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from train_random_init_smoke import (
    LAW_PROBES,
    TinyGPT,
    choose_device,
    choose_precision,
    generate,
    run_law_probes,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--precision", choices=["auto", "fp32", "bf16", "fp16"], default="auto")
    parser.add_argument("--generation-length", type=int, default=240)
    parser.add_argument("--seed", type=int, default=1686)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = choose_device(args.device)
    precision = choose_precision(args.precision, device)
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    saved = checkpoint["args"]
    model = TinyGPT(
        int(saved["context"]),
        int(saved["width"]),
        int(saved["heads"]),
        int(saved["layers"]),
    ).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    report = {
        "checkpoint": str(args.checkpoint),
        "label": saved.get("label", "unnamed"),
        "device": str(device),
        "precision": precision,
        "law_evaluation": run_law_probes(model, device, precision),
        "free_generations": {
            probe["id"]: generate(
                model,
                probe["prompt"],
                device,
                precision,
                length=args.generation_length,
            )
            for probe in LAW_PROBES
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
