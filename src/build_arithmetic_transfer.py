#!/usr/bin/env python3
"""Freeze wording/range probes before evaluating existing mathematical models."""
import hashlib
import json
import random
from pathlib import Path


def build(train):
    arithmetic = [r for r in train if r['family'] == 'math_subtraction']
    seen = sorted({(r['numerator'], r['known']) for r in arithmetic})
    answers = {a - b for a, b in seen}
    rng = random.Random(1691)
    groups = [('seen_operands', rng.sample(seen, 24))]
    for name, familiar_answer in [('unseen_operands_known_answer', True), ('unseen_operands_new_answer', False)]:
        eligible = [(a, b) for a in range(-16, 17) for b in range(-16, 17)
                    if max(abs(a), abs(b)) > 8 and ((a-b in answers) == familiar_answer)]
        groups.append((name, rng.sample(eligible, 24)))
    probes = []
    for group, pairs in groups:
        for pair_index, (a, b) in enumerate(pairs):
            questions = [('legacy_minus', f'Question: What is {a} minus {b}?'),
                         ('legacy_subtract', f'Question: Subtract {b} from {a}.')]
            if group == 'seen_operands':
                questions += [('new_verbal', f'Question: Calculate the difference obtained by taking {b} away from {a}.'),
                              ('new_symbolic', f'Question: Evaluate ({a}) - ({b}).')]
            for wording, question in questions:
                prompt = question + '\nAnswer: '
                probes.append({'id': f'{group}_{pair_index}_{wording}', 'group': group,
                               'wording': wording, 'a': a, 'b': b, 'expected': a-b,
                               'prompt': prompt, 'target': 'correct',
                               'candidates': {'correct': f'{a-b}.', 'lower': f'{a-b-1}.', 'higher': f'{a-b+1}.'}})
    training_prompts = {r['prompt'] for r in arithmetic}
    assert len(probes) == 192 and len({p['id'] for p in probes}) == 192
    assert all((p['a'], p['b']) not in ((1, 3), (3, 1)) for p in probes)
    assert all((p['prompt'] in training_prompts) == (p['group'] == 'seen_operands' and p['wording'].startswith('legacy'))
               for p in probes)
    return probes


if __name__ == '__main__':
    path = Path('data/math_calibration/train.jsonl')
    probes = build([json.loads(line) for line in path.read_text().splitlines()])
    output = Path('audit/arithmetic_transfer')
    output.mkdir(parents=True, exist_ok=True)
    content = json.dumps(probes, indent=2) + '\n'
    (output / 'probes.json').write_text(content)
    (output / 'manifest.json').write_text(json.dumps({
        'seed': 1691, 'cases': len(probes), 'pairs_per_group': 24,
        'training_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'probes_sha256': hashlib.sha256(content.encode()).hexdigest(),
        'scope': 'Prospective inference diagnostic on two existing synthetic capability checkpoints; not discovery',
    }, indent=2) + '\n')
