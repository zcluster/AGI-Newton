#!/usr/bin/env python3
"""Synthetic language calibration, explicitly outside the historical-only arm."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path


def build(nouns, heldout=False):
    records = []
    pairs = list(itertools.combinations(nouns, 2)) if not heldout else list(zip(nouns, nouns[1:] + nouns[:1]))
    for left, right in pairs:
        for power in ("square", "cube"):
            other = "cube" if power == "square" else "square"
            passage = f"The {power}s of the {left} are as the {other}s of the {right}."
            for noun, target in ((left, power), (right, other)):
                for form in ("question", "continuation"):
                    suffix = (f"\nQuestion: What power of the {noun} is compared?\nAnswer: "
                              if form == "question" else f"\nThe passage compares the power of the {noun}, namely the ")
                    if heldout and form == "continuation":
                        suffix = f"\nQuestion: According to the statement, which power applies to the {noun}?\nAnswer: "
                    prompt = passage + suffix
                    answer = target + f" of the {noun}."
                    records.append({"id": f"{left}_{right}_{power}_{noun}_{form}",
                                    "prompt": prompt, "target": target,
                                    "candidates": {p: p + f" of the {noun}." for p in ("square", "cube")},
                                    "text": prompt + answer, "source": "procedural"})
    return records


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    train = build(["lengths", "widths", "weights", "prices", "areas", "volumes"])
    test = build(["heights", "breadths", "depths", "costs"], heldout=True)
    assert len(train) == 120 and len(test) == 32
    assert not {r["prompt"] for r in train} & {r["prompt"] for r in test}
    assert sum(r["target"] == "square" for r in test) == 16
    assert all(word not in r["text"].lower() for r in train for word in ("gravity", "period", "distance", "newton", "inverse"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, records in (("train", train), ("validation", test)):
        content = "".join(json.dumps(r) + "\n" for r in records)
        (args.output_dir / f"{name}.jsonl").write_text(content)
    (args.output_dir / "probes.json").write_text(json.dumps(test, indent=2) + "\n")
    manifest = {"train_records": len(train), "heldout_records": len(test),
                "historical_data": False, "target_answer_training": False,
                "train_sha256": hashlib.sha256((args.output_dir / "train.jsonl").read_bytes()).hexdigest(),
                "test_sha256": hashlib.sha256((args.output_dir / "probes.json").read_bytes()).hexdigest()}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
