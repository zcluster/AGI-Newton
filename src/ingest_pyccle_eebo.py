#!/usr/bin/env python3
"""Build a target-screened pre-1687 English bootstrap from PYCCLE EEBO."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import re
import tarfile
from collections import Counter
from pathlib import Path

from build_corpus import CUTOFF_YEAR, chunk, compile_policy, normalise, scan


NEWTON_RE = re.compile(r"\b(?:sir\s+|isaac\s+)?newton(?:ian)?\b|\bprincipia\b", re.I)
PUNCT_LEFT = re.compile(r"\s+([,.;:!?\)\]\}])")
PUNCT_RIGHT = re.compile(r"([\(\[\{])\s+")


def read_dates(path: Path):
    dates = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for source_id, year in csv.reader(handle):
            try:
                dates[source_id] = int(year)
            except ValueError:
                continue
    return dates


def detag(payload: bytes):
    tokens = []
    for raw_line in payload.decode("utf-8", errors="replace").splitlines():
        line = raw_line.strip()
        if not line:
            tokens.append("\n")
            continue
        tokens.append(line.split("\t", 1)[0])
    text = " ".join(tokens).replace(" \n ", "\n").replace("\n ", "\n")
    text = PUNCT_LEFT.sub(r"\1", text)
    text = PUNCT_RIGHT.sub(r"\1", text)
    return normalise(text)


def file_sha256(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--dates", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-documents", type=int, default=5000)
    parser.add_argument("--max-train-bytes", type=int, default=200_000_000)
    parser.add_argument("--minimum-characters", type=int, default=5000)
    parser.add_argument("--chunk-size", type=int, default=8000)
    parser.add_argument("--seed", type=int, default=1686)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "policies" / "leakage_terms.json",
    )
    args = parser.parse_args()

    dates = read_dates(args.dates)
    candidates = [source_id for source_id, year in dates.items() if year <= CUTOFF_YEAR]
    random.Random(args.seed).shuffle(candidates)
    selected = set(candidates[: args.sample_documents])
    policy = compile_policy(args.policy)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "train": args.output_dir / "general_train.jsonl",
        "validation": args.output_dir / "general_validation.jsonl",
        "quarantine": args.output_dir / "general_quarantine.jsonl",
    }
    handles = {name: path.open("w", encoding="utf-8") for name, path in paths.items()}
    counts = Counter()
    reason_counts = Counter()
    year_counts = Counter()
    accepted = []
    train_bytes = 0

    try:
        with tarfile.open(args.archive, "r|gz") as archive:
            for member in archive:
                if not member.isfile() or "/texts/" not in member.name:
                    continue
                source_id = Path(member.name).name.split(".", 1)[0]
                if source_id not in selected:
                    continue
                counts["selected_members_seen"] += 1
                extracted = archive.extractfile(member)
                if extracted is None:
                    continue
                text = detag(extracted.read())
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
                if NEWTON_RE.search(text):
                    reasons.append("newton_reference")
                metadata = {
                    "source_id": source_id,
                    "year": dates[source_id],
                    "source": "PYCCLE-EEBO-Phase1",
                    "sha256": digest,
                }
                if reasons:
                    handles["quarantine"].write(
                        json.dumps({**metadata, "reasons": sorted(set(reasons)), "findings": findings}, ensure_ascii=False) + "\n"
                    )
                    counts["quarantine_documents"] += 1
                    reason_counts.update(set(reasons))
                    continue
                if train_bytes >= args.max_train_bytes:
                    counts["over_byte_cap_documents"] += 1
                    continue
                bucket = "validation" if int(digest[:8], 16) % 50 == 0 else "train"
                parts = chunk(text, args.chunk_size)
                for index, part in enumerate(parts):
                    handles[bucket].write(
                        json.dumps({"text": part, **metadata, "chunk_index": index}, ensure_ascii=False) + "\n"
                    )
                    counts[f"{bucket}_chunks"] += 1
                    if bucket == "train":
                        train_bytes += len(part.encode())
                counts[f"{bucket}_documents"] += 1
                year_counts[dates[source_id]] += 1
                accepted.append({**metadata, "characters": len(text), "bucket": bucket})
                if counts["selected_members_seen"] % 250 == 0:
                    print(
                        f"seen={counts['selected_members_seen']} accepted={len(accepted)} train_MB={train_bytes/1e6:.1f}",
                        flush=True,
                    )
    finally:
        for handle in handles.values():
            handle.close()

    audit = {
        "cutoff_year": CUTOFF_YEAR,
        "source": "PYCCLE EEBO Phase I public release",
        "archive_sha256": file_sha256(args.archive),
        "seed": args.seed,
        "pre_cutoff_candidates": len(candidates),
        "sample_documents": len(selected),
        "counts": dict(counts),
        "reason_counts": dict(reason_counts),
        "kept_year_counts": dict(sorted(year_counts.items())),
        "train_bytes": train_bytes,
        "accepted_documents": accepted,
    }
    (args.output_dir / "general_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps({key: value for key, value in audit.items() if key != "accepted_documents"}, indent=2))


if __name__ == "__main__":
    main()
