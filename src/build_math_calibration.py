#!/usr/bin/env python3
"""Modern synthetic mathematics only; seal the Newton exponent combination."""
import argparse
import hashlib
import json
import random
from pathlib import Path

from generate_admissible_reasoning import diverse_elimination_examples
from split_curriculum import is_validation


def build():
    rows = []
    for example in diverse_elimination_examples(random.Random(1686), 10000, with_metadata=True):
        text = example["text"]
        question, continuation = text.split("\n", 1)
        base, known = example["base"], example["known"]
        numerator, target = example["numerator"], example["result_name"]
        for style in ("reasoning", "short", "relation"):
            prompt = question + ("\n" if style == "reasoning" else "\nAnswer: ")
            answer = (continuation if style == "reasoning" else
                      f"{base}^{numerator-known}." if style == "short" else
                      f"{target} is proportional to {base}^{numerator-known}.")
            rows.append({"source": "procedural", "family": "math_elimination", "prompt": prompt,
                         "text": prompt + answer, "known": known, "numerator": numerator,
                         "split": "validation" if is_validation(question) else "train"})
    for a in range(-8, 9):
        for b in range(-8, 9):
            if (a, b) in ((1, 3), (3, 1)):
                continue
            for question in (f"Question: What is {a} minus {b}?",
                             f"Question: Subtract {b} from {a}."):
                prompt = question + "\nAnswer: "
                # Group paraphrases of the same numerical operands together.
                rows.append({"source": "procedural", "family": "math_subtraction", "prompt": prompt,
                             "text": prompt + f"{a-b}.", "known": b, "numerator": a,
                             "split": "validation" if is_validation(f"subtraction:{a}:{b}") else "train"})
    rows = list({r["text"]: r for r in rows}.values())
    assert all((r["numerator"], r["known"]) != (1, 3) for r in rows)
    assert all(word not in r["text"].lower() for r in rows
               for word in ("gravity", "period", "distance", "newton", "inverse"))
    train = [r for r in rows if r["split"] == "train"]
    validation = [r for r in rows if r["split"] == "validation"]
    assert train and validation
    assert not {r["prompt"] for r in train} & {r["prompt"] for r in validation}
    return train, validation


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    audit = {"provenance": "Modern synthetic calibration, not historical source text",
             "sealed_pair": {"numerator": 1, "known": 3},
             "limitation": "Other mathematical -2 results are allowed; the answer value is not sealed"}
    for name, rows in zip(("train", "validation"), build()):
        path = args.output_dir / f"{name}.jsonl"
        content = "".join(json.dumps(row) + "\n" for row in rows)
        path.write_text(content)
        audit[name] = {"records": len(rows), "sha256": hashlib.sha256(content.encode()).hexdigest()}
    (args.output_dir / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
