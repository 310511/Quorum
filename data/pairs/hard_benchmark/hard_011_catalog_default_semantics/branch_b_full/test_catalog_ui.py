import unittest
from catalog_ui import preview_catalog

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_catalog()), 10)

if __name__ == "__main__":
    unittest.main()
