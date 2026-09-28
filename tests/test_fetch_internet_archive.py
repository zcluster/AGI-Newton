import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fetch_internet_archive import choose_text_file  # noqa: E402


class InternetArchiveFileSelectionTest(unittest.TestCase):
    def test_prefers_djvu_text_over_derived_search_text(self):
        files = [
            {"name": "book_searchtext.txt", "format": "Text", "size": "900"},
            {"name": "book.txt", "format": "Text", "size": "800"},
            {"name": "book_djvu.txt", "format": "DjVuTXT", "size": "700"},
        ]
        self.assertEqual(choose_text_file(files)["name"], "book_djvu.txt")

    def test_returns_none_without_plain_text(self):
        self.assertIsNone(choose_text_file([{"name": "book.pdf", "format": "PDF"}]))


if __name__ == "__main__":
    unittest.main()

