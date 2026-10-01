"""Reproduce strict source-transfer counts; not a semantic discovery grader."""
import hashlib
import json
from pathlib import Path

HASHES = {
    'continuation_1686': '9dc1d7042a8ccdcd5a85d54927c520f1c6bdf90de516fc60299b7ff0eb19a197',
    'continuation_1687': 'f748de3f373f01641734054a3b7f567f0bb7f6e7c2bd70e9f08fe21a8c1bb1aa',
    'continuation_1688': '1676b49d902b22374664abd5f8b67fa9601f470e06a86f7f3384a9ac9e1c91a3',
    'answer_only_1686': 'edd25e3da54170fcd97e5a9c5ffd3650f53ebd87dd646fb3466c72f36ac73c51',
    'answer_only_1687': 'ad47aa901b70fec13af90d28b09199f6f1ae664977be6499fb9319f2e9b45861',
    'answer_only_1688': '685e3a6939dee1bc3a651e3465833055a2a83f5fcb638614b466fc2fca50c93f',
}


def audit(report, fixture, digest, checkpoint_hash):
    assert report['source_sha256'] == digest
    assert report['checkpoint_sha256'] == checkpoint_hash
    assert report['prepend_bos'] is False
    assert len(report['probes']) == len(fixture) == 4
    exact, ranking, suffixes = [], [], []
    for expected, actual in zip(fixture, report['probes']):
        assert all(expected[k] == actual[k] for k in ('id', 'prompt', 'target', 'candidates'))
        prefix = actual['prompt'].rstrip(' \t')
        assert actual['generation'].startswith(prefix)
        suffix = actual['generation'][len(prefix):].strip()
        exact.append(suffix == actual['candidates'][actual['target']])
        ranking.append(actual['winner'] == actual['target'])
        suffixes.append(suffix)
    return {'exact_candidate_text': sum(exact), 'ranking_correct': sum(ranking),
            'exact_complete_pairs': sum(exact[i] and exact[i + 2] for i in (0, 1)),
            'ranking_complete_pairs': sum(ranking[i] and ranking[i + 2] for i in (0, 1)),
            'generated_suffixes': suffixes}


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1] / 'audit/source_pages'
    path = root / 'streete_clean_reading_probes.json'
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == 'cd270a121c8ee40e9d9104c60c8833af31fdd7dcb0019b4aeb539ee8e9e32a7d'
    fixture = json.loads(path.read_text())
    result = {name: audit(json.loads((root / f'streete_{name}.json').read_text()),
                          fixture, digest, checksum) for name, checksum in HASHES.items()}
    (root / 'streete_transfer_summary.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
