#!/usr/bin/env python3
"""Generate target-free mathematical/astronomical reasoning curricula."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path


FORBIDDEN = re.compile(
    r"inverse[- ]square|reciprocal square|1\s*/\s*r\s*\^?\s*2|r\s*\^\s*-2|"
    r"duplicate ratio of (?:the )?distance|square of (?:the )?distance",
    re.I,
)


def record(text: str, family: str, index: int):
    if FORBIDDEN.search(text):
        raise ValueError(f"target leakage in generated curriculum: {text}")
    digest = hashlib.sha256(text.encode()).hexdigest()
    return {
        "text": text,
        "source_id": f"generated_{family}_{index:06d}",
        "title": "Admissible pre-Newton reasoning curriculum",
        "year": 1686,
        "source": "procedural",
        "family": family,
        "sha256": digest,
    }


def ratio_examples(rng: random.Random, count: int):
    templates = []
    powers = {-3: "reciprocal cube", -1: "reciprocal", 0: "constant", 1: "simple ratio", 2: "square", 3: "cube"}
    allowed = list(powers)
    for _ in range(count):
        first = rng.choice(allowed)
        second = rng.choice(allowed)
        operation = rng.choice(("product", "quotient"))
        result = first + second if operation == "product" else first - second
        if result == -2 or result not in powers:
            continue
        if operation == "product":
            question = (
                f"Question: A varies in the {powers[first]} of B, and C varies in the "
                f"{powers[second]} of B. In what ratio does the product A times C vary with B?"
            )
        else:
            question = (
                f"Question: A varies in the {powers[first]} of B, and C varies in the "
                f"{powers[second]} of B. In what ratio does the quotient A divided by C vary with B?"
            )
        templates.append(f"{question}\nAnswer: It varies in the {powers[result]} of B.")
    return templates


def arithmetic_examples(rng: random.Random, count: int):
    output = []
    for _ in range(count):
        a, b = rng.randint(2, 40), rng.randint(2, 20)
        family = rng.choice(("multiply", "divide", "proportion"))
        if family == "multiply":
            output.append(f"Question: What number is {a} multiplied by {b}?\nAnswer: {a*b}.")
        elif family == "divide":
            output.append(f"Question: If {a*b} is divided into {b} equal parts, what is each part?\nAnswer: {a}.")
        else:
            c = rng.randint(2, 15)
            output.append(
                f"Question: As {a} is to {b}, so is {a*c} to what number?\nAnswer: {b*c}."
            )
    return output


def kepler_examples(rng: random.Random, count: int):
    radii = [(1, 1), (4, 8), (9, 27), (16, 64), (25, 125)]
    output = []
    for _ in range(count):
        r1, t1 = rng.choice(radii)
        scale = rng.randint(1, 6)
        output.append(
            "Question: Kepler's harmonic rule says that the squares of orbital periods have the same "
            "ratio as the cubes of mean distances. If one orbit has mean distance "
            f"{scale} and period {scale}, while another has mean distance {scale*r1}, what is its period?\n"
            f"Answer: Its period is {scale*t1}."
        )
    return output


def circular_examples(rng: random.Random, count: int):
    output = []
    for _ in range(count):
        radius = rng.randint(1, 12)
        period = rng.randint(1, 8)
        tendency = radius / (period * period)
        rendered = str(int(tendency)) if tendency.is_integer() else f"{tendency:.3f}"
        output.append(
            "Question: For uniform circular motion, compare the turning tendency by dividing the radius "
            f"by the square of the period. If the radius is {radius} and the period is {period}, what is the measure?\n"
            f"Answer: The measure is {radius}/({period} times {period}), or {rendered}."
        )
    return output


def symbolic_examples(rng: random.Random, count: int, allow_minus_two: bool = False):
    """Teach exponent elimination without linking any result to physical force."""
    allowed = (-3, -1, 0, 1, 2, 3)
    output = []
    while len(output) < count:
        first = rng.choice(allowed)
        second = rng.choice(allowed)
        operation = rng.choice(("multiply", "divide"))
        result = first + second if operation == "multiply" else first - second
        # In the bridge condition, ordinary -2 results are admitted but the
        # exact held-out quotient 1 - 3 remains unseen.
        held_out_combination = operation == "divide" and first == 1 and second == 3
        if result < -4 or result > 4 or held_out_combination:
            continue
        if result == -2 and not allow_minus_two:
            continue
        sign = "+" if operation == "multiply" else "-"
        noun = "product A times B" if operation == "multiply" else "quotient A divided by B"
        output.append(
            f"Question: Suppose A is proportional to x^{first}, and B is proportional to x^{second}. "
            f"To what power of x is the {noun} proportional?\n"
            f"Reasoning: The indices {first} and {second} are combined as {first} {sign} ({second}) = {result}.\n"
            f"Answer: The {noun} is proportional to x^{result}."
        )
    return output


def elimination_examples(rng: random.Random, count: int):
    """Teach two-premise substitution while holding out the decisive 1-3 case."""
    names = (("A", "B", "x"), ("P", "Q", "y"), ("M", "N", "z"))
    power_names = {1: "first power", 2: "square", 3: "cube"}
    exponents = (-3, -1, 0, 1, 2, 3)
    output = []
    while len(output) < count:
        intermediate_power = rng.choice((1, 2, 3))
        known_power = rng.choice(exponents)
        numerator_power = rng.choice(exponents)
        # This is the exact exponent pair needed by the final physics problem.
        if known_power == 3 and numerator_power == 1:
            continue
        result = numerator_power - known_power
        if result < -5 or result > 5:
            continue
        middle, result_name, base = rng.choice(names)
        phrase = power_names[intermediate_power]
        output.append(
            f"Question: The {phrase} of {middle} is proportional to {base}^{known_power}. "
            f"Also {result_name} is proportional to {base}^{numerator_power} divided by the {phrase} of {middle}. "
            f"To what power of {base} is {result_name} proportional?\n"
            f"Reasoning: Replace the {phrase} of {middle} by {base}^{known_power}. Then {result_name} is proportional "
            f"to {base}^{numerator_power} divided by {base}^{known_power}. The indices combine as "
            f"{numerator_power} - ({known_power}) = {result}.\n"
            f"Answer: {result_name} is proportional to {base}^{result}."
        )
    return output


def diverse_elimination_examples(rng: random.Random, count: int):
    """A varied two-relation curriculum; the exponent pair 1 minus 3 is sealed."""
    symbols = tuple("ABCDEFGHJKLMNPQSTUVW")
    bases = tuple("xyzstuvw")
    power_names = {1: "first power", 2: "square", 3: "cube"}
    exponents = (-3, -1, 0, 1, 2, 3)
    questions = (
        "Question: Given {middle}^{middle_power} proportional to {base}^{known}, and {result_name} proportional to {base}^{numerator}/{middle}^{middle_power}, find the exponent of {base} in {result_name}.",
        "Problem: Two relations are known: {middle}^{middle_power} varies as {base}^{known}; {result_name} varies as {base}^{numerator} divided by {middle}^{middle_power}. Eliminate {middle} and state the resulting power.",
        "Question: The {power_phrase} of {middle} follows {base}^{known}. Meanwhile {result_name} follows the quotient of {base}^{numerator} by that {power_phrase}. Combining these relations, how does {result_name} depend on {base}?",
        "Exercise: Let {middle}^{middle_power} ∝ {base}^{known} and {result_name} ∝ {base}^{numerator}/{middle}^{middle_power}. Substitute the first relation into the second and simplify.",
        "Question: If the {power_phrase} of {middle} has index {known} in {base}, while {result_name} is {base}^{numerator} over that same quantity, what index does {result_name} have?",
        "Problem: First relation, {middle}^{middle_power} is as {base}^{known}. Second relation, {result_name} is as {base}^{numerator} divided by {middle}^{middle_power}. Use both relations to determine {result_name}.",
    )
    reasonings = (
        "Reasoning: Substitute {base}^{known} for {middle}^{middle_power}. The quotient becomes {base}^{numerator}/{base}^{known}, so the indices give {numerator} - ({known}) = {result}.",
        "Work: Elimination of {middle}^{middle_power} leaves powers {numerator} and {known}. Division subtracts them: {numerator} - ({known}) = {result}.",
        "Derivation: Replace the denominator by the first relation. Thus {result_name} ∝ {base}^{numerator}/{base}^{known} = {base}^{result}.",
        "Solution: From the first relation the denominator carries index {known}. Therefore the remaining index is {numerator} - ({known}) = {result}.",
    )
    answers = (
        "Answer: {result_name} is proportional to {base}^{result}.",
        "Therefore: {result_name} ∝ {base}^{result}.",
        "Result: the required exponent is {result}.",
    )
    output = []
    while len(output) < count:
        middle_power = rng.choice((1, 2, 3))
        known = rng.choice(exponents)
        numerator = rng.choice(exponents)
        if known == 3 and numerator == 1:
            continue
        result = numerator - known
        if result < -5 or result > 5:
            continue
        middle, result_name = rng.sample(symbols, 2)
        values = {
            "middle": middle,
            "result_name": result_name,
            "base": rng.choice(bases),
            "middle_power": middle_power,
            "power_phrase": power_names[middle_power],
            "known": known,
            "numerator": numerator,
            "result": result,
        }
        output.append(
            "\n".join(
                (
                    rng.choice(questions).format(**values),
                    rng.choice(reasonings).format(**values),
                    rng.choice(answers).format(**values),
                )
            )
        )
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--examples-per-family", type=int, default=6000)
    parser.add_argument("--seed", type=int, default=1686)
    parser.add_argument("--allow-abstract-minus-two", action="store_true")
    parser.add_argument("--include-elimination", action="store_true")
    parser.add_argument("--diverse-elimination-examples", type=int, default=0)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    families = {
        "arithmetic": arithmetic_examples(rng, args.examples_per_family),
        "ratio": ratio_examples(rng, args.examples_per_family * 2),
        "kepler": kepler_examples(rng, args.examples_per_family),
        "circular": circular_examples(rng, args.examples_per_family),
        "symbolic": symbolic_examples(
            rng, args.examples_per_family, allow_minus_two=args.allow_abstract_minus_two
        ),
    }
    if args.include_elimination:
        families["elimination"] = elimination_examples(rng, args.examples_per_family)
    if args.diverse_elimination_examples:
        families["diverse_elimination"] = diverse_elimination_examples(
            rng, args.diverse_elimination_examples
        )
    rows = []
    for family, texts in families.items():
        rows.extend(record(text, family, index) for index, text in enumerate(texts))
    rng.shuffle(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"rows": len(rows), "bytes": args.output.stat().st_size, "families": {key: len(value) for key, value in families.items()}}, indent=2))


if __name__ == "__main__":
    main()
