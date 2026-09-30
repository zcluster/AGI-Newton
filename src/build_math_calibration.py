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
    splits = build()
    for name, rows in zip(("train", "validation"), splits):
        path = args.output_dir / f"{name}.jsonl"
        content = "".join(json.dumps(row) + "\n" for row in rows)
        path.write_text(content)
        audit[name] = {"records": len(rows), "sha256": hashlib.sha256(content.encode()).hexdigest()}
    seen = []
    for result in range(-3, 4):
        examples = [r for r in splits[0] if r["family"] == "math_subtraction"
                    and r["numerator"] - r["known"] == result][:2]
        assert len(examples) == 2
        for row in examples:
            seen.append({"id": f"seen_{len(seen)}", "group": "seen_subtraction",
                         "prompt": row["prompt"], "target": "correct",
                         "candidates": {"correct": f"{result}.", "lower": f"{result-1}.",
                                        "higher": f"{result+1}."}})
    assert len(seen) == 14 and all(p["prompt"] + p["candidates"]["correct"]
                                in {r["text"] for r in splits[0]} for p in seen)
    (args.output_dir / "seen_subtraction.json").write_text(json.dumps(seen, indent=2) + "\n")
    membership = {r["prompt"]: name for name, rows in zip(("train", "validation"), splits)
                  for r in rows if r["family"] == "math_subtraction"}
    grid = []
    for a in range(-8, 9):
        for b in range(-8, 9):
            for style, question in enumerate((f"Question: What is {a} minus {b}?",
                                               f"Question: Subtract {b} from {a}.")):
                prompt = question + "\nAnswer: "
                group = ("sealed_newton" if (a, b) == (1, 3) else
                         "sealed_reverse" if (a, b) == (3, 1) else membership[prompt])
                grid.append({"id": f"sub_{a}_{b}_{style}", "group": group,
                             "a": a, "b": b, "expected": a-b, "prompt": prompt, "target": "correct",
                             "candidates": {"correct": f"{a-b}.", "lower": f"{a-b-1}.", "higher": f"{a-b+1}."}})
    assert len(grid) == 578 and len({p["prompt"] for p in grid}) == 578
    assert {g: sum(r["group"] == g for r in grid) for g in set(membership.values())} == {"train": 544, "validation": 30}
    (args.output_dir / "subtraction_grid.json").write_text(json.dumps(grid, indent=2) + "\n")
    (args.output_dir / "audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
