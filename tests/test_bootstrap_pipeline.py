import importlib.util
import random
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reasoning = load_module("generate_admissible_reasoning", ROOT / "src" / "generate_admissible_reasoning.py")
eebo = load_module("ingest_pyccle_eebo", ROOT / "src" / "ingest_pyccle_eebo.py")
split = load_module("split_curriculum", ROOT / "src" / "split_curriculum.py")


class BootstrapPipelineTests(unittest.TestCase):
    def test_key_premise_can_be_pinned_to_training_split(self):
        text = next(str(index) for index in range(1000) if split.is_validation(str(index)))
        row = {"text": text, "sha256": "premise"}
        self.assertEqual(split.split_name(row, set()), "validation")
        self.assertEqual(split.split_name(row, {"premise"}), "train")

    def test_generated_curriculum_does_not_state_target(self):
        rng = random.Random(1686)
        examples = []
        examples.extend(reasoning.arithmetic_examples(rng, 100))
        examples.extend(reasoning.ratio_examples(rng, 200))
        examples.extend(reasoning.kepler_examples(rng, 100))
        examples.extend(reasoning.circular_examples(rng, 100))
        symbolic = reasoning.symbolic_examples(rng, 100)
        examples.extend(symbolic)
        self.assertGreater(len(examples), 300)
        for text in examples:
            self.assertIsNone(reasoning.FORBIDDEN.search(text), text)
            reasoning.record(text, "test", 0)
        self.assertTrue(all("x^-2" not in text for text in symbolic))

    def test_abstract_minus_two_bridge_keeps_exact_target_combination_held_out(self):
        examples = reasoning.symbolic_examples(random.Random(1686), 2000, allow_minus_two=True)
        self.assertTrue(any("x^-2" in text for text in examples))
        self.assertTrue(all("1 - (3) = -2" not in text for text in examples))

    def test_two_premise_curriculum_holds_out_decisive_exponent_pair(self):
        examples = reasoning.elimination_examples(random.Random(1686), 2000)
        self.assertTrue(any(" = -2." in text for text in examples))
        self.assertTrue(all(re.search(r"indices combine as 1 - \(3\)", text) is None for text in examples))
        for text in examples:
            self.assertIsNone(reasoning.FORBIDDEN.search(text), text)

    def test_diverse_elimination_is_varied_and_keeps_target_pair_sealed(self):
        examples = reasoning.diverse_elimination_examples(random.Random(1686), 4000)
        self.assertGreater(len({text.splitlines()[0] for text in examples}), 3000)
        self.assertTrue(any(" = -2." in text or " = -2\n" in text for text in examples))
        self.assertTrue(all(re.search(r"1 - \(3\) = -2", text) is None for text in examples))
        for text in examples:
            self.assertIsNone(reasoning.FORBIDDEN.search(text), text)

    def test_eebo_pos_tags_are_removed_without_losing_words(self):
        payload = b"The\tAT0\nEarth\tNN1\n,\tPUN\nturneth\tVVZ\n.\tPUN\n"
        self.assertEqual(eebo.detag(payload), "The Earth, turneth.")


if __name__ == "__main__":
    unittest.main()
