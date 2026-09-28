#!/usr/bin/env python3
"""Download OCR for explicitly selected Internet Archive candidates."""

from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from pathlib import Path

METADATA_URL = "https://archive.org/metadata/{identifier}"
DOWNLOAD_URL = "https://archive.org/download/{identifier}/{filename}"


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def choose_text_file(files: list[dict]) -> dict | None:
    candidates = []
    for item in files:
        name = item.get("name", "")
        file_format = item.get("format", "")
        if name.endswith("_djvu.txt"):
            priority = 0
        elif file_format == "DjVuTXT":
            priority = 1
        elif name.lower().endswith(".txt") and "searchtext" not in name.lower():
            priority = 2
        else:
            continue
        try:
            size = int(item.get("size", 0))
        except (TypeError, ValueError):
            size = 0
        candidates.append((priority, -size, item))
    return min(candidates, default=(None, None, None))[-1]


def get_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "pre-newton-corpus/0.1"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": "pre-newton-corpus/0.1"})
    temporary = destination.with_suffix(destination.suffix + ".part")
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as handle:
        while block := response.read(1024 * 1024):
            handle.write(block)
    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--selection", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    args = parser.parse_args()

    sources = {row["id"]: row for row in read_jsonl(args.manifest)}
    args.raw_dir.mkdir(parents=True, exist_ok=True)
    args.audit.parent.mkdir(parents=True, exist_ok=True)
    with args.audit.open("w", encoding="utf-8") as handle:
        for selected in read_jsonl(args.selection):
            source = sources[selected["id"]]
            identifier = selected["ia_identifier"]
            destination = args.raw_dir / f"{source['id']}.txt"
            record = {
                "id": source["id"],
                "ia_identifier": identifier,
                "expected_title": source["title"],
                "expected_edition_year": source["edition_year"],
                "details_url": f"https://archive.org/details/{identifier}",
            }
            try:
                metadata = get_json(METADATA_URL.format(identifier=identifier))
                text_file = choose_text_file(metadata.get("files", []))
                record.update(
                    {
                        "catalog_title": metadata.get("metadata", {}).get("title"),
                        "catalog_date": metadata.get("metadata", {}).get("date"),
                        "ocr_file": text_file.get("name") if text_file else None,
                        "ocr_size": int(text_file.get("size", 0))
                        if text_file and str(text_file.get("size", "")).isdigit()
                        else None,
                    }
                )
                if destination.exists():
                    record["status"] = "existing_pending_review"
                elif text_file:
                    download(
                        DOWNLOAD_URL.format(identifier=identifier, filename=urllib.parse.quote(text_file["name"])),
                        destination,
                    )
                    record["status"] = "downloaded_pending_review"
                else:
                    record["status"] = "no_plaintext_found"
                if destination.exists():
                    record["downloaded_bytes"] = destination.stat().st_size
            except Exception as exc:
                record.update({"status": "error", "error": f"{type(exc).__name__}: {exc}"})
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            print(f"{record['status']}: {source['id']}", flush=True)


if __name__ == "__main__":
    main()
