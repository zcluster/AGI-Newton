#!/usr/bin/env python3
"""Inventory a pinned TCP arithmetic transcription; never admit it automatically."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from build_corpus import compile_policy, scan

NS = {'t': 'http://www.tei-c.org/ns/1.0'}
COMMIT = 'af1ffd3fe85d6b00a0178ff42c1236574a10b9f9'


def render(node):
    tag = node.tag.rsplit('}', 1)[-1]
    if tag == 'gap':
        return f"[GAP:{node.get('reason', 'unknown')}]"
    if tag == 'g':
        return f"[CHAR:{node.get('ref', 'unknown')}]"
    return (node.text or '') + ''.join(render(child) + (child.tail or '') for child in node)


def inspect(xml):
    root = ET.fromstring(xml)
    date = root.find('t:teiHeader/t:fileDesc/t:sourceDesc/t:biblFull/t:publicationStmt/t:date', NS)
    assert date is not None and '1582' in ''.join(date.itertext())
    text = root.find('t:text', NS)
    assert text is not None
    gaps = Counter(g.get('reason', 'unknown') for g in text.findall('.//t:gap', NS))
    page, candidates, paragraphs = None, [], 0
    for node in text.iter():
        tag = node.tag.rsplit('}', 1)[-1]
        if tag == 'pb':
            page = {'n': node.get('n'), 'facs': node.get('facs')}
        if tag != 'p':
            continue
        paragraphs += 1
        display = re.sub(r'\s+', ' ', render(node)).strip()
        if not re.search(r'subtrac|subtract|substract|subtrah', display.replace('ſ', 's'), re.I):
            continue
        flags = {name: len(node.findall(f'.//t:{name}', NS)) for name in ('gap', 'g', 'table', 'figure')}
        candidates.append({'paragraph_index': paragraphs, 'page_start': page,
                           'text': display, 'markup_counts': flags,
                           'status': 'review_candidate_only',
                           'text_sha256': hashlib.sha256(display.encode()).hexdigest()})
    return {'edition_date': ''.join(date.itertext()), 'paragraphs': paragraphs,
            'gaps_by_reason': dict(gaps), 'subtraction_candidate_paragraphs': len(candidates)}, candidates, render(text)


if __name__ == '__main__':
    path = Path('raw/recorde_ground_artes_A10530.xml')
    content = path.read_bytes()
    summary, candidates, display = inspect(content)
    findings = scan(display, compile_policy(Path('policies/leakage_terms.json')))
    summary.update({'source_id': 'A10530', 'commit': COMMIT,
                    'source_url': f'https://raw.githubusercontent.com/textcreationpartnership/A10530/{COMMIT}/A10530.xml',
                    'xml_sha256': hashlib.sha256(content).hexdigest(),
                    'policy_finding_counts': {key: len(value) for key, value in findings.items()},
                    'status': 'Not admitted to training; bibliographic metadata and transcription are not expert certification',
                    'rendering': 'Review display only; preserve explicit GAP and unresolved CHAR markers; original TEI retained'})
    output = Path('audit/historical_arithmetic_recorde')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (output / 'candidates.json').write_text(json.dumps(candidates, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(summary, indent=2))
