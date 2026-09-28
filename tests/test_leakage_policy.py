import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from build_corpus import compile_policy, scan  # noqa: E402


class LeakagePolicyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = compile_policy(ROOT / "policies" / "leakage_terms.json")

    def test_latin_quantum_is_not_modern_quantum_theory(self):
        self.assertFalse(scan("Quantum est quod quaeritur.", self.policy)["modern"])
        self.assertTrue(scan("Quantum mechanics predicts the result.", self.policy)["modern"])

    def test_generic_duplicate_ratio_is_review_not_hard_leakage(self):
        findings = scan("Spatia sunt in ratione duplicata temporum.", self.policy)
        self.assertFalse(findings["hard"])
        self.assertTrue(findings["review"])

    def test_physical_duplicate_ratio_requires_review(self):
        findings = scan("Vis solis est in ratione duplicata distantiae.", self.policy)
        self.assertFalse(findings["hard"])
        self.assertTrue(findings["review"])


if __name__ == "__main__":
    unittest.main()
