#!/usr/bin/env python3
"""Evaluate a V3 checkpoint on physics and abstract exponent transfer."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sentencepiece as spm
import torch

from train_bpe_gpt import GPT, TokenStream, evaluate_laws, generate, score, validation_loss
from train_random_init_smoke import LAW_PROBES


ABSTRACT_PROBES = [
    {
        "id": "seen_exponent_control",
        "prompt": (
            "Question: Suppose A is proportional to x^3, and B is proportional to x^1. "
            "To what power of x is the quotient A divided by B proportional?\nReasoning: "
        ),
        "answer": "power_2",
        "first": 3,
        "second": 1,
    },
    {
        "id": "withheld_exponent_minus_two",
        "prompt": (
            "Question: Suppose A is proportional to x^1, and B is proportional to x^3. "
            "To what power of x is the quotient A divided by B proportional?\nReasoning: "
        ),
        "answer": "power_minus_2",
        "first": 1,
        "second": 3,
    },
    {
        "id": "neutral_two_premise_transfer",
        "prompt": (
            "The square of P is proportional to the cube of R. Q is proportional "
            "to R divided by the square of P. Combining the two relations, Q is proportional to "
        ),
        "answer": "power_minus_2",
    },
]

POWERS = {"power_0": 0, "power_minus_1": -1, "power_2": 2, "power_minus_2": -2, "power_minus_3": -3}

PHYSICS_BRIDGE_PROMPT = (
    "Question: The square of an orbital period is proportional to distance^3. "
    "The circular turning tendency is proportional to distance^1 divided by the square of the orbital period. "
    "To what power of distance is the turning tendency proportional?\nReasoning: "
)


def physics_bridge_candidates():
    return {
        name: (
            "Replace the square of the orbital period by distance^3. Then the turning tendency is proportional "
            f"to distance^1 divided by distance^3. The indices combine as 1 - (3) = {power}.\n"
            f"Answer: The turning tendency is proportional to distance^{power}."
        )
        for name, power in POWERS.items()
    }


def candidates_for(probe):
    if "first" in probe:
        first, second = probe["first"], probe["second"]
        return {
            name: (
                f"The indices {first} and {second} are combined as {first} - ({second}) = {power}.\n"
                f"Answer: The quotient A divided by B is proportional to x^{power}."
            )
            for name, power in POWERS.items()
        }
    return {
        name: (
            "First replace the square of P by the cube of R. Then Q is proportional "
            f"to R divided by R^3, which is R^{power}."
        )
        for name, power in POWERS.items()
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--validation", type=Path, help="Optional scientific-language retention audit")
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--precision", default="bf16", choices=["fp32", "bf16", "fp16"])
    args = parser.parse_args()

    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    saved = checkpoint["args"]
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    model = GPT(
        tokenizer.vocab_size(),
        int(saved["context"]),
        int(saved["width"]),
        int(saved["heads"]),
        int(saved["layers"]),
    ).to(args.device)
    model.load_state_dict(checkpoint["model"])
    model.eval()
    abstract = []
    for probe in ABSTRACT_PROBES:
        candidates = candidates_for(probe)
        scores = {
            name: score(model, tokenizer, probe["prompt"], candidate, torch.device(args.device), args.precision)
            for name, candidate in candidates.items()
        }
        abstract.append({
            **probe,
            "winner": min(scores, key=lambda key: scores[key]["mean_nll"]),
            "scores": scores,
            "generation": generate(
                model, tokenizer, probe["prompt"], torch.device(args.device), args.precision,
                length=80, minimum_length=30
            ),
        })
    report = {
        "checkpoint": str(args.checkpoint),
        "label": saved["label"],
        "physics_probes": evaluate_laws(model, tokenizer, torch.device(args.device), args.precision),
        "physics_generations": {
            probe["id"]: generate(
                model, tokenizer, probe["prompt"], torch.device(args.device), args.precision,
                length=120, minimum_length=30
            )
            for probe in LAW_PROBES
        },
        "abstract_transfer": abstract,
    }
    bridge_scores = {
        name: score(
            model, tokenizer, PHYSICS_BRIDGE_PROMPT, candidate, torch.device(args.device), args.precision
        )
        for name, candidate in physics_bridge_candidates().items()
    }
    report["physics_symbolic_bridge"] = {
        "prompt": PHYSICS_BRIDGE_PROMPT,
        "answer": "power_minus_2",
        "winner": min(bridge_scores, key=lambda key: bridge_scores[key]["mean_nll"]),
        "scores": bridge_scores,
        "generation": generate(
            model, tokenizer, PHYSICS_BRIDGE_PROMPT, torch.device(args.device), args.precision,
            length=120, minimum_length=30
        ),
    }
    if args.validation:
        torch.manual_seed(1686)  # Same sampled windows in paired retention audits.
        report["scientific_retention"] = {
            "validation": str(args.validation), "sampling_seed": 1686, "batch_size": 8,
            "rounds": 16, "mean_loss": validation_loss(
                model, TokenStream(args.validation), 8, int(saved["context"]),
                torch.device(args.device), args.precision),
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
