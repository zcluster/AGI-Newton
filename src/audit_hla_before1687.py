#!/usr/bin/env python3
"""Fetch the complete date-filtered Hla slice; retain per-shard evidence."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import duckdb


def fetch(shard, root, base, with_text):
    path = root / f"shard_{shard:05d}.json"
    if path.exists():
        cached = json.loads(path.read_text())
        if cached["base_url"] == base and (not with_text or cached["with_text"]):
            return cached
    url = f"{base}/shard_{shard:05d}.parquet"
    columns = "file_row_number, year, title, source, ocr_score, legibility"
    if with_text:
        columns += ", text"
    with duckdb.connect() as connection:
        connection.execute("LOAD httpfs")
        connection.execute("SET http_timeout=45; SET http_retries=2; SET threads=1; SET enable_progress_bar=false")
        total = connection.execute("SELECT count(*) FROM read_parquet(?)", [url]).fetchone()[0]
        result = connection.execute(
            f"SELECT {columns} FROM read_parquet(?, file_row_number=true) WHERE year < 1687 ORDER BY file_row_number",
            [url],
        )
        names = [entry[0] for entry in result.description]
        rows = [dict(zip(names, values)) for values in result.fetchall()]
    evidence = {"base_url": base, "shard": shard, "total_rows": total, "with_text": with_text, "rows": rows}
    path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--base-url", default="https://huggingface.co/datasets/mhla/pre1900-corpus/resolve/main")
    parser.add_argument("--with-text", action="store_true")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    evidence, failures = [], []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch, shard, args.output_dir, args.base_url, args.with_text): shard for shard in range(42)}
        for future in as_completed(futures):
            shard = futures[future]
            try:
                value = future.result()
                evidence.append(value)
                print(f"shard {shard:02d}: {len(value['rows'])} pre-1687 / {value['total_rows']} total", flush=True)
            except Exception as error:
                failures.append({"shard": shard, "error": str(error)})
                print(f"shard {shard:02d}: FAILED {error}", flush=True)
    summary = {"cutoff_exclusive": 1687, "complete": len(evidence) == 42, "with_text": args.with_text,
               "base_url": args.base_url, "shards_read": len(evidence), "total_rows": sum(v["total_rows"] for v in evidence),
               "pre1687_rows": sum(len(v["rows"]) for v in evidence), "failures": failures}
    (args.output_dir / "coverage.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit(1)
    assert summary["shards_read"] == 42


if __name__ == "__main__":
    main()
