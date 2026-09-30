import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_corpus import build  # noqa: E402


class CorpusBoundaryTest(unittest.TestCase):
    def test_alternate_scan_and_front_matter_cut_are_audited(self):
        fixtures = ROOT / "tests" / "fixtures"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = json.loads((fixtures / "manifest.jsonl").read_text().splitlines()[0])
            source.update(raw_file="galileo_fixture.txt", skip_initial_lines=2)
            manifest = root / "manifest.jsonl"
            manifest.write_text(json.dumps(source) + "\n")
            audit = build(manifest, fixtures / "raw", root / "output",
                          ROOT / "policies" / "leakage_terms.json", 8000)
            document = audit["documents"][0]
            self.assertEqual(document["skip_initial_lines"], 2)
            self.assertEqual(document["raw_sha256"], hashlib.sha256(
                (fixtures / "raw" / "galileo_fixture.txt").read_bytes()).hexdigest())
            row = json.loads((root / "output" / "strict_clean.jsonl").read_text())
            self.assertEqual(row["text"], "Observation and geometrical demonstration must be compared.")

    def test_strict_and_precursor_arms_are_isolated(self):
        fixtures = ROOT / "tests" / "fixtures"
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            audit = build(
                fixtures / "manifest.jsonl",
                fixtures / "raw",
                output,
                ROOT / "policies" / "leakage_terms.json",
                8000,
            )
            self.assertEqual(audit["counts"]["strict_clean"], 2)
            self.assertEqual(audit["counts"]["precursor_only"], 1)
            self.assertEqual(audit["counts"]["date_only_all"], 3)
            self.assertEqual(audit["counts"]["quarantine"], 2)

            euclid = next(row for row in audit["documents"] if row["id"] == "euclid_fixture")
            raw = (fixtures / "raw" / "euclid_fixture.txt").read_bytes()
            self.assertEqual(euclid["raw_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertNotEqual(euclid["raw_sha256"], euclid["normalized_sha256"])

            strict = (output / "strict_clean.jsonl").read_text()
            precursor = (output / "precursor_only.jsonl").read_text()
            self.assertNotIn("inverse", strict.lower())
            self.assertIn("square of the distance", precursor.lower())

            quarantined = [json.loads(line) for line in (output / "quarantine.jsonl").read_text().splitlines()]
            reasons = {record["id"]: record["reasons"] for record in quarantined}
            self.assertIn("modern_concept_detected", reasons["modern_fixture"])
            self.assertIn("edition_after_cutoff", reasons["late_fixture"])


if __name__ == "__main__":
    unittest.main()
