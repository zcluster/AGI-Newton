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


def varied():
    nouns = ["lengths", "widths", "weights", "prices", "areas", "volumes",
             "heights", "breadths", "depths", "costs", "sums", "numbers",
             "roots", "products", "values", "measures", "totals", "parts",
             "lines", "sides", "edges", "diameters", "quantities", "magnitudes"]
    train = []
    for row in build(nouns):
        for style in ("plain", "rephrased", "distractor_before", "distractor_after"):
            prompt = row["prompt"]
            if style == "rephrased":
                prompt = prompt.replace("What power of the", "Which power of the")
            if style.startswith("distractor"):
                sentence, question = prompt.split("\n", 1)
                distractor = "The cubes of the counters are as the squares of the stones."
                passage = (distractor + "\n" + sentence if style.endswith("before")
                           else sentence + "\n" + distractor)
                prompt = passage + "\n" + question
            # Continuation rephrasing is unchanged; avoid exact duplicate records.
            if style == "rephrased" and prompt == row["prompt"]:
                continue
            train.append({**row, "id": row["id"] + "_" + style, "prompt": prompt,
                          "text": prompt + row["candidates"][row["target"]]})
    test = []
    for group, entities in (("new_nouns", ["profits", "debts", "rents", "wages", "sizes", "counts"]),
                            ("new_template", nouns[:6])):
        for row in build(entities, heldout=True):
            novel_template = row["id"].endswith("continuation")
            if group == "new_template" and not novel_template:
                continue  # Familiar nouns + familiar question would overlap training.
            subgroup = "combined" if group == "new_nouns" and novel_template else group
            test.append({**row, "id": subgroup + "_" + row["id"], "group": subgroup})
    assert len(train) == 7728 and len(test) == 72
    assert all(sum(r["group"] == group for r in test) == 24
               for group in ("new_nouns", "new_template", "combined"))
    assert len({r["prompt"] for r in train}) == len(train)
    return train, test


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--varied", action="store_true")
    args = parser.parse_args()
    train = build(["lengths", "widths", "weights", "prices", "areas", "volumes"])
    test = build(["heights", "breadths", "depths", "costs"], heldout=True)
    if args.varied:
        train, test = varied()
    else:
        assert len(train) == 120 and len(test) == 32
    assert not {r["prompt"] for r in train} & {r["prompt"] for r in test}
    assert sum(r["target"] == "square" for r in test) * 2 == len(test)
    assert all(word not in r["text"].lower() for r in train for word in ("gravity", "period", "distance", "newton", "inverse"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, records in (("train", train), ("validation", test)):
        content = "".join(json.dumps(r) + "\n" for r in records)
        (args.output_dir / f"{name}.jsonl").write_text(content)
    (args.output_dir / "probes.json").write_text(json.dumps(test, indent=2) + "\n")
    manifest = {"train_records": len(train), "heldout_records": len(test),
                "variant": "varied" if args.varied else "tiny",
                "historical_data": False, "target_answer_training": False,
                "train_sha256": hashlib.sha256((args.output_dir / "train.jsonl").read_bytes()).hexdigest(),
                "test_sha256": hashlib.sha256((args.output_dir / "probes.json").read_bytes()).hexdigest()}
    (args.output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))


if __name__ == "__main__":
    main()
