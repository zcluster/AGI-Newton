#!/usr/bin/env python3
"""Split a JSONL curriculum by text identity, not by row."""

import argparse
import hashlib
import json
from pathlib import Path


def is_validation(text):
    return int.from_bytes(hashlib.sha256(text.encode()).digest()[:4], "big") % 20 == 0


def split_name(row, force_train_sha):
    if row.get("sha256") in force_train_sha:
        return "train"
    return "validation" if is_validation(row["text"]) else "train"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--train", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--force-train-sha", action="append", default=[],
                        help="Keep a predeclared source passage in training")
    args = parser.parse_args()
    if len({path.resolve() for path in (args.input, args.train, args.validation)}) != 3:
        parser.error("input, train, and validation must be distinct files")
    args.train.parent.mkdir(parents=True, exist_ok=True)
    args.validation.parent.mkdir(parents=True, exist_ok=True)
    counts = {"train": 0, "validation": 0}
    forced = set(args.force_train_sha)
    seen = set()
    with args.input.open(encoding="utf-8") as source, \
            args.train.open("w", encoding="utf-8") as train, \
            args.validation.open("w", encoding="utf-8") as validation:
        for line in source:
            row = json.loads(line)
            name = split_name(row, forced)
            if row.get("sha256") in forced:
                seen.add(row["sha256"])
            (validation if name == "validation" else train).write(line)
            counts[name] += 1
    if seen != forced:
        raise ValueError(f"force-train passage hashes not found: {sorted(forced - seen)}")
    print(json.dumps(counts))


if __name__ == "__main__":
    main()
