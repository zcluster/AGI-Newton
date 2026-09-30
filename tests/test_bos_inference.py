import sys
import json
import tempfile
import unittest
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from train_bpe_gpt import generate, score
from summarise_bos_ablation import summarise


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
    def test_paired_summary_checks_reproduction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'bos_ablation'
            root.mkdir()
            rows = []
            for group, count in [('train', 544), ('validation', 30), ('sealed_newton', 2), ('sealed_reverse', 2)]:
                rows.extend({'id': f'{group}_{i}', 'group': group, 'prompt': 'Q ', 'expected': -2,
                             'candidates': {'correct': '-2.'}, 'generation': 'Q 0.', 'prompt_tokens': 1}
                            for i in range(count))
            for arm, previous in [('answer_only', 'baseline'), ('subtraction128', 'weighted')]:
                old = root.parent / 'subtraction_weight128' / previous
                old.mkdir(parents=True)
                (old / 'subtraction_grid.json').write_text(json.dumps({'probes': rows}))
                for mode in ('legacy', 'bos'):
                    output = [{**r, 'prompt_tokens': 1 + int(mode == 'bos'),
                               'generation': 'Q -2.' if mode == 'bos' else r['generation']} for r in rows]
                    (root / f'{arm}_{mode}.json').write_text(json.dumps({
                        'probes': output, 'prepend_bos': mode == 'bos',
                        'checkpoint_sha256': arm, 'source_sha256': 'fixture'}))
            result = summarise(root)
            self.assertEqual(result['answer_only']['groups']['train']['rescued'], 544)
            path = root / 'answer_only_legacy.json'
            corrupted = json.loads(path.read_text())
            corrupted['probes'][0]['generation'] = 'Q 1.'
            path.write_text(json.dumps(corrupted))
            with self.assertRaises(AssertionError):
                summarise(root)

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
