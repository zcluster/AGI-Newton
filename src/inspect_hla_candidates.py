#!/usr/bin/env python3
"""Inspect candidate rows from the existing census, without another date scan."""
import hashlib
import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1] / "audit/hla_before1687"
TERMS = ("philosophical transactions", "naturall philosophie", "antiquities and wonders",
         "tabacco", "lead-mines", "voyages and travels", "revised and refined",
         "revised, etc", "with additions", "cowley")


def main():
    output = ROOT / "candidate_texts"
    output.mkdir(exist_ok=True)
    for path in sorted(ROOT.glob("shard_*.json")):
        cache = json.loads(path.read_text())
        candidates = [r for r in cache["rows"] if any(t in r["title"].lower() for t in TERMS)]
        for row in candidates:
            target = output / f"{cache['shard']:05d}_{row['file_row_number']}.json"
            if target.exists():
                continue
            with duckdb.connect() as con:
                con.execute("LOAD httpfs")
                con.execute("SET http_timeout=45; SET http_retries=2; SET threads=1")
                url = f"{cache['base_url']}/shard_{cache['shard']:05d}.parquet"
                text = con.execute("SELECT text FROM read_parquet(?, file_row_number=true) WHERE file_row_number = ?",
                                   [url, row["file_row_number"]]).fetchone()[0]
            evidence = {**row, "shard": cache["shard"], "base_url": cache["base_url"],
                        "characters": len(text), "sha256": hashlib.sha256(text.encode()).hexdigest(), "text": text}
            target.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
            print(target.name, len(text), text[:600], flush=True)


if __name__ == "__main__":
    main()
