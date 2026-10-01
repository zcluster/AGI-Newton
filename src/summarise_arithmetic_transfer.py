#!/usr/bin/env python3
"""Score the frozen transfer suite using existing integer-generation graders."""
import hashlib
import json
from pathlib import Path

from summarise_balanced_math import validation_errors
from summarise_subtraction_weight import numeric_correct


def summarise(root):
    content = (root / 'probes.json').read_bytes()
    probes = json.loads(content)
    manifest = json.loads((root / 'manifest.json').read_text())
    assert hashlib.sha256(content).hexdigest() == manifest['probes_sha256']
    expected_hashes = {'answer_only': '2565030214e3860c16b693523bed43ef4934eee7a5e28194a212dc5a016865ef',
                       'balanced': 'a270638321e841743f5a1a089d52f3ba7ec0776106cd272f430942a196827faa'}
    result = {}
    for arm, checkpoint_hash in expected_hashes.items():
        report = json.loads((root / f'{arm}.json').read_text())
        assert report['checkpoint_sha256'] == checkpoint_hash
        assert report['source_sha256'] == manifest['probes_sha256']
        assert report['prepend_bos'] is False and len(report['probes']) == len(probes) == 192
        for actual, original in zip(report['probes'], probes):
            assert all(actual[key] == value for key, value in original.items())
        groups = {}
        for name in ('seen_legacy_wording', 'seen_new_wording', 'unseen_operands_known_answer', 'unseen_operands_new_answer'):
            if name.startswith('seen_'):
                subset = [p for p in report['probes'] if p['group'] == 'seen_operands'
                          and p['wording'].startswith('legacy' if name == 'seen_legacy_wording' else 'new')]
            else:
                subset = [p for p in report['probes'] if p['group'] == name]
            assert len(subset) == 48
            pairs = {}
            for p in subset:
                pairs.setdefault((p['a'], p['b']), []).append(numeric_correct(p))
            assert len(pairs) == 24 and all(len(v) == 2 for v in pairs.values())
            groups[name] = validation_errors(subset, group=None) | {
                'operand_pairs': 24, 'both_wordings_correct': sum(all(v) for v in pairs.values())}
        result[arm] = groups
    return result


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'audit/arithmetic_transfer'
    result = summarise(root)
    (root / 'summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
