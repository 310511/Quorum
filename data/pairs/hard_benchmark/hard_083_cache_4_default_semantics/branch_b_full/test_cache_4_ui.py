import unittest
from cache_4_ui import preview_cache_4

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_cache_4()), 10)

if __name__ == "__main__":
    unittest.main()
