#!/usr/bin/env python3
"""Exact-wording-disjoint exponent-elimination grid with narrow trace checks."""

import argparse
import json
import re
from pathlib import Path

import sentencepiece as spm
import torch

from evaluate_generalization_suite import generation_is_correct
from train_bpe_gpt import GPT, generate


EXPONENTS = (-3, -1, 0, 1, 2, 3)
SYMBOLS = (("M", "N", "z", 1), ("P", "Q", "y", 2), ("H", "J", "x", 3))
TEMPLATES = (
    "Exercise: {middle}^{power} carries the same dependence on {base} as "
    "{base}^{known}. A second quantity {target} follows {base}^{numerator} "
    "per unit of {middle}^{power}. Replace that denominator and give "
    "{target}'s resulting index in {base}.\nDerivation: ",
    "Two measurements: {middle}^{power} changes as {base}^{known}; "
    "{target} changes as the quotient {base}^{numerator}/{middle}^{power}. "
    "Resolve this pair and state {target}'s exponent in {base}.\nWork: ",
)
EQUATION = re.compile(r"(?<![\w^])(-?\d+)\s*-\s*\(?\s*(-?\d+)\s*\)?\s*=\s*(-?\d+)(?!\d)")


def cases():
    for template_id, template in enumerate(TEMPLATES):
        for middle, target, base, power in SYMBOLS:
            for known in EXPONENTS:
                for numerator in EXPONENTS:
                    expected = numerator - known
                    if not -5 <= expected <= 5:
                        continue
                    prompt = template.format(**locals())
                    yield {
                        "id": f"t{template_id}_{middle}_{known}_{numerator}",
                        "prompt": prompt,
                        "target": target,
                        "base": base,
                        "known": known,
                        "numerator": numerator,
                        "expected": expected,
                        "sealed_pair": (numerator, known) == (1, 3),
                    }


def equation_and_answer_correct(text, case):
    if not generation_is_correct(
        text, case["prompt"], case["target"], case["base"], case["expected"]
    ):
        return False
    continuation = text[len(case["prompt"]):]
    equations = [tuple(map(int, match)) for match in EQUATION.findall(continuation)]
    quotient = re.compile(rf"{re.escape(case['base'])}\s*\^\s*(-?\d+)\s*/\s*"
                          rf"{re.escape(case['base'])}\s*\^\s*(-?\d+)")
    quotients = [tuple(map(int, match)) for match in quotient.findall(continuation)]
    return bool(equations) and all(a - b == c for a, b, c in equations) and (
        case["numerator"], case["known"], case["expected"]
    ) in equations and all(pair == (case["numerator"], case["known"])
                           for pair in quotients)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--tokenizer", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--precision", choices=("fp32", "bf16", "fp16"), default="bf16")
    args = parser.parse_args()
    device = torch.device(args.device)
    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    saved = checkpoint["args"]
    tokenizer = spm.SentencePieceProcessor(model_file=str(args.tokenizer))
    model = GPT(tokenizer.vocab_size(), int(saved["context"]), int(saved["width"]),
                int(saved["heads"]), int(saved["layers"])).to(device)
    model.load_state_dict(checkpoint["model"])
    model.eval()

    rows = []
    for case in cases():
        completion = generate(model, tokenizer, case["prompt"], device, args.precision,
                              length=100, temperature=0, minimum_length=30)
        rows.append({**case, "generation": completion,
                     "answer_correct": generation_is_correct(
                         completion, case["prompt"], case["target"], case["base"], case["expected"]
                     ), "equation_and_answer_correct": equation_and_answer_correct(completion, case)})

    def summary(items):
        return {"cases": len(items),
                "answer_correct": sum(row["answer_correct"] for row in items),
                "equation_and_answer_correct": sum(row["equation_and_answer_correct"] for row in items)}

    report = {"benchmark_version": 2, "checkpoint": str(args.checkpoint),
              "label": saved["label"], "all": summary(rows),
              "sealed_pair": summary([row for row in rows if row["sealed_pair"]]),
              "controls": summary([row for row in rows if not row["sealed_pair"]]),
              "cases": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({key: report[key] for key in ("all", "sealed_pair", "controls")}))


if __name__ == "__main__":
    main()
