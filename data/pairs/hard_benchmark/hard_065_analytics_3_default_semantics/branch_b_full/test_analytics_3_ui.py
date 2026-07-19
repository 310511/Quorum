import unittest
from analytics_3_ui import preview_analytics_3

class UiTests(unittest.TestCase):
    def test_preview(self):
        self.assertEqual(len(preview_analytics_3()), 10)

if __name__ == "__main__":
    unittest.main()
