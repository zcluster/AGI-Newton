#!/usr/bin/env python3
"""Build a conservative pre-1687 language layer from Hla via Parquet ranges.

DuckDB performs predicate pushdown on the remote Parquet shards, so this reads
the small pre-1687 slice without downloading the full 56 GB dataset.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from build_corpus import CUTOFF_YEAR, chunk, compile_policy, normalise, scan


SHARD_COUNT = 42
MIRROR = "https://hf-mirror.com/datasets/mhla/pre1900-corpus/resolve/main"
NEWTON_RE = re.compile(r"\b(?:sir\s+|isaac\s+)?newton(?:ian)?\b|\bprincipia\b", re.I)
POST_CUTOFF_IMPRINT_RE = re.compile(
    r"\b(?:copyright|published|reprinted|printed)\b.{0,50}\b((?:17|18|19|20)\d{2})\b",
    re.I,
)


def reasons_for(text: str, row: dict, policy: dict, minimum_characters: int):
    findings = scan(text, policy)
    reasons = []
    if len(text) < minimum_characters:
        reasons.append("too_short")
    if findings["hard"]:
        reasons.append("target_answer_detected")
    if findings["modern"]:
        reasons.append("modern_concept_detected")
    if findings["review"]:
        reasons.append("target_related_requires_review")
    if NEWTON_RE.search(text):
        reasons.append("newton_reference")
    future_imprints = [
        int(match.group(1))
        for match in POST_CUTOFF_IMPRINT_RE.finditer(text)
        if int(match.group(1)) > CUTOFF_YEAR
    ]
    if future_imprints:
        reasons.append("post_cutoff_imprint_in_text")
    if row.get("ocr_score", -1) not in (-1, None) and row["ocr_score"] < 0.75:
        reasons.append("low_ocr_score")
    return sorted(set(reasons)), findings, future_imprints[:10]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--minimum-characters", type=int, default=5000)
    parser.add_argument("--chunk-size", type=int, default=8000)
    parser.add_argument("--max-train-bytes", type=int, default=200_000_000)
    parser.add_argument(
        "--shards",
        type=int,
        nargs="*",
        default=list(range(SHARD_COUNT)),
        help="Optional audited shard subset; defaults to all 42 shards",
    )
    parser.add_argument("--mirror", default=MIRROR)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "policies" / "leakage_terms.json",
    )
    args = parser.parse_args()

    try:
        import duckdb
    except ImportError as exc:
        raise SystemExit("Install duckdb first: pip install duckdb") from exc

    args.output_dir.mkdir(parents=True, exist_ok=True)
    policy = compile_policy(args.policy)
    output_paths = {
        "train": args.output_dir / "general_train.jsonl",
        "validation": args.output_dir / "general_validation.jsonl",
        "quarantine": args.output_dir / "general_quarantine.jsonl",
    }
    handles = {name: path.open("w", encoding="utf-8") for name, path in output_paths.items()}
    counts = Counter()
    reason_counts = Counter()
    year_counts = Counter()
    kept_documents = []
    seen_hashes = set()
    train_bytes = 0
    connection = duckdb.connect()

    try:
        for shard in args.shards:
            url = f"{args.mirror}/shard_{shard:05d}.parquet"
            rows = connection.execute(
                """
                SELECT text, year, title, source, ocr_score, legibility
                FROM read_parquet(?) WHERE year <= ?
                """,
                [url, CUTOFF_YEAR],
            ).fetchall()
            print(f"shard={shard:05d} pre_cutoff_rows={len(rows)}", flush=True)
            for values in rows:
                row = dict(zip(("text", "year", "title", "source", "ocr_score", "legibility"), values))
                counts["seen_pre_cutoff"] += 1
                text = normalise(row.get("text") or "")
                digest = hashlib.sha256(text.encode()).hexdigest()
                if digest in seen_hashes:
                    reasons = ["exact_duplicate"]
                    findings = {level: [] for level in policy}
                    future_imprints = []
                else:
                    seen_hashes.add(digest)
                    reasons, findings, future_imprints = reasons_for(
                        text, row, policy, args.minimum_characters
                    )
                metadata = {
                    "source_id": digest,
                    "title": row.get("title"),
                    "year": int(row["year"]),
                    "source": row.get("source"),
                    "ocr_score": row.get("ocr_score"),
                    "legibility": row.get("legibility"),
                    "sha256": digest,
                }
                if reasons:
                    record = {
                        **metadata,
                        "reasons": reasons,
                        "findings": findings,
                        "future_imprints": future_imprints,
                    }
                    handles["quarantine"].write(json.dumps(record, ensure_ascii=False) + "\n")
                    counts["quarantine_documents"] += 1
                    reason_counts.update(reasons)
                    continue
                if train_bytes >= args.max_train_bytes:
                    counts["over_byte_cap_documents"] += 1
                    continue
                bucket = "validation" if int(digest[:8], 16) % 50 == 0 else "train"
                parts = chunk(text, args.chunk_size)
                for index, part in enumerate(parts):
                    record = {"text": part, **metadata, "chunk_index": index}
                    handles[bucket].write(json.dumps(record, ensure_ascii=False) + "\n")
                    counts[f"{bucket}_chunks"] += 1
                    if bucket == "train":
                        train_bytes += len(part.encode())
                counts[f"{bucket}_documents"] += 1
                year_counts[int(row["year"])] += 1
                kept_documents.append({**metadata, "characters": len(text), "chunks": len(parts), "bucket": bucket})
    finally:
        for handle in handles.values():
            handle.close()
        connection.close()

    audit = {
        "cutoff_year": CUTOFF_YEAR,
        "source_dataset": "mhla/pre1900-corpus",
        "source_mirror": args.mirror,
        "method": "DuckDB Parquet predicate pushdown followed by local target-specific filters",
        "counts": dict(counts),
        "reason_counts": dict(reason_counts),
        "kept_year_counts": dict(sorted(year_counts.items())),
        "train_bytes": train_bytes,
        "kept_documents": kept_documents,
    }
    (args.output_dir / "general_audit.json").write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps({key: value for key, value in audit.items() if key != "kept_documents"}, indent=2))


if __name__ == "__main__":
    main()
