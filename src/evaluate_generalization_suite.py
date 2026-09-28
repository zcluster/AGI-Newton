#!/usr/bin/env python3
"""Blinded paraphrase suite for two-premise elimination and physics transfer."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import sentencepiece as spm
import torch

from train_bpe_gpt import GPT, generate, score


OPTIONS = (-3, -2, -1, 0, 2)

CASES = [
    ("heldout_a", "The square of H scales as q^3. J scales as q^1 divided by that square. After eliminating H, determine the power of q in J.\nReasoning: ", "H", "J", "q", 3, 1),
    ("heldout_b", "Suppose U^2 is proportional to w^3, whereas V is proportional to w/U^2. Combine both statements and simplify V.\nDerivation: ", "U", "V", "w", 3, 1),
    ("heldout_c", "Two facts are given. The cube of C follows s^3. D follows s divided by the cube of C. What exponent of s remains in D?\nWork: ", "C", "D", "s", 3, 1),
    ("heldout_d", "Let K^1 vary with t^3 and let L vary with t^1/K^1. Remove K from the relations and give the dependence of L on t.\nSolution: ", "K", "L", "t", 3, 1),
    ("control_2", "The square of H scales as q^1. J scales as q^3 divided by that square. Eliminate H and determine J.\nReasoning: ", "H", "J", "q", 1, 3),
    ("control_minus_1", "Suppose U^2 is proportional to w^1, whereas V is proportional to w^0/U^2. Combine both statements.\nDerivation: ", "U", "V", "w", 1, 0),
    ("control_0", "The cube of C follows s^2. D follows s^2 divided by the cube of C. What exponent remains?\nWork: ", "C", "D", "s", 2, 2),
    ("control_other_minus_2", "Let K^1 vary with t^1 and let L vary with t^-1/K^1. Remove K and give L's dependence.\nSolution: ", "K", "L", "t", 1, -1),
    ("control_reverse_2", "The square of M is proportional to z^-1. N is proportional to z^1 divided by that square. Simplify N.\nReasoning: ", "M", "N", "z", -1, 1),
    ("control_minus_3", "Suppose A^3 follows x^3 and B follows x^0/A^3. Combine the relations.\nWork: ", "A", "B", "x", 3, 0),
    ("control_zero_2", "The first power of P varies as y^-1. Q varies as y^-1 divided by P. Eliminate P.\nDerivation: ", "P", "Q", "y", -1, -1),
    ("control_minus_1_b", "Let F^2 follow v^3 and G follow v^2/F^2. Determine G after substitution.\nSolution: ", "F", "G", "v", 3, 2),
]

PHYSICS_PROMPTS = [
    "Kepler gives period squared proportional to distance cubed. Circular turning tendency is distance divided by period squared. Eliminate the period and state the power of distance.\nReasoning: ",
    "The square of orbital time follows the cube of mean distance; the turning tendency follows mean distance over orbital time squared. Combine the relations.\nDerivation: ",
    "Let T^2 be proportional to R^3 and let the circular tendency C be proportional to R/T^2. Express C as a power of R.\nWork: ",
    "Two observations are supplied: P^2 ∝ d^3 and A ∝ d/P^2. Without using any other law, remove P and determine A's distance exponent.\nSolution: ",
]


def candidates(target, base, known, numerator):
    return {
        str(power): (
            f"Substitute {base}^{known} for the intermediate quantity. Then {target} is proportional to "
            f"{base}^{numerator}/{base}^{known}. The indices combine as {numerator} - ({known}) = {power}. "
            f"Therefore {target} is proportional to {base}^{power}."
        )
        for power in OPTIONS
    }


def generation_is_correct(text, prompt, base, known, numerator, result):
    suffix = text[len(prompt) :]
    equation = re.escape(f"{numerator} - ({known}) = {result}")
    power = re.escape(f"{base}^{result}")
    return bool(re.search(equation, suffix) or re.search(power, suffix))


def evaluate_case(model, tokenizer, device, precision, case):
    case_id, prompt, _middle, target, base, known, numerator = case
    expected = numerator - known
    choices = candidates(target, base, known, numerator)
    scores = {
        power: score(model, tokenizer, prompt, completion, device, precision)
        for power, completion in choices.items()
    }
    winner = min(scores, key=lambda key: scores[key]["mean_nll"])
    completion = generate(
        model, tokenizer, prompt, device, precision,
        length=100, temperature=0, minimum_length=30
    )
    return {
        "id": case_id,
        "prompt": prompt,
        "expected": expected,
        "winner": int(winner),
        "candidate_correct": int(winner) == expected,
        "scores": scores,
        "generation": completion,
        "generation_correct": generation_is_correct(
            completion, prompt, base, known, numerator, expected
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--precision", default="bf16", choices=["fp32", "bf16", "fp16"])
    args = parser.parse_args()
    device = torch.device(args.device)
    saved_checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    saved = saved_checkpoint["args"]
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    model = GPT(
        tokenizer.vocab_size(), int(saved["context"]), int(saved["width"]),
        int(saved["heads"]), int(saved["layers"])
    ).to(device)
    model.load_state_dict(saved_checkpoint["model"])
    model.eval()

    abstract = [evaluate_case(model, tokenizer, device, args.precision, case) for case in CASES]
    physics_cases = [
        (f"physics_{index}", prompt, "T", "C", "R", 3, 1)
        for index, prompt in enumerate(PHYSICS_PROMPTS)
    ]
    physics = [evaluate_case(model, tokenizer, device, args.precision, case) for case in physics_cases]

    def metrics(rows):
        return {
            "cases": len(rows),
            "candidate_accuracy": sum(row["candidate_correct"] for row in rows) / len(rows),
            "generation_accuracy": sum(row["generation_correct"] for row in rows) / len(rows),
        }

    report = {
        "checkpoint": str(args.checkpoint),
        "label": saved["label"],
        "deterministic_generation": True,
        "abstract_metrics": metrics(abstract),
        "physics_metrics": metrics(physics),
        "abstract_cases": abstract,
        "physics_cases": physics,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
