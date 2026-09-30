#!/usr/bin/env python3
"""Paired BOS diagnostics with legacy-output reproduction checks."""
import json
from pathlib import Path

from summarise_subtraction_weight import numeric_correct


def summarise(root):
    result = {}
    for arm, old_dir in [('answer_only', 'baseline'), ('subtraction128', 'weighted')]:
        reports = [json.loads((root / f'{arm}_{mode}.json').read_text()) for mode in ('legacy', 'bos')]
        legacy, bos = reports
        assert legacy['prepend_bos'] is False and bos['prepend_bos'] is True
        assert legacy['checkpoint_sha256'] == bos['checkpoint_sha256']
        assert legacy['source_sha256'] == bos['source_sha256']
        rows, with_bos = legacy['probes'], bos['probes']
        old = json.loads((root.parent / 'subtraction_weight128' / old_dir / 'subtraction_grid.json').read_text())['probes']
        assert len(rows) == len(with_bos) == len(old) == 578
        for left, right, previous in zip(rows, with_bos, old):
            for key in ('id', 'prompt', 'group', 'expected', 'candidates'):
                assert left[key] == right[key] == previous[key]
            assert left['generation'] == previous['generation'], 'Legacy output did not reproduce'
            assert right['prompt_tokens'] == left['prompt_tokens'] + 1
        groups = {}
        for group in ('train', 'validation', 'sealed_newton', 'sealed_reverse'):
            pairs = [(numeric_correct(a), numeric_correct(b)) for a, b in zip(rows, with_bos) if a['group'] == group]
            groups[group] = {
                'cases': len(pairs), 'legacy_correct': sum(a for a, b in pairs),
                'bos_correct': sum(b for a, b in pairs),
                'rescued': sum(not a and b for a, b in pairs),
                'regressed': sum(a and not b for a, b in pairs),
            }
        assert [v['cases'] for v in groups.values()] == [544, 30, 2, 2]
        result[arm] = {'checkpoint_sha256': legacy['checkpoint_sha256'],
                       'legacy_generation_reproduced': True, 'groups': groups}
    return result


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'audit/bos_ablation'
    result = summarise(root)
    (root / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
