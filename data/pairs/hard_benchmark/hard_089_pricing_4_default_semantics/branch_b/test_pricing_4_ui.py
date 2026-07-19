import unittest
from pricing_4_ui import preview_pricing_4

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_pricing_4()), 10)

if __name__ == "__main__":
    unittest.main()
