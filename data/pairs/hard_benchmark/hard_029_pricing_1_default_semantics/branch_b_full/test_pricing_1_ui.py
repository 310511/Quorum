import unittest
from pricing_1_ui import preview_pricing_1

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_pricing_1()), 10)

if __name__ == "__main__":
    unittest.main()
