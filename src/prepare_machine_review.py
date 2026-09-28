#!/usr/bin/env python3
"""Join verified downloads to the bibliography for a preliminary pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    sources = {row["id"]: row for row in read_jsonl(args.manifest)}
    downloads = read_jsonl(args.audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for item in downloads:
            if item["status"] not in {"downloaded_pending_review", "existing_pending_review"}:
                continue
            source = dict(sources[item["id"]])
            source.update(
                {
                    "review_status": "machine_reviewed",
                    "reviewed_by": "Codex preliminary bibliographic audit",
                    "source_url": item["details_url"],
                    "carrier_catalog_title": item.get("catalog_title"),
                    "carrier_catalog_date": item.get("catalog_date"),
                    "ocr_file": item.get("ocr_file"),
                }
            )
            handle.write(json.dumps(source, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

