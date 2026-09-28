#!/usr/bin/env python3
"""Stream the Hla corpus and make a conservative pre-1687 language layer."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from build_corpus import CUTOFF_YEAR, compile_policy, normalise, scan


def as_year(value) -> int | None:
    if value is None:
        return None
    try:
        return int(str(value)[:4])
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-records", type=int, default=0, help="0 means scan the full stream")
    parser.add_argument("--minimum-characters", type=int, default=5000)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "policies" / "leakage_terms.json",
    )
    args = parser.parse_args()

    try:
        from datasets import load_dataset
    except ImportError as exc:
        raise SystemExit("Install the optional dependency first: pip install datasets") from exc

    args.output_dir.mkdir(parents=True, exist_ok=True)
    policy = compile_policy(args.policy)
    counts = {"seen": 0, "before_cutoff": 0, "train": 0, "validation": 0, "quarantine": 0}

    paths = {
        "train": args.output_dir / "general_train.jsonl",
        "validation": args.output_dir / "general_validation.jsonl",
        "quarantine": args.output_dir / "general_quarantine.jsonl",
    }
    handles = {name: path.open("w", encoding="utf-8") for name, path in paths.items()}
    try:
        stream = load_dataset("mhla/pre1900-corpus", split="train", streaming=True)
        for row in stream:
            counts["seen"] += 1
            if args.max_records and counts["seen"] > args.max_records:
                break
            year = as_year(row.get("year"))
            if year is None or year > CUTOFF_YEAR:
                continue
            counts["before_cutoff"] += 1
            text = normalise(row.get("text") or "")
            digest = hashlib.sha256(text.encode()).hexdigest()
            findings = scan(text, policy)
            reasons = []
            if len(text) < args.minimum_characters:
                reasons.append("too_short")
            if findings["hard"]:
                reasons.append("target_answer_detected")
            if findings["modern"]:
                reasons.append("modern_concept_detected")
            if findings["review"]:
                reasons.append("target_related_requires_review")

            metadata = {
                "source_id": digest,
                "title": row.get("title"),
                "year": year,
                "source": row.get("source"),
                "ocr_score": row.get("ocr_score"),
                "legibility": row.get("legibility"),
                "sha256": digest,
            }
            if reasons:
                record = {**metadata, "reasons": reasons, "findings": findings}
                bucket = "quarantine"
            else:
                record = {"text": text, **metadata}
                bucket = "validation" if int(digest[:8], 16) % 200 == 0 else "train"
            handles[bucket].write(json.dumps(record, ensure_ascii=False) + "\n")
            counts[bucket] += 1
    finally:
        for handle in handles.values():
            handle.close()

    (args.output_dir / "general_audit.json").write_text(
        json.dumps({"cutoff_year": CUTOFF_YEAR, "counts": counts}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()

