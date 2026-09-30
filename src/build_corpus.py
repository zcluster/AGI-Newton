#!/usr/bin/env python3
"""Build auditable strict and leakage-control corpora from reviewed sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

CUTOFF_YEAR = 1686


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: {exc}") from exc
    return records


def normalise(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).replace("\r\n", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def compile_policy(path: Path) -> dict[str, list[tuple[str, re.Pattern]]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {
        level: [(item["id"], re.compile(item["pattern"], re.I | re.S)) for item in items]
        for level, items in raw.items()
    }


def scan(text: str, policy: dict) -> dict[str, list[dict]]:
    findings: dict[str, list[dict]] = {level: [] for level in policy}
    for level, patterns in policy.items():
        for pattern_id, pattern in patterns:
            for match in pattern.finditer(text):
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                findings[level].append(
                    {"pattern": pattern_id, "context": text[start:end].replace("\n", " ")}
                )
    return findings


def chunk(text: str, size: int) -> list[str]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > size:
            chunks.append(current)
            current = ""
        while len(paragraph) > size:
            chunks.append(paragraph[:size])
            paragraph = paragraph[size:]
        current = f"{current}\n\n{paragraph}".strip()
    if current:
        chunks.append(current)
    return chunks


def output_record(source: dict, text: str, chunk_index: int) -> dict:
    return {
        "text": text,
        "source_id": source["id"],
        "title": source["title"],
        "author": source["author"],
        "work_year": source["work_year"],
        "edition_year": source["edition_year"],
        "language": source["language"],
        "role": source["role"],
        "source_url": source.get("source_url", ""),
        "chunk_index": chunk_index,
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
    }


def build(
    manifest_path: Path,
    raw_dir: Path,
    output_dir: Path,
    policy_path: Path,
    chunk_size: int,
    allow_machine_reviewed: bool = False,
) -> dict:
    policy = compile_policy(policy_path)
    buckets = {name: [] for name in ("strict_clean", "precursor_only", "date_only_all", "quarantine")}
    audit = {"cutoff_year": CUTOFF_YEAR, "documents": [], "counts": {}}

    for source in read_jsonl(manifest_path):
        required = {"id", "title", "author", "work_year", "edition_year", "language", "role", "target_risk", "review_status"}
        missing = sorted(required - source.keys())
        if missing:
            raise ValueError(f"{source.get('id', '<unknown>')}: missing {', '.join(missing)}")

        raw_file = source.get("raw_file", f"{source['id']}.txt")
        if Path(raw_file).name != raw_file:
            raise ValueError(f"{source['id']}: raw_file must be a filename")
        skip_initial_lines = source.get("skip_initial_lines", 0)
        if not isinstance(skip_initial_lines, int) or skip_initial_lines < 0:
            raise ValueError(f"{source['id']}: skip_initial_lines must be nonnegative")
        raw_path = raw_dir / raw_file
        reasons = []
        accepted_statuses = {"approved"}
        if allow_machine_reviewed:
            accepted_statuses.add("machine_reviewed")
        if source["review_status"] not in accepted_statuses:
            reasons.append("not_human_approved")
        if source["work_year"] > CUTOFF_YEAR:
            reasons.append("work_after_cutoff")
        if source["edition_year"] > CUTOFF_YEAR:
            reasons.append("edition_after_cutoff")
        if not raw_path.exists():
            reasons.append("missing_text")

        raw_bytes = raw_path.read_bytes() if raw_path.exists() else b""
        lines = raw_bytes.decode("utf-8").splitlines(keepends=True) if raw_bytes else []
        if skip_initial_lines and skip_initial_lines >= len(lines):
            raise ValueError(f"{source['id']}: skip_initial_lines removes the entire source")
        text = normalise("".join(lines[skip_initial_lines:])) if lines else ""
        findings = scan(text, policy) if text else {level: [] for level in policy}
        is_precursor = source["role"] == "precursor_target" or source["target_risk"] == "high"
        if findings["hard"] and not is_precursor:
            reasons.append("target_answer_detected")
        if findings["modern"]:
            reasons.append("modern_concept_detected")
        review_ids = {item["pattern"] for item in findings["review"]}
        allowed_review_ids = set(source.get("allowed_review_patterns", []))
        if review_ids - allowed_review_ids and not is_precursor:
            reasons.append("target_related_requires_review")

        doc_audit = {
            "id": source["id"],
            "raw_file": raw_file,
            "raw_sha256": hashlib.sha256(raw_bytes).hexdigest() if raw_path.exists() else None,
            "normalized_sha256": hashlib.sha256(text.encode()).hexdigest() if text else None,
            "skip_initial_lines": skip_initial_lines,
            "characters": len(text),
            "precursor": is_precursor,
            "findings": findings,
            "reasons": reasons,
        }
        audit["documents"].append(doc_audit)

        records = [output_record(source, part, index) for index, part in enumerate(chunk(text, chunk_size))]
        if reasons:
            buckets["quarantine"].append({**source, "reasons": reasons, "findings": findings})
            continue

        buckets["date_only_all"].extend(records)
        if is_precursor:
            buckets["precursor_only"].extend(records)
        else:
            buckets["strict_clean"].extend(records)

    output_dir.mkdir(parents=True, exist_ok=True)
    for name, records in buckets.items():
        with (output_dir / f"{name}.jsonl").open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        audit["counts"][name] = len(records)
    (output_dir / "audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--policy",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "policies" / "leakage_terms.json",
    )
    parser.add_argument("--chunk-size", type=int, default=8000)
    parser.add_argument(
        "--allow-machine-reviewed",
        action="store_true",
        help="Build a preliminary pilot; never use this flag for the publication-grade strict corpus",
    )
    args = parser.parse_args()
    audit = build(
        args.manifest,
        args.raw_dir,
        args.output_dir,
        args.policy,
        args.chunk_size,
        args.allow_machine_reviewed,
    )
    print(json.dumps(audit["counts"], indent=2))


if __name__ == "__main__":
    main()
