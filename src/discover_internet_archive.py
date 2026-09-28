#!/usr/bin/env python3
"""Find Internet Archive candidates; discovery never implies approval."""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://archive.org/advancedsearch.php"


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def search(query: str, rows: int) -> list[dict]:
    params = urllib.parse.urlencode(
        [
            ("q", f"({query}) AND mediatype:texts"),
            ("fl[]", "identifier"),
            ("fl[]", "title"),
            ("fl[]", "creator"),
            ("fl[]", "date"),
            ("fl[]", "language"),
            ("fl[]", "downloads"),
            ("sort[]", "downloads desc"),
            ("rows", str(rows)),
            ("page", "1"),
            ("output", "json"),
        ]
    )
    request = urllib.request.Request(f"{ENDPOINT}?{params}", headers={"User-Agent": "pre-newton-corpus/0.1"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)["response"]["docs"]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--rows", type=int, default=5)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for source in read_jsonl(args.manifest):
            query = source.get("locator_query")
            if not query:
                continue
            for candidate in search(query, args.rows):
                record = {
                    "manifest_id": source["id"],
                    "candidate": candidate,
                    "details_url": f"https://archive.org/details/{candidate['identifier']}",
                    "review_status": "unreviewed",
                }
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()

