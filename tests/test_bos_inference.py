import sys
import unittest
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from train_bpe_gpt import generate, score


class Tokenizer:
    def encode(self, text, out_type=int):
        return [3] if text == 'Q' else [4]

    def decode(self, ids):
        return ''.join({1: '', 3: 'Q', 4: 'A'}.get(i, '') for i in ids)

    def bos_id(self): return 1
    def eos_id(self): return 2
    def pad_id(self): return 0
    def unk_id(self): return -1


class Model:
    context = 8

    def eval(self): pass

    def __call__(self, tokens):
        self.last_input = tokens.tolist()[0]
        logits = torch.zeros(1, tokens.shape[1], 5)
        logits[..., 4] = 10
        return logits


class BosInferenceTest(unittest.TestCase):
    def test_optional_bos_preserves_output_and_scoring_alignment(self):
        model, tokenizer = Model(), Tokenizer()
        for bos in (False, True):
            expected = [1, 3] if bos else [3]
            output = generate(model, tokenizer, 'Q ', torch.device('cpu'), 'fp32',
                              length=1, temperature=0, prepend_bos=bos)
            self.assertEqual(model.last_input, expected)
            self.assertEqual(output, 'Q A')
            result = score(model, tokenizer, 'Q ', 'A', torch.device('cpu'), 'fp32', prepend_bos=bos)
            self.assertEqual(model.last_input, expected)
            self.assertEqual(result['tokens'], 1)
            self.assertLess(result['mean_nll'], 0.001)


if __name__ == '__main__':
    unittest.main()
