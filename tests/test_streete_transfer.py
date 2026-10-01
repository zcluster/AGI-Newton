import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from summarise_streete_transfer import audit, HASHES


class StreeteTransferTest(unittest.TestCase):
    def test_real_counts_and_mismatched_prompt(self):
        root = ROOT / 'audit/source_pages'
        fixture = json.loads((root / 'streete_clean_reading_probes.json').read_text())
        report = json.loads((root / 'streete_continuation_1686.json').read_text())
        result = audit(report, fixture, report['source_sha256'], HASHES['continuation_1686'])
        self.assertEqual(result['exact_candidate_text'], 0)
        self.assertEqual(result['ranking_correct'], 2)
        self.assertEqual(result['ranking_complete_pairs'], 0)
        altered = copy.deepcopy(report)
        altered['probes'][0]['prompt'] += ' changed'
        with self.assertRaises(AssertionError):
            audit(altered, fixture, report['source_sha256'], HASHES['continuation_1686'])


if __name__ == '__main__':
    unittest.main()
