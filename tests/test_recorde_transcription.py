import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from audit_recorde_transcription import inspect


class RecordeAuditTest(unittest.TestCase):
    def test_header_excluded_and_math_gaps_preserved(self):
        xml = '''<TEI xmlns="http://www.tei-c.org/ns/1.0"><teiHeader><fileDesc><sourceDesc>
        <biblFull><publicationStmt><date>1582</date></publicationStmt></biblFull></sourceDesc>
        </fileDesc><p>Modern Newton subtraction commentary</p></teiHeader><text><body>
        <pb n="3" facs="tcp:2279:4"/><p>Subtraction: <gap reason="math"/> then <g ref="char:x"/>.</p>
        </body></text></TEI>'''
        summary, candidates, text = inspect(xml)
        self.assertNotIn('Newton', text)
        self.assertIn('[GAP:math]', text)
        self.assertIn('[CHAR:char:x]', text)
        self.assertEqual(summary['gaps_by_reason'], {'math': 1})
        self.assertEqual(candidates[0]['page_start']['n'], '3')
        self.assertEqual(candidates[0]['markup_counts']['gap'], 1)
        with self.assertRaises(AssertionError):
            inspect(xml.replace('1582', '1782'))


if __name__ == '__main__':
    unittest.main()
