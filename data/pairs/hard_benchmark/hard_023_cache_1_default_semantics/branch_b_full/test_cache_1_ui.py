import unittest
from cache_1_ui import preview_cache_1

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_cache_1()), 10)

if __name__ == "__main__":
    unittest.main()
