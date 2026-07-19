import unittest
from search_2_ui import preview_search_2

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_search_2()), 10)

if __name__ == "__main__":
    unittest.main()
